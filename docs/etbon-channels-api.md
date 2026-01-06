# ETB On (etbon.eus) - Live Channels API Documentation

This document describes the API endpoints used for live TV channels on ETB On.

## Overview

ETB On provides live streaming channels through a separate set of API endpoints from the on-demand content (VOD/series). Channels include both standard TV channels (ETB-1, ETB-2, etc.) and special "FAST" channels (Free Ad-Supported Streaming TV) like Euskadi Meteo.

## API Endpoints

### 1. List All Live Channels

**Endpoint:** `GET /api/v1/pages/zuzenekoak`

**Description:** Returns the live channels page structure with all available channels.

**Response Structure:**
```json
{
  "id": 123,
  "slug": "zuzenekoak",
  "title": "Zuzenekoak",
  "children": [
    {
      "type": "row",
      "children": [
        {
          "slug": "euskadi-meteo",
          "title": "Euskadi Meteo",
          "type": "live",
          "m3u8": "https://cdn1.etbon.eus/meteo/index.m3u8",
          "mpd": "https://cdn1.etbon.eus/meteo/index.mpd",
          "is_fast_channel": true
        },
        {
          "slug": "etb-1",
          "title": "ETB 1",
          "type": "live",
          "is_fast_channel": false
        }
      ]
    }
  ]
}
```

**Notes:**
- Channels are nested within `children` arrays (sometimes in row objects)
- Each channel has a `slug` identifier
- FAST channels (`is_fast_channel: true`) may include direct manifest URLs
- Standard TV channels require authentication and may be geo-restricted

### 2. Get Channel Stream Metadata

**Endpoint:** `GET /api/v1/stream/{slug}`

**Description:** Returns detailed streaming information for a specific channel, including manifest URLs and geo-restriction status.

**Example:** `GET /api/v1/stream/euskadi-meteo`

**Response Structure (Accessible Channel):**
```json
{
  "slug": "euskadi-meteo",
  "title": "Euskadi Meteo",
  "manifests": [
    {
      "type": "dash",
      "manifestURL": "https://cdn1.etbon.eus/meteo/index.mpd",
      "dvr_window_minutes": 0,
      "drmConfig": null
    },
    {
      "type": "hls",
      "manifestURL": "https://cdn1.etbon.eus/meteo/index.m3u8",
      "dvr_window_minutes": 0,
      "drmConfig": null
    }
  ],
  "access_restriction": null
}
```

**Response Structure (Geo-Restricted Channel):**
```json
{
  "error": true,
  "code": 403,
  "message": "MEDIA_GEO_RESTRICTED_ACCESS"
}
```

**Notes:**
- Returns HTTP 200 with manifests if accessible
- Returns HTTP 403 with error message if geo-restricted
- Standard TV channels (ETB-1, ETB-2, etc.) are typically geo-restricted
- FAST channels (Euskadi Meteo) are typically not geo-restricted

### 3. Get Electronic Program Guide (EPG)

**Endpoint:** `GET /api/v1/epg/{slug}/{timestamp}`

**Description:** Returns the program schedule for a specific channel and time period.

**Timestamp Format:** `YYYYMMDDHH` (Year, Month, Day, Hour)

**Example:** `GET /api/v1/epg/etb-1/2026010611`

**Response Structure:**
```json
[
  {
    "id": 12345,
    "title": "Gaur Egun",
    "description": "Informazio programa...",
    "start_date": "2026-01-06T11:00:00+00:00",
    "end_date": "2026-01-06T12:00:00+00:00",
    "thumbnail": "https://cdnstorage.primeran.eus/directus/eitb/...",
    "duration": 3600
  },
  {
    "id": 12346,
    "title": "Next Program",
    "start_date": "2026-01-06T12:00:00+00:00",
    ...
  }
]
```

**Notes:**
- Returns an array of program objects
- Each program includes title, description, start/end times, and thumbnail
- Used to display "Now Playing" and upcoming schedule in the player UI

## Channel Types

### Standard TV Channels
- **Examples:** ETB-1, ETB-2, ETB-3
- **Geo-Restriction:** Yes (typically restricted to Basque Country/Spain)
- **Authentication:** Required
- **URL Pattern:** `/ch/{slug}`

### FAST Channels
- **Examples:** Euskadi Meteo
- **Geo-Restriction:** No (globally accessible)
- **Authentication:** May not require authentication
- **URL Pattern:** `/ch/{slug}`
- **Special Features:** Direct manifest URLs may be included in channel list

## Geo-Restriction Detection for Channels

To check if a live channel is geo-restricted:

1. Call `GET /api/v1/stream/{slug}`
2. Check response:
   - **HTTP 200** → Channel is accessible
   - **HTTP 403** with `MEDIA_GEO_RESTRICTED_ACCESS` → Channel is geo-restricted

This is similar to the VOD geo-restriction check but uses the `/stream/` endpoint instead of `/media/`.

## Typical API Call Sequence

When loading a live channel page:

1. **Get channel list:** `GET /api/v1/pages/zuzenekoak`
2. **Get stream metadata:** `GET /api/v1/stream/{slug}`
3. **Get current program:** `GET /api/v1/epg/{slug}/{current_timestamp}`
4. **Start playback:** Browser fetches manifest from CDN URL

## Implementation Notes

- Channels use a different API structure than VOD/series content
- The `/stream/` endpoint is specific to live channels
- EPG data is fetched separately and updated periodically
- FAST channels may bypass some authentication requirements
- Geo-restriction is enforced at the API level (403 response) rather than CDN level for channels

## Related Endpoints

- `GET /api/v1/application` - Application configuration
- `GET /api/v1/settings` - User settings
- `GET /api/v1/menus/{id}` - Menu structure (includes link to `/zuzenekoak`)
