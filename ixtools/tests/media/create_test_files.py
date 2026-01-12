"""
Helper functions to create test media files for testing.
"""

from PIL import Image


def create_test_image(file_path: str, width: int, height: int, format: str = "PNG"):
    """
    Create a test image file for testing.
    
    Args:
        file_path: Path where the image should be created.
        width: Image width in pixels.
        height: Image height in pixels.
        format: Image format ("PNG" or "JPEG").
    """
    # Create a simple test image
    image = Image.new("RGB", (width, height), color=(128, 128, 128))
    
    # Save in the requested format
    if format.upper() == "PNG":
        image.save(file_path, "PNG")
    elif format.upper() in ["JPEG", "JPG"]:
        image.save(file_path, "JPEG")
    else:
        raise ValueError(f"Unsupported format: {format}")

