#!/usr/bin/env python3
"""Analyze format test results and generate compatibility sheet."""

import json
import re
from pathlib import Path
from collections import defaultdict

# Load results
RESULTS_FILE = Path("format_tests_results/test_results.json")
with open(RESULTS_FILE) as f:
    results = json.load(f)

# Parse each result
compatibility_data = []

for result in results:
    filename = result["file"]
    stdout = result["stdout"]

    # Determine if imported by parsing output
    imported = False
    compatible = False
    refused = False

    # Look for import statistics - handle ANSI codes and variable spacing
    if "Total imported:" in stdout:
        # Extract number after "Total imported:" - handle ANSI escape sequences and spaces
        match = re.search(r"Total imported:.*?(\d+)", stdout)
        if match:
            total_imported = int(match.group(1))
            imported = total_imported > 0

    # Check if marked as compatible - handle ANSI codes
    if "Compatible (no conversion):" in stdout:
        match = re.search(r"Compatible \(no conversion\):.*?(\d+)", stdout)
        if match:
            compatible_count = int(match.group(1))
            compatible = compatible_count > 0

    # Check if refused - handle ANSI codes
    if "Refused by Apple Photos:" in stdout:
        match = re.search(r"Refused by Apple Photos:.*?(\d+)", stdout)
        if match:
            refused_count = int(match.group(1))
            refused = refused_count > 0

    # Parse filename to extract format info
    parts = filename.replace("test_", "").split("_")
    category = parts[0] if parts else "unknown"

    # Update the result dict with corrected parsing
    result["imported"] = imported
    result["compatible"] = compatible
    result["refused"] = refused

    compatibility_data.append({
        "file": filename,
        "extension": result["extension"],
        "category": category,
        "imported": imported,
        "compatible": compatible,
        "refused": refused,
        "size": result["size"],
    })

# Group by category
by_category = defaultdict(list)
for item in compatibility_data:
    by_category[item["category"]].append(item)

# Print summary
print("=" * 80)
print("FORMAT COMPATIBILITY TEST RESULTS")
print("=" * 80)
print()

total_tested = len(compatibility_data)
total_imported = sum(1 for item in compatibility_data if item["imported"])
total_compatible = sum(1 for item in compatibility_data if item["compatible"])
total_refused = sum(1 for item in compatibility_data if item["refused"])

print(f"Total files tested:      {total_tested}")
print(f"Successfully imported:   {total_imported} ({total_imported/total_tested*100:.1f}%)")
print(f"Marked as compatible:    {total_compatible} ({total_compatible/total_tested*100:.1f}%)")
print(f"Refused by Photos:       {total_refused} ({total_refused/total_tested*100:.1f}%)")
print()

# Print by category
for category in sorted(by_category.keys()):
    items = by_category[category]
    imported_count = sum(1 for item in items if item["imported"])
    print(f"{category.upper()}: {imported_count}/{len(items)} imported")

print()
print("=" * 80)
print("DETAILED RESULTS")
print("=" * 80)
print()

# Print detailed table
print(f"{'File':<45} {'Extension':<10} {'Imported':<10} {'Compatible':<12} {'Refused':<10}")
print("-" * 87)

for item in sorted(compatibility_data, key=lambda x: (x["category"], x["file"])):
    imported_str = "✅ YES" if item["imported"] else "❌ NO"
    compatible_str = "✅ YES" if item["compatible"] else "⚠️  NO"
    refused_str = "❌ YES" if item["refused"] else "✅ NO"

    print(f"{item['file']:<45} {item['extension']:<10} {imported_str:<10} {compatible_str:<12} {refused_str:<10}")

# Save summary
summary_file = Path("format_tests_results/compatibility_summary.txt")
with open(summary_file, "w") as f:
    f.write("FORMAT COMPATIBILITY TEST RESULTS\n")
    f.write("=" * 80 + "\n\n")
    f.write(f"Total files tested:      {total_tested}\n")
    f.write(f"Successfully imported:   {total_imported} ({total_imported/total_tested*100:.1f}%)\n")
    f.write(f"Marked as compatible:    {total_compatible} ({total_compatible/total_tested*100:.1f}%)\n")
    f.write(f"Refused by Photos:       {total_refused} ({total_refused/total_tested*100:.1f}%)\n\n")

    for category in sorted(by_category.keys()):
        items = by_category[category]
        imported_count = sum(1 for item in items if item["imported"])
        f.write(f"{category.upper()}: {imported_count}/{len(items)} imported\n")

# Save corrected results back to JSON
with open(RESULTS_FILE, "w") as f:
    json.dump(results, f, indent=2)

print()
print(f"Updated test results saved to: {RESULTS_FILE}")
print(f"Summary saved to: {summary_file}")
