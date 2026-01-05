# Test Samples

Synthetic test media files generated with FFmpeg. Total size must stay under 3MB.

## License

All files in this directory are **synthetically generated** using FFmpeg's test source filters (`testsrc`, `color`). They contain no copyrighted content and are free to use, modify, and distribute.

## Contents

### Images (`images/`)

| File | Format | Size | Description |
|------|--------|------|-------------|
| `test_pattern.jpg` | JPEG | 320x240 | Test pattern |
| `test_pattern.png` | PNG | 320x240 | Test pattern |
| `test_pattern.webp` | WebP | 320x240 | Test pattern |
| `test_pattern.bmp` | BMP | 160x120 | Test pattern |
| `test_pattern.tiff` | TIFF | 160x120 | Test pattern |
| `test_pattern.heic` | HEIC | 320x240 | Test pattern |
| `static.gif` | GIF | 160x120 | Solid color (static) |
| `animated.gif` | GIF | 160x120 | Animated (3 frames) |
| `animated.apng` | APNG | 160x120 | Animated PNG |

### Videos (`videos/`)

| File | Format | Codec | Duration | Description |
|------|--------|-------|----------|-------------|
| `test_video.mp4` | MP4 | H.264 | 1s | Test pattern |
| `test_video.mov` | MOV | H.264 | 1s | Test pattern |
| `test_hevc.mp4` | MP4 | HEVC | 1s | Test pattern |

### RAW (`raw/`)

Reserved for RAW camera format samples (must be copyright-free).

## Regenerating

All files can be regenerated using FFmpeg:

```bash
# Image example
ffmpeg -f lavfi -i "testsrc=duration=1:size=320x240:rate=1" -frames:v 1 output.jpg

# Video example
ffmpeg -f lavfi -i "testsrc=duration=1:size=320x240:rate=15" -c:v libx264 output.mp4
```

## Guidelines

- Keep total size under 3MB
- Only synthetic or verified public domain content
- No personal photos or videos
- For large test files, use `samples_dev/` (gitignored)
