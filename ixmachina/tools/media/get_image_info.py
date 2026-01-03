"""
Image metadata extraction tools.
"""

from typing import Dict, Any, Optional
import os
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


def get_image_info(
    file_path: str,
) -> Dict[str, Any]:
    """
    Get detailed metadata information about an image file.

    Supports formats including JPEG, PNG, GIF, BMP, TIFF, WebP, and more.

    Args:
        file_path: Path to the image file.

    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - file_path: Path to the file.
            - file_size: File size in bytes (None if file doesn't exist).
            - format: Image format (e.g., "JPEG", "PNG", "GIF") (None if not available).
            - format_description: Format description (None if not available).
            - mode: Image mode (e.g., "RGB", "RGBA", "L") (None if not available).
            - width: Image width in pixels (None if not available).
            - height: Image height in pixels (None if not available).
            - resolution: Resolution as "WIDTHxHEIGHT" (None if not available).
            - aspect_ratio: Aspect ratio as float (width/height) (None if not available).
            - colour_depth: Colour depth in bits per pixel (None if not available).
            - has_transparency: Boolean indicating if image has transparency (None if not available).
            - dpi: DPI (dots per inch) as tuple (x, y) (None if not available).
            - exif: Dictionary of EXIF metadata (None if not available).
            - gps: Dictionary of GPS coordinates if available (None if not available).
            - error: Error message if operation failed (None if successful).
    """
    try:
        if not os.path.exists(file_path):
            return {
                "success": False,
                "file_path": file_path,
                "file_size": None,
                "format": None,
                "format_description": None,
                "mode": None,
                "width": None,
                "height": None,
                "resolution": None,
                "aspect_ratio": None,
                "colour_depth": None,
                "has_transparency": None,
                "dpi": None,
                "exif": None,
                "gps": None,
                "error": f"File does not exist: {file_path}",
            }

        if not os.path.isfile(file_path):
            return {
                "success": False,
                "file_path": file_path,
                "file_size": None,
                "format": None,
                "format_description": None,
                "mode": None,
                "width": None,
                "height": None,
                "resolution": None,
                "aspect_ratio": None,
                "colour_depth": None,
                "has_transparency": None,
                "dpi": None,
                "exif": None,
                "gps": None,
                "error": f"Path is not a file: {file_path}",
            }

        file_size = os.path.getsize(file_path)

        try:
            with Image.open(file_path) as img:
                format_name = img.format
                format_description = None
                if format_name:
                    format_description = Image.MIME.get(img.format)

                mode = img.mode
                width, height = img.size
                resolution = f"{width}x{height}"

                aspect_ratio = None
                if height > 0:
                    aspect_ratio = width / height

                # Calculate colour depth
                colour_depth = None
                if mode:
                    # Map common modes to bit depth
                    mode_bits = {
                        "1": 1,  # 1-bit pixels, black and white
                        "L": 8,  # 8-bit pixels, grayscale
                        "P": 8,  # 8-bit pixels, mapped to palette
                        "RGB": 24,  # 3x8-bit pixels, true colour
                        "RGBA": 32,  # 4x8-bit pixels, true colour with transparency
                        "CMYK": 32,  # 4x8-bit pixels, colour separation
                        "YCbCr": 24,  # 3x8-bit pixels, colour video format
                        "LAB": 24,  # 3x8-bit pixels, L*a*b colour space
                        "HSV": 24,  # 3x8-bit pixels, Hue, Saturation, Value
                        "I": 32,  # 32-bit signed integer pixels
                        "F": 32,  # 32-bit floating point pixels
                    }
                    colour_depth = mode_bits.get(mode)

                has_transparency = None
                if mode in ("RGBA", "LA", "P"):
                    has_transparency = img.info.get("transparency") is not None or "transparency" in img.info

                # Get DPI
                dpi = None
                if "dpi" in img.info:
                    dpi_info = img.info["dpi"]
                    if isinstance(dpi_info, tuple) and len(dpi_info) == 2:
                        dpi = dpi_info
                elif "resolution" in img.info:
                    resolution_info = img.info["resolution"]
                    if isinstance(resolution_info, tuple) and len(resolution_info) == 2:
                        dpi = resolution_info

                # Extract EXIF data
                exif_data = None
                gps_data = None

                if hasattr(img, "_getexif") and img._getexif() is not None:
                    exif_dict = {}
                    for tag_id, value in img._getexif().items():
                        tag = TAGS.get(tag_id, tag_id)
                        exif_dict[tag] = value

                        # Extract GPS data if available
                        if tag == "GPSInfo":
                            gps_dict = {}
                            for gps_tag_id, gps_value in value.items():
                                gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                                gps_dict[gps_tag] = gps_value
                            gps_data = gps_dict

                    if exif_dict:
                        exif_data = exif_dict

                # Also try getexif() method (Pillow 8.0+)
                elif hasattr(img, "getexif"):
                    try:
                        exif = img.getexif()
                        if exif:
                            exif_dict = {}
                            for tag_id, value in exif.items():
                                tag = TAGS.get(tag_id, tag_id)
                                exif_dict[tag] = value

                                # Extract GPS data if available
                                if tag == "GPSInfo":
                                    gps_dict = {}
                                    for gps_tag_id, gps_value in value.items():
                                        gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                                        gps_dict[gps_tag] = gps_value
                                    gps_data = gps_dict

                            if exif_dict:
                                exif_data = exif_dict
                    except Exception:
                        pass

                return {
                    "success": True,
                    "file_path": file_path,
                    "file_size": file_size,
                    "format": format_name,
                    "format_description": format_description,
                    "mode": mode,
                    "width": width,
                    "height": height,
                    "resolution": resolution,
                    "aspect_ratio": aspect_ratio,
                    "colour_depth": colour_depth,
                    "has_transparency": has_transparency,
                    "dpi": dpi,
                    "exif": exif_data,
                    "gps": gps_data,
                    "error": None,
                }

        except Exception as e:
            return {
                "success": False,
                "file_path": file_path,
                "file_size": file_size,
                "format": None,
                "format_description": None,
                "mode": None,
                "width": None,
                "height": None,
                "resolution": None,
                "aspect_ratio": None,
                "colour_depth": None,
                "has_transparency": None,
                "dpi": None,
                "exif": None,
                "gps": None,
                "error": f"Error reading image file: {str(e)}",
            }

    except Exception as e:
        return {
            "success": False,
            "file_path": file_path,
            "file_size": None,
            "format": None,
            "format_description": None,
            "mode": None,
            "width": None,
            "height": None,
            "resolution": None,
            "aspect_ratio": None,
            "colour_depth": None,
            "has_transparency": None,
            "dpi": None,
            "exif": None,
            "gps": None,
            "error": f"Unexpected error: {str(e)}",
        }

