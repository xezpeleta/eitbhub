# Geo-Restriction Detection Methodology

This document explains how the geo-restriction detection system works. The methodology applies to all platforms in this project (Primeran, Makusi, Guau, Etbon).

---

## Overview

The geo-restriction checker identifies content that is not accessible from certain geographic locations by testing access to video manifest files. Content is marked as geo-restricted if the manifest URL returns a `403 Forbidden` status code.

---

## Detection Methods Tested

### Method 1: Manifest URL Check ✅ (Selected)

**How it works:**
1. For each media item or episode, construct the DASH manifest URL (platform-specific):
   ```
   https://{platform_domain}/manifests/{slug}/{lang}/widevine/dash.mpd
   ```
   Example for Primeran: `https://primeran.eus/manifests/{slug}/eu/widevine/dash.mpd`
2. Send a HEAD request to check accessibility
3. Interpret the response:
   - `200 OK` → Content is accessible (not geo-restricted)
   - `403 Forbidden` → Content is geo-restricted
   - `404 Not Found` → Content doesn't exist or slug is incorrect

**Why this method:**
- ✅ **Reliable**: 100% accuracy verified against browser behavior
- ✅ **Fast**: HEAD requests are lightweight
- ✅ **Simple**: No complex parsing or DRM handling required
- ✅ **Direct**: Tests actual video access, not just metadata

**Verification:**
- Tested against known geo-restricted content (`27-ordu`, `itoiz-udako-sesioak`)
- Results match browser behavior exactly (100% accuracy confirmed)

---

### Method 2: Metadata Analysis ❌ (Rejected)

**How it works:**
- Analyze API response metadata for geo-restriction indicators
- Check for flags, error messages, or availability fields

**Why rejected:**
- ❌ **Insufficient**: API metadata doesn't reliably indicate geo-restrictions
- ❌ **Inconsistent**: Some restricted content has no metadata indicators
- ❌ **Unreliable**: False positives and negatives

---

### Method 3: DRM License Check ❌ (Not Implemented)

**How it works:**
- Attempt to acquire a DRM license for the content
- Interpret license server response

**Why not implemented:**
- ❌ **Complex**: Requires Widevine CDM (Content Decryption Module)
- ❌ **Legal concerns**: CDM libraries have licensing restrictions
- ❌ **Overkill**: Manifest check is sufficient and simpler

---

## Content Types

### Individual Media Items

For standalone media (movies, documentaries, concerts):
1. Get media metadata from `/api/v1/media/{slug}`
2. Test manifest URL: `/manifests/{slug}/eu/widevine/dash.mpd`
3. Mark as restricted if status is `403`

**Example (Primeran):**
```python
# Media: "la-infiltrada"
manifest_url = "https://primeran.eus/manifests/la-infiltrada/eu/widevine/dash.mpd"
response = requests.head(manifest_url)
# 200 = accessible, 403 = geo-restricted
```

---

### Series and Episodes

**Important**: Series do NOT have manifest URLs. Only individual episodes do.

**Process:**
1. Get series metadata from platform API (e.g., `/api/v1/series/{slug}`)
2. Iterate through all seasons and episodes
3. For each episode, test its manifest URL (platform-specific format)
4. Mark each episode individually as restricted or accessible

**Example (Primeran):**
```python
# Series: "lau-hankan"
series = api.get_series("lau-hankan")

for season in series['seasons']:
    for episode in season['episodes']:
        episode_slug = episode['slug']
        manifest_url = f"https://primeran.eus/manifests/{episode_slug}/eu/widevine/dash.mpd"
        response = requests.head(manifest_url)
        # Check status: 200 = accessible, 403 = geo-restricted
```

**Why this approach:**
- Different episodes in the same series can have different geo-restriction status
- Some episodes may be accessible while others are restricted
- Provides granular information about content availability

---

## API-Level vs Manifest-Level Restrictions

### API-Level Restrictions (403 at `/api/v1/media/{slug}`)

Some content is restricted at the API level:
- Requesting `/api/v1/media/{slug}` returns `403 Forbidden`
- Cannot retrieve metadata
- Automatically marked as geo-restricted

**Handling:**
- Save with `is_geo_restricted: True`
- `restriction_type: 'api_403'`
- Limited metadata (title derived from slug)

**Example (Primeran):**
```python
response = session.get(f"https://primeran.eus/api/v1/media/27-ordu")
# Status: 403 Forbidden
# → Marked as geo-restricted at API level
```

---

### Manifest-Level Restrictions (403 at manifest URL)

Most restrictions are at the manifest level:
- API metadata is accessible
- Manifest URL returns `403 Forbidden`
- Content appears in listings but cannot be streamed

**Handling:**
- Save with full metadata
- `is_geo_restricted: True`
- `restriction_type: 'manifest_403'`

