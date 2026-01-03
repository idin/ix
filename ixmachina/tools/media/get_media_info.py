"""
Unified media information extraction tool.

Automatically detects file type and returns appropriate metadata.
Supports single file or multiple files (batch processing).
"""

from typing import Dict, Any, List, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

from .get_audio_info import get_audio_info
from .get_video_info import get_video_info
from .get_image_info import get_image_info


def _get_media_info_single(
    file_path: str,
) -> Dict[str, Any]:
    """
    Get detailed metadata information about a single media file.

    Automatically detects whether the file is audio, video, or image and
    returns appropriate metadata. Supports many formats including:
    - Audio: MP3, FLAC, OGG, AAC, M4A, WAV, and more
    - Video: MP4, AVI, MKV, MOV, WebM, and more
    - Image: JPEG, PNG, GIF, BMP, TIFF, WebP, and more

    Args:
        file_path: Path to the media file.

    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - media_type: Type of media ("audio", "video", "image", or "unknown").
            - file_path: Path to the file.
            - file_size: File size in bytes (None if file doesn't exist).
            - audio_info: Audio-specific metadata (if audio file, see get_audio_info for details).
            - video_info: Video-specific metadata (if video file, see get_video_info for details).
            - image_info: Image-specific metadata (if image file, see get_image_info for details).
            - error: Error message if operation failed (None if successful).
    """
    try:
        if not os.path.exists(file_path):
            return {
                "success": False,
                "media_type": "unknown",
                "file_path": file_path,
                "file_size": None,
                "audio_info": None,
                "video_info": None,
                "image_info": None,
                "error": f"File does not exist: {file_path}",
            }

        if not os.path.isfile(file_path):
            return {
                "success": False,
                "media_type": "unknown",
                "file_path": file_path,
                "file_size": None,
                "audio_info": None,
                "video_info": None,
                "image_info": None,
                "error": f"Path is not a file: {file_path}",
            }

        # Get file extension to help determine type
        _, ext = os.path.splitext(file_path.lower())
        ext = ext.lstrip(".")

        # Common media file extensions
        audio_extensions = {
            "mp3", "flac", "ogg", "oga", "aac", "m4a", "mp4a", "wav", "wma",
            "opus", "aiff", "aif", "au", "ra", "amr", "3gp", "ac3", "dts",
            "mp2", "mpa", "wv", "ape", "tta", "tak", "ofr", "ofs", "rka",
        }
        video_extensions = {
            "mp4", "avi", "mkv", "mov", "webm", "flv", "wmv", "m4v", "3gp",
            "3g2", "asf", "rm", "rmvb", "vob", "ogv", "divx", "xvid", "mpg",
            "mpeg", "m2v", "ts", "mts", "m2ts", "flv", "f4v", "swf", "wmv",
        }
        image_extensions = {
            "jpg", "jpeg", "png", "gif", "bmp", "tiff", "tif", "webp", "ico",
            "svg", "heic", "heif", "raw", "cr2", "nef", "orf", "sr2", "arw",
            "dng", "psd", "xcf", "pcx", "tga", "exr", "hdr",
        }

        # Try to determine media type and get info
        media_type = "unknown"
        audio_info = None
        video_info = None
        image_info = None

        # Try image first (fastest check)
        if ext in image_extensions:
            image_info = get_image_info(file_path=file_path)
            if image_info.get("success"):
                media_type = "image"
                return {
                    "success": True,
                    "media_type": media_type,
                    "file_path": file_path,
                    "file_size": image_info.get("file_size"),
                    "audio_info": None,
                    "video_info": None,
                    "image_info": image_info,
                    "error": None,
                }

        # Try audio
        if ext in audio_extensions:
            audio_info = get_audio_info(file_path=file_path)
            if audio_info.get("success"):
                media_type = "audio"
                return {
                    "success": True,
                    "media_type": media_type,
                    "file_path": file_path,
                    "file_size": audio_info.get("file_size"),
                    "audio_info": audio_info,
                    "video_info": None,
                    "image_info": None,
                    "error": None,
                }

        # Try video
        if ext in video_extensions:
            video_info = get_video_info(file_path=file_path)
            if video_info.get("success"):
                media_type = "video"
                return {
                    "success": True,
                    "media_type": media_type,
                    "file_path": file_path,
                    "file_size": video_info.get("file_size"),
                    "audio_info": None,
                    "video_info": video_info,
                    "image_info": None,
                    "error": None,
                }

        # If extension-based detection failed, try all types
        # But respect extension priority - don't try audio for video extensions, etc.
        if media_type == "unknown":
            # Try image (only if not already tried or extension doesn't suggest another type)
            if ext not in video_extensions and ext not in audio_extensions:
                image_info = get_image_info(file_path=file_path)
                if image_info.get("success"):
                    media_type = "image"
                    return {
                        "success": True,
                        "media_type": media_type,
                        "file_path": file_path,
                        "file_size": image_info.get("file_size"),
                        "audio_info": None,
                        "video_info": None,
                        "image_info": image_info,
                        "error": None,
                    }

            # Try audio (only if extension doesn't suggest video)
            if ext not in video_extensions:
                audio_info = get_audio_info(file_path=file_path)
                if audio_info.get("success"):
                    media_type = "audio"
                    return {
                        "success": True,
                        "media_type": media_type,
                        "file_path": file_path,
                        "file_size": audio_info.get("file_size"),
                        "audio_info": audio_info,
                        "video_info": None,
                        "image_info": None,
                        "error": None,
                    }

            # Try video (only if extension doesn't suggest audio)
            if ext not in audio_extensions:
                video_info = get_video_info(file_path=file_path)
                if video_info.get("success"):
                    media_type = "video"
                    return {
                        "success": True,
                        "media_type": media_type,
                        "file_path": file_path,
                        "file_size": video_info.get("file_size"),
                        "audio_info": None,
                        "video_info": video_info,
                        "image_info": None,
                        "error": None,
                    }

        # If we get here, none of the types worked
        # Return the most informative error message
        error_messages = []
        if audio_info and not audio_info.get("success"):
            error_messages.append(f"Audio: {audio_info.get('error')}")
        if video_info and not video_info.get("success"):
            error_messages.append(f"Video: {video_info.get('error')}")
        if image_info and not image_info.get("success"):
            error_messages.append(f"Image: {image_info.get('error')}")

        error_msg = "; ".join(error_messages) if error_messages else "File format not recognized as audio, video, or image"

        return {
            "success": False,
            "media_type": "unknown",
            "file_path": file_path,
            "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else None,
            "audio_info": audio_info,
            "video_info": video_info,
            "image_info": image_info,
            "error": error_msg,
        }

    except Exception as e:
        return {
            "success": False,
            "media_type": "unknown",
            "file_path": file_path,
            "file_size": None,
            "audio_info": None,
            "video_info": None,
            "image_info": None,
            "error": f"Unexpected error: {str(e)}",
        }


