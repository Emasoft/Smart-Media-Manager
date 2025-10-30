#!/usr/bin/env python3
"""Generate all possible ffmpeg format conversion commands."""

import re
from pathlib import Path
from itertools import product
from typing import List, Dict, Tuple

def parse_formats(file_path: str) -> List[Dict]:
    """Parse formats/muxers from ffprobe output."""
    formats = []
    with open(file_path) as f:
        lines = f.readlines()
        started = False
        for line in lines:
            if line.strip().startswith('--'):
                started = True
                continue
            if started and line.strip():
                match = re.match(r'\s*([DE\s]{2})\s+(\S+)\s+(.+)', line)
                if match:
                    flags, name, description = match.groups()
                    if 'E' in flags:  # Can encode
                        formats.append({
                            'name': name.strip(),
                            'description': description.strip(),
                            'extensions': get_common_extension(name.strip())
                        })
    return formats

def parse_codecs(file_path: str, codec_type: str) -> List[Dict]:
    """Parse video or audio codecs from ffprobe output."""
    codecs = []
    with open(file_path) as f:
        lines = f.readlines()
        started = False
        for line in lines:
            if line.strip().startswith('------'):
                started = True
                continue
            if started and line.strip():
                match = re.match(r'\s*([DEVAILS\.]{6})\s+(\S+)\s+(.+)', line)
                if match:
                    flags, name, description = match.groups()
                    type_flag = 'V' if codec_type == 'video' else 'A'
                    if type_flag in flags and 'E' in flags:  # Can encode
                        codecs.append({
                            'name': name.strip(),
                            'description': description.strip()
                        })
    return codecs

def parse_pix_fmts(file_path: str, limit: int = 50) -> List[str]:
    """Parse pixel formats, return most common ones."""
    pix_fmts = []
    common_formats = [
        'yuv420p', 'yuv422p', 'yuv444p', 'yuv420p10le', 'yuv422p10le', 'yuv444p10le',
        'yuv420p12le', 'rgb24', 'rgba', 'bgr24', 'bgra', 'gray', 'nv12', 'nv21',
        'yuyv422', 'uyvy422', 'gbrp', 'gbrap'
    ]

    with open(file_path) as f:
        lines = f.readlines()
        started = False
        for line in lines:
            if line.strip().startswith('-----'):
                started = True
                continue
            if started and line.strip():
                match = re.match(r'\s*([IO\.]{5})\s+(\S+)', line)
                if match:
                    flags, name = match.groups()
                    if 'O' in flags:  # Can output
                        pix_fmts.append(name.strip())

    # Prioritize common formats
    result = []
    for fmt in common_formats:
        if fmt in pix_fmts:
            result.append(fmt)

    # Add others up to limit
    for fmt in pix_fmts:
        if fmt not in result and len(result) < limit:
            result.append(fmt)

    return result[:limit]

