"""
Constants for MusicBrainz API.
"""

# Base URL for MusicBrainz API
BASE_URL = "https://musicbrainz.org/ws/2"

# Required User-Agent header (MusicBrainz requires this per their API terms)
# Format: ApplicationName/Version (ContactInfo)
USER_AGENT = "ixmachina/1.0"

# Rate limit: ~1 request per second
RATE_LIMIT_DELAY = 1.0

# Default timeout
DEFAULT_TIMEOUT = 30

