#!/usr/bin/env python3
"""Analyze ffprobe outputs and identify missing format combinations."""

import re
from pathlib import Path
from collections import defaultdict

# Parse ffprobe outputs
def parse_formats(file_path):
    """Parse formats/muxers/demuxers."""
    formats = []
    with open(file_path) as f:
        lines = f.readlines()
        started = False
        for line in lines:
            if line.strip().startswith('--'):
                started = True
                continue
            if started and line.strip():
                # Format: " D. matroska        Matroska / WebM"
                match = re.match(r'\s*([DE\s]{2})\s+(\S+)\s+(.+)', line)
                if match:
                    flags, name, description = match.groups()
                    formats.append({
                        'name': name.strip(),
                        'description': description.strip(),
                        'demux': 'D' in flags,
                        'mux': 'E' in flags
                    })
    return formats

def parse_codecs(file_path):
    """Parse codecs."""
    codecs = []
    with open(file_path) as f:
        lines = f.readlines()
        started = False
        for line in lines:
            if line.strip().startswith('------'):
                started = True
                continue
            if started and line.strip():
                # Format: " DEV.L. h264                 H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10"
                match = re.match(r'\s*([DEVAILS\.]{6})\s+(\S+)\s+(.+)', line)
                if match:
                    flags, name, description = match.groups()
                    codec_type = 'video' if 'V' in flags else 'audio' if 'A' in flags else 'subtitle' if 'S' in flags else 'data'
                    codecs.append({
                        'name': name.strip(),
                        'description': description.strip(),
                        'type': codec_type,
                        'decode': 'D' in flags,
                        'encode': 'E' in flags
                    })
    return codecs

def parse_pix_fmts(file_path):
    """Parse pixel formats."""
    pix_fmts = []
    with open(file_path) as f:
        lines = f.readlines()
        started = False
        for line in lines:
            if line.strip().startswith('-----'):
                started = True
                continue
            if started and line.strip():
                # Format: "IO... yuv420p                3            12"
                match = re.match(r'\s*([IO\.]{5})\s+(\S+)', line)
                if match:
                    flags, name = match.groups()
                    pix_fmts.append({
                        'name': name.strip(),
                        'input': 'I' in flags,
                        'output': 'O' in flags
                    })
    return pix_fmts

