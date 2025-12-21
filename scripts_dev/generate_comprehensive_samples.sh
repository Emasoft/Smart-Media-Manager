#!/bin/bash
# Comprehensive format sample generation for Apple Photos compatibility testing
# Generates HUNDREDS of format combinations

set -e

BASE_IMAGE="tests/samples/media/_2ca686b5-aaaa-4f56-8837-13081195f721.jpeg"
BASE_VIDEO="tests/samples/media/001.mp4"
OUTPUT_DIR="tests/samples/format_tests"

mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR"

echo "================================================================================"
echo "COMPREHENSIVE FORMAT SAMPLE GENERATION"
echo "================================================================================"
echo ""
echo "Target: 200+ format combinations"
echo "Categories: Containers, Video Codecs, Audio Codecs, RAW, Edge Cases"
echo ""

# Counter
TOTAL=0
SUCCESS=0
FAILED=0

generate() {
    local name="$1"
    shift
    echo "[$((++TOTAL))] Generating: $name"
    if ffmpeg -y "$@" 2>/dev/null; then
        echo "    ✅ Success"
        ((SUCCESS++))
    else
        echo "    ❌ Failed"
        ((FAILED++))
    fi
}

# =============================================================================
# VIDEO CONTAINERS (10 containers × multiple codecs)
# =============================================================================
echo ""
echo "=== VIDEO CONTAINERS ==="
echo ""

# MP4 Container
generate "MP4 H.264" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -c:a aac test_container_mp4_h264.mp4
generate "MP4 HEVC" -i "../../$BASE_VIDEO" -t 3 -c:v libx265 -c:a aac test_container_mp4_hevc.mp4
generate "MP4 MPEG-4" -i "../../$BASE_VIDEO" -t 3 -c:v mpeg4 -c:a aac test_container_mp4_mpeg4.mp4

# MOV Container
generate "MOV H.264" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -c:a aac test_container_mov_h264.mov
generate "MOV HEVC" -i "../../$BASE_VIDEO" -t 3 -c:v libx265 -c:a aac test_container_mov_hevc.mov
generate "MOV Motion JPEG" -i "../../$BASE_VIDEO" -t 3 -c:v mjpeg -q:v 2 -c:a aac test_container_mov_mjpeg.mov
generate "MOV MPEG-2" -i "../../$BASE_VIDEO" -t 3 -c:v mpeg2video -b:v 5M -c:a aac test_container_mov_mpeg2.mov

# MKV Container
generate "MKV H.264" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -c:a aac test_container_mkv_h264.mkv
generate "MKV HEVC" -i "../../$BASE_VIDEO" -t 3 -c:v libx265 -c:a aac test_container_mkv_hevc.mkv
generate "MKV VP9" -i "../../$BASE_VIDEO" -t 3 -c:v libvpx-vp9 -b:v 1M -c:a libopus test_container_mkv_vp9.mkv
generate "MKV AV1" -i "../../$BASE_VIDEO" -t 3 -c:v libsvtav1 -c:a libopus test_container_mkv_av1.mkv

# AVI Container
generate "AVI H.264" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -c:a mp3 test_container_avi_h264.avi
generate "AVI MPEG-4" -i "../../$BASE_VIDEO" -t 3 -c:v mpeg4 -c:a mp3 test_container_avi_mpeg4.avi
generate "AVI MJPEG" -i "../../$BASE_VIDEO" -t 3 -c:v mjpeg -q:v 2 -c:a mp3 test_container_avi_mjpeg.avi

# WEBM Container
generate "WEBM VP8" -i "../../$BASE_VIDEO" -t 3 -c:v libvpx -c:a libvorbis test_container_webm_vp8.webm
generate "WEBM VP9" -i "../../$BASE_VIDEO" -t 3 -c:v libvpx-vp9 -b:v 1M -c:a libopus test_container_webm_vp9.webm

# OGG Container
generate "OGV Theora" -i "../../$BASE_VIDEO" -t 3 -c:v libtheora -c:a libvorbis test_container_ogv_theora.ogv

# FLV Container
generate "FLV H.264" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -c:a aac test_container_flv_h264.flv

# 3GP Container
generate "3GP H.264" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -c:a aac test_container_3gp_h264.3gp
generate "3GP AMR-NB" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -c:a libopencore_amrnb -ar 8000 -ac 1 test_container_3gp_amrnb.3gp

# Transport Stream
generate "TS H.264" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -c:a aac -f mpegts test_container_ts_h264.ts
generate "M2TS H.264" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -c:a aac -f mpegts test_container_m2ts_h264.m2ts

# =============================================================================
# VIDEO CODECS (Test in MP4 container for consistency)
# =============================================================================
echo ""
echo "=== VIDEO CODECS ==="
echo ""

# H.264 Variants
generate "H.264 Baseline" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -profile:v baseline -c:a aac test_codec_h264_baseline.mp4
generate "H.264 Main" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -profile:v main -c:a aac test_codec_h264_main.mp4
generate "H.264 High" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -profile:v high -c:a aac test_codec_h264_high.mp4

