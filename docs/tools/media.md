# Media Tools

Tools for extracting metadata from audio, video, and image files. These tools help you understand the technical properties of media files without needing to manually inspect them.

## Core Design Principles

### Automatic Type Detection

The `get_media_info` function automatically detects whether a file is audio, video, or image and returns appropriate metadata. You don't need to know the file type in advance.

**Why implemented this way**: Media files come in many formats, and users shouldn't need to know the specific type. The tool handles detection automatically.

### Comprehensive Metadata

Each media type provides detailed technical information:
- **Audio**: Sample rate, bit depth, bitrate, channels, duration, format
- **Video**: Resolution, frame rate, codec, bitrate, duration, format
- **Image**: Dimensions, format, colour depth, EXIF data

**Why this matters**: Different use cases need different information. A video editor needs frame rate and codec. A web developer needs dimensions and file size. These tools provide everything.

## Understanding the Tools

### `get_media_info` - Unified Media Information

**What it does**: Automatically detects file type (audio, video, or image) and returns comprehensive metadata.

**Why we use it**: Single function for all media types. No need to know the file type in advance.

**Why implemented this way**:
- Uses file extension and content analysis for detection
- Calls appropriate specialized function (`get_audio_info`, `get_video_info`, `get_image_info`)
- Returns structured data with type-specific information nested
- Handles errors gracefully (missing files, unsupported formats)

**How to use**:
```python
from ixmachina.tools.media import get_media_info

result = get_media_info("my_video.mp4")
if result["success"]:
    print(f"Type: {result['media_type']}")
    print(f"Size: {result['file_size']} bytes")
    
    if result["media_type"] == "video":
        video_info = result["video_info"]
        print(f"Resolution: {video_info['width']}x{video_info['height']}")
        print(f"Frame rate: {video_info['frame_rate']} fps")
        print(f"Duration: {video_info['duration']} seconds")
```

**When to use**: When you don't know the file type in advance, or when you want a single function for all media types.

---

### `get_audio_info` - Audio File Metadata

**What it does**: Extracts detailed metadata from audio files (MP3, FLAC, OGG, AAC, M4A, WAV, and more).

**Why we use it**: When you specifically need audio information or want to avoid the overhead of type detection.

**Why implemented this way**:
- Uses `mutagen` library for broad format support
- Provides technical details (sample rate, bit depth, bitrate)
- Includes playback information (duration, channels)
- Handles metadata tags (artist, title, album) when available

**How to use**:
```python
from ixmachina.tools.media import get_audio_info

result = get_audio_info("song.mp3")
if result["success"]:
    audio = result["audio_info"]
    print(f"Format: {audio['format']}")
    print(f"Sample rate: {audio['sample_rate']} Hz")
    print(f"Bitrate: {audio['bitrate']} kbps")
    print(f"Duration: {audio['duration']} seconds")
    print(f"Channels: {audio['channels']}")
```

**When to use**: When you know the file is audio, or when you need audio-specific information.

---

### `get_video_info` - Video File Metadata

**What it does**: Extracts detailed metadata from video files (MP4, AVI, MKV, MOV, WebM, and more).

**Why we use it**: When you specifically need video information or want to avoid the overhead of type detection.

**Why implemented this way**:
- Uses `ffprobe` (from FFmpeg) for comprehensive video analysis
- Provides visual properties (resolution, aspect ratio)
- Includes technical details (codec, bitrate, frame rate)
- Handles container formats and codec information

**How to use**:
```python
from ixmachina.tools.media import get_video_info

result = get_video_info("video.mp4")
if result["success"]:
    video = result["video_info"]
    print(f"Resolution: {video['width']}x{video['height']}")
    print(f"Frame rate: {video['frame_rate']} fps")
    print(f"Codec: {video['codec']}")
    print(f"Duration: {video['duration']} seconds")
    print(f"Bitrate: {video['bitrate']} bps")
```

**When to use**: When you know the file is video, or when you need video-specific information.

**Note**: Requires FFmpeg to be installed on the system. The tool will return an error if `ffprobe` is not available.

---

### `get_image_info` - Image File Metadata

**What it does**: Extracts detailed metadata from image files (JPEG, PNG, GIF, BMP, TIFF, WebP, and more).

**Why we use it**: When you specifically need image information or want to avoid the overhead of type detection.

**Why implemented this way**:
- Uses `Pillow` (PIL) for broad format support
- Provides visual properties (dimensions, colour mode)
- Includes technical details (format, colour depth)
- Extracts EXIF data when available (camera settings, GPS, etc.)

**How to use**:
```python
from ixmachina.tools.media import get_image_info

result = get_image_info("photo.jpg")
if result["success"]:
    image = result["image_info"]
    print(f"Dimensions: {image['width']}x{image['height']}")
    print(f"Format: {image['format']}")
    print(f"Colour mode: {image['colour_mode']}")
    print(f"File size: {image['file_size']} bytes")
    
    if image.get("exif_data"):
        print("EXIF data available")
```

**When to use**: When you know the file is an image, or when you need image-specific information.

---

## Common Patterns

### Checking File Before Processing

Always check if the file exists and if the operation succeeded:

```python
result = get_media_info("my_file.mp4")
if not result["success"]:
    print(f"Error: {result['error']}")
    return

# Process based on type
if result["media_type"] == "video":
    # Handle video
elif result["media_type"] == "audio":
    # Handle audio
elif result["media_type"] == "image":
    # Handle image
```

### Filtering by Properties

Use metadata to filter or categorize files:

```python
result = get_media_info("video.mp4")
if result["success"] and result["media_type"] == "video":
    video = result["video_info"]
    if video["width"] >= 1920:  # Full HD or higher
        print("High resolution video")
    if video["duration"] > 3600:  # Longer than 1 hour
        print("Long video")
```

### Batch Processing

Process multiple files efficiently:

```python
from ixmachina.tools.media import get_media_info

files = ["video1.mp4", "audio1.mp3", "image1.jpg"]
for file_path in files:
    result = get_media_info(file_path)
    if result["success"]:
        print(f"{file_path}: {result['media_type']}")
```

---

## Design Decisions

### Why Separate Functions?

Three specialized functions (`get_audio_info`, `get_video_info`, `get_image_info`) plus one unified function (`get_media_info`):

- **Specialized functions**: Faster when you know the type, avoid detection overhead
- **Unified function**: Convenient when type is unknown, single interface for all types
- **Flexibility**: Choose based on your use case

### Why Different Libraries?

Each media type uses the best library for that format:
- **Audio**: `mutagen` - excellent format support, handles metadata well
- **Video**: `ffprobe` (FFmpeg) - industry standard, comprehensive analysis
- **Image**: `Pillow` - Python standard, broad format support, EXIF handling

This ensures the best possible metadata extraction for each type.

### Why Structured Output?

Metadata is nested by type:
- Top level: `media_type`, `file_size`, `file_path`
- Type-specific: `audio_info`, `video_info`, `image_info`

This makes it easy to access relevant information without checking every possible field.

### Error Handling

All functions return structured errors:
- File doesn't exist: Clear error message
- Unsupported format: Identifies the issue
- Missing dependencies: Explains what's needed (e.g., FFmpeg for video)

This helps users understand and fix issues quickly.