def parse_sample_fmts(file_path: str) -> List[str]:
    """Parse audio sample formats."""
    sample_fmts = []
    with open(file_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('name'):
                parts = line.split()
                if parts:
                    sample_fmts.append(parts[0])
    return sample_fmts

def get_common_extension(format_name: str) -> str:
    """Get file extension for format."""
    extension_map = {
        'mp4': '.mp4', 'mov': '.mov', 'mkv': '.mkv', 'avi': '.avi', 'webm': '.webm',
        'flv': '.flv', 'wmv': '.wmv', 'mpg': '.mpg', 'mpeg': '.mpeg', '3gp': '.3gp',
        '3g2': '.3g2', 'ts': '.ts', 'mts': '.mts', 'm2ts': '.m2ts', 'vob': '.vob',
        'asf': '.asf', 'ogv': '.ogv', 'ogg': '.ogg', 'f4v': '.f4v', 'gif': '.gif',
        'apng': '.apng', 'mxf': '.mxf', 'gxf': '.gxf', 'nut': '.nut', 'dv': '.dv',
        'matroska': '.mkv', 'webm': '.webm', 'ipod': '.m4v', 'ismv': '.ismv',
        'mp3': '.mp3', 'aac': '.aac', 'ac3': '.ac3', 'flac': '.flac', 'wav': '.wav',
        'opus': '.opus', 'ogg': '.ogg', 'aiff': '.aiff', 'au': '.au', 'caf': '.caf',
        'image2': '.png', 'png': '.png', 'jpg': '.jpg', 'jpeg': '.jpg', 'tiff': '.tiff',
        'bmp': '.bmp', 'gif': '.gif', 'webp': '.webp', 'avif': '.avif',
        'hevc': '.hevc', 'h264': '.h264', 'h263': '.h263', 'mjpeg': '.mjpeg',
        'rawvideo': '.yuv', 'dnxhd': '.dnxhd', 'prores': '.mov'
    }
    return extension_map.get(format_name, f'.{format_name}')

def filter_compatible_combinations(container: Dict, video_codec: Dict, audio_codec: Dict) -> bool:
    """Check if container/codec combination is valid."""
    # Known incompatible combinations
    container_name = container['name']
    video_name = video_codec['name']
    audio_name = audio_codec['name']

    # WebM only supports VP8/VP9/AV1 + Vorbis/Opus
    if container_name == 'webm':
        if video_name not in ['vp8', 'vp9', 'av1', 'libaom-av1', 'libvpx', 'libvpx-vp9']:
            return False
        if audio_name not in ['libvorbis', 'vorbis', 'libopus', 'opus']:
            return False

    # OGG/OGV typically uses Theora + Vorbis
    if container_name in ['ogg', 'ogv']:
        if video_name not in ['libtheora', 'theora'] and video_name:
            return False
        if audio_name not in ['libvorbis', 'vorbis', 'libopus', 'opus', 'flac']:
            return False

    # MP4/MOV prefer H.264/HEVC/MPEG-4 + AAC/MP3
    if container_name in ['mp4', 'mov', 'ipod', 'ismv', 'f4v']:
        valid_video = ['libx264', 'h264', 'libx265', 'hevc', 'mpeg4', 'mpeg2video',
                       'libvpx-vp9', 'libaom-av1', 'mjpeg', 'png', 'prores']
        valid_audio = ['aac', 'mp3', 'ac3', 'eac3', 'alac', 'pcm_s16le', 'pcm_s24le',
                       'libfdk_aac', 'libmp3lame']
        if video_name and video_name not in valid_video:
            return False
        if audio_name and audio_name not in valid_audio:
            return False

    # MKV is very flexible, accepts almost anything

    # AVI prefers older codecs
    if container_name == 'avi':
        if video_name in ['vp9', 'av1', 'hevc']:  # AVI doesn't handle these well
            return False

    # FLV prefers H.264/VP6 + MP3/AAC
    if container_name == 'flv':
        if video_name not in ['libx264', 'h264', 'flv', 'vp6']:
            return False
        if audio_name not in ['mp3', 'aac', 'libmp3lame', 'libfdk_aac']:
            return False

    return True

def generate_video_commands(input_file: str, base_output_dir: str) -> List[Dict]:
    """Generate all video conversion commands."""
    commands = []

    # Parse available formats
    formats = parse_formats('format_analysis/ffprobe_formats.txt')
    video_codecs = parse_codecs('format_analysis/ffprobe_codecs.txt', 'video')
    audio_codecs = parse_codecs('format_analysis/ffprobe_codecs.txt', 'audio')
    pix_fmts = parse_pix_fmts('format_analysis/ffprobe_pix_fmts.txt', limit=20)

    # Common bitrates for testing
    video_bitrates = ['500k', '1M', '2M', '5M']
    audio_bitrates = ['96k', '128k', '192k', '320k']
    sample_rates = [8000, 16000, 22050, 44100, 48000, 96000]

    # Prioritize common combinations
    common_containers = ['mp4', 'mkv', 'avi', 'webm', 'mov', 'flv', 'wmv', 'mpg', '3gp', 'ogv']
    common_video_codecs = ['libx264', 'libx265', 'mpeg4', 'mpeg2video', 'mpeg1video',
                           'libvpx', 'libvpx-vp9', 'libaom-av1', 'mjpeg', 'libtheora']
    common_audio_codecs = ['aac', 'mp3', 'ac3', 'eac3', 'libvorbis', 'libopus', 'libmp3lame']

    # Filter to common formats
    formats = [f for f in formats if f['name'] in common_containers]
    video_codecs = [c for c in video_codecs if c['name'] in common_video_codecs]
    audio_codecs = [c for c in audio_codecs if c['name'] in common_audio_codecs]

    test_id = 0

    # Generate basic container + codec combinations
    for container in formats:
        for video_codec in video_codecs:
            for audio_codec in audio_codecs:
                if not filter_compatible_combinations(container, video_codec, audio_codec):
                    continue

                test_id += 1
                output_file = f"{base_output_dir}/test_{test_id:04d}_{container['name']}_{video_codec['name']}_{audio_codec['name']}{container['extensions']}"

                cmd = f"ffmpeg -y -i {input_file} -t 3 -c:v {video_codec['name']} -c:a {audio_codec['name']}"

                # Add preset for x264/x265 for speed
                if 'x264' in video_codec['name'] or 'x265' in video_codec['name']:
                    cmd += " -preset ultrafast"

                # Add specific flags for some codecs
                if video_codec['name'] == 'libaom-av1':
                    cmd += " -cpu-used 8"
                elif video_codec['name'] in ['libvpx', 'libvpx-vp9']:
                    cmd += " -deadline realtime -cpu-used 8"

                cmd += f" {output_file}"

                commands.append({
                    'id': test_id,
                    'type': 'video',
                    'container': container['name'],
                    'video_codec': video_codec['name'],
                    'audio_codec': audio_codec['name'],
                    'output': output_file,
                    'command': cmd
                })

    # Generate pixel format variations
    for pix_fmt in pix_fmts[:10]:  # Limit to 10 most common
        test_id += 1
        container = 'mp4'
        output_file = f"{base_output_dir}/test_{test_id:04d}_pixfmt_{pix_fmt}.mp4"

        cmd = f"ffmpeg -y -i {input_file} -t 3 -c:v libx264 -pix_fmt {pix_fmt} -c:a aac -preset ultrafast {output_file}"

        commands.append({
            'id': test_id,
            'type': 'video_pixfmt',
            'container': container,
            'video_codec': 'libx264',
            'pix_fmt': pix_fmt,
            'output': output_file,
            'command': cmd
        })

    # Generate audio sample rate variations
    for sample_rate in sample_rates:
        test_id += 1
        output_file = f"{base_output_dir}/test_{test_id:04d}_audio_{sample_rate}hz.mp4"

        cmd = f"ffmpeg -y -i {input_file} -t 3 -c:v libx264 -c:a aac -ar {sample_rate} -preset ultrafast {output_file}"

        commands.append({
            'id': test_id,
            'type': 'audio_samplerate',
            'sample_rate': sample_rate,
            'output': output_file,
            'command': cmd
        })

    return commands

def generate_image_commands(input_file: str, base_output_dir: str) -> List[Dict]:
    """Generate all image conversion commands."""
    commands = []

    image_formats = [
        ('png', '.png', ['-compression_level 0', '-compression_level 9']),
        ('jpeg', '.jpg', ['-q:v 2', '-q:v 10', '-q:v 31']),
        ('tiff', '.tiff', ['-compression none', '-compression lzw', '-compression deflate']),
        ('bmp', '.bmp', ['']),
        ('webp', '.webp', ['-lossless 0 -q:v 75', '-lossless 1']),
        ('gif', '.gif', ['']),
        ('avif', '.avif', ['-crf 23', '-crf 40']),
    ]

    test_id = 0

    for fmt_name, ext, options in image_formats:
        for opt in options:
            test_id += 1
            opt_name = opt.replace(' ', '_').replace(':', '_').replace('-', '') or 'default'
            output_file = f"{base_output_dir}/test_{test_id:04d}_img_{fmt_name}_{opt_name}{ext}"

            cmd = f"ffmpeg -y -i {input_file} -vframes 1 {opt} {output_file}".replace('  ', ' ')

            commands.append({
                'id': test_id,
                'type': 'image',
                'format': fmt_name,
                'options': opt,
                'output': output_file,
                'command': cmd
            })

    return commands

def save_commands_to_file(commands: List[Dict], output_file: str):
    """Save commands to a JSON file."""
    import json
    with open(output_file, 'w') as f:
        json.dump(commands, f, indent=2)

if __name__ == '__main__':
    print("Generating all format conversion commands...")

    # Generate commands
    video_commands = generate_video_commands('tests/samples/media/001.mp4', 'tests/samples/format_tests')
    image_commands = generate_image_commands('tests/samples/media/463108291_3854235968172130_2760581135168458128_n.jpg', 'tests/samples/format_tests')

    all_commands = video_commands + image_commands

    # Save to file
    save_commands_to_file(all_commands, 'format_test_commands.json')

    print(f"✅ Generated {len(all_commands)} commands:")
    print(f"   - Video/audio combinations: {len(video_commands)}")
    print(f"   - Image formats: {len(image_commands)}")
    print(f"   - Saved to: format_test_commands.json")
