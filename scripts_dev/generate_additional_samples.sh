#!/bin/bash
# Generate additional format samples including RAW proxies, edge cases, and rare formats

set -e

# Change to the format_tests directory
cd tests/samples/format_tests

# Source video for generating samples
BASE_VIDEO="../media/001.mp4"
BASE_IMAGE="../media/463108291_3854235968172130_2760581135168458128_n.jpg"

if [[ ! -f "$BASE_VIDEO" ]]; then
    echo "ERROR: Base video not found: $BASE_VIDEO"
    exit 1
fi

if [[ ! -f "$BASE_IMAGE" ]]; then
    echo "ERROR: Base image not found: $BASE_IMAGE"
    exit 1
fi

echo "Generating additional format samples..."
echo "========================================"

# RAW/DNG Formats
# Note: We can create DNG (Adobe's open RAW format) but not proprietary RAW formats
# DNG can be created from JPEG/TIFF
echo "Creating DNG (Adobe RAW) sample..."
if command -v convert &> /dev/null; then
    convert "$BASE_IMAGE" test_raw_dng.dng 2>/dev/null || echo "  Skipped DNG (requires ImageMagick with DNG support)"
else
    echo "  Skipped DNG (ImageMagick not found)"
fi

# ProRes formats (Apple's professional codec)
echo "Creating ProRes samples..."
ffmpeg -y -i "$BASE_VIDEO" -t 3 -c:v prores -profile:v 0 -c:a pcm_s16le test_codec_prores_proxy.mov 2>&1 | grep -v "^\[" || true
ffmpeg -y -i "$BASE_VIDEO" -t 3 -c:v prores -profile:v 2 -c:a pcm_s16le test_codec_prores_422.mov 2>&1 | grep -v "^\[" || true
ffmpeg -y -i "$BASE_VIDEO" -t 3 -c:v prores -profile:v 3 -c:a pcm_s16le test_codec_prores_422hq.mov 2>&1 | grep -v "^\[" || true

# Variable Frame Rate (VFR) video
echo "Creating VFR sample..."
ffmpeg -y -i "$BASE_VIDEO" -t 3 -c:v libx264 -vsync vfr -r 30 -c:a aac test_edge_vfr.mp4 2>&1 | grep -v "^\[" || true

# Multi-track audio
echo "Creating multi-track audio sample..."
ffmpeg -y -i "$BASE_VIDEO" -i "$BASE_VIDEO" -t 3 -map 0:v:0 -map 0:a:0 -map 1:a:0 -c:v libx264 -c:a aac test_edge_multitrack_audio.mp4 2>&1 | grep -v "^\[" || true

# Subtitle streams (soft subtitles)
echo "Creating subtitle sample..."
# First create a simple SRT file
cat > temp_subtitles.srt <<'EOF'
1
00:00:00,000 --> 00:00:02,000
Test subtitle 1

2
00:00:02,000 --> 00:00:03,000
Test subtitle 2
EOF

ffmpeg -y -i "$BASE_VIDEO" -i temp_subtitles.srt -t 3 -c:v libx264 -c:a aac -c:s mov_text test_edge_subtitles.mp4 2>&1 | grep -v "^\[" || true
rm -f temp_subtitles.srt

# HDR video (BT.2020 color space, 10-bit)
echo "Creating HDR sample..."
ffmpeg -y -i "$BASE_VIDEO" -t 3 -c:v libx265 -pix_fmt yuv420p10le -colorspace bt2020nc -color_primaries bt2020 -color_trc smpte2084 -c:a aac test_edge_hdr_bt2020.mp4 2>&1 | grep -v "^\[" || true

# Interlaced video
echo "Creating interlaced sample..."
ffmpeg -y -i "$BASE_VIDEO" -t 3 -c:v libx264 -flags +ilme+ildct -top 1 -c:a aac test_edge_interlaced.mp4 2>&1 | grep -v "^\[" || true

# Very high resolution (4K)
echo "Creating 4K sample..."
ffmpeg -y -i "$BASE_VIDEO" -t 3 -vf scale=3840:2160 -c:v libx264 -preset ultrafast -c:a aac test_edge_4k.mp4 2>&1 | grep -v "^\[" || true

# Very low resolution
echo "Creating low-res sample..."
ffmpeg -y -i "$BASE_VIDEO" -t 3 -vf scale=320:240 -c:v libx264 -c:a aac test_edge_lowres.mp4 2>&1 | grep -v "^\[" || true