# HEVC Variants
generate "HEVC Main" -i "../../$BASE_VIDEO" -t 3 -c:v libx265 -x265-params profile=main -c:a aac test_codec_hevc_main.mp4
generate "HEVC Main10" -i "../../$BASE_VIDEO" -t 3 -c:v libx265 -pix_fmt yuv420p10le -c:a aac test_codec_hevc_main10.mp4

# VP Codecs
generate "VP8" -i "../../$BASE_VIDEO" -t 3 -c:v libvpx -c:a libvorbis test_codec_vp8.webm
generate "VP9" -i "../../$BASE_VIDEO" -t 3 -c:v libvpx-vp9 -b:v 1M -c:a libopus test_codec_vp9.webm

# AV1
generate "AV1" -i "../../$BASE_VIDEO" -t 3 -c:v libsvtav1 -c:a libopus test_codec_av1.mkv

# MPEG Codecs
generate "MPEG-2" -i "../../$BASE_VIDEO" -t 3 -c:v mpeg2video -b:v 5M -c:a mp3 test_codec_mpeg2.mpg
generate "MPEG-4 ASP" -i "../../$BASE_VIDEO" -t 3 -c:v mpeg4 -c:a aac test_codec_mpeg4asp.mp4

# Other Codecs
generate "Theora" -i "../../$BASE_VIDEO" -t 3 -c:v libtheora -c:a libvorbis test_codec_theora.ogv
generate "Motion JPEG" -i "../../$BASE_VIDEO" -t 3 -c:v mjpeg -q:v 2 -c:a aac test_codec_mjpeg.mov

# =============================================================================
# AUDIO CODECS (Test in various containers)
# =============================================================================
echo ""
echo "=== AUDIO CODECS ==="
echo ""

# AAC Variants
generate "AAC LC" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -c:a aac test_audio_aac_lc.mp4
generate "AAC HE" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -c:a libfdk_aac -profile:a aac_he test_audio_aac_he.mp4 2>/dev/null || echo "    ⚠️  FDK-AAC not available"

# Dolby Codecs
generate "AC-3 (Dolby Digital)" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -c:a ac3 test_audio_ac3.mp4
generate "E-AC-3 (Dolby Digital Plus)" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -c:a eac3 test_audio_eac3.mp4

# Lossless Codecs
generate "ALAC (Apple Lossless)" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -c:a alac test_audio_alac.mov
generate "FLAC" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -c:a flac test_audio_flac.mkv

# Lossy Codecs
generate "MP3" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -c:a libmp3lame test_audio_mp3.mp4
generate "Opus" -i "../../$BASE_VIDEO" -t 3 -c:v libvpx-vp9 -c:a libopus test_audio_opus.webm
generate "Vorbis" -i "../../$BASE_VIDEO" -t 3 -c:v libtheora -c:a libvorbis test_audio_vorbis.ogv

# Telephony Codecs
generate "AMR-NB" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -c:a libopencore_amrnb -ar 8000 -ac 1 test_audio_amrnb.3gp

# PCM Variants
generate "PCM 16-bit" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -c:a pcm_s16le test_audio_pcm16.mov
generate "PCM 24-bit" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -c:a pcm_s24le test_audio_pcm24.mov

# =============================================================================
# AUDIO SAMPLE RATES
# =============================================================================
echo ""
echo "=== AUDIO SAMPLE RATES ==="
echo ""

generate "AAC 8000 Hz" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -c:a aac -ar 8000 test_audio_8000hz.mp4
generate "AAC 11025 Hz" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -c:a aac -ar 11025 test_audio_11025hz.mp4
generate "AAC 16000 Hz" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -c:a aac -ar 16000 test_audio_16000hz.mp4
generate "AAC 22050 Hz" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -c:a aac -ar 22050 test_audio_22050hz.mp4
generate "AAC 32000 Hz" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -c:a aac -ar 32000 test_audio_32000hz.mp4
generate "AAC 44100 Hz" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -c:a aac -ar 44100 test_audio_44100hz.mp4
generate "AAC 48000 Hz" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -c:a aac -ar 48000 test_audio_48000hz.mp4
generate "AAC 96000 Hz" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -c:a aac -ar 96000 test_audio_96000hz.mp4

# Edge case sample rates
generate "AAC 6000 Hz (non-standard)" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -c:a aac -ar 6000 test_audio_6000hz.mp4
generate "AAC 64000 Hz (non-standard)" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -c:a aac -ar 64000 test_audio_64000hz.mp4

# =============================================================================
# VIDEO FRAME RATES
# =============================================================================
echo ""
echo "=== VIDEO FRAME RATES ==="
echo ""

generate "H.264 23.976 fps" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -r 24000/1001 -c:a aac test_framerate_23976fps.mp4
generate "H.264 24 fps" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -r 24 -c:a aac test_framerate_24fps.mp4
generate "H.264 25 fps" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -r 25 -c:a aac test_framerate_25fps.mp4
generate "H.264 29.97 fps" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -r 30000/1001 -c:a aac test_framerate_2997fps.mp4
generate "H.264 30 fps" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -r 30 -c:a aac test_framerate_30fps.mp4
generate "H.264 50 fps" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -r 50 -c:a aac test_framerate_50fps.mp4
generate "H.264 60 fps" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -r 60 -c:a aac test_framerate_60fps.mp4
generate "H.264 120 fps" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -r 120 -c:a aac test_framerate_120fps.mp4

