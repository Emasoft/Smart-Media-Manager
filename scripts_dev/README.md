# Development Scripts (scripts_dev/)

This directory contains development and compatibility testing scripts used during research, analysis, and prototyping. These scripts are **tracked in git** but **excluded from the package distribution**.

## Purpose

- **Development-only tools** - Scripts for analysis, testing, and research
- **Not for production** - These scripts are not part of the main codebase
- **Local experiments** - One-off scripts, prototypes, and investigations
- **Compatibility tester support** - Tools to generate and validate format samples locally

## Current Scripts

### Metadata Registry Analysis (October 2025)

These scripts were created during research into FFmpeg's image metadata support:

#### `audit_cross_tool_mappings.py`
Verifies cross-tool consistency in the metadata registry.

**Usage**:
```bash
uv run scripts_dev/audit_cross_tool_mappings.py
```

**Checks**:
- Fields mapped across multiple tools (ExifTool + FFmpeg/FFprobe)
- Fields only mapped in one tool
- Common fields that should be cross-mapped

**Output**: Console report showing cross-tool coverage statistics

#### `audit_metadata_duplicates.py`
Detects semantic duplicates in the metadata registry (same field name mapped to multiple UUIDs).

**Usage**:
```bash
uv run scripts_dev/audit_metadata_duplicates.py
```

**Checks**:
- GPS location composite vs individual lat/lon fields
- Date field duplicate mappings
- codec_name over-mapping to multiple UUIDs

**Output**: Console report listing duplicate mappings found

#### `identify_missing_exif_tags.py`
Analyzes EXIF tag coverage in the metadata registry.

**Usage**:
```bash
uv run scripts_dev/identify_missing_exif_tags.py
```

**Shows**:
- Standard EXIF tags already covered (70 fields)
- Commonly used tags potentially missing (~53 fields)
- Priority categories for expansion
- Recommendations for registry expansion

**Output**: Console report with coverage analysis and recommendations

## Related Documentation

See `scripts_dev/README_TESTING.md` for compatibility test workflows and sample generation details.

## Guidelines

### When to Add Scripts Here

Add scripts to `scripts_dev/` when:
- Prototyping new features or approaches
- Analyzing codebase or data for research
- Creating one-off tools for debugging
- Testing external tools or libraries

### When NOT to Add Scripts Here

Do NOT add scripts here if they are:
- Part of the production codebase → Use `smart_media_manager/`
- Permanent testing infrastructure → Use `tests/`
- Published tools for users → Use `scripts/` (tracked in git)
- Part of the package distribution → Use `scripts/` (tracked in git)

## Directory Structure

```
scripts_dev/          ← This directory (tracked, development only)
  ├── README.md       ← This file
  ├── *.py            ← Analysis/prototyping scripts
  └── ...

scripts/              ← Production scripts (tracked, in package)
  ├── protect_docs_dev.sh
  └── ...

docs_dev/             ← Development docs (gitignored)
  └── claude_reports/
      ├── README.md
      └── ...

docs/                 ← Production docs (tracked, in package)
  └── ...
```

## Cleanup Policy

Scripts in this directory can be:
- Deleted when no longer needed
- Moved to `scripts/` if they become permanent tools
- Archived to `docs_dev/` if they're reference material

Keep generated sample outputs out of git; the large sample directories remain gitignored.
