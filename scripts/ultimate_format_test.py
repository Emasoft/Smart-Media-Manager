#!/usr/bin/env python3
"""
Ultimate Format Compatibility Testing Orchestrator

Features:
- Auto-installs ffmpeg/ffprobe from Homebrew if missing
- Runs ffprobe to discover all available formats
- Loads extra formats from custom file
- Deduplicates and merges format lists
- Generates all test commands
- Executes sample generation
- Tests with Smart Media Manager
- Analyzes and generates comprehensive reports

Usage:
    uv run python3 scripts/ultimate_format_test.py
    uv run python3 scripts/ultimate_format_test.py --max-samples 20
    uv run python3 scripts/ultimate_format_test.py --skip-install
"""

import json
import subprocess
import sys
import shutil
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Set
from collections import defaultdict
import time

class UltimateFormatTester:
    def __init__(self, base_video: str, base_image: str, output_dir: str, results_dir: str):
        self.base_video = Path(base_video)
        self.base_image = Path(base_image)
        self.output_dir = Path(output_dir)
        self.results_dir = Path(results_dir)
        self.script_dir = Path(__file__).parent
        self.extra_formats_file = self.script_dir / 'extra_formats.txt'

        # Create directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # Format storage
        self.formats: List[Dict] = []
        self.video_codecs: List[Dict] = []
        self.audio_codecs: List[Dict] = []
        self.pix_fmts: List[str] = []
        self.sample_fmts: List[str] = []
        self.layouts: List[str] = []

        # Results
        self.commands: List[Dict] = []
        self.results: List[Dict] = []
        self.stats = {
            'total_commands': 0,
            'generated': 0,
            'generation_failed': 0,
            'tested': 0,
            'imported': 0,
            'failed': 0,
            'start_time': None,
            'end_time': None
        }

    def check_and_install_dependencies(self):
        """Check for ffmpeg/ffprobe and install via Homebrew if missing."""
        print("\n" + "="*80)
        print("DEPENDENCY CHECK")
        print("="*80)

        dependencies = ['ffmpeg', 'ffprobe']
        missing = []

        for dep in dependencies:
            if shutil.which(dep):
                print(f"✅ {dep} found: {shutil.which(dep)}")
            else:
                print(f"❌ {dep} not found")
                missing.append(dep)

        if missing:
            print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")

            # Check for Homebrew
            if not shutil.which('brew'):
                print("❌ Homebrew not found. Please install Homebrew first:")
                print("   /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
                sys.exit(1)

            print("\n📦 Installing missing dependencies via Homebrew...")
            try:
                # Install ffmpeg (includes ffprobe)
                print("   Installing ffmpeg (this may take a few minutes)...")
                subprocess.run(['brew', 'install', 'ffmpeg'], check=True)
                print("✅ ffmpeg installed successfully")

                # Verify installation
                if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
                    print("❌ Installation succeeded but commands not found. Try restarting terminal.")
                    sys.exit(1)

            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install dependencies: {e}")
                sys.exit(1)
        else:
            print("\n✅ All dependencies available")

    def run_ffprobe_queries(self):
        """Run all ffprobe queries to discover available formats."""
        print("\n" + "="*80)
        print("DISCOVERING FORMATS WITH FFPROBE")
        print("="*80)

        queries = {
            'formats': '-formats',
            'muxers': '-muxers',
            'demuxers': '-demuxers',
            'codecs': '-codecs',
            'pix_fmts': '-pix_fmts',
            'layouts': '-layouts',
            'sample_fmts': '-sample_fmts',
            'dispositions': '-dispositions'
        }

        outputs = {}

        for name, flag in queries.items():
            print(f"Running: ffprobe {flag}")
            try:
                result = subprocess.run(
                    ['ffprobe', flag],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                outputs[name] = result.stdout + result.stderr
                print(f"  ✅ Captured {len(outputs[name])} characters")
            except Exception as e:
                print(f"  ❌ Failed: {e}")
                outputs[name] = ""

        return outputs

    def parse_formats_from_text(self, text: str) -> List[Dict]:
        """Parse formats/muxers from text output."""
        formats = []
        lines = text.split('\n')
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
                    if 'E' in flags:  # Can encode
                        formats.append({
                            'name': name.strip(),
                            'description': description.strip()
                        })
        return formats

    def parse_codecs_from_text(self, text: str, codec_type: str) -> List[Dict]:
        """Parse video or audio codecs from text output."""
        codecs = []
        lines = text.split('\n')
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
                    type_flag = 'V' if codec_type == 'video' else 'A'
                    if type_flag in flags and 'E' in flags:  # Can encode
                        codecs.append({
                            'name': name.strip(),
                            'description': description.strip()
                        })
        return codecs

    def parse_pix_fmts_from_text(self, text: str) -> List[str]:
        """Parse pixel formats from text output."""
        pix_fmts = []
        lines = text.split('\n')
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
                    if 'O' in flags:  # Can output
                        pix_fmts.append(name.strip())
        return pix_fmts

    def parse_sample_fmts_from_text(self, text: str) -> List[str]:
        """Parse audio sample formats from text output."""
        sample_fmts = []
        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if line and not line.startswith('name'):
                parts = line.split()
                if parts:
                    sample_fmts.append(parts[0])
        return sample_fmts

    def parse_layouts_from_text(self, text: str) -> List[str]:
        """Parse channel layouts from text output."""
        layouts = []
        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if line and not line.startswith('NAME') and not line.startswith('Individual'):
                parts = line.split()
                if parts:
                    layouts.append(parts[0])
        return layouts

    def load_extra_formats(self):
        """Load extra formats from custom file."""
        print("\n" + "="*80)
        print("LOADING EXTRA FORMATS")
        print("="*80)

        if not self.extra_formats_file.exists():
            print(f"⚠️  Extra formats file not found: {self.extra_formats_file}")
            return {}, [], [], [], [], []

        print(f"Loading: {self.extra_formats_file}")

        with open(self.extra_formats_file) as f:
            text = f.read()

        # Parse different sections
        formats_text = ""
        codecs_text = ""
        pix_fmts_text = ""
        sample_fmts_text = ""
        layouts_text = ""

        current_section = None
        for line in text.split('\n'):
            if '===== FORMATS/MUXERS =====' in line:
                current_section = 'formats'
            elif '===== CODECS =====' in line:
                current_section = 'codecs'
            elif '===== PIXEL FORMATS =====' in line:
                current_section = 'pix_fmts'
            elif '===== SAMPLE FORMATS =====' in line:
                current_section = 'sample_fmts'
            elif '===== CHANNEL LAYOUTS =====' in line:
                current_section = 'layouts'
            elif not line.startswith('#') and line.strip():
                if current_section == 'formats':
                    formats_text += line + '\n'
                elif current_section == 'codecs':
                    codecs_text += line + '\n'
                elif current_section == 'pix_fmts':
                    pix_fmts_text += line + '\n'
                elif current_section == 'sample_fmts':
                    sample_fmts_text += line + '\n'
                elif current_section == 'layouts':
                    layouts_text += line + '\n'

        extra_formats = self.parse_formats_from_text(formats_text)
        extra_video_codecs = self.parse_codecs_from_text(codecs_text, 'video')
        extra_audio_codecs = self.parse_codecs_from_text(codecs_text, 'audio')
        extra_pix_fmts = self.parse_pix_fmts_from_text(pix_fmts_text)
        extra_sample_fmts = self.parse_sample_fmts_from_text(sample_fmts_text)
        extra_layouts = self.parse_layouts_from_text(layouts_text)

        print(f"  ✅ Loaded {len(extra_formats)} extra formats")
        print(f"  ✅ Loaded {len(extra_video_codecs)} extra video codecs")
        print(f"  ✅ Loaded {len(extra_audio_codecs)} extra audio codecs")
        print(f"  ✅ Loaded {len(extra_pix_fmts)} extra pixel formats")
        print(f"  ✅ Loaded {len(extra_sample_fmts)} extra sample formats")
        print(f"  ✅ Loaded {len(extra_layouts)} extra layouts")

        return extra_formats, extra_video_codecs, extra_audio_codecs, extra_pix_fmts, extra_sample_fmts, extra_layouts

    def deduplicate_formats(self):
        """Deduplicate all format lists."""
        print("\n" + "="*80)
        print("DEDUPLICATING FORMATS")
        print("="*80)

        # Deduplicate formats by name
        formats_dict = {}
        for fmt in self.formats:
            formats_dict[fmt['name']] = fmt
        self.formats = list(formats_dict.values())
        print(f"  Formats: {len(self.formats)} unique")

        # Deduplicate video codecs
        video_dict = {}
        for codec in self.video_codecs:
            video_dict[codec['name']] = codec
        self.video_codecs = list(video_dict.values())
        print(f"  Video codecs: {len(self.video_codecs)} unique")

        # Deduplicate audio codecs
        audio_dict = {}
        for codec in self.audio_codecs:
            audio_dict[codec['name']] = codec
        self.audio_codecs = list(audio_dict.values())
        print(f"  Audio codecs: {len(self.audio_codecs)} unique")

        # Deduplicate pixel formats
        self.pix_fmts = list(set(self.pix_fmts))
        print(f"  Pixel formats: {len(self.pix_fmts)} unique")

        # Deduplicate sample formats
        self.sample_fmts = list(set(self.sample_fmts))
        print(f"  Sample formats: {len(self.sample_fmts)} unique")

        # Deduplicate layouts
        self.layouts = list(set(self.layouts))
        print(f"  Layouts: {len(self.layouts)} unique")

    def discover_all_formats(self):
        """Main format discovery orchestration."""
        # Run ffprobe
        outputs = self.run_ffprobe_queries()

        # Parse ffprobe outputs
        print("\nParsing ffprobe outputs...")
        self.formats = self.parse_formats_from_text(outputs['formats'])
        self.video_codecs = self.parse_codecs_from_text(outputs['codecs'], 'video')
        self.audio_codecs = self.parse_codecs_from_text(outputs['codecs'], 'audio')
        self.pix_fmts = self.parse_pix_fmts_from_text(outputs['pix_fmts'])
        self.sample_fmts = self.parse_sample_fmts_from_text(outputs['sample_fmts'])
        self.layouts = self.parse_layouts_from_text(outputs['layouts'])

        print(f"  ffprobe formats: {len(self.formats)}")
        print(f"  ffprobe video codecs: {len(self.video_codecs)}")
        print(f"  ffprobe audio codecs: {len(self.audio_codecs)}")
        print(f"  ffprobe pixel formats: {len(self.pix_fmts)}")
        print(f"  ffprobe sample formats: {len(self.sample_fmts)}")
        print(f"  ffprobe layouts: {len(self.layouts)}")

        # Load extra formats
        extra_formats, extra_video, extra_audio, extra_pix, extra_sample, extra_layouts = self.load_extra_formats()

        # Merge
        self.formats.extend(extra_formats)
        self.video_codecs.extend(extra_video)
        self.audio_codecs.extend(extra_audio)
        self.pix_fmts.extend(extra_pix)
        self.sample_fmts.extend(extra_sample)
        self.layouts.extend(extra_layouts)

        # Deduplicate
        self.deduplicate_formats()

    def is_video_compatible_with_container(self, container: str, video_codec: str) -> bool:
        """Check if video codec is compatible with container."""
        # WebM only supports VP8/VP9/AV1
        if container == 'webm':
            return video_codec in ['vp8', 'vp9', 'av1', 'libaom-av1', 'libvpx', 'libvpx-vp9']

        # AVI has limitations with modern codecs
        if container == 'avi':
            return video_codec not in ['hevc', 'libx265', 'vp9', 'av1', 'libaom-av1']

        # MP4/MOV skip exotic codecs
        if container in ['mp4', 'mov']:
            return video_codec not in ['vp8', 'vp9', 'theora', 'ffv1']

        # OGG/OGV only support Theora
        if container in ['ogg', 'ogv']:
            return video_codec in ['theora', 'libtheora']

        # MKV is very flexible, accept most
        # For unknown containers, try it
        return True

    def is_audio_compatible_with_container(self, container: str, audio_codec: str) -> bool:
        """Check if audio codec is compatible with container."""
        # WebM only supports Vorbis/Opus
        if container == 'webm':
            return audio_codec in ['libvorbis', 'vorbis', 'libopus', 'opus']

        # AVI has limitations
        if container == 'avi':
            return audio_codec not in ['opus', 'vorbis', 'flac']

        # MP4/MOV prefer common codecs
        if container in ['mp4', 'mov']:
            # Skip very exotic
            return audio_codec not in ['vorbis', 'libvorbis']

        # OGG/OGV only support Vorbis/Opus/FLAC
        if container in ['ogg', 'ogv', 'oga']:
            return audio_codec in ['vorbis', 'libvorbis', 'opus', 'libopus', 'flac']

        # MKV is very flexible
        # For unknown containers, try it
        return True

    def generate_all_commands(self, max_samples: int = None):
        """Generate all format conversion commands.

        Uses independent testing approach:
        - Container + Video Codec (with default audio)
        - Container + Audio Codec (with default video)
        - Pixel format variations
        - Image format variations

        This avoids unnecessary combinations since:
        - Video codec support is independent of audio codec
        - Audio codec support is independent of video codec
        - Both depend on container format
        """
        print("\n" + "="*80)
        print("GENERATING FORMAT CONVERSION COMMANDS")
        print("="*80)

        commands = []
        cmd_id = 0

        # Use ALL discovered formats (not just priority)
        containers = self.formats
        video_codecs = self.video_codecs
        audio_codecs = self.audio_codecs

        print(f"\nFormat inventory:")
        print(f"  Containers: {len(containers)}")
        print(f"  Video codecs: {len(video_codecs)}")
        print(f"  Audio codecs: {len(audio_codecs)}")
        print(f"  Pixel formats: {len(self.pix_fmts)}")
        print(f"  Sample formats: {len(self.sample_fmts)}")
        print(f"  Layouts: {len(self.layouts)}")

        # Test 1: Container + Video Codec (independent of audio)
        # Use AAC as default audio since it's widely supported
        print(f"\n1. Testing Container + Video Codec combinations:")
        for container in containers:
            if max_samples and len(commands) >= max_samples:
                break
            for video_codec in video_codecs:
                if max_samples and len(commands) >= max_samples:
                    break

                # Check container-video compatibility
                if not self.is_video_compatible_with_container(container['name'], video_codec['name']):
                    continue

                cmd_id += 1
                output_name = f"test_{cmd_id:04d}_{container['name']}_video_{video_codec['name']}.{container['name']}"
                output_path = self.output_dir / output_name

                # Use AAC as default audio (widely supported)
                command = (
                    f"ffmpeg -y -i {self.base_video} "
                    f"-c:v {video_codec['name']} -c:a aac "
                    f"-t 5 -map_metadata 0 {output_path}"
                )

                commands.append({
                    'id': cmd_id,
                    'type': 'container_video',
                    'container': container['name'],
                    'video_codec': video_codec['name'],
                    'audio_codec': 'aac',
                    'command': command,
                    'output': str(output_path),
                    'description': f"{container['name'].upper()} + {video_codec['name']} video codec"
                })

        # Test 2: Container + Audio Codec (independent of video)
        # Use H.264 as default video since it's universally supported
        print(f"2. Testing Container + Audio Codec combinations:")
        for container in containers:
            if max_samples and len(commands) >= max_samples:
                break
            for audio_codec in audio_codecs:
                if max_samples and len(commands) >= max_samples:
                    break

                # Check container-audio compatibility
                if not self.is_audio_compatible_with_container(container['name'], audio_codec['name']):
                    continue

                cmd_id += 1
                output_name = f"test_{cmd_id:04d}_{container['name']}_audio_{audio_codec['name']}.{container['name']}"
                output_path = self.output_dir / output_name

                # Use H.264 as default video (universally supported)
                command = (
                    f"ffmpeg -y -i {self.base_video} "
                    f"-c:v libx264 -c:a {audio_codec['name']} "
                    f"-t 5 -map_metadata 0 {output_path}"
                )

                commands.append({
                    'id': cmd_id,
                    'type': 'container_audio',
                    'container': container['name'],
                    'video_codec': 'libx264',
                    'audio_codec': audio_codec['name'],
                    'command': command,
                    'output': str(output_path),
                    'description': f"{container['name'].upper()} + {audio_codec['name']} audio codec"
                })

        # Test 3: Pixel format variations (ALL formats)
        # Test with MP4+H.264 as baseline
        if not max_samples or len(commands) < max_samples:
            print(f"3. Testing Pixel Format variations:")
            for pix_fmt in self.pix_fmts:
                if max_samples and len(commands) >= max_samples:
                    break

                cmd_id += 1
                output_name = f"test_{cmd_id:04d}_pixfmt_{pix_fmt}.mp4"
                output_path = self.output_dir / output_name

                command = (
                    f"ffmpeg -y -i {self.base_video} "
                    f"-c:v libx264 -pix_fmt {pix_fmt} -c:a aac "
                    f"-t 5 {output_path}"
                )

                commands.append({
                    'id': cmd_id,
                    'type': 'pixel_format',
                    'pix_fmt': pix_fmt,
                    'command': command,
                    'output': str(output_path),
                    'description': f"Pixel format: {pix_fmt}"
                })

        # Test 4: Image format variations (ALL image containers)
        if not max_samples or len(commands) < max_samples:
            print(f"4. Testing Image Format variations:")
            # Map image containers to their codecs
            image_format_map = {
                'png': 'png',
                'jpg': 'mjpeg',
                'jpeg': 'mjpeg',
                'webp': 'libwebp',
                'tiff': 'tiff',
                'tif': 'tiff',
                'bmp': 'bmp',
                'gif': 'gif',
                'jp2': 'jpeg2000',
                'j2k': 'jpeg2000',
            }

            # Test all container formats that look like images
            for container in self.formats:
                if max_samples and len(commands) >= max_samples:
                    break

                ext = container['name']
                if ext in image_format_map:
                    cmd_id += 1
                    output_name = f"test_{cmd_id:04d}_image_{ext}.{ext}"
                    output_path = self.output_dir / output_name

                    codec = image_format_map[ext]
                    command = f"ffmpeg -y -i {self.base_image} -c:v {codec} {output_path}"

                    commands.append({
                        'id': cmd_id,
                        'type': 'image',
                        'format': ext,
                        'codec': codec,
                        'command': command,
                        'output': str(output_path),
                        'description': f"Image format: {ext.upper()}"
                    })

        self.commands = commands
        self.stats['total_commands'] = len(commands)

        print(f"\n✅ Generated {len(commands)} commands")
        print(f"   - Container + Video: {sum(1 for c in commands if c['type'] == 'container_video')}")
        print(f"   - Container + Audio: {sum(1 for c in commands if c['type'] == 'container_audio')}")
        print(f"   - Pixel formats: {sum(1 for c in commands if c['type'] == 'pixel_format')}")
        print(f"   - Image formats: {sum(1 for c in commands if c['type'] == 'image')}")
        return commands

    def step2_generate_samples(self, skip_existing: bool = True):
        """Step 2: Execute ffmpeg commands to generate test samples."""
        print("\n" + "="*80)
        print("STEP 2: GENERATING TEST SAMPLES")
        print("="*80)

        total = len(self.commands)
        print(f"\nGenerating {total} samples...")

        for i, cmd_info in enumerate(self.commands, 1):
            output_file = Path(cmd_info['output'])

            # Skip if exists
            if skip_existing and output_file.exists():
                print(f"[{i}/{total}] SKIP: {output_file.name} (already exists)")
                self.stats['generated'] += 1
                continue

            print(f"[{i}/{total}] Generating: {output_file.name}")

            try:
                # Execute ffmpeg command
                result = subprocess.run(
                    cmd_info['command'],
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=120
                )

                if result.returncode == 0 and output_file.exists():
                    self.stats['generated'] += 1
                    print(f"           ✅ Success ({output_file.stat().st_size} bytes)")
                else:
                    self.stats['generation_failed'] += 1
                    print(f"           ❌ Failed (exit code {result.returncode})")
                    # Log error
                    error_log = self.results_dir / f"generation_error_{cmd_info['id']}.log"
                    with open(error_log, 'w') as f:
                        f.write(f"Command: {cmd_info['command']}\n")
                        f.write(f"Exit code: {result.returncode}\n")
                        f.write(f"STDERR:\n{result.stderr}\n")

            except subprocess.TimeoutExpired:
                self.stats['generation_failed'] += 1
                print(f"           ⏱️  Timeout")
            except Exception as e:
                self.stats['generation_failed'] += 1
                print(f"           ❌ Error: {e}")

        print(f"\n✅ Sample generation complete:")
        print(f"   - Successfully generated: {self.stats['generated']}")
        print(f"   - Failed: {self.stats['generation_failed']}")

    def step3_test_samples(self):
        """Step 3: Test each sample with Smart Media Manager."""
        print("\n" + "="*80)
        print("STEP 3: TESTING SAMPLES WITH SMART MEDIA MANAGER")
        print("="*80)

        # Get all generated test files
        test_files = sorted(self.output_dir.glob('test_*'))
        print(f"\nFound {len(test_files)} test samples")

        for i, test_file in enumerate(test_files, 1):
            print(f"\n[{i}/{len(test_files)}] Testing: {test_file.name}")

            result = {
                'file': test_file.name,
                'size': test_file.stat().st_size,
                'extension': test_file.suffix,
                'timestamp': datetime.now().isoformat(),
            }

            # Run smart-media-manager
            cmd = [
                'uv', 'run', 'smart-media-manager',
                str(test_file),
                '--file',
                '--skip-renaming',
                '--skip-convert',
                '--skip-compatibility-check',
            ]

            try:
                proc = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=180
                )

                result['exit_code'] = proc.returncode
                result['stdout'] = proc.stdout
                result['stderr'] = proc.stderr

                # Parse import status
                imported = False
                compatible = False
                refused = False

                stdout = proc.stdout

                # Extract statistics
                if 'Total imported:' in stdout:
                    match = re.search(r'Total imported:.*?(\d+)', stdout)
                    if match:
                        total_imported = int(match.group(1))
                        imported = total_imported > 0

                if 'Compatible (no conversion):' in stdout:
                    match = re.search(r'Compatible \(no conversion\):.*?(\d+)', stdout)
                    if match:
                        compatible_count = int(match.group(1))
                        compatible = compatible_count > 0

                if 'Refused by Apple Photos:' in stdout:
                    match = re.search(r'Refused by Apple Photos:.*?(\d+)', stdout)
                    if match:
                        refused_count = int(match.group(1))
                        refused = refused_count > 0

                result['imported'] = imported
                result['compatible'] = compatible
                result['refused'] = refused

                # Save individual log
                log_file = self.results_dir / f"{test_file.stem}.log"
                with open(log_file, 'w') as f:
                    f.write(f"Test file: {test_file}\n")
                    f.write(f"Command: {' '.join(cmd)}\n")
                    f.write(f"\n=== STDOUT ===\n{proc.stdout}\n")
                    f.write(f"\n=== STDERR ===\n{proc.stderr}\n")
                    f.write(f"\n=== EXIT CODE ===\n{proc.returncode}\n")

                result['log_file'] = str(log_file)

                # Update stats
                self.stats['tested'] += 1
                if imported:
                    self.stats['imported'] += 1
                    print(f"           ✅ IMPORTED")
                elif proc.returncode == 0:
                    print(f"           ⚠️  Processed but not imported")
                else:
                    self.stats['failed'] += 1
                    print(f"           ❌ FAILED (exit code {proc.returncode})")

            except subprocess.TimeoutExpired:
                result['error'] = 'timeout'
                result['imported'] = False
                self.stats['failed'] += 1
                print(f"           ⏱️  TIMEOUT")
            except Exception as e:
                result['error'] = str(e)
                result['imported'] = False
                self.stats['failed'] += 1
                print(f"           ❌ ERROR: {e}")

            self.results.append(result)

        # Save results
        results_file = self.results_dir / 'comprehensive_test_results.json'
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\n✅ Testing complete:")
        print(f"   - Total tested: {self.stats['tested']}")
        if self.stats['tested'] > 0:
            print(f"   - Successfully imported: {self.stats['imported']} ({self.stats['imported']/self.stats['tested']*100:.1f}%)")
        print(f"   - Failed: {self.stats['failed']}")
        print(f"   - Results saved to: {results_file}")

    def step4_analyze_results(self):
        """Step 4: Analyze results and generate reports."""
        print("\n" + "="*80)
        print("STEP 4: ANALYZING RESULTS AND GENERATING REPORTS")
        print("="*80)

        # Run analysis scripts
        print("\nRunning analysis...")
        subprocess.run(['uv', 'run', 'python3', 'scripts/analyze_test_results.py'],
                      cwd=Path.cwd())

        print("\nGenerating compatibility sheet...")
        subprocess.run(['uv', 'run', 'python3', 'scripts/create_compatibility_sheet.py'],
                      cwd=Path.cwd())

        print("\nGenerating missing formats analysis...")
        subprocess.run(['uv', 'run', 'python3', 'scripts/analyze_missing_formats.py'],
                      cwd=Path.cwd())

        print("\n✅ Reports generated:")
        print("   - COMPATIBILITY_SHEET.md")
        print("   - compatibility.json")
        print("   - MISSING_FORMATS.md")
        print("   - format_tests_results/compatibility_summary.txt")

    def run_full_test(self, max_samples: int = None, skip_install: bool = False):
        """Run complete test pipeline."""
        self.stats['start_time'] = datetime.now()

        print("\n" + "="*80)
        print("ULTIMATE FORMAT COMPATIBILITY TEST")
        print("="*80)
        print(f"\nStarted: {self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")

        try:
            # Step 0: Check/install dependencies
            if not skip_install:
                self.check_and_install_dependencies()

            # Step 1: Discover formats
            self.discover_all_formats()

            # Step 2: Generate commands
            self.generate_all_commands(max_samples=max_samples)

            # Step 3: Generate samples
            self.step2_generate_samples()

            # Step 4: Test samples
            self.step3_test_samples()

            # Step 5: Analyze and report
            self.step4_analyze_results()

        except KeyboardInterrupt:
            print("\n\n⚠️  Test interrupted by user")
        except Exception as e:
            print(f"\n\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

        self.stats['end_time'] = datetime.now()
        duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()

        # Final summary
        print("\n" + "="*80)
        print("TEST COMPLETE")
        print("="*80)
        print(f"\nDuration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        print(f"\nStatistics:")
        print(f"  Total commands generated:  {self.stats['total_commands']}")
        print(f"  Samples generated:         {self.stats['generated']}")
        print(f"  Generation failed:         {self.stats['generation_failed']}")
        print(f"  Samples tested:            {self.stats['tested']}")
        if self.stats['tested'] > 0:
            print(f"  Successfully imported:     {self.stats['imported']} ({self.stats['imported']/self.stats['tested']*100:.1f}%)")
        print(f"  Failed:                    {self.stats['failed']}")
        print(f"\nReports available:")
        print(f"  - COMPATIBILITY_SHEET.md")
        print(f"  - compatibility.json")
        print(f"  - MISSING_FORMATS.md")
        print(f"  - format_tests_results/comprehensive_test_results.json")
        print(f"  - format_tests_results/compatibility_summary.txt")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Ultimate format compatibility testing with auto-discovery and auto-install',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run complete test (auto-installs dependencies)
  uv run python3 scripts/ultimate_format_test.py

  # Run with sample limit
  uv run python3 scripts/ultimate_format_test.py --max-samples 20

  # Skip dependency installation
  uv run python3 scripts/ultimate_format_test.py --skip-install

  # Custom paths
  uv run python3 scripts/ultimate_format_test.py \\
      --base-video path/to/video.mp4 \\
      --base-image path/to/image.jpg \\
      --output-dir path/to/samples \\
      --results-dir path/to/results
        """
    )

    parser.add_argument('--base-video', default='tests/samples/media/001.mp4',
                       help='Base video file for generating test samples')
    parser.add_argument('--base-image', default='tests/samples/media/463108291_3854235968172130_2760581135168458128_n.jpg',
                       help='Base image file for generating test samples')
    parser.add_argument('--output-dir', default='tests/samples/format_tests',
                       help='Output directory for test samples')
    parser.add_argument('--results-dir', default='format_tests_results',
                       help='Output directory for test results')
    parser.add_argument('--max-samples', type=int, default=None,
                       help='Maximum number of samples to generate (default: all)')
    parser.add_argument('--skip-install', action='store_true',
                       help='Skip automatic installation of dependencies')

    args = parser.parse_args()

    tester = UltimateFormatTester(
        base_video=args.base_video,
        base_image=args.base_image,
        output_dir=args.output_dir,
        results_dir=args.results_dir
    )

    tester.run_full_test(max_samples=args.max_samples, skip_install=args.skip_install)
