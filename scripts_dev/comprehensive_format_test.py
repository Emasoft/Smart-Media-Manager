#!/usr/bin/env python3
"""
Comprehensive Format Compatibility Testing Orchestrator

This script:
1. Generates all format conversion commands
2. Executes ffmpeg to create test samples
3. Tests each sample with Smart Media Manager
4. Collects and analyzes results
5. Generates comprehensive compatibility reports (MD + JSON)
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import time

# Import the command generator
sys.path.insert(0, str(Path(__file__).parent))
from generate_all_format_commands import (
    generate_video_commands,
    generate_image_commands,
    save_commands_to_file
)

class ComprehensiveFormatTester:
    def __init__(self, base_video: str, base_image: str, output_dir: str, results_dir: str):
        self.base_video = Path(base_video)
        self.base_image = Path(base_image)
        self.output_dir = Path(output_dir)
        self.results_dir = Path(results_dir)
        self.commands_file = Path('format_test_commands.json')
        self.results_file = self.results_dir / 'comprehensive_test_results.json'

        # Create directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)

        self.commands: List[Dict] = []
        self.results: List[Dict] = []
        self.stats = {
            'total': 0,
            'generated': 0,
            'generation_failed': 0,
            'tested': 0,
            'imported': 0,
            'failed': 0,
            'start_time': None,
            'end_time': None
        }

    def step1_generate_commands(self):
        """Step 1: Generate all ffmpeg conversion commands."""
        print("\n" + "="*80)
        print("STEP 1: Generating Format Conversion Commands")
        print("="*80)

        print(f"\nBase video: {self.base_video}")
        print(f"Base image: {self.base_image}")
        print(f"Output directory: {self.output_dir}")

        # Generate commands
        print("\nGenerating video format commands...")
        video_commands = generate_video_commands(str(self.base_video), str(self.output_dir))

        print("Generating image format commands...")
        image_commands = generate_image_commands(str(self.base_image), str(self.output_dir))

        self.commands = video_commands + image_commands
        self.stats['total'] = len(self.commands)

        # Save commands
        save_commands_to_file(self.commands, str(self.commands_file))

        print(f"\n✅ Generated {len(self.commands)} commands:")
        print(f"   - Video/audio combinations: {len(video_commands)}")
        print(f"   - Image formats: {len(image_commands)}")
        print(f"   - Commands saved to: {self.commands_file}")

    def step2_generate_samples(self, max_samples: int = None, skip_existing: bool = True):
        """Step 2: Execute ffmpeg commands to generate test samples."""
        print("\n" + "="*80)
        print("STEP 2: Generating Test Samples with ffmpeg")
        print("="*80)

        if not self.commands:
            print("Loading commands from file...")
            with open(self.commands_file) as f:
                self.commands = json.load(f)

        total = len(self.commands) if max_samples is None else min(len(self.commands), max_samples)
        print(f"\nGenerating {total} samples...")

        for i, cmd_info in enumerate(self.commands[:total], 1):
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
        print("STEP 3: Testing Samples with Smart Media Manager")
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
                    import re
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
        with open(self.results_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\n✅ Testing complete:")
        print(f"   - Total tested: {self.stats['tested']}")
        print(f"   - Successfully imported: {self.stats['imported']} ({self.stats['imported']/self.stats['tested']*100:.1f}%)")
        print(f"   - Failed: {self.stats['failed']}")
        print(f"   - Results saved to: {self.results_file}")

    def step4_analyze_results(self):
        """Step 4: Analyze results and generate reports."""
        print("\n" + "="*80)
        print("STEP 4: Analyzing Results and Generating Reports")
        print("="*80)

        if not self.results:
            print("Loading results from file...")
            with open(self.results_file) as f:
                self.results = json.load(f)

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

    def run_full_test(self, max_samples: int = None):
        """Run complete test pipeline."""
        self.stats['start_time'] = datetime.now()

        print("\n" + "="*80)
        print("COMPREHENSIVE FORMAT COMPATIBILITY TEST")
        print("="*80)
        print(f"\nStarted: {self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")

        try:
            # Step 1: Generate commands
            self.step1_generate_commands()

            # Step 2: Generate samples
            self.step2_generate_samples(max_samples=max_samples)

            # Step 3: Test samples
            self.step3_test_samples()

            # Step 4: Analyze and report
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
        print(f"  Total commands generated:  {self.stats['total']}")
        print(f"  Samples generated:         {self.stats['generated']}")
        print(f"  Generation failed:         {self.stats['generation_failed']}")
        print(f"  Samples tested:            {self.stats['tested']}")
        print(f"  Successfully imported:     {self.stats['imported']} ({self.stats['imported']/self.stats['tested']*100 if self.stats['tested'] else 0:.1f}%)")
        print(f"  Failed:                    {self.stats['failed']}")
        print(f"\nReports available:")
        print(f"  - COMPATIBILITY_SHEET.md")
        print(f"  - compatibility.json")
        print(f"  - MISSING_FORMATS.md")
        print(f"  - format_tests_results/comprehensive_test_results.json")
        print(f"  - format_tests_results/compatibility_summary.txt")

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Comprehensive format compatibility testing')
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
    parser.add_argument('--step', type=int, choices=[1, 2, 3, 4],
                       help='Run only a specific step (1-4)')

    args = parser.parse_args()

    tester = ComprehensiveFormatTester(
        base_video=args.base_video,
        base_image=args.base_image,
        output_dir=args.output_dir,
        results_dir=args.results_dir
    )

    if args.step:
        if args.step == 1:
            tester.step1_generate_commands()
        elif args.step == 2:
            tester.step2_generate_samples(max_samples=args.max_samples)
        elif args.step == 3:
            tester.step3_test_samples()
        elif args.step == 4:
            tester.step4_analyze_results()
    else:
        tester.run_full_test(max_samples=args.max_samples)
