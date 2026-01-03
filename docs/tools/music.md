# Music Tools

Tools for accessing music information from various APIs: MusicBrainz (free music encyclopedia), Spotify (popularity and features), and Genius (lyrics and annotations).

## Core Design Principles

### Multiple Data Sources

Different APIs provide different information:
- **MusicBrainz**: Comprehensive metadata, release information, relationships
- **Spotify**: Popularity, audio features, recommendations
- **Genius**: Lyrics, annotations, song meanings

**Why this matters**: No single source has everything. These tools let you combine information from multiple sources for a complete picture.

### Caching

All search functions are cached to reduce API calls and improve performance:
- MusicBrainz searches: 30 minutes
- Spotify searches: 15 minutes
- Genius searches: 15 minutes

**Why implemented this way**: Music metadata doesn't change frequently. Caching reduces API costs and speeds up repeated queries.

## Understanding the Tools

### MusicBrainz Tools

MusicBrainz is a free, open music encyclopedia with comprehensive metadata about artists, albums, and tracks.

#### `search_on_musicbrainz` - Search Music

**What it does**: Searches MusicBrainz for artists, albums (releases), or tracks (recordings).

**Why we use it**: MusicBrainz has the most comprehensive music metadata available. It's free, open, and covers music from all genres and eras.

**Why implemented this way**:
- Uses MusicBrainz REST API (no authentication required)
- Supports three search types: artist, album (releases), track (recordings)
- Returns structured results with metadata
- Cached for 30 minutes (metadata is relatively stable)

**How to use**:
```python
from ixmachina.tools.music import search_on_musicbrainz

# Search for artists
result = search_on_musicbrainz("The Beatles", type="artist", limit=5)
if result["success"]:
    for artist in result["result"]["artists"]:
        print(f"{artist['name']} - {artist.get('disambiguation', '')}")

# Search for albums
result = search_on_musicbrainz("Abbey Road", type="album", limit=5)
if result["success"]:
    for release in result["result"]["releases"]:
        print(f"{release['title']} ({release.get('date', 'Unknown date')})")

# Search for tracks
result = search_on_musicbrainz("Hey Jude", type="track", limit=5)
if result["success"]:
    for recording in result["result"]["recordings"]:
        print(f"{recording['title']} by {recording.get('artist', 'Unknown')}")
```

**When to use**: 
- Finding comprehensive music metadata
- Discovering releases and recordings
- Building music databases
- Researching music history

**Note**: 
- "album" searches for releases (specific album releases, not just album titles)
- "track" searches for recordings (specific recorded performances, not just song titles)

---

#### `get_from_musicbrainz` - Get Detailed Information

**What it does**: Retrieves detailed information about a specific MusicBrainz entity (artist, release, recording) by ID.

**Why we use it**: After searching, you get IDs. This function retrieves full details for those entities.

**How to use**:
```python
from ixmachina.tools.music import get_from_musicbrainz

# Get artist details
result = get_from_musicbrainz(
    entity_type="artist",
    mbid="b10bbbfc-cf9e-42e0-be17-e2c3e1d2600d"  # The Beatles
)
if result["success"]:
    artist = result["result"]
    print(f"Name: {artist['name']}")
    print(f"Type: {artist.get('type', 'Unknown')}")
    print(f"Country: {artist.get('country', 'Unknown')}")
```

**When to use**: When you have a MusicBrainz ID and need detailed information about that entity.

---

### Spotify Tools

Spotify provides popularity metrics, audio features, and recommendations. Requires OAuth authentication.

#### `search_on_spotify` - Search Spotify

**What it does**: Searches Spotify for artists, albums, tracks, or playlists.

**Why we use it**: Spotify has popularity data, audio features, and recommendations that MusicBrainz doesn't provide.

**Why implemented this way**:
- Uses Spotify Web API (requires OAuth access token)
- Supports four search types: artist, album, track, playlist
- Returns popularity scores and audio features
- Cached for 15 minutes (popularity changes more frequently than metadata)

**How to use**:
```python
from ixmachina.tools.music import search_on_spotify

# Requires Spotify access token
result = search_on_spotify(
    "The Beatles",
    access_token=spotify_token,  # Or set SPOTIFY_ACCESS_TOKEN env var
    type="artist",
    limit=5
)
if result["success"]:
    for artist in result["result"]["artists"]:
        print(f"{artist['name']} - Popularity: {artist.get('popularity', 0)}")
```