# Extremely high bitrate
echo "Creating high bitrate sample..."
ffmpeg -y -i "$BASE_VIDEO" -t 3 -c:v libx264 -b:v 50M -maxrate 50M -bufsize 100M -c:a aac test_edge_high_bitrate.mp4 2>&1 | grep -v "^\[" || true

# Portrait orientation (9:16)
echo "Creating portrait orientation sample..."
ffmpeg -y -i "$BASE_VIDEO" -t 3 -vf "crop=ih*9/16:ih" -c:v libx264 -c:a aac test_edge_portrait.mp4 2>&1 | grep -v "^\[" || true

# Square video (1:1)
echo "Creating square video sample..."
ffmpeg -y -i "$BASE_VIDEO" -t 3 -vf "crop=min(iw\\,ih):min(iw\\,ih)" -c:v libx264 -c:a aac test_edge_square.mp4 2>&1 | grep -v "^\[" || true

# Video with rotation metadata
echo "Creating rotated video sample..."
ffmpeg -y -i "$BASE_VIDEO" -t 3 -c:v libx264 -c:a aac -metadata:s:v:0 rotate=90 test_edge_rotated.mp4 2>&1 | grep -v "^\[" || true

# Audio-only file (no video)
echo "Creating audio-only sample..."
ffmpeg -y -i "$BASE_VIDEO" -t 3 -vn -c:a aac test_edge_audio_only.m4a 2>&1 | grep -v "^\[" || true

# Silent video (no audio)
echo "Creating silent video sample..."
ffmpeg -y -i "$BASE_VIDEO" -t 3 -an -c:v libx264 test_edge_silent_video.mp4 2>&1 | grep -v "^\[" || true

# MPEG-2 codec (older format)
echo "Creating MPEG-2 sample..."
ffmpeg -y -i "$BASE_VIDEO" -t 3 -c:v mpeg2video -q:v 2 -c:a mp2 test_codec_mpeg2.mpg 2>&1 | grep -v "^\[" || true

# MPEG-1 codec (very old format)
echo "Creating MPEG-1 sample..."
ffmpeg -y -i "$BASE_VIDEO" -t 3 -c:v mpeg1video -q:v 2 -c:a mp2 test_codec_mpeg1.mpg 2>&1 | grep -v "^\[" || true

# DNxHD codec (Avid's codec)
echo "Creating DNxHD sample..."
ffmpeg -y -i "$BASE_VIDEO" -t 3 -vf scale=1920:1080 -c:v dnxhd -b:v 145M -c:a pcm_s16le test_codec_dnxhd.mov 2>&1 | grep -v "^\[" || true

# AV1 codec in MP4 (modern efficient codec)
echo "Creating AV1 in MP4 sample..."
ffmpeg -y -i "$BASE_VIDEO" -t 3 -c:v libaom-av1 -cpu-used 8 -c:a aac test_codec_av1.mp4 2>&1 | grep -v "^\[" || true

# VP9 in MP4 (usually in WebM, but can be in MP4)
echo "Creating VP9 in MP4 sample..."
ffmpeg -y -i "$BASE_VIDEO" -t 3 -c:v libvpx-vp9 -c:a aac test_codec_vp9.mp4 2>&1 | grep -v "^\[" || true

# WMV (Windows Media Video)
echo "Creating WMV sample..."
ffmpeg -y -i "$BASE_VIDEO" -t 3 -c:v wmv2 -c:a wmav2 test_container_wmv.wmv 2>&1 | grep -v "^\[" || true

# ASF container
echo "Creating ASF sample..."
ffmpeg -y -i "$BASE_VIDEO" -t 3 -c:v mpeg4 -c:a mp3 test_container_asf.asf 2>&1 | grep -v "^\[" || true

# 3GP with AMR-WB audio (wideband)
echo "Creating 3GP with AMR-WB sample..."
ffmpeg -y -i "$BASE_VIDEO" -t 3 -c:v h263 -s 176x144 -c:a amr_wb test_audio_amr_wb.3gp 2>&1 | grep -v "^\[" || true

# MXF container (professional broadcasting)
echo "Creating MXF sample..."
ffmpeg -y -i "$BASE_VIDEO" -t 3 -c:v mpeg2video -c:a pcm_s16le test_container_mxf.mxf 2>&1 | grep -v "^\[" || true

