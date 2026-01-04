#!/usr/bin/env python3
"""
Main entry point for Primeran content scraper

Usage:
    python run_scraper.py [--test] [--media-slug SLUG] [--series-slug SLUG]
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.primeran_api import PrimeranAPI
from src.database import ContentDatabase
from src.scraper import ContentScraper
from src.exporter import JSONExporter


def main():
    parser = argparse.ArgumentParser(description='Scrape Primeran.eus content and check geo-restrictions')
    parser.add_argument('--test', action='store_true', help='Run with test data (few items)')
    parser.add_argument('--media-slug', help='Check specific media slug')
    parser.add_argument('--series-slug', help='Check specific series slug')
    parser.add_argument('--db', default='platforms/primeran/primeran_content.db', help='Database file path')
    parser.add_argument('--output-dir', default='dashboard/data', help='Output directory for JSON')
    parser.add_argument('--delay', type=float, default=0.5, help='Delay between requests (seconds)')
    parser.add_argument('--limit', type=int, help='Limit number of items to check (for testing)')
    
    args = parser.parse_args()
    
    try:
        # Initialize components
        print("Initializing API client...")
        api = PrimeranAPI()
        api.login()
        print("✓ Authenticated")
        
        print(f"Initializing database: {args.db}")
        db = ContentDatabase(args.db)
        print("✓ Database ready")
        
        scraper = ContentScraper(api, db, delay=args.delay)
        exporter = JSONExporter(db, args.output_dir)
        
        # Run scraper
        if args.test:
            # Test with known content
            print("\n[TEST MODE] Running with test data...")
            test_media = ['la-infiltrada', 'itoiz-udako-sesioak', 'gatibu-azken-kontzertua-zuzenean']
            test_series = ['lau-hankan', 'krimenak-gure-kronika-beltza']
            scraper.scrape_all(media_slugs=test_media, series_slugs=test_series)
        elif args.media_slug:
            print(f"\nChecking media: {args.media_slug}")
            scraper.check_media(args.media_slug)
        elif args.series_slug:
            print(f"\nChecking series: {args.series_slug}")
            scraper.check_series(args.series_slug)
        else:
            # Full scrape
            print("\n[FULL MODE] Starting full content scrape...")
            print("This will discover and check all content (may take a while)...")
            scraper.scrape_all(limit=args.limit)
        
        # Export to JSON
        print("\n" + "=" * 80)
        print("Exporting to JSON...")
        print("=" * 80)
        exporter.export_all()
        exporter.export_statistics_only()
        exporter.export_geo_restricted_only()
        
        print("\n✓ Scraping complete!")
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
