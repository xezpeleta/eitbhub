#!/usr/bin/env python3
"""
Test script to verify published_on is being captured from API responses
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.primeran_api import PrimeranAPI
from src.makusi_api import MakusiAPI
from src.etbon_api import EtbonAPI


def test_primeran():
    """Test Primeran API captures published_on"""
    print("\n" + "=" * 80)
    print("Testing Primeran API")
    print("=" * 80)
    
    try:
        api = PrimeranAPI()
        api.login()
        
        # Test with a known series
        series_slug = "altsasu"
        print(f"\nFetching episodes from series: {series_slug}")
        
        episodes = api.get_all_episodes_from_series(series_slug)
        
        if episodes:
            print(f"✓ Found {len(episodes)} episodes")
            
            # Check first few episodes for published_on
            for i, episode in enumerate(episodes[:3], 1):
                published_on = episode.get('published_on')
                slug = episode.get('episode_slug')
                title = episode.get('episode_title')
                
                if published_on:
                    print(f"  {i}. {slug}: {title}")
                    print(f"     ✓ published_on: {published_on}")
                else:
                    print(f"  {i}. {slug}: {title}")
                    print(f"     ✗ published_on: NOT FOUND")
            
            # Summary
            with_dates = sum(1 for ep in episodes if ep.get('published_on'))
            print(f"\nSummary: {with_dates}/{len(episodes)} episodes have published_on")
            
            if with_dates == len(episodes):
                print("✓ All episodes have published_on field")
                return True
            elif with_dates > 0:
                print("⚠ Some episodes missing published_on field")
                return False
            else:
                print("✗ No episodes have published_on field")
                return False
        else:
            print("✗ No episodes found")
            return False
            
    except Exception as e:
        print(f"✗ Error testing Primeran: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_makusi():
    """Test Makusi API captures published_on"""
    print("\n" + "=" * 80)
    print("Testing Makusi API")
    print("=" * 80)
    
    try:
        api = MakusiAPI()
        api.login()
        
        # Test with a known series
        series_slug = "kody-kapow"
        print(f"\nFetching episodes from series: {series_slug}")
        
        episodes = api.get_all_episodes_from_series(series_slug)
        
        if episodes:
            print(f"✓ Found {len(episodes)} episodes")
            
            # Check first few episodes for published_on
            for i, episode in enumerate(episodes[:3], 1):
                published_on = episode.get('published_on')
                slug = episode.get('episode_slug')
                title = episode.get('episode_title')
                
                if published_on:
                    print(f"  {i}. {slug}: {title}")
                    print(f"     ✓ published_on: {published_on}")
                else:
                    print(f"  {i}. {slug}: {title}")
                    print(f"     ✗ published_on: NOT FOUND")
            
            # Summary
            with_dates = sum(1 for ep in episodes if ep.get('published_on'))
            print(f"\nSummary: {with_dates}/{len(episodes)} episodes have published_on")
            
            if with_dates == len(episodes):
                print("✓ All episodes have published_on field")
                return True
            elif with_dates > 0:
                print("⚠ Some episodes missing published_on field")
                return False
            else:
                print("✗ No episodes have published_on field")
                return False
        else:
            print("✗ No episodes found")
            return False
            
    except Exception as e:
        print(f"✗ Error testing Makusi: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_etbon():
    """Test ETB On API captures published_on"""
    print("\n" + "=" * 80)
    print("Testing ETB On API")
    print("=" * 80)
    
    try:
        api = EtbonAPI()
        api.login()
        
        # Test with a known series
        series_slug = "krimenak-gure-kronika-beltza"
        print(f"\nFetching episodes from series: {series_slug}")
        
        episodes = api.get_all_episodes_from_series(series_slug)
        
        if episodes:
            print(f"✓ Found {len(episodes)} episodes")
            
            # Check first few episodes for published_on
            for i, episode in enumerate(episodes[:3], 1):
                published_on = episode.get('published_on')
                slug = episode.get('episode_slug')
                title = episode.get('episode_title')
                
                if published_on:
                    print(f"  {i}. {slug}: {title}")
                    print(f"     ✓ published_on: {published_on}")
                else:
                    print(f"  {i}. {slug}: {title}")
                    print(f"     ✗ published_on: NOT FOUND")
            
            # Summary
            with_dates = sum(1 for ep in episodes if ep.get('published_on'))
            print(f"\nSummary: {with_dates}/{len(episodes)} episodes have published_on")
            
            if with_dates == len(episodes):
                print("✓ All episodes have published_on field")
                return True
            elif with_dates > 0:
                print("⚠ Some episodes missing published_on field")
                return False
            else:
                print("✗ No episodes have published_on field")
                return False
        else:
            print("✗ No episodes found")
            return False
            
    except Exception as e:
        print(f"✗ Error testing ETB On: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("Testing published_on field capture across all platforms")
    print("=" * 80)
    
    results = {
        'primeran': test_primeran(),
        'makusi': test_makusi(),
        'etbon': test_etbon()
    }
    
    print("\n" + "=" * 80)
    print("Final Results")
    print("=" * 80)
    
    for platform, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{platform.capitalize()}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n✓ All platforms successfully capture published_on!")
        print("You can now run the full scraper to populate the database.")
        sys.exit(0)
    else:
        print("\n✗ Some platforms failed to capture published_on")
        print("Please review the errors above before running full scrape.")
        sys.exit(1)
