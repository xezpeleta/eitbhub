---
name: add-etbon-platform-support
overview: Add full ETB On (etbon.eus) support to the scraper, database, and static content export so it behaves consistently with Primeran and Makusi.
todos:
  - id: api-client-etbon
    content: Add EtbonAPI client class in src/etbon_api.py with login, get_media, get_series, get_home_content (or equivalent), check_geo_restriction, and get_all_episodes_from_series, mirroring PrimeranAPI/MakusiAPI.
    status: completed
  - id: wire-scraper-etbon
    content: Wire EtbonAPI into run_scraper.py and ContentScraper so --platform etbon instantiates the new API client and runs discovery and checks.
    status: completed
    dependencies:
      - api-client-etbon
  - id: discovery-strategy-etbon
    content: Implement ETB On–specific discovery logic in ContentScraper.discover_media_from_sections and discover_series_from_sections using series API and EPG instead of Primeran-specific search/pages.
    status: completed
    dependencies:
      - wire-scraper-etbon
  - id: urls-etbon
    content: Update URL generation in ContentScraper._generate_platform_url and JSONExporter._get_content_url to support etbon.eus URLs and use metadata.platform_urls where available.
    status: completed
    dependencies:
      - wire-scraper-etbon
  - id: export-ui-etbon
    content: Ensure JSON export and docs dashboard include ETB On content, with filters and counts that treat 'etbon.eus' as a first-class platform.
    status: completed
    dependencies:
      - urls-etbon
  - id: test-etbon
    content: Run limited ETB On scrapes, export JSON, and manually verify DB rows and web UI entries for a sample of series and media.
    status: completed
    dependencies:
      - discovery-strategy-etbon
      - export-ui-etbon
---

# Plan: Add ETB On (etbon.eus) Platform Support

## 1. API client for ETB On

- **Create ETB On API client** in `src` mirroring existing patterns:
- Add a new `EtbonAPI` class in a file like [`src/etbon_api.py`](src/etbon_api.py).
- Reuse `PRIMERAN_USERNAME` / `PRIMERAN_PASSWORD` env vars and Gigya SSO, but with ETB On’s public key `4_eUfqY3nplenbM2JKHjSxLw` and `base_url = "https://etbon.eus/api/v1"`.
- Implement methods matching `PrimeranAPI` / `MakusiAPI` contracts used by `ContentScraper`:
- `platform` property returning `'etbon.eus'`.
- `login()` / `ensure_authenticated()`.
- `get_media(slug)`, `get_series(slug)`, `get_home_content()` (or suitable discovery endpoints if `/home` does not exist).
- `get_all_episodes_from_series(series_slug)` to return the normalized episodes list expected by `check_series`.
- `check_geo_restriction(slug, language='eu', media_metadata=None)`, even if it initially returns a stub with `is_geo_restricted=None` until streaming endpoints are fully reverse‑engineered.

## 2. Extend scraper to handle ETB On

- **Update scraper wiring** so ETB On can be selected as a platform:
- In [`run_scraper.py`](run_scraper.py), extend CLI options (e.g., `--platform etbon`) and instantiate `EtbonAPI` when requested.
- Pass the `EtbonAPI` instance into `ContentScraper(api=EtbonAPI(...), db=...)` just like Primeran/Makusi.
- **Discovery strategy for ETB On**:
- Add an ETB On branch inside `ContentScraper.discover_media_from_sections` and `.discover_series_from_sections` that uses ETB On endpoints instead of Primeran‑specific ones:
- Prefer EPG + series/media API if `/api/v1/home` is not available, or add `EtbonAPI.get_home_like_content()` if ETB On exposes a home endpoint later.
- For series: crawl curated rows by hitting a small, fixed set of `series` slugs (initially hard‑coded from UI, then optionally expanded via EPG or future search endpoints).
- For media: for each series, rely on `get_all_episodes_from_series` to enumerate episodes; for standalone films/specials, maintain a small curated list of known `media` slugs and call `check_media` on them.
- Ensure ETB On discovery runs independently of Primeran’s `/search` and `/pages` hacks so that existing logic is not broken.

## 3. Generate correct platform URLs

- **Teach scraper and exporter about ETB On URLs**:
- Update `ContentScraper._generate_platform_url` to handle `self.platform == 'etbon.eus'` and generate canonical ETB On URLs:
- Series: `https://etbon.eus/s/{slug}`.
- Episodes / media: `https://etbon.eus/m/{slug}`.
- Ensure these URLs are inserted into `metadata['platform_urls']['etbon.eus'] `via `_add_platform_url_to_metadata` for all ETB On items.
- Update `JSONExporter._get_content_url` so if the first platform is `'etbon.eus'`, it uses `platform_urls['etbon.eus']` when present, or falls back to a generated ETB On URL if not.

## 4. Database representation & stats

- **Platform storage**:
- Confirm the `ContentDatabase` schema can already store multiple platforms per slug (it appears to store a single `platform` column; if needed, keep storing `'etbon.eus'` as a simple string, consistent with `'primeran.eus'` / `'makusi.eus'`).
- Verify `get_statistics()` aggregates correctly when a third platform is present (no code changes may be needed if stats are platform‑agnostic).

## 5. Static content export & web UI

- **Include ETB On content in `docs` JSONs**:
- Run the exporter (`JSONExporter.export_all`, `export_statistics_only`, `export_geo_restricted_only`) without code changes to confirm that ETB On items are included correctly once `platform` is `'etbon.eus'` and `platform_urls` is set.
- If the front‑end dashboard groups or filters by platform (in `docs/js/dashboard.js` and `docs/data/content.json`), update the UI logic to:
- Recognize `'etbon.eus'` as a valid platform key.
- Optionally add ETB On‑specific filters / counts (e.g., show total ETB On items, geo‑restricted ratio, etc.).

## 6. Testing & validation

- **Unit‑style checks (manual):**
- Use `uv` to run a limited ETB On scrape:
- `uv run python run_scraper.py --platform etbon --limit 5`.
- Inspect the resulting DB rows for ETB On:
- Confirm `platform = 'etbon.eus'`, `metadata.platform_urls.etbon.eus` exists, and series/episode relationships look correct.
- **Export & UI sanity check:**
- Run the exporter and open the static dashboard:
- Confirm ETB On content appears with correct titles, thumbnails, platforms and links pointing to `https://etbon.eus/...`.
- Spot‑check a few ETB On items by clicking through from the dashboard to the live site.

## 7. Optional future enhancements

- Once streaming endpoints are fully known for ETB On:
- Extend `EtbonAPI.check_geo_restriction` to test live/VOD manifests (and DRM license if needed), mirroring the detailed geo‑check in Primeran/Makusi.
- Add automated discovery of ETB On content using any future `/home`, `/menus`, or `/search` endpoints that become visible, replacing any initial curated slug lists.