def get_media_info(
    file_paths: Union[str, List[str]],
    max_workers: int = 4,
) -> Dict[str, Any]:
    """
    Get detailed metadata information about one or more media files.

    Automatically detects whether each file is audio, video, or image and
    returns appropriate metadata. Supports many formats including:
    - Audio: MP3, FLAC, OGG, AAC, M4A, WAV, and more
    - Video: MP4, AVI, MKV, MOV, WebM, and more
    - Image: JPEG, PNG, GIF, BMP, TIFF, WebP, and more

    When processing multiple files, they are processed in parallel for better performance.

    Args:
        file_paths: A single file path (string) or list of file paths.
        max_workers: Maximum number of parallel workers (only used for multiple files).
            Default: 4.

    Returns:
        For a single file path:
            Dictionary with:
                - success: Boolean indicating if the operation was successful.
                - media_type: Type of media ("audio", "video", "image", or "unknown").
                - file_path: Path to the file.
                - file_size: File size in bytes (None if file doesn't exist).
                - audio_info: Audio-specific metadata (if audio file).
                - video_info: Video-specific metadata (if video file).
                - image_info: Image-specific metadata (if image file).
                - error: Error message if operation failed (None if successful).

        For multiple file paths:
            Dictionary with:
                - success: Boolean indicating if the overall operation completed
                    (True if at least one file was processed successfully, False if all failed).
                - results: Dictionary mapping each file path to its media info result.
                - successful_paths: List of file paths that were successfully processed.
                - failed_paths: List of file paths that failed to process.
                - total_count: Total number of files attempted.
                - success_count: Number of files successfully processed.
                - failure_count: Number of files that failed to process.
                - error: Error message if the overall operation failed (None if successful).
    """
    # Normalize file_paths to list
    if isinstance(file_paths, str):
        path_list = [file_paths]
    else:
        path_list = file_paths

    if not path_list:
        return {
            "success": False,
            "error": "At least one file path must be provided.",
        }

    # Single file case - return result directly
    if len(path_list) == 1:
        return _get_media_info_single(file_path=path_list[0])

    # Multiple files case - process in parallel
    results = {}
    successful_paths = []
    failed_paths = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_path = {
            executor.submit(_get_media_info_single, file_path): file_path
            for file_path in path_list
        }

        for future in as_completed(future_to_path):
            file_path = future_to_path[future]
            try:
                result = future.result()
                results[file_path] = result

                if result.get("success"):
                    successful_paths.append(file_path)
                else:
                    failed_paths.append(file_path)
            except Exception as e:
                results[file_path] = {
                    "success": False,
                    "media_type": "unknown",
                    "file_path": file_path,
                    "file_size": None,
                    "audio_info": None,
                    "video_info": None,
                    "image_info": None,
                    "error": f"Error processing file: {str(e)}",
                }
                failed_paths.append(file_path)

    success_count = len(successful_paths)
    failure_count = len(failed_paths)
    overall_success = success_count > 0

    return {
        "success": overall_success,
        "results": results,
        "successful_paths": successful_paths,
        "failed_paths": failed_paths,
        "total_count": len(path_list),
        "success_count": success_count,
        "failure_count": failure_count,
        "error": None if overall_success else "All media info extractions failed.",
    }
