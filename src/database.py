#!/usr/bin/env python3
"""
Database layer for storing content and geo-restriction data
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path


class ContentDatabase:
    """SQLite database for Primeran content and geo-restriction data"""
    
    def __init__(self, db_path: str = "platforms/primeran/primeran_content.db"):
        """
        Initialize database connection
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        cursor = self.conn.cursor()
        
        # Main content table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slug TEXT UNIQUE NOT NULL,
                title TEXT,
                type TEXT NOT NULL,  -- 'movie', 'episode', 'documentary', 'concert', etc.
                duration INTEGER,  -- Duration in seconds
                year INTEGER,
                genres TEXT,  -- JSON array
                series_slug TEXT,  -- For episodes, the parent series slug
                series_title TEXT,  -- For episodes, the parent series title
                season_number INTEGER,  -- For episodes
                episode_number INTEGER,  -- For episodes
                is_geo_restricted BOOLEAN,
                restriction_type TEXT,  -- 'manifest_403', 'manifest_404', etc.
                last_checked TIMESTAMP,
                metadata TEXT,  -- JSON blob with full API response
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Check history for tracking changes over time
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS check_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slug TEXT NOT NULL,
                checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                was_restricted BOOLEAN,
                status_code INTEGER,
                method_used TEXT,
                error TEXT,
                FOREIGN KEY (slug) REFERENCES content(slug)
            )
        """)
        
        # Indexes for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_content_type ON content(type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_content_geo_restricted ON content(is_geo_restricted)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_content_series_slug ON content(series_slug)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_check_history_slug ON check_history(slug)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_check_history_checked_at ON check_history(checked_at)
        """)
        
        self.conn.commit()
    
    def upsert_content(self, content_data: Dict[str, Any]) -> int:
        """
        Insert or update content record
        
        Args:
            content_data: Dictionary with content information
            
        Returns:
            Content ID
        """
        cursor = self.conn.cursor()
        
        # Prepare data
        slug = content_data['slug']
        title = content_data.get('title')
        content_type = content_data.get('type', 'unknown')
        duration = content_data.get('duration')
        year = content_data.get('year')
        genres = json.dumps(content_data.get('genres', [])) if content_data.get('genres') else None
        series_slug = content_data.get('series_slug')
        series_title = content_data.get('series_title')
        season_number = content_data.get('season_number')
        episode_number = content_data.get('episode_number')
        is_geo_restricted = content_data.get('is_geo_restricted')
        restriction_type = content_data.get('restriction_type')
        metadata = json.dumps(content_data.get('metadata', {}))
        last_checked = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO content (
                slug, title, type, duration, year, genres,
                series_slug, series_title, season_number, episode_number,
                is_geo_restricted, restriction_type, last_checked, metadata
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(slug) DO UPDATE SET
                title = excluded.title,
                type = excluded.type,
                duration = excluded.duration,
                year = excluded.year,
                genres = excluded.genres,
                series_slug = excluded.series_slug,
                series_title = excluded.series_title,
                season_number = excluded.season_number,
                episode_number = excluded.episode_number,
                is_geo_restricted = excluded.is_geo_restricted,
                restriction_type = excluded.restriction_type,
                last_checked = excluded.last_checked,
                metadata = excluded.metadata,
                updated_at = CURRENT_TIMESTAMP
        """, (
            slug, title, content_type, duration, year, genres,
            series_slug, series_title, season_number, episode_number,
            is_geo_restricted, restriction_type, last_checked, metadata
        ))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_content_status(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        Get existing content's geo-restriction status
        
        Args:
            slug: Content slug
            
        Returns:
            Dictionary with is_geo_restricted and restriction_type, or None if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT is_geo_restricted, restriction_type 
            FROM content 
            WHERE slug = ?
        """, (slug,))
        row = cursor.fetchone()
        if row:
            return {
                'is_geo_restricted': row['is_geo_restricted'],
                'restriction_type': row['restriction_type']
            }
        return None
    
    def add_check_history(self, slug: str, check_result: Dict[str, Any]):
        """
        Add a check history record
        
        Args:
            slug: Content slug
            check_result: Result from geo-restriction check
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO check_history (
                slug, was_restricted, status_code, method_used, error
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            slug,
            check_result.get('is_geo_restricted'),
            check_result.get('status_code'),
            'manifest_check',
            check_result.get('error')
        ))
        
        self.conn.commit()
    
    def get_content(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        Get content by slug
        
        Args:
            slug: Content slug
            
        Returns:
            Content dictionary or None if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM content WHERE slug = ?", (slug,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def get_all_content(self, 
                       content_type: Optional[str] = None,
                       geo_restricted_only: bool = False) -> List[Dict[str, Any]]:
        """
        Get all content with optional filters
        
        Args:
            content_type: Filter by type (e.g., 'episode', 'movie')
            geo_restricted_only: Only return geo-restricted content
            
        Returns:
            List of content dictionaries
        """
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM content WHERE 1=1"
        params = []
        
        if content_type:
            query += " AND type = ?"
            params.append(content_type)
        
        if geo_restricted_only:
            query += " AND is_geo_restricted = 1"
        
        query += " ORDER BY title"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics
        
        Returns:
            Dictionary with statistics
        """
        cursor = self.conn.cursor()
        
        stats = {}
        
        # Total content
        cursor.execute("SELECT COUNT(*) FROM content")
        stats['total_content'] = cursor.fetchone()[0]
        
        # By type
        cursor.execute("""
            SELECT type, COUNT(*) as count 
            FROM content 
            GROUP BY type
        """)
        stats['by_type'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Geo-restricted
        cursor.execute("SELECT COUNT(*) FROM content WHERE is_geo_restricted = 1")
        stats['geo_restricted_count'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM content WHERE is_geo_restricted = 0")
        stats['accessible_count'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM content WHERE is_geo_restricted IS NULL")
        stats['unknown_count'] = cursor.fetchone()[0]
        
        # Percentage
        if stats['total_content'] > 0:
            stats['geo_restricted_percentage'] = (
                stats['geo_restricted_count'] / stats['total_content'] * 100
            )
        else:
            stats['geo_restricted_percentage'] = 0
        
        # Last check
        cursor.execute("SELECT MAX(last_checked) FROM content")
        stats['last_check'] = cursor.fetchone()[0]
        
        return stats
    
    def close(self):
        """Close database connection"""
        self.conn.close()
