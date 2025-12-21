#!/usr/bin/env python3
"""Debug MOV detection to find out why it's being rejected."""

import logging
from pathlib import Path
from smart_media_manager.cli import detect_media, RunStatistics, SkipLogger

# Enable DEBUG logging to see what's happening
logging.basicConfig(level=logging.DEBUG, format='%(name)s:%(levelname)s: %(message)s')

# Test MOV fixture
mov_fixture = Path("tests/fixtures/compatible_h264.mov")

if not mov_fixture.exists():
    print(f"❌ Fixture not found: {mov_fixture}")
    exit(1)

print(f"Testing: {mov_fixture}")
print(f"Exists: {mov_fixture.exists()}")
print(f"Size: {mov_fixture.stat().st_size} bytes")
print()

# Attempt detection
stats = RunStatistics()
result, reason = detect_media(mov_fixture, skip_compatibility_check=False)

print("="*80)
if result:
    print("✅ DETECTED")
    print(f"Kind: {result.kind}")
    print(f"Extension: {result.extension}")
    print(f"Format: {result.format_name}")
    print(f"Compatible: {result.compatible}")
    print(f"Action: {result.action}")
    print(f"Rule ID: {result.rule_id}")
    print(f"Requires Processing: {result.requires_processing}")
    print(f"Notes: {result.notes}")
    print(f"Video Codec: {result.video_codec}")
    print(f"Audio Codec: {result.audio_codec}")
else:
    print("❌ REJECTED")
    print(f"Reason: {reason}")
print("="*80)