def parse_sample_fmts(file_path):
    """Parse sample formats."""
    sample_fmts = []
    with open(file_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('name'):
                parts = line.split()
                if parts:
                    sample_fmts.append(parts[0])
    return sample_fmts

def parse_layouts(file_path):
    """Parse channel layouts."""
    layouts = []
    with open(file_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('NAME') and not line.startswith('Individual'):
                parts = line.split()
                if parts:
                    layouts.append(parts[0])
    return layouts

# Load current test samples
def get_tested_formats():
    """Get list of already tested format combinations."""
    tested = {
        'containers': set(),
        'video_codecs': set(),
        'audio_codecs': set(),
        'pixel_formats': set(),
        'sample_rates': set(),
        'channel_layouts': set(),
        'edge_cases': set()
    }

    samples_dir = Path('tests/samples/format_tests')
    if samples_dir.exists():
        for f in samples_dir.glob('test_*'):
            name = f.stem.replace('test_', '')

            # Categorize by prefix
            if name.startswith('container_'):
                parts = name.replace('container_', '').split('_')
                if len(parts) >= 2:
                    tested['containers'].add(parts[0])  # e.g., 'mp4', 'mkv'
                    tested['video_codecs'].add(parts[1])  # e.g., 'h264', 'hevc'
            elif name.startswith('codec_'):
                codec = name.replace('codec_', '')
                tested['video_codecs'].add(codec.split('_')[0])
            elif name.startswith('audio_'):
                parts = name.replace('audio_', '').split('_')
                tested['audio_codecs'].add(parts[0])
            elif name.startswith('color_'):
                tested['pixel_formats'].add(name.replace('color_', ''))
            elif name.startswith('edge_'):
                tested['edge_cases'].add(name.replace('edge_', ''))

    return tested

# Main analysis
print("Parsing ffprobe outputs...")
formats = parse_formats('format_analysis/ffprobe_formats.txt')
codecs = parse_codecs('format_analysis/ffprobe_codecs.txt')
pix_fmts = parse_pix_fmts('format_analysis/ffprobe_pix_fmts.txt')
sample_fmts = parse_sample_fmts('format_analysis/ffprobe_sample_fmts.txt')
layouts = parse_layouts('format_analysis/ffprobe_layouts.txt')

tested = get_tested_formats()

# Categorize codecs
video_codecs = [c for c in codecs if c['type'] == 'video' and c['encode']]
audio_codecs = [c for c in codecs if c['type'] == 'audio' and c['encode']]
subtitle_codecs = [c for c in codecs if c['type'] == 'subtitle']

# Create markdown report
md = []
md.append("# Missing Format Combinations Analysis")
md.append("")
md.append("Comprehensive analysis of untested format combinations based on ffprobe capabilities.")
md.append("")
md.append("---")
md.append("")

# Summary statistics
md.append("## Summary Statistics")
md.append("")
md.append("| Category | Total Available | Currently Tested | Missing |")
md.append("|----------|-----------------|------------------|---------|")
md.append(f"| **Container Formats** | {len([f for f in formats if f['mux']])} | {len(tested['containers'])} | {len([f for f in formats if f['mux']]) - len(tested['containers'])} |")
md.append(f"| **Video Codecs** | {len(video_codecs)} | {len(tested['video_codecs'])} | {len(video_codecs) - len(tested['video_codecs'])} |")
md.append(f"| **Audio Codecs** | {len(audio_codecs)} | {len(tested['audio_codecs'])} | {len(audio_codecs) - len(tested['audio_codecs'])} |")
md.append(f"| **Pixel Formats** | {len([p for p in pix_fmts if p['output']])} | {len(tested['pixel_formats'])} | {len([p for p in pix_fmts if p['output']]) - len(tested['pixel_formats'])} |")
md.append("")

# Missing containers
md.append("## Missing Container Formats")
md.append("")
md.append("Container formats that can be encoded but have not been tested:")
md.append("")
md.append("| Format | Description | Status |")
md.append("|--------|-------------|--------|")

missing_containers = []
for fmt in formats:
    if fmt['mux'] and fmt['name'] not in tested['containers']:
        md.append(f"| `{fmt['name']}` | {fmt['description']} | ❌ Not tested |")
        missing_containers.append(fmt['name'])

if not missing_containers:
    md.append("| — | No missing containers | ✅ Complete |")

md.append("")
md.append(f"**Total missing containers**: {len(missing_containers)}")
md.append("")

# Missing video codecs
md.append("## Missing Video Codecs")
md.append("")
md.append("Video codecs that can be encoded but have not been tested:")
md.append("")
md.append("| Codec | Description | Status |")
md.append("|-------|-------------|--------|")

missing_video_codecs = []
for codec in video_codecs:
    # Simplify codec name for comparison
    codec_simple = codec['name'].split('_')[0]
    if codec_simple not in tested['video_codecs']:
        md.append(f"| `{codec['name']}` | {codec['description']} | ❌ Not tested |")
        missing_video_codecs.append(codec['name'])

md.append("")
md.append(f"**Total missing video codecs**: {len(missing_video_codecs)}")
md.append("")

# Missing audio codecs
md.append("## Missing Audio Codecs")
md.append("")
md.append("Audio codecs that can be encoded but have not been tested:")
md.append("")
md.append("| Codec | Description | Status |")
md.append("|-------|-------------|--------|")

missing_audio_codecs = []
for codec in audio_codecs:
    codec_simple = codec['name'].split('_')[0]
    if codec_simple not in tested['audio_codecs']:
        md.append(f"| `{codec['name']}` | {codec['description']} | ❌ Not tested |")
        missing_audio_codecs.append(codec['name'])

md.append("")
md.append(f"**Total missing audio codecs**: {len(missing_audio_codecs)}")
md.append("")

# Missing pixel formats
md.append("## Missing Pixel Formats")
md.append("")
md.append("Showing first 50 untested pixel formats (many are esoteric):")
md.append("")
md.append("| Pixel Format | Status |")
md.append("|--------------|--------|")

missing_pix = []
for pix in pix_fmts[:50]:  # Limit to 50 for readability
    if pix['output'] and pix['name'] not in tested['pixel_formats']:
        md.append(f"| `{pix['name']}` | ❌ Not tested |")
        missing_pix.append(pix['name'])

md.append("")
md.append(f"**Total missing pixel formats**: {len([p for p in pix_fmts if p['output']])} (showing first 50)")
md.append("")

# RAW formats (special category)
md.append("## RAW Camera Formats (Not in ffprobe)")
md.append("")
md.append("Camera RAW formats require special handling and cannot be generated with ffmpeg:")
md.append("")
md.append("| Brand | Extensions | Status |")
md.append("|-------|------------|--------|")

raw_formats = [
    ("Canon", ".cr2, .cr3, .crw", "❌ Not tested"),
    ("Nikon", ".nef, .nrw", "❌ Not tested"),
    ("Sony", ".arw, .srf, .sr2", "❌ Not tested"),
    ("Fujifilm", ".raf", "❌ Not tested"),
    ("Olympus", ".orf", "❌ Not tested"),
    ("Panasonic", ".rw2, .raw", "❌ Not tested"),
    ("Pentax", ".pef, .ptx", "❌ Not tested"),
    ("Leica", ".rwl, .dng", "❌ Not tested (DNG attempted)"),
    ("Hasselblad", ".3fr, .fff", "❌ Not tested"),
    ("Phase One", ".iiq", "❌ Not tested"),
    ("Sigma", ".x3f", "❌ Not tested"),
    ("Epson", ".erf", "❌ Not tested"),
    ("Kodak", ".dcr, .kdc", "❌ Not tested"),
    ("Minolta", ".mrw", "❌ Not tested"),
    ("Samsung", ".srw", "❌ Not tested"),
]

for brand, exts, status in raw_formats:
    md.append(f"| {brand} | {exts} | {status} |")

md.append("")
md.append("**Note**: RAW formats require actual camera files or specialized converters, cannot be generated synthetically.")
md.append("")

# Priority recommendations
md.append("## Priority Testing Recommendations")
md.append("")
md.append("### High Priority (Common Formats)")
md.append("")
md.append("These are commonly used formats that should be tested:")
md.append("")

high_priority = []
common_containers = ['mp4', 'mov', 'mkv', 'avi', 'webm', 'flv', 'wmv', 'mpg', 'mpeg', '3gp', 'm2ts', 'ts', 'mts', 'vob', 'f4v']
common_video = ['h264', 'hevc', 'vp8', 'vp9', 'av1', 'mpeg4', 'mpeg2video', 'mpeg1video', 'mjpeg', 'msmpeg4v3', 'wmv2']
common_audio = ['aac', 'mp3', 'ac3', 'eac3', 'flac', 'opus', 'vorbis', 'alac', 'pcm_s16le', 'pcm_s24le', 'dts', 'truehd']

for container in common_containers:
    if container not in tested['containers']:
        high_priority.append(f"Container: `{container}`")

for codec in common_video:
    if codec not in tested['video_codecs']:
        high_priority.append(f"Video codec: `{codec}`")

for codec in common_audio:
    if codec not in tested['audio_codecs']:
        high_priority.append(f"Audio codec: `{codec}`")

for item in high_priority[:20]:  # Show top 20
    md.append(f"- {item}")

if not high_priority:
    md.append("- ✅ All high-priority formats have been tested!")

md.append("")

# Exotic/professional formats
md.append("### Medium Priority (Professional/Broadcast)")
md.append("")
professional = ['mxf', 'gxf', 'lxf', 'dnxhd', 'prores', 'ffv1', 'huffyuv', 'utvideo', 'cineform']
md.append("Professional and broadcast formats:")
md.append("")
for fmt in professional:
    status = "✅ Tested" if fmt in tested['containers'] or fmt in tested['video_codecs'] else "❌ Not tested"
    md.append(f"- `{fmt}`: {status}")

md.append("")

# Full lists
md.append("## Complete Available Formats")
md.append("")
md.append(f"### All Muxable Containers ({len([f for f in formats if f['mux']])} total)")
md.append("")
md.append("| Format | Description |")
md.append("|--------|-------------|")
for fmt in sorted([f for f in formats if f['mux']], key=lambda x: x['name']):
    tested_mark = "✅" if fmt['name'] in tested['containers'] else "❌"
    md.append(f"| {tested_mark} `{fmt['name']}` | {fmt['description']} |")

md.append("")
md.append(f"### All Encodable Video Codecs ({len(video_codecs)} total)")
md.append("")
md.append("| Codec | Description |")
md.append("|-------|-------------|")
for codec in sorted(video_codecs, key=lambda x: x['name']):
    codec_simple = codec['name'].split('_')[0]
    tested_mark = "✅" if codec_simple in tested['video_codecs'] else "❌"
    md.append(f"| {tested_mark} `{codec['name']}` | {codec['description']} |")

md.append("")
md.append(f"### All Encodable Audio Codecs ({len(audio_codecs)} total)")
md.append("")
md.append("| Codec | Description |")
md.append("|-------|-------------|")
for codec in sorted(audio_codecs, key=lambda x: x['name']):
    codec_simple = codec['name'].split('_')[0]
    tested_mark = "✅" if codec_simple in tested['audio_codecs'] else "❌"
    md.append(f"| {tested_mark} `{codec['name']}` | {codec['description']} |")

md.append("")
md.append("---")
md.append("")
md.append("*Generated by analyze_missing_formats.py*")

# Write output
output_file = Path('MISSING_FORMATS.md')
with open(output_file, 'w') as f:
    f.write('\n'.join(md))

print(f"✅ Created {output_file}")
print(f"\nSummary:")
print(f"  - Missing containers: {len(missing_containers)}")
print(f"  - Missing video codecs: {len(missing_video_codecs)}")
print(f"  - Missing audio codecs: {len(missing_audio_codecs)}")
print(f"  - RAW formats: 15 brands untested")
