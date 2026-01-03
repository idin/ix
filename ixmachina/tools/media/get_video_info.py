"""
Video metadata extraction tools.
"""

from typing import Dict, Any, Optional
import os
import subprocess
import json


def get_video_info(
    file_path: str,
) -> Dict[str, Any]:
    """
    Get detailed metadata information about a video file.

    Supports formats including MP4, AVI, MKV, MOV, WebM, and more.
    Requires ffprobe (from ffmpeg) to be installed on the system.

    Args:
        file_path: Path to the video file.

    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - file_path: Path to the file.
            - file_size: File size in bytes (None if file doesn't exist).
            - format: Video container format (e.g., "mp4", "avi", "mkv") (None if not available).
            - format_long_name: Full format name (None if not available).
            - duration: Duration in seconds (None if not available).
            - duration_formatted: Duration formatted as "HH:MM:SS" (None if not available).
            - bitrate: Overall bitrate in bits per second (None if not available).
            - video_streams: List of video stream information dictionaries, each containing:
                - codec_name: Video codec (e.g., "h264", "hevc", "vp9") (None if not available).
                - codec_long_name: Full codec name (None if not available).
                - width: Video width in pixels (None if not available).
                - height: Video height in pixels (None if not available).
                - resolution: Resolution as "WIDTHxHEIGHT" (None if not available).
                - aspect_ratio: Aspect ratio (e.g., "16:9") (None if not available).
                - frame_rate: Frame rate as fraction string (e.g., "30/1") (None if not available).
                - frame_rate_float: Frame rate as float (None if not available).
                - pixel_format: Pixel format (e.g., "yuv420p") (None if not available).
                - bitrate: Video bitrate in bits per second (None if not available).
                - colour_space: Colour space (e.g., "bt709") (None if not available).
                - bit_depth: Bit depth in bits (None if not available).
            - audio_streams: List of audio stream information dictionaries, each containing:
                - codec_name: Audio codec (e.g., "aac", "mp3", "opus") (None if not available).
                - codec_long_name: Full codec name (None if not available).
                - sample_rate: Sample rate in Hz (None if not available).
                - channels: Number of audio channels (None if not available).
                - channel_layout: Channel layout (e.g., "stereo") (None if not available).
                - bitrate: Audio bitrate in bits per second (None if not available).
                - bit_depth: Bit depth in bits (None if not available).
            - subtitle_streams: List of subtitle stream information dictionaries, each containing:
                - codec_name: Subtitle codec (None if not available).
                - language: Language code (None if not available).
            - error: Error message if operation failed (None if successful).
    """
    try:
        if not os.path.exists(file_path):
            return {
                "success": False,
                "file_path": file_path,
                "file_size": None,
                "format": None,
                "format_long_name": None,
                "duration": None,
                "duration_formatted": None,
                "bitrate": None,
                "video_streams": None,
                "audio_streams": None,
                "subtitle_streams": None,
                "error": f"File does not exist: {file_path}",
            }

        if not os.path.isfile(file_path):
            return {
                "success": False,
                "file_path": file_path,
                "file_size": None,
                "format": None,
                "format_long_name": None,
                "duration": None,
                "duration_formatted": None,
                "bitrate": None,
                "video_streams": None,
                "audio_streams": None,
                "subtitle_streams": None,
                "error": f"Path is not a file: {file_path}",
            }

        file_size = os.path.getsize(file_path)

        # Check if ffprobe is available
        try:
            subprocess.run(
                ["ffprobe", "-version"],
                capture_output=True,
                check=True,
                timeout=5,
            )
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return {
                "success": False,
                "file_path": file_path,
                "file_size": file_size,
                "format": None,
                "format_long_name": None,
                "duration": None,
                "duration_formatted": None,
                "bitrate": None,
                "video_streams": None,
                "audio_streams": None,
                "subtitle_streams": None,
                "error": "ffprobe not found. Please install ffmpeg to use this function.",
            }

        # Use ffprobe to get video information
        try:
            result = subprocess.run(
                [
                    "ffprobe",
                    "-v", "quiet",
                    "-print_format", "json",
                    "-show_format",
                    "-show_streams",
                    file_path,
                ],
                capture_output=True,
                text=True,
                timeout=30,
                check=True,
            )

            probe_data = json.loads(result.stdout)

        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "file_path": file_path,
                "file_size": file_size,
                "format": None,
                "format_long_name": None,
                "duration": None,
                "duration_formatted": None,
                "bitrate": None,
                "video_streams": None,
                "audio_streams": None,
                "subtitle_streams": None,
                "error": f"ffprobe error: {e.stderr.decode() if e.stderr else str(e)}",
            }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "file_path": file_path,
                "file_size": file_size,
                "format": None,
                "format_long_name": None,
                "duration": None,
                "duration_formatted": None,
                "bitrate": None,
                "video_streams": None,
                "audio_streams": None,
                "subtitle_streams": None,
                "error": f"Error parsing ffprobe output: {str(e)}",
            }

        # Extract format information
        format_info = probe_data.get("format", {})
        format_name = format_info.get("format_name")
        format_long_name = format_info.get("format_long_name")
        duration = None
        if "duration" in format_info:
            try:
                duration = float(format_info["duration"])
            except (ValueError, TypeError):
                pass

        bitrate = None
        if "bit_rate" in format_info:
            try:
                bitrate = int(format_info["bit_rate"])
            except (ValueError, TypeError):
                pass

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

        # Extract stream information
        streams = probe_data.get("streams", [])
        video_streams = []
        audio_streams = []
        subtitle_streams = []

        for stream in streams:
            codec_type = stream.get("codec_type")
            if codec_type == "video":
                width = None
                height = None
                if "width" in stream:
                    try:
                        width = int(stream["width"])
                    except (ValueError, TypeError):
                        pass
                if "height" in stream:
                    try:
                        height = int(stream["height"])
                    except (ValueError, TypeError):
                        pass

                resolution = None
                if width is not None and height is not None:
                    resolution = f"{width}x{height}"

                aspect_ratio = stream.get("display_aspect_ratio")

                frame_rate = stream.get("r_frame_rate")
                frame_rate_float = None
                if frame_rate:
                    try:
                        num, den = map(int, frame_rate.split("/"))
                        if den > 0:
                            frame_rate_float = num / den
                    except (ValueError, ZeroDivisionError):
                        pass

                stream_bitrate = None
                if "bit_rate" in stream:
                    try:
                        stream_bitrate = int(stream["bit_rate"])
                    except (ValueError, TypeError):
                        pass

                bit_depth = None
                if "bits_per_raw_sample" in stream:
                    try:
                        bit_depth = int(stream["bits_per_raw_sample"])
                    except (ValueError, TypeError):
                        pass

                video_streams.append({
                    "codec_name": stream.get("codec_name"),
                    "codec_long_name": stream.get("codec_long_name"),
                    "width": width,
                    "height": height,
                    "resolution": resolution,
                    "aspect_ratio": aspect_ratio,
                    "frame_rate": frame_rate,
                    "frame_rate_float": frame_rate_float,
                    "pixel_format": stream.get("pix_fmt"),
                    "bitrate": stream_bitrate,
                    "colour_space": stream.get("color_space"),
                    "bit_depth": bit_depth,
                })

            elif codec_type == "audio":
                sample_rate = None
                if "sample_rate" in stream:
                    try:
                        sample_rate = int(float(stream["sample_rate"]))
                    except (ValueError, TypeError):
                        pass

                channels = None
                if "channels" in stream:
                    try:
                        channels = int(stream["channels"])
                    except (ValueError, TypeError):
                        pass

                stream_bitrate = None
                if "bit_rate" in stream:
                    try:
                        stream_bitrate = int(stream["bit_rate"])
                    except (ValueError, TypeError):
                        pass

                bit_depth = None
                if "bits_per_sample" in stream:
                    try:
                        bit_depth = int(stream["bits_per_sample"])
                    except (ValueError, TypeError):
                        pass

                audio_streams.append({
                    "codec_name": stream.get("codec_name"),
                    "codec_long_name": stream.get("codec_long_name"),
                    "sample_rate": sample_rate,
                    "channels": channels,
                    "channel_layout": stream.get("channel_layout"),
                    "bitrate": stream_bitrate,
                    "bit_depth": bit_depth,
                })

            elif codec_type == "subtitle":
                subtitle_streams.append({
                    "codec_name": stream.get("codec_name"),
                    "language": stream.get("tags", {}).get("language"),
                })

        return {
            "success": True,
            "file_path": file_path,
            "file_size": file_size,
            "format": format_name,
            "format_long_name": format_long_name,
            "duration": duration,
            "duration_formatted": duration_formatted,
            "bitrate": bitrate,
            "video_streams": video_streams if video_streams else None,
            "audio_streams": audio_streams if audio_streams else None,
            "subtitle_streams": subtitle_streams if subtitle_streams else None,
            "error": None,
        }

    except Exception as e:
        return {
            "success": False,
            "file_path": file_path,
            "file_size": None,
            "format": None,
            "format_long_name": None,
            "duration": None,
            "duration_formatted": None,
            "bitrate": None,
            "video_streams": None,
            "audio_streams": None,
            "subtitle_streams": None,
            "error": f"Unexpected error: {str(e)}",
        }

