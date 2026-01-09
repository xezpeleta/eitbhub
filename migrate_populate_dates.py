#!/usr/bin/env python3
"""
Migration script to populate available_until and publication_date columns
from metadata JSON for existing content records.

Optimized for large databases (18K+ records) with memory-efficient batch processing.
"""

import sqlite3
import json
import sys
from pathlib import Path


def populate_dates(db_path: str, batch_size: int = 500):
    """
    Populate available_until and publication_date columns from metadata.
    
    Args:
        db_path: Path to SQLite database
        batch_size: Number of records to process per batch (default: 500)
    """
    print(f"Starting migration for: {db_path}")
    print(f"Batch size: {batch_size} records")
    print("-" * 60)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    # Get total count
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM content")
    total_count = cursor.fetchone()[0]
    print(f"Total content records: {total_count}")
    
    # Check how many already have dates
    cursor.execute("""
        SELECT COUNT(*) FROM content 
        WHERE available_until IS NOT NULL OR publication_date IS NOT NULL
    """)
    already_populated = cursor.fetchone()[0]
    print(f"Already populated: {already_populated}")
    print(f"To process: {total_count - already_populated}")
    print("-" * 60)
    
    # Process in batches to avoid memory issues
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    offset = 0
    
    while True:
        # Fetch batch
        cursor.execute("""
            SELECT id, metadata 
            FROM content 
            ORDER BY id
            LIMIT ? OFFSET ?
        """, (batch_size, offset))
        
        batch = cursor.fetchall()
        
        if not batch:
            break
        
        # Process batch
        for row in batch:
            content_id = row['id']
            metadata_json = row['metadata']
            
            if not metadata_json:
                skipped_count += 1
                continue
            
            try:
                metadata = json.loads(metadata_json)
                
                # Extract available_until
                available_until = metadata.get('available_until')
                
                # Extract publication_date - prefer content date_created, fallback to oldest image
                publication_date = metadata.get('date_created')
                if not publication_date:
                    images = metadata.get('images', [])
                    if images and isinstance(images, list):
                        image_dates = [
                            img.get('date_created') 
                            for img in images 
                            if isinstance(img, dict) and img.get('date_created')
                        ]
                        if image_dates:
                            publication_date = min(image_dates)
                
                # Update if we have at least one date
                if available_until or publication_date:
                    cursor.execute("""
                        UPDATE content 
                        SET available_until = ?, publication_date = ?
                        WHERE id = ?
                    """, (available_until, publication_date, content_id))
                    updated_count += 1
                else:
                    skipped_count += 1
            
            except (json.JSONDecodeError, TypeError, ValueError) as e:
                error_count += 1
                if error_count <= 5:  # Only print first few errors
                    print(f"  ⚠️  Error processing record ID {content_id}: {e}")
                continue
        
        # Commit batch
        conn.commit()
        
        # Progress update
        offset += batch_size
        processed = min(offset, total_count)
        percentage = (processed / total_count * 100) if total_count > 0 else 0
        print(f"  Progress: {processed}/{total_count} ({percentage:.1f}%) - "
              f"Updated: {updated_count}, Skipped: {skipped_count}, Errors: {error_count}")
    
    conn.close()
    
    print("-" * 60)
    print("✓ Migration complete!")
    print(f"  Total records processed: {total_count}")
    print(f"  Successfully updated: {updated_count}")
    print(f"  Skipped (no dates): {skipped_count}")
    print(f"  Errors: {error_count}")
    
    return updated_count, skipped_count, error_count


def verify_migration(db_path: str):
    """Verify the migration results"""
    print("\n" + "=" * 60)
    print("VERIFICATION")
    print("=" * 60)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check columns exist
    cursor.execute("PRAGMA table_info(content)")
    columns = {row[1] for row in cursor.fetchall()}
    
    if 'available_until' not in columns or 'publication_date' not in columns:
        print("❌ ERROR: Columns not found!")
        conn.close()
        return False
    
    print("✓ Columns exist: available_until, publication_date")
    
    # Check indexes
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='content'")
    indexes = {row[0] for row in cursor.fetchall()}
    
    if 'idx_content_available_until' in indexes:
        print("✓ Index exists: idx_content_available_until")
    else:
        print("⚠️  Index missing: idx_content_available_until")
    
    if 'idx_content_publication_date' in indexes:
        print("✓ Index exists: idx_content_publication_date")
    else:
        print("⚠️  Index missing: idx_content_publication_date")
    
    # Statistics
    cursor.execute("SELECT COUNT(*) FROM content")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM content WHERE available_until IS NOT NULL")
    with_available = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM content WHERE publication_date IS NOT NULL")
    with_publication = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM content 
        WHERE available_until IS NOT NULL OR publication_date IS NOT NULL
    """)
    with_any_date = cursor.fetchone()[0]
    
    print(f"\nStatistics:")
    print(f"  Total records: {total}")
    print(f"  With available_until: {with_available} ({with_available/total*100:.1f}%)")
    print(f"  With publication_date: {with_publication} ({with_publication/total*100:.1f}%)")
    print(f"  With any date: {with_any_date} ({with_any_date/total*100:.1f}%)")
    
    # Sample data
    print("\nSample records:")
    cursor.execute("""
        SELECT slug, available_until, publication_date 
        FROM content 
        WHERE available_until IS NOT NULL OR publication_date IS NOT NULL
        LIMIT 3
    """)
    for row in cursor.fetchall():
        print(f"  {row[0][:50]:<50} | avail: {row[1][:19] if row[1] else 'NULL':<19} | pub: {row[2][:19] if row[2] else 'NULL':<19}")
    
    conn.close()
    return True


if __name__ == "__main__":
    # Default database path
    db_path = "platforms/primeran/primeran_content.db"
    
    # Allow custom path from command line
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    
    # Check if database exists
    if not Path(db_path).exists():
        print(f"❌ ERROR: Database not found: {db_path}")
        sys.exit(1)
    
    # Run migration
    try:
        updated, skipped, errors = populate_dates(db_path, batch_size=500)
        verify_migration(db_path)
        
        if errors > 0:
            print(f"\n⚠️  Warning: {errors} errors occurred during migration")
            sys.exit(1)
        else:
            print("\n✓ All done! Migration completed successfully.")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Migration interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ ERROR: Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
