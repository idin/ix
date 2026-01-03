"""
Media tools for extracting metadata from audio, video, and image files.

This package provides tools for:
- Audio metadata (sample rate, bit depth, bitrate, channels, duration, format)
- Video metadata (resolution, frame rate, codec, bitrate, duration, format)
- Image metadata (dimensions, format, colour depth, EXIF data)
- File size and other technical information
"""

from .get_media_info import get_media_info

__all__ = [
    "get_media_info",
]