**Example (Primeran):**
```python
media = api.get_media("itoiz-udako-sesioak")  # 200 OK
manifest_url = "https://primeran.eus/manifests/itoiz-udako-sesioak/eu/widevine/dash.mpd"
response = requests.head(manifest_url)  # 403 Forbidden
# → Marked as geo-restricted at manifest level
```

---

## Content Discovery

The scraper discovers content through multiple methods:

### 1. Search API
- Platform-specific search endpoint (e.g., `/api/v1/search?q=`)
- Empty query may return all content (platform-dependent)
- Filters by content type (media, series, etc.)

### 2. Category Pages
- Platform-specific category endpoints (e.g., `/api/v1/pages/{category}`)
- Recursively extracts slugs from nested structures
- Categories vary by platform

### 3. Home Page
- Platform-specific home endpoint (e.g., `/api/v1/home`)
- Extracts featured and recommended content
- Includes all content types

### 4. Series Episode Discovery
- For each series, fetch platform-specific series endpoint (e.g., `/api/v1/series/{slug}`)
- Extract all episode slugs from seasons
- Test each episode individually

**Note**: Exact endpoints and structures vary by platform. See platform-specific API documentation for details.

---

## Error Handling

### 404 Not Found
- **Cause**: Item doesn't exist or slug is incorrect
- **Action**: Skip item (not saved to database)
- **Reason**: Likely a collection/category page, not actual media

### 403 Forbidden (API Level)
- **Cause**: Content is geo-restricted at API level
- **Action**: Save as geo-restricted with limited metadata
- **Type**: `api_403`

### 403 Forbidden (Manifest Level)
- **Cause**: Content is geo-restricted at manifest level
- **Action**: Save as geo-restricted with full metadata
- **Type**: `manifest_403`

### Network Errors
- **Cause**: Connection issues, timeouts
- **Action**: Log error, continue with next item
- **Retry**: Not implemented (would require queue system)

---

## Database Schema

### Content Table
- `slug` (PRIMARY KEY) - Unique identifier
- `title` - Content title
- `type` - Content type (episode, vod, etc.)
- `is_geo_restricted` - Boolean flag
- `restriction_type` - `api_403`, `manifest_403`, `manifest_200`, etc.
- `series_slug` - For episodes, parent series
- `season_number` - For episodes
- `episode_number` - For episodes
- `last_checked` - Timestamp of last check
- `metadata` - Full JSON metadata (see "Metadata Structure" section below)

### Check History Table
- Tracks historical checks
- Enables analysis of restriction changes over time
- Links to content via `slug` foreign key

---

## Metadata Structure

The `metadata` field in the database stores different structures depending on the content type and how it was discovered:

### 1. Regular Media Items (Movies, Documentaries, Concerts, VOD)

For individual media items, `metadata` contains the **complete JSON response** from `GET /api/v1/media/{slug}`. This includes:

**Core Fields:**
- `id` - Numeric media ID
- `slug` - URL-friendly identifier
- `title` - Content title
- `type` - Content type (`vod`, `movie`, `documentary`, `concert`, etc.)
- `description` - Full description/synopsis
- `duration` - Duration in seconds
- `production_year` - Production/release year
- `collection` - Content collection type (`media`, `series`, etc.)

**Access & Restrictions:**
- `access_restriction` - Access level (`registration_required`, `public`, `subscription_required`, etc.)
- `age_rating` - Age rating object with `id`, `age`, `label`, `background_color`, etc.
- `available_until` - Expiration date (ISO 8601)
- `offline_expiration_date` - Offline availability expiration

**Media Assets:**
- `images` - Array of image objects, each with:
  - `id`, `file` (CDN URL), `width`, `height`, `format`, `has_text`
  - Different formats: landscape, portrait, slider, square, etc.
- `manifests` - Array of streaming manifest objects with:
  - `manifestURL` - Path to DASH/HLS manifest
  - `type` - Stream type (`dash`, `hls`)
  - `drmConfig` - DRM configuration (Widevine, PlayReady, FairPlay)
  - `thumbnailMetadata` - Thumbnail/preview configuration

**Audio/Subtitle Tracks:**
- `audios` - Array of available audio languages with:
  - `id`, `code`, `label`, `transcoding_code`
- `subtitle` / `subtitles` - Arrays of subtitle track objects with:
  - `id`, `file` (VTT URL), `language` object, `sort`

**Additional Metadata:**
- `custom_tags` - Array of custom tag objects (e.g., "Euskal Zinema Icon")
- `eitb_visual_radio` - Boolean flag
- `is_external_manifest` - Boolean flag
- `is_playable_offline` - Boolean flag
- `media_format` - Format type (e.g., `episode`)
- `media_type` - Media type (e.g., `video`)
- `theme` - Complete theme configuration object (large, includes all UI icons/logos)