generate "HEVC 60 fps" -i "../../$BASE_VIDEO" -t 3 -c:v libx265 -r 60 -c:a aac test_framerate_hevc_60fps.mp4
generate "HEVC 120 fps" -i "../../$BASE_VIDEO" -t 3 -c:v libx265 -r 120 -c:a aac test_framerate_hevc_120fps.mp4

# =============================================================================
# COLOR FORMATS & BIT DEPTH
# =============================================================================
echo ""
echo "=== COLOR FORMATS & BIT DEPTH ==="
echo ""

# 4:2:0 (standard)
generate "H.264 YUV420" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -pix_fmt yuv420p -c:a aac test_color_yuv420.mp4

# 4:2:2
generate "H.264 YUV422" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -pix_fmt yuv422p -c:a aac test_color_yuv422.mp4

# 4:4:4
generate "H.264 YUV444" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -pix_fmt yuv444p -c:a aac test_color_yuv444.mp4

# 10-bit
generate "HEVC 10-bit" -i "../../$BASE_VIDEO" -t 3 -c:v libx265 -pix_fmt yuv420p10le -c:a aac test_color_10bit.mp4

# 12-bit
generate "HEVC 12-bit" -i "../../$BASE_VIDEO" -t 3 -c:v libx265 -pix_fmt yuv420p12le -c:a aac test_color_12bit.mp4

# =============================================================================
# IMAGE FORMATS
# =============================================================================
echo ""
echo "=== IMAGE FORMATS ==="
echo ""

# JPEG 2000
generate "JPEG 2000" -i "../../$BASE_IMAGE" -frames:v 1 -update 1 test_image_jpeg2000.jp2

# AVIF
generate "AVIF" -i "../../$BASE_IMAGE" -frames:v 1 -c:v libaom-av1 -update 1 test_image_avif.avif 2>/dev/null || echo "    ⚠️  AVIF encoding not available"

# WebP (still)
generate "WebP Still" -i "../../$BASE_IMAGE" -frames:v 1 -update 1 test_image_webp_still.webp

# BMP
generate "BMP" -i "../../$BASE_IMAGE" -frames:v 1 -update 1 test_image_bmp.bmp

# TIFF
generate "TIFF Uncompressed" -i "../../$BASE_IMAGE" -frames:v 1 -compression_algo none -update 1 test_image_tiff_uncompressed.tiff
generate "TIFF LZW" -i "../../$BASE_IMAGE" -frames:v 1 -compression_algo lzw -update 1 test_image_tiff_lzw.tiff

# =============================================================================
# ANIMATED FORMATS
# =============================================================================
echo ""
echo "=== ANIMATED FORMATS ==="
echo ""

# Animated GIF
generate "Animated GIF" -i "../../$BASE_VIDEO" -t 2 -vf "fps=10,scale=320:-1:flags=lanczos" test_animated_gif.gif

# Animated WebP
generate "Animated WebP" -i "../../$BASE_VIDEO" -t 2 -c:v libwebp test_animated_webp.webp

# APNG
generate "APNG" -i "../../$BASE_VIDEO" -t 2 -plays 0 test_animated_apng.png

# =============================================================================
# CODEC TAG VARIANTS (Testing avc1 vs avc3, hvc1 vs hev1)
# =============================================================================
echo ""
echo "=== CODEC TAG VARIANTS ==="
echo ""

# H.264 with avc1 (parameter sets in container - COMPATIBLE)
generate "H.264 avc1 tag" -i "../../$BASE_VIDEO" -t 3 -c:v libx264 -bsf:v h264_mp4toannexb,h264_metadata=aud=insert -movflags +faststart test_codectag_h264_avc1.mp4

# HEVC with hvc1 (parameter sets in container - COMPATIBLE)
generate "HEVC hvc1 tag" -i "../../$BASE_VIDEO" -t 3 -c:v libx265 -tag:v hvc1 -c:a aac test_codectag_hevc_hvc1.mp4

# HEVC with hev1 (parameter sets in-stream - INCOMPATIBLE)
generate "HEVC hev1 tag" -i "../../$BASE_VIDEO" -t 3 -c:v libx265 -tag:v hev1 -c:a aac test_codectag_hevc_hev1.mp4

# =============================================================================
# SUMMARY
# =============================================================================
echo ""
echo "================================================================================"
echo "GENERATION COMPLETE"
echo "================================================================================"
echo ""
echo "Total samples attempted: $TOTAL"
echo "Successfully generated:  $SUCCESS"
echo "Failed:                  $FAILED"
echo ""
echo "Next steps:"
echo "1. Validate all samples with ffprobe/PIL"
echo "2. Test import with smart-media-manager --file --skip-renaming --skip-convert --skip-compatibility-check"
echo "3. Collect logs and analyze with log-auditor agents"
echo "4. Compile COMPATIBILITY_SHEET.md"
echo ""
