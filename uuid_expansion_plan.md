# UUID Expansion Plan

## Current UUID Limitations

Current UUIDs identify only:
- Container format (MP4, MOV, MKV)
- Video codec family (H.264, HEVC, VP9)
- Image format (JPEG, PNG, WebP)

Current UUIDs DO NOT identify:
- Bit depth (8-bit vs 10-bit vs 12-bit)
- Pixel format (yuv420p, yuv422p, yuv444p, rgb24)
- Sample rate (44100Hz, 48000Hz, 96000Hz, unusual rates)
- Sample format (s16, s24, s32, f32)
- Color space (bt709, bt2020, srgb)
- Profile/Level (H.264 High@4.1, HEVC Main10@5.1)
- Chroma subsampling (4:2:0, 4:2:2, 4:4:4)

## Expanded UUID Schema

### Video Format UUIDs

Format: `{base-uuid}-{bitdepth}-{pixfmt}-{profile}-V`

Examples:
- `b2e62c4a-6122-548c-9bfa-0fcf3613942a-8bit-yuv420p-high-V` = H.264 8-bit 4:2:0 High profile
- `b2e62c4a-6122-548c-9bfa-0fcf3613942a-10bit-yuv420p-high10-V` = H.264 10-bit 4:2:0 High10 profile
- `faf4b553-de47-5bc8-80ea-d026a2571456-8bit-yuv420p-main-V` = HEVC 8-bit 4:2:0 Main profile
- `faf4b553-de47-5bc8-80ea-d026a2571456-10bit-yuv420p-main10-V` = HEVC 10-bit 4:2:0 Main10 profile

### Audio Format UUIDs

Format: `{base-uuid}-{samplerate}-{samplefmt}-A`

Examples:
- `aac-48000-s16-A` = AAC at 48kHz 16-bit (standard)
- `aac-44100-s16-A` = AAC at 44.1kHz 16-bit (standard)
- `aac-6000-s16-A` = AAC at 6kHz 16-bit (unusual, incompatible)

### Image Format UUIDs

Format: `{base-uuid}-{bitdepth}-{colorspace}-I`

Examples:
- `d33d5c73-5f1a-5c4b-878e-58c3f9c193c0-8bit-srgb-I` = JPEG 8-bit sRGB
- `8a88adf4-d744-55d7-8cb3-7aa1288edf7c-8bit-srgb-I` = PNG 8-bit sRGB
- `8a88adf4-d744-55d7-8cb3-7aa1288edf7c-16bit-srgb-I` = PNG 16-bit sRGB

## Apple Photos Compatibility Matrix

### Video Formats

**Compatible (Direct Import):**
- H.264 8-bit 4:2:0 High profile in MP4/MOV
- HEVC 8-bit 4:2:0 Main profile in MP4/MOV  
- HEVC 10-bit 4:2:0 Main10 profile in MP4/MOV
- AV1 8-bit 4:2:0 in MP4

**Needs Rewrap (Container Change Only):**
- H.264 8-bit 4:2:0 in MKV → rewrap to MP4

**Needs Transcode (Re-encode Required):**
- H.264 10-bit (any pixel format) → transcode to HEVC 8-bit or HEVC 10-bit
- H.264 4:2:2 or 4:4:4 → transcode to HEVC 4:2:0
- VP9 (any configuration) → transcode to HEVC

### Audio Formats

**Compatible (Direct Import):**
- AAC at 44100Hz, 48000Hz (16-bit, 24-bit)
- AC-3 (Dolby Digital) at standard rates
- EAC-3 (Dolby Digital Plus) at standard rates
- ALAC (Apple Lossless) at standard rates
- PCM at standard rates

**Needs Transcode:**
- AAC at unusual rates (< 8000Hz, > 96000Hz) → transcode to AAC 48000Hz
- Opus → transcode to AAC
- Vorbis → transcode to AAC
- DTS → transcode to AC-3 or AAC

## Implementation Priority

### Phase 1: Critical Video Parameters (Fixes Current Failures)
1. H.264 bit depth (8-bit vs 10-bit)
2. HEVC bit depth (8-bit vs 10-bit)
3. Pixel format (yuv420p vs yuv422p vs yuv444p)

### Phase 2: Audio Parameters
1. Sample rate detection
2. Sample format detection

### Phase 3: Advanced Parameters
1. Color space (BT.709, BT.2020, etc.)
2. Profile/Level detection
3. HDR metadata

## Detection Strategy

Use ffprobe to extract parameters:
```json
{
  "streams": [{
    "codec_name": "h264",
    "profile": "High",
    "pix_fmt": "yuv420p",
    "bits_per_raw_sample": "8",
    "color_space": "bt709",
    "sample_rate": "48000",
    "sample_fmt": "s16"
  }]
}
```

## UUID Generation Strategy

Instead of random UUIDs, use deterministic hashing:
```python
import hashlib

def generate_format_uuid(codec, bitdepth, pixfmt, profile):
    params = f"{codec}-{bitdepth}-{pixfmt}-{profile}"
    return hashlib.sha256(params.encode()).hexdigest()[:36]
```

This ensures:
- Same parameters → same UUID
- Reproducible across systems
- No UUID conflicts