**Example Structure:**
```json
{
  "id": 112598,
  "slug": "la-infiltrada",
  "title": "La infiltrada",
  "type": "vod",
  "description": "Hainbat urtez ezker abertzaleko giroetan...",
  "duration": 6817,
  "production_year": 2024,
  "access_restriction": "registration_required",
  "age_rating": {
    "id": 3,
    "age": 12,
    "label": "+12",
    "background_color": "#FFC23B"
  },
  "images": [
    {
      "id": 76121,
      "file": "https://cdnstorage.primeran.eus/directus/eitb/...",
      "width": 3840,
      "format": 6,
      "height": 1380,
      "has_text": true
    }
  ],
  "manifests": [
    {
      "manifestURL": "/manifests/la-infiltrada/eu/widevine/dash.mpd",
      "type": "dash",
      "drmConfig": {
        "type": "widevine",
        "licenseAcquisitionURL": "/drm/widevine/112598/..."
      }
    }
  ],
  "audios": [
    {
      "id": 1,
      "code": "eu",
      "label": "Euskara",
      "transcoding_code": "baq"
    }
  ],
  "subtitle": [
    {
      "id": 92505,
      "file": "https://cdnstorage.primeran.eus/directus/eitb/...",
      "language": {
        "id": 1,
        "code": "eu",
        "label": "Euskara"
      }
    }
  ]
}
```

### 2. Episodes (from Series)

For episodes, `metadata` contains a **transformed object** created by `get_all_episodes_from_series()`, not the raw API response. This is a flattened structure:

**Fields:**
- `episode_id` - Numeric episode ID
- `episode_slug` - Episode slug
- `episode_title` - Episode title
- `episode_number` - Episode number within season
- `duration` - Duration in seconds
- `series_slug` - Parent series slug
- `series_title` - Parent series title
- `season_number` - Season number
- `type` - Always `"episode"`

**Example Structure:**
```json
{
  "episode_id": 36867,
  "episode_slug": "erreserban-1-leire-juanes",
  "episode_title": "1. Leire Juanes",
  "episode_number": 1,
  "duration": 1190,
  "series_slug": "erreserban",
  "series_title": "Erreserban",
  "season_number": 1046,
  "type": "episode"
}
```

**Note**: Episodes do NOT contain the full API response. To get complete episode metadata, you would need to call `/api/v1/media/{episode_slug}` separately.

### 3. API-Level Geo-Restricted Items

For content that returns `403 Forbidden` at the API level (e.g., `/api/v1/media/{slug}`), `metadata` contains only error information:

**Fields:**
- `error` - Error message (e.g., `"MEDIA_GEO_RESTRICTED_ACCESS"`)
- `api_restricted` - Boolean flag set to `true`

**Example Structure:**
```json
{
  "error": "MEDIA_GEO_RESTRICTED_ACCESS",
  "api_restricted": true
}
```

**Note**: Full metadata is not available for these items since the API request fails. The title is derived from the slug.

---

## Metadata vs. Exported JSON

**Important**: The full `metadata` JSON blob is only stored in the SQLite database. The exported JSON files (`dashboard/data/content.json`) contain a **subset** of fields for performance reasons:

**Exported Fields:**
- `slug`, `title`, `type`
- `duration`, `year`
- `genres` (as array of strings)
- `series_slug`, `series_title`
- `season_number`, `episode_number`
- `is_geo_restricted`, `restriction_type`
- `last_checked`

**Not Exported:**
- Full `metadata` JSON (too large)
- Complete image arrays
- Manifest configurations
- Theme objects
- Full subtitle/audio track details

To access the complete metadata, query the SQLite database directly.

---

## Verification Process

### Browser Verification
1. Open browser developer tools
2. Navigate to content page on the platform
3. Attempt to play video
4. Check network tab for manifest request
5. Compare status code with script results

**Result**: 100% match between browser behavior and script results (verified for Primeran platform)

---

## Statistics (Primeran Example)

As of 2026-01-04:
- **Total content**: 6,294 items
- **Geo-restricted**: 1,503 items (23.9%)
- **Accessible**: 4,791 items (76.1%)
- **API-level restrictions**: 32 items
- **Manifest-level restrictions**: 1,471 items

*Statistics will vary by platform. See platform-specific documentation for current numbers.*

---

## Limitations

1. **Rate Limiting**: Scraper includes delays to avoid overwhelming the API
2. **Time**: Full scrape takes several hours for large content catalogs
3. **Network**: Requires stable internet connection
4. **Authentication**: Requires valid platform account credentials
5. **Dynamic Content**: New content added after scraping won't appear until next run

---

## Future Improvements

- [ ] Implement retry logic for network errors
- [ ] Add incremental updates (only check new/changed content)
- [ ] Track restriction changes over time
- [ ] Add support for other EITB platforms (Makusi, Guau, Etbon)
- [ ] Implement parallel checking for faster scraping
- [ ] Platform-specific detection method customization

---

*Last updated: 2026-01-04*
