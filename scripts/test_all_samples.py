#!/usr/bin/env python3
"""Test all format samples and collect results."""

import json
import subprocess
from pathlib import Path
from datetime import datetime

# Directories
SAMPLES_DIR = Path("tests/samples/format_tests")
RESULTS_DIR = Path("format_tests_results")
RESULTS_DIR.mkdir(exist_ok=True)

# Get all test files
test_files = sorted([f for f in SAMPLES_DIR.iterdir() if f.is_file() and f.name.startswith("test_")])

print(f"Found {len(test_files)} test files to process")
print("=" * 80)

results = []

for i, test_file in enumerate(test_files, 1):
    print(f"\n[{i}/{len(test_files)}] Testing: {test_file.name}")

    result = {
        "file": test_file.name,
        "size": test_file.stat().st_size,
        "extension": test_file.suffix,
        "timestamp": datetime.now().isoformat(),
    }

    # Run smart-media-manager
    cmd = [
        "uv", "run", "smart-media-manager",
        str(test_file),
        "--file",
        "--skip-renaming",
        "--skip-convert",
        "--skip-compatibility-check",
    ]

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )

        result["exit_code"] = proc.returncode
        result["stdout"] = proc.stdout
        result["stderr"] = proc.stderr

        # Parse import status
        if "Successfully imported" in proc.stdout or "Total imported:" in proc.stdout:
            # Check if actual import happened
            if "Imported (direct):" in proc.stdout:
                # Extract number
                for line in proc.stdout.split("\n"):
                    if "Imported (direct):" in line:
                        # Look for number after the colon
                        parts = line.split(":")
                        if len(parts) > 1:
                            num_str = parts[1].strip().split()[0]
                            try:
                                imported = int(num_str)
                                result["imported"] = imported > 0
                            except:
                                result["imported"] = False
                        break
            else:
                result["imported"] = False
        else:
            result["imported"] = False

        # Save individual log
        log_file = RESULTS_DIR / f"{test_file.stem}.log"
        with open(log_file, "w") as f:
            f.write(f"Test file: {test_file}\n")
            f.write(f"Command: {' '.join(cmd)}\n")
            f.write(f"\n=== STDOUT ===\n{proc.stdout}\n")
            f.write(f"\n=== STDERR ===\n{proc.stderr}\n")
            f.write(f"\n=== EXIT CODE ===\n{proc.returncode}\n")

        result["log_file"] = str(log_file)

        if result.get("imported"):
            print(f"  ✅ IMPORTED")
        elif proc.returncode == 0:
            print(f"  ⚠️  Processed but not imported")
        else:
            print(f"  ❌ FAILED (exit code {proc.returncode})")

    except subprocess.TimeoutExpired:
        result["error"] = "timeout"
        result["imported"] = False
        print(f"  ⏱️  TIMEOUT")
    except Exception as e:
        result["error"] = str(e)
        result["imported"] = False
        print(f"  ❌ ERROR: {e}")

    results.append(result)

# Save results
results_file = RESULTS_DIR / "test_results.json"
with open(results_file, "w") as f:
    json.dump(results, f, indent=2)

# Print summary
print("\n" + "=" * 80)
print("TESTING COMPLETE")
print("=" * 80)

imported = sum(1 for r in results if r.get("imported"))
failed = sum(1 for r in results if not r.get("imported") and r.get("exit_code", 1) != 0)
processed = sum(1 for r in results if r.get("exit_code") == 0 and not r.get("imported"))

print(f"\nResults:")
print(f"  ✅ Successfully imported:     {imported}")
print(f"  ⚠️  Processed (not imported): {processed}")
print(f"  ❌ Failed:                    {failed}")
print(f"\nResults saved to: {results_file}")
print(f"Individual logs in: {RESULTS_DIR}/")
