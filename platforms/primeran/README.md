# Primeran.eus Platform

## Overview

Primeran.eus is a Basque streaming platform operated by EITB. This platform provides access to Basque films, series, documentaries, and music content.

## Status

✅ **Complete** - API documented + Geo-restriction checker implemented

## Quick Start

### Authentication

Primeran uses **Gigya SSO** (SAP Customer Data Cloud) for authentication.

```python
import requests

session = requests.Session()
response = session.post('https://login.primeran.eus/accounts.login', data={
    'apiKey': '4_iXtBSPAhyZYN6kg3DlaQuQ',  # Public API key
    'loginID': 'your_username',
    'password': 'your_password',
    'format': 'json'
})

if response.json().get('errorCode') == 0:
    # Authenticated - can now access API
    profile = session.get('https://primeran.eus/api/v1/profiles/me').json()
```

### Environment Variables

Add to your `.env` file:

```bash
PRIMERAN_USERNAME=your_username_or_email
PRIMERAN_PASSWORD=your_password
```

### Running the Scraper

```bash
# Full scrape
uv run python run_scraper.py --platform primeran

# Test with limited items
uv run python run_scraper.py --platform primeran --limit 10

# Check specific content
uv run python run_scraper.py --platform primeran --media-slug la-infiltrada
```

## API Documentation

See [API.md](API.md) for complete API reference including:
- Authentication flow
- Content discovery endpoints
- Video streaming (MPEG-DASH, Widevine DRM)
- User management
- Analytics integration

## Current Statistics

- **Total content**: 6,294 items
- **Geo-restricted**: 1,503 items (23.9%)
- **Accessible**: 4,791 items (76.1%)
- **Last updated**: 2026-01-04

## Key Features

- ✅ Complete API documentation
- ✅ Automated geo-restriction detection
- ✅ Content discovery (media + series)
- ✅ SQLite database storage
- ✅ EITBHub web UI visualization

---

*For project-wide information, see the main [README.md](../../README.md)*
