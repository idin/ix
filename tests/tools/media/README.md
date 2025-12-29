# Media Tools Tests

This directory contains tests for the media tools (`get_audio_info`, `get_video_info`, `get_image_info`, `get_media_info`).

## Test Files

- **Image tests**: Can run fully with programmatically generated test images
- **Audio tests**: Basic error handling tests are included. For full testing, actual audio files (MP3, FLAC, etc.) are needed
- **Video tests**: Basic error handling tests are included. For full testing, actual video files (MP4, AVI, etc.) and `ffprobe` (from ffmpeg) are needed

## Getting Test Media Files

To fully test audio and video functionality, you'll need actual media files. Here are some options:

### Option 1: Use Your Own Media Files
Place test media files in the test directory:
- Audio: MP3, FLAC, OGG, AAC, M4A, WAV files
- Video: MP4, AVI, MKV, MOV, WebM files

### Option 2: Download Sample Files
You can download small sample files from:
- [Sample Audio Files](https://file-examples.com/index.php/sample-audio-files/)
- [Sample Video Files](https://file-examples.com/index.php/sample-video-files/)

### Option 3: Create Test Files with ffmpeg
If you have ffmpeg installed, you can create minimal test files:

```bash
# Create a short test audio file (MP3)
ffmpeg -f lavfi -i "sine=frequency=1000:duration=5" -acodec libmp3lame test.mp3

# Create a short test video file (MP4)
ffmpeg -f lavfi -i "testsrc=duration=5:size=320x240:rate=1" -c:v libx264 test.mp4
```

## Running Tests

Run all media tests:
```bash
pytest tests/tools/media/
```

Run specific test file:
```bash
pytest tests/tools/media/get_image_info/test_get_image_info.py
```