# Matroska with different audio codecs
echo "Creating MKV with DTS audio..."
ffmpeg -y -i "$BASE_VIDEO" -t 3 -c:v libx264 -c:a dca test_audio_dts.mkv 2>&1 | grep -v "^\[" || true

# Multiple subtitle tracks
echo "Creating sample with multiple subtitle tracks..."
cat > temp_sub1.srt <<'EOF'
1
00:00:00,000 --> 00:00:02,000
English subtitle
EOF

cat > temp_sub2.srt <<'EOF'
1
00:00:00,000 --> 00:00:02,000
Spanish subtitle
EOF

ffmpeg -y -i "$BASE_VIDEO" -i temp_sub1.srt -i temp_sub2.srt -t 3 -c:v libx264 -c:a aac -c:s mov_text -metadata:s:s:0 language=eng -metadata:s:s:1 language=spa test_edge_multiple_subtitles.mp4 2>&1 | grep -v "^\[" || true
rm -f temp_sub1.srt temp_sub2.srt

# Chapter markers
echo "Creating sample with chapters..."
cat > temp_chapters.txt <<'EOF'
;FFMETADATA1
[CHAPTER]
TIMEBASE=1/1000
START=0
END=1500
title=Chapter 1

[CHAPTER]
TIMEBASE=1/1000
START=1500
END=3000
title=Chapter 2
EOF

ffmpeg -y -i "$BASE_VIDEO" -i temp_chapters.txt -t 3 -c:v libx264 -c:a aac -map_metadata 1 test_edge_chapters.mp4 2>&1 | grep -v "^\[" || true
rm -f temp_chapters.txt

# Unusual aspect ratios
echo "Creating ultrawide sample..."
ffmpeg -y -i "$BASE_VIDEO" -t 3 -vf "scale=2560:1080,setsar=1" -c:v libx264 -c:a aac test_edge_ultrawide.mp4 2>&1 | grep -v "^\[" || true

# Very short duration (1 frame)
echo "Creating single-frame video..."
ffmpeg -y -i "$BASE_VIDEO" -frames:v 1 -c:v libx264 -c:a aac test_edge_single_frame.mp4 2>&1 | grep -v "^\[" || true

# High frame count image sequence container
echo "Creating image sequence container..."
ffmpeg -y -i "$BASE_VIDEO" -t 1 -c:v mjpeg -q:v 2 test_edge_mjpeg_sequence.avi 2>&1 | grep -v "^\[" || true

# Create TIFF with various compressions
echo "Creating TIFF samples..."
convert "$BASE_IMAGE" -compress None test_image_tiff_uncompressed.tiff 2>/dev/null || echo "  Skipped uncompressed TIFF"
convert "$BASE_IMAGE" -compress LZW test_image_tiff_lzw.tiff 2>/dev/null || echo "  Skipped LZW TIFF"
convert "$BASE_IMAGE" -compress Zip test_image_tiff_zip.tiff 2>/dev/null || echo "  Skipped ZIP TIFF"

# Multi-page TIFF
echo "Creating multi-page TIFF..."
convert "$BASE_IMAGE" "$BASE_IMAGE" test_image_tiff_multipage.tiff 2>/dev/null || echo "  Skipped multi-page TIFF"

# PNG with different bit depths
echo "Creating PNG samples..."
convert "$BASE_IMAGE" -depth 8 test_image_png_8bit.png 2>/dev/null || echo "  Skipped 8-bit PNG"
convert "$BASE_IMAGE" -depth 16 test_image_png_16bit.png 2>/dev/null || echo "  Skipped 16-bit PNG"

# Grayscale images
echo "Creating grayscale samples..."
convert "$BASE_IMAGE" -colorspace Gray test_image_gray.jpg 2>/dev/null || echo "  Skipped grayscale JPEG"
convert "$BASE_IMAGE" -colorspace Gray test_image_gray.png 2>/dev/null || echo "  Skipped grayscale PNG"

# CMYK JPEG (unusual)
echo "Creating CMYK JPEG..."
convert "$BASE_IMAGE" -colorspace CMYK test_image_cmyk.jpg 2>/dev/null || echo "  Skipped CMYK JPEG"

echo ""
echo "========================================"
echo "Additional sample generation complete!"
echo "========================================"

# Count and list generated files
echo ""
echo "Generated files:"
ls -lh test_* 2>/dev/null | awk '{print $9, "("$5")"}'

# Count total
TOTAL=$(ls test_* 2>/dev/null | wc -l)
echo ""
echo "Total new samples: $TOTAL"