**When to use**: 
- When you need popularity metrics
- When you need audio features (tempo, energy, danceability, etc.)
- When you want Spotify-specific data

**Note**: Requires Spotify OAuth access token. Get one by:
1. Registering at https://developer.spotify.com/dashboard
2. Using OAuth 2.0 Client Credentials flow
3. Passing token to function or setting `SPOTIFY_ACCESS_TOKEN` environment variable

---

### Genius Tools

Genius provides lyrics, annotations, and song meanings. Great for understanding song content.

#### `search_song_on_genius` - Search for Songs

**What it does**: Searches Genius for songs and returns results with links to lyrics pages.

**Why we use it**: Genius has the largest collection of song lyrics with annotations and explanations.

**How to use**:
```python
from ixmachina.tools.music import search_song_on_genius

result = search_song_on_genius("Hey Jude", limit=5)
if result["success"]:
    for song in result["result"]["songs"]:
        print(f"{song['title']} by {song.get('artist', 'Unknown')}")
        print(f"URL: {song.get('url', '')}")
```

**When to use**: When you need to find songs on Genius to get their lyrics.

---

#### `get_lyrics_from_genius` - Get Song Lyrics

**What it does**: Retrieves lyrics for a song from Genius, optionally with annotations.

**Why we use it**: Get full lyrics text for analysis, display, or processing.

**How to use**:
```python
from ixmachina.tools.music import get_lyrics_from_genius

result = get_lyrics_from_genius(
    song_url="https://genius.com/The-beatles-hey-jude-lyrics",
    include_annotations=False
)
if result["success"]:
    print(result["result"]["lyrics"])
```

**When to use**: When you have a Genius song URL and need the lyrics text.

---

## Common Patterns

### Combining Sources

Use multiple APIs to get complete information:

```python
# Get metadata from MusicBrainz
mb_result = search_on_musicbrainz("The Beatles", type="artist")
if mb_result["success"]:
    artist = mb_result["result"]["artists"][0]
    print(f"Name: {artist['name']}")
    print(f"Type: {artist.get('type', 'Unknown')}")

# Get popularity from Spotify
spotify_result = search_on_spotify("The Beatles", type="artist", access_token=token)
if spotify_result["success"]:
    spotify_artist = spotify_result["result"]["artists"][0]
    print(f"Popularity: {spotify_artist.get('popularity', 0)}")

# Get lyrics from Genius
genius_result = search_song_on_genius("Hey Jude")
if genius_result["success"]:
    song = genius_result["result"]["songs"][0]
    lyrics_result = get_lyrics_from_genius(song["url"])
    if lyrics_result["success"]:
        print("Lyrics available")
```

### Error Handling

Always check for success and handle errors:

```python
result = search_on_musicbrainz("query", type="artist")
if not result["success"]:
    print(f"Error: {result['error']}")
    return
# Use result["result"] here
```

### Working with IDs

MusicBrainz uses MusicBrainz IDs (MBIDs) for entities. After searching, use IDs to get detailed information:

```python
# Search first
search_result = search_on_musicbrainz("The Beatles", type="artist")
if search_result["success"]:
    artist_id = search_result["result"]["artists"][0]["id"]
    
    # Get detailed info
    detail_result = get_from_musicbrainz("artist", artist_id)
    if detail_result["success"]:
        # Use detailed information
        pass
```

---

## Design Decisions

### Why Multiple APIs?

Each API serves different purposes:
- **MusicBrainz**: Best for comprehensive metadata, relationships, release information
- **Spotify**: Best for popularity, audio features, current trends
- **Genius**: Best for lyrics, annotations, song meanings

Using multiple sources gives you the most complete picture.

### Why Caching?

Music metadata is relatively stable:
- Artist information doesn't change frequently
- Release dates are fixed
- Popularity changes but not minute-to-minute

Caching reduces API costs and improves performance without sacrificing accuracy.

### Why Different Cache Durations?

- **MusicBrainz (30 min)**: Metadata is very stable
- **Spotify (15 min)**: Popularity can change more frequently
- **Genius (15 min)**: Lyrics are stable, but search results may vary

Cache durations balance freshness with performance.

### Why No Authentication for MusicBrainz?

MusicBrainz is free and open. No authentication required, making it easy to use. Spotify and Genius require authentication for their APIs.

### Error Handling

All functions return structured errors:
- API failures: Network errors, rate limits
- Authentication errors: Missing or invalid tokens
- Not found: No results for query

This helps users understand and handle issues appropriately.

