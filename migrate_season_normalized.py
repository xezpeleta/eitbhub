#!/usr/bin/env python3
"""
Migration script to add and populate season_number_normalized column

This script migrates all existing databases to add the season_number_normalized
column and populates it with normalized values (1, 2, 3...) per series.

Usage:
    python migrate_season_normalized.py
"""

import os
import sys
from pathlib import Path

# Add src to path so we can import the database module
sys.path.insert(0, str(Path(__file__).parent))

from src.database import ContentDatabase


def main():
    """Run migration on all platform databases"""
    print("=" * 80)
    print("Season Number Normalization Migration")
    print("=" * 80)
    print()
    
    # Support all platforms
    databases = [
        'platforms/primeran/primeran_content.db',
        'platforms/makusi/makusi_content.db',
        'platforms/etbon/etbon_content.db'
    ]
    
    migrated_count = 0
    skipped_count = 0
    
    for db_path in databases:
        if os.path.exists(db_path):
            print(f"Processing: {db_path}")
            try:
                # Create database connection - migration runs automatically in __init__
                db = ContentDatabase(db_path)
                
                # Count episodes with normalized season numbers
                cursor = db.conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM content 
                    WHERE season_number_normalized IS NOT NULL
                """)
                normalized_count = cursor.fetchone()[0]
                
                # Count total episodes
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM content 
                    WHERE type = 'episode'
                """)
                total_episodes = cursor.fetchone()[0]
                
                # Count total content
                cursor.execute("SELECT COUNT(*) FROM content")
                total_content = cursor.fetchone()[0]
                
                db.close()
                
                print(f"  ✓ Migration complete")
                print(f"    - Total content: {total_content}")
                print(f"    - Total episodes: {total_episodes}")
                print(f"    - Episodes with normalized seasons: {normalized_count}")
                print()
                
                migrated_count += 1
            except Exception as e:
                print(f"  ✗ Error migrating {db_path}: {e}")
                import traceback
                traceback.print_exc()
                print()
        else:
            print(f"Skipping: {db_path} (not found)")
            print()
            skipped_count += 1
    
    print("=" * 80)
    print("Migration Summary")
    print("=" * 80)
    print(f"Databases migrated: {migrated_count}")
    print(f"Databases skipped: {skipped_count}")
    print()
    
    if migrated_count > 0:
        print("✓ Migration completed successfully!")
    else:
        print("⚠ No databases were migrated")


if __name__ == '__main__':
    main()
