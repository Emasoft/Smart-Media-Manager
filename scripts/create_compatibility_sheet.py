#!/usr/bin/env python3
"""Generate COMPATIBILITY_SHEET.md and compatibility.json from test results."""

import json
from pathlib import Path
from collections import defaultdict

# Load results
RESULTS_FILE = Path("format_tests_results/test_results.json")
with open(RESULTS_FILE) as f:
    results = json.load(f)

# Group by category
by_category = defaultdict(list)
for result in results:
    # Parse filename to extract format info
    filename = result["file"]
    parts = filename.replace("test_", "").split("_")
    category = parts[0] if parts else "unknown"
    by_category[category].append(result)

# Calculate stats
total_tested = len(results)
imported = [r for r in results if r.get("imported")]
compatible = [r for r in results if r.get("compatible")]
refused = [r for r in results if r.get("refused")]

# Create markdown document
md = []
md.append("# Apple Photos Format Compatibility Matrix")
md.append("")
md.append("Comprehensive test results for media format compatibility with Apple Photos.")
md.append("")
md.append("## Test Configuration")
md.append("")
md.append("- **Tool**: Smart Media Manager")
md.append("- **Test Mode**: Direct import, no conversion")
md.append("- **Flags**: `--file --skip-renaming --skip-convert --skip-compatibility-check`")
md.append("- **Total Samples**: " + str(total_tested))
md.append("")
md.append("## Overall Results")
md.append("")
md.append(f"| Metric | Count | Percentage |")
md.append(f"|--------|-------|------------|")
md.append(f"| **Total files tested** | {total_tested} | 100.0% |")
md.append(f"| **Successfully imported** | {len(imported)} | {len(imported)/total_tested*100:.1f}% |")
md.append(f"| **Marked as compatible** | {len(compatible)} | {len(compatible)/total_tested*100:.1f}% |")
md.append(f"| **Refused by Apple Photos** | {len(refused)} | {len(refused)/total_tested*100:.1f}% |")
md.append("")

# Category summary
md.append("## Results by Category")
md.append("")
md.append("| Category | Imported | Total | Success Rate |")
md.append("|----------|----------|-------|--------------|")
for category in sorted(by_category.keys()):
    items = by_category[category]
    imported_count = sum(1 for item in items if item.get("imported"))
    success_rate = imported_count / len(items) * 100 if items else 0
    md.append(f"| {category.upper()} | {imported_count} | {len(items)} | {success_rate:.1f}% |")
md.append("")

# Detailed results by category
md.append("## Detailed Results by Category")
md.append("")

for category in sorted(by_category.keys()):
    items = by_category[category]
    md.append(f"### {category.upper()}")
    md.append("")
    md.append("| File | Extension | Imported | Compatible | Refused |")
    md.append("|------|-----------|----------|------------|---------|")

    for item in sorted(items, key=lambda x: x["file"]):
        imported_icon = "✅" if item.get("imported") else "❌"
        compatible_icon = "✅" if item.get("compatible") else "⚠️"
        refused_icon = "❌" if item.get("refused") else "✅"

        md.append(f"| {item['file']} | {item['extension']} | {imported_icon} | {compatible_icon} | {refused_icon} |")
    md.append("")

# Format recommendations
md.append("## Format Recommendations")
md.append("")
md.append("### ✅ Highly Compatible Formats")
md.append("")
md.append("Based on test results, the following formats show excellent compatibility:")
md.append("")

# Find formats with 100% success rate
success_formats = []
for category in sorted(by_category.keys()):
    items = by_category[category]
    imported_count = sum(1 for item in items if item.get("imported"))
    if imported_count == len(items) and len(items) > 0:
        success_formats.append((category, items))

if success_formats:
    for category, items in success_formats:
        extensions = set(item["extension"] for item in items)
        md.append(f"- **{category.upper()}**: {', '.join(sorted(extensions))}")
else:
    md.append("- No formats achieved 100% import success rate")

md.append("")
md.append("### ⚠️ Problematic Formats")
md.append("")
md.append("The following formats showed compatibility issues:")
md.append("")

# Find formats with <50% success rate
problem_formats = []
for category in sorted(by_category.keys()):
    items = by_category[category]
    imported_count = sum(1 for item in items if item.get("imported"))
    success_rate = imported_count / len(items) * 100 if items else 0
    if success_rate < 50:
        problem_formats.append((category, items, success_rate))

if problem_formats:
    for category, items, success_rate in problem_formats:
        extensions = set(item["extension"] for item in items)
        md.append(f"- **{category.upper()}** ({success_rate:.1f}% success): {', '.join(sorted(extensions))}")
else:
    md.append("- All formats achieved >50% import success rate")

md.append("")
md.append("## Technical Notes")
md.append("")
md.append("### About the Tests")
md.append("")
md.append("- Tests were performed with conversion and compatibility checks disabled")
md.append("- Results show native Apple Photos format support without Smart Media Manager's conversion features")
md.append("- \"Compatible\" means marked as compatible by the tool")
md.append("- \"Imported\" means successfully imported into Apple Photos library")
md.append("- \"Refused\" indicates Apple Photos rejected the file")
md.append("")
md.append("### Smart Media Manager Capabilities")
md.append("")
md.append("Smart Media Manager can convert many incompatible formats to Apple Photos-compatible formats:")
md.append("")
md.append("- **Images**: Converts PSD, WebP, JPEG XL → TIFF/HEIC")
md.append("- **Videos**: Transcodes VP9, AV1, Theora → HEVC/H.264")
md.append("- **Containers**: Rewraps MKV, WebM → MP4")
md.append("- **Audio**: Converts Opus, Vorbis → AAC")
md.append("")
md.append("---")
md.append("")
md.append(f"*Generated from {total_tested} test samples*")

# Write markdown file
output_file = Path("COMPATIBILITY_SHEET.md")
with open(output_file, "w") as f:
    f.write("\n".join(md))

print(f"✅ Created {output_file}")

# Create JSON version
json_output = {
    "metadata": {
        "total_samples": total_tested,
        "imported": len(imported),
        "compatible": len(compatible),
        "refused": len(refused),
        "test_date": "2025-10-29"
    },
    "by_category": {}
}

for category in sorted(by_category.keys()):
    items = by_category[category]
    imported_count = sum(1 for item in items if item.get("imported"))

    json_output["by_category"][category] = {
        "total": len(items),
        "imported": imported_count,
        "success_rate": imported_count / len(items) * 100 if items else 0,
        "files": [
            {
                "filename": item["file"],
                "extension": item["extension"],
                "size": item["size"],
                "imported": item.get("imported", False),
                "compatible": item.get("compatible", False),
                "refused": item.get("refused", False)
            }
            for item in sorted(items, key=lambda x: x["file"])
        ]
    }

json_file = Path("compatibility.json")
with open(json_file, "w") as f:
    json.dump(json_output, f, indent=2)

print(f"✅ Created {json_file}")
