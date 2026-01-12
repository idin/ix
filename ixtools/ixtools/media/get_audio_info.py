"""
Audio metadata extraction tools.
"""

from typing import Dict, Any, Optional
import os
from mutagen import File as MutagenFile

from ..constants import SUCCESS_KEY, ERROR_KEY, RESULT_KEY, METADATA_KEY
from ..file_system.constants import PATH_KEY


def get_audio_info(
    file_path: str,
) -> Dict[str, Any]:
    """
    Get detailed metadata information about an audio file.

    Supports formats including MP3, FLAC, OGG, AAC, M4A, WAV, and more.

    Args:
        file_path: Path to the audio file.

    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - file_path: Path to the file.
            - file_size: File size in bytes (None if file doesn't exist).
            - format: Audio format/container (e.g., "MP3", "FLAC", "OGG") (None if not available).
            - codec: Audio codec name (None if not available).
            - sample_rate: Sample rate in Hz (None if not available).
            - bit_depth: Bit depth in bits (None if not available).
            - bitrate: Bitrate in bits per second (None if not available).
            - bitrate_mode: Bitrate mode (e.g., "VBR", "CBR", "ABR") (None if not available).
            - channels: Number of audio channels (None if not available).
            - channel_layout: Channel layout description (e.g., "stereo", "mono") (None if not available).
            - duration: Duration in seconds (None if not available).
            - duration_formatted: Duration formatted as "HH:MM:SS" (None if not available).
            - tags: Dictionary of metadata tags (title, artist, album, etc.) (None if not available).
            - error: Error message if operation failed (None if successful).
    """
    try:
        if not os.path.exists(file_path):
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                METADATA_KEY: {
                    PATH_KEY: file_path,
                },
                ERROR_KEY: f"File does not exist: {file_path}",
            }

        if not os.path.isfile(file_path):
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                METADATA_KEY: {
                    PATH_KEY: file_path,
                },
                ERROR_KEY: f"Path is not a file: {file_path}",
            }

        file_size = os.path.getsize(file_path)

        try:
            audio_file = MutagenFile(file_path)
        except Exception as e:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                METADATA_KEY: {
                    PATH_KEY: file_path,
                },
                ERROR_KEY: f"Error reading audio file: {str(e)}",
            }

        if audio_file is None:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                METADATA_KEY: {
                    PATH_KEY: file_path,
                },
                ERROR_KEY: "File format not recognized or not an audio file",
            }

        # Get format information
        format_name = None
        if hasattr(audio_file, "mime"):
            mime_type = audio_file.mime[0] if isinstance(audio_file.mime, list) else audio_file.mime
            if mime_type:
                format_name = mime_type.split("/")[-1].upper()

        # Get codec information
        codec = None
        if hasattr(audio_file, "codec"):
            codec = str(audio_file.codec[0]) if isinstance(audio_file.codec, list) else str(audio_file.codec)

        # Get audio properties
        sample_rate = None
        bit_depth = None
        bitrate = None
        bitrate_mode = None
        channels = None
        channel_layout = None
        duration = None

        if hasattr(audio_file.info, "sample_rate"):
            sample_rate = int(audio_file.info.sample_rate)

        if hasattr(audio_file.info, "bits_per_sample"):
            bit_depth = audio_file.info.bits_per_sample
        elif hasattr(audio_file.info, "bitdepth"):
            bit_depth = audio_file.info.bitdepth

        if hasattr(audio_file.info, "bitrate"):
            bitrate = audio_file.info.bitrate

        if hasattr(audio_file.info, "bitrate_mode"):
            bitrate_mode = str(audio_file.info.bitrate_mode)

        if hasattr(audio_file.info, "channels"):
            channels = audio_file.info.channels
            # Map common channel counts to layout names
            if channels == 1:
                channel_layout = "mono"
            elif channels == 2:
                channel_layout = "stereo"
            elif channels == 4:
                channel_layout = "quad"
            elif channels == 5:
                channel_layout = "5.0"
            elif channels == 6:
                channel_layout = "5.1"
            elif channels == 7:
                channel_layout = "6.1"
            elif channels == 8:
                channel_layout = "7.1"
            else:
                channel_layout = f"{channels} channels"

        if hasattr(audio_file.info, "length"):
            duration = float(audio_file.info.length)

        # Format duration as HH:MM:SS
        duration_formatted = None
        if duration is not None:
            hours = int(duration // 3600)
            minutes = int((duration % 3600) // 60)
            seconds = int(duration % 60)
            if hours > 0:
                duration_formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                duration_formatted = f"{minutes:02d}:{seconds:02d}"

        # Extract tags/metadata
        tags = {}
        if hasattr(audio_file, "tags"):
            if audio_file.tags is not None:
                for key in audio_file.tags.keys():
                    value = audio_file.tags[key]
                    if isinstance(value, list) and len(value) > 0:
                        tags[key] = str(value[0])
                    elif value is not None:
                        tags[key] = str(value)

        # Normalize common tag names
        normalized_tags = {}
        tag_mapping = {
            "TIT2": "title",
            "TALB": "album",
            "TPE1": "artist",
            "TPE2": "album_artist",
            "TDRC": "date",
            "TRCK": "track",
            "TCON": "genre",
            "COMM": "comment",
            "TCOM": "composer",
        }

        for key, value in tags.items():
            normalized_key = tag_mapping.get(key, key.lower().replace(" ", "_"))
            normalized_tags[normalized_key] = value

        return {
            SUCCESS_KEY: True,
            RESULT_KEY: {
                "file_size": file_size,
                "format": format_name,
                "codec": codec,
                "sample_rate": sample_rate,
                "bit_depth": bit_depth,
                "bitrate": bitrate,
                "bitrate_mode": bitrate_mode,
                "channels": channels,
                "channel_layout": channel_layout,
                "duration": duration,
                "duration_formatted": duration_formatted,
                "tags": normalized_tags if normalized_tags else None,
            },
            METADATA_KEY: {
                PATH_KEY: file_path,
            },
            ERROR_KEY: None,
        }

    except Exception as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            METADATA_KEY: {
                PATH_KEY: file_path,
            },
            ERROR_KEY: f"Unexpected error: {str(e)}",
        }

