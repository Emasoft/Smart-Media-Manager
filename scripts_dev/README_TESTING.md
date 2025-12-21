# Comprehensive Format Compatibility Testing System

This directory contains a complete automated testing system for comprehensive format compatibility testing with Apple Photos.

## System Overview

The testing system consists of several integrated scripts that work together:

```
┌─────────────────────────────────────────────────────────────┐
│                  COMPREHENSIVE TEST PIPELINE                 │
└─────────────────────────────────────────────────────────────┘

1. GENERATE COMMANDS
   ├─ generate_all_format_commands.py
   └─ Output: format_test_commands.json
          ↓
2. GENERATE SAMPLES
   ├─ Execute ffmpeg commands
   └─ Output: tests/samples/format_tests/test_*.{mp4,mkv,avi,...}
          ↓
3. TEST SAMPLES
   ├─ Run smart-media-manager on each sample
   └─ Output: format_tests_results/*.log
          ↓
4. ANALYZE & REPORT
   ├─ analyze_test_results.py
   ├─ create_compatibility_sheet.py
   └─ analyze_missing_formats.py
          ↓
5. DELIVERABLES
   ├─ COMPATIBILITY_SHEET.md
   ├─ compatibility.json
   ├─ MISSING_FORMATS.md
   └─ format_tests_results/comprehensive_test_results.json
```

**Important:** Generated samples under `tests/samples/format_tests/` and logs under `format_tests_results/` are gitignored. Do not commit them.

## Scripts

### 1. `ultimate_format_test.py` ⭐ **RECOMMENDED**

**The all-in-one automated testing solution.**

Single script that handles everything:
- Auto-installs ffmpeg/ffprobe via Homebrew if missing
- Discovers all available formats directly from ffprobe
- Loads extra formats not supported by ffprobe (JPEG XL, HEIF, RAW)
- Merges and deduplicates all format sources
- Generates format conversion commands
- Executes ffmpeg to create test samples
- Tests with Smart Media Manager
- Analyzes results and generates all reports

**Features**:
- **Zero manual configuration** - Discovers formats automatically
- **Homebrew bootstrapping** - Installs dependencies if needed
- **Extra formats support** - Includes formats ffprobe doesn't know about
- **Intelligent filtering** - Skips incompatible codec/container combinations
- **Comprehensive reporting** - Generates .md and .json files

**Usage**:
```bash
# Run complete pipeline (installs dependencies, discovers formats, tests everything)
uv run python3 scripts_dev/ultimate_format_test.py

# Run with sample limit (faster for testing)
uv run python3 scripts_dev/ultimate_format_test.py --max-samples 20

# Skip dependency installation (if already installed)
uv run python3 scripts_dev/ultimate_format_test.py --skip-install

# Custom paths
uv run python3 scripts_dev/ultimate_format_test.py \
    --base-video path/to/video.mp4 \
    --base-image path/to/image.jpg \
    --output-dir path/to/samples \
    --results-dir path/to/results
```

**Output**: All reports generated automatically

**Estimated time**:
- With `--max-samples 20`: ~15-20 minutes
- Full run (hundreds of samples): 2-4 hours

---

### 2. `generate_all_format_commands.py`

Generates all possible ffmpeg format conversion commands based on available codecs, containers, and format options.

**Features**:
- Parses ffprobe outputs to discover available formats
- Generates video/audio codec combinations
- Generates pixel format variations
- Generates audio sample rate variations
- Generates image format variations
- Filters incompatible combinations (e.g., WebM only supports VP8/VP9/AV1)
- Outputs commands to JSON for processing

**Usage**:
```bash
uv run python3 scripts_dev/generate_all_format_commands.py
```

**Output**: `format_test_commands.json` with ~86+ commands

### 2. `comprehensive_format_test.py`

Master orchestration script that runs the complete test pipeline.

**Features**:
- **Step 1**: Generate commands
- **Step 2**: Execute ffmpeg to create test samples
- **Step 3**: Test each sample with Smart Media Manager
- **Step 4**: Analyze results and generate reports

**Usage**:
```bash
# Run complete pipeline
uv run python3 scripts_dev/comprehensive_format_test.py

# Run complete pipeline with sample limit
uv run python3 scripts_dev/comprehensive_format_test.py --max-samples 20

# Run individual steps
uv run python3 scripts_dev/comprehensive_format_test.py --step 1  # Generate commands only
uv run python3 scripts_dev/comprehensive_format_test.py --step 2  # Generate samples only
uv run python3 scripts_dev/comprehensive_format_test.py --step 3  # Test samples only
uv run python3 scripts_dev/comprehensive_format_test.py --step 4  # Analyze only

# Custom paths
uv run python3 scripts_dev/comprehensive_format_test.py \
    --base-video path/to/video.mp4 \
    --base-image path/to/image.jpg \
    --output-dir path/to/samples \
    --results-dir path/to/results
```

### 3. `analyze_test_results.py`

Parses test results and generates summary statistics.

**Features**:
- Extracts import statistics from log files
- Handles ANSI escape codes in output
- Categorizes results by format type
- Generates detailed tables
- Updates test_results.json with correct parsing

**Usage**:
```bash
uv run python3 scripts_dev/analyze_test_results.py
```

### 4. `create_compatibility_sheet.py`

Generates comprehensive markdown and JSON compatibility documentation.

**Features**:
- Overall statistics
- Category-wise breakdown
- Detailed result tables
- Format recommendations
- Technical notes

**Output**:
- `COMPATIBILITY_SHEET.md`
- `compatibility.json`

**Usage**:
```bash
uv run python3 scripts_dev/create_compatibility_sheet.py
```

### 5. `analyze_missing_formats.py`

Compares tested formats against all available ffprobe formats to identify gaps.

**Features**:
- Parses ffprobe outputs (formats, codecs, pixel formats, etc.)
- Identifies untested combinations
- Prioritizes common vs. exotic formats
- Lists RAW camera formats
- Generates comprehensive gap analysis

**Output**: `MISSING_FORMATS.md`

**Usage**:
```bash
uv run python3 scripts_dev/analyze_missing_formats.py
```

## Quick Start

### Recommended: Ultimate Format Test ⭐

The easiest way to run comprehensive format testing:

```bash
# Quick test (20 samples)
uv run python3 scripts_dev/ultimate_format_test.py --max-samples 20

# Full test (auto-discovers all formats)
uv run python3 scripts_dev/ultimate_format_test.py
```

This will automatically:
1. Install ffmpeg/ffprobe if missing
2. Discover all available formats from ffprobe
3. Load extra formats (JPEG XL, HEIF, RAW)
4. Generate hundreds of format conversion commands
5. Create test samples with ffmpeg
6. Test each sample with Smart Media Manager
7. Generate all reports and documentation

**Estimated time**:
- 20 samples: ~15-20 minutes
- Full run: 2-4 hours

---

### Alternative: Comprehensive Format Test (Fixed Commands)

Test with pre-defined format combinations:

```bash
# Test with first 20 format combinations
uv run python3 scripts_dev/comprehensive_format_test.py --max-samples 20

# Full test run
uv run python3 scripts_dev/comprehensive_format_test.py
```

This will:
1. Generate 86+ format conversion commands
2. Create test samples with ffmpeg (~5-15 minutes)
3. Test each sample with Smart Media Manager (~30-60 minutes)
4. Generate all reports and documentation

**Estimated time**: 45-90 minutes for complete run

### Step-by-Step Execution

For debugging or incremental testing:

```bash
# Step 1: Generate commands (fast)
uv run python3 scripts_dev/comprehensive_format_test.py --step 1

# Step 2: Generate samples (5-15 min)
uv run python3 scripts_dev/comprehensive_format_test.py --step 2

# Step 3: Test samples (30-60 min)
uv run python3 scripts_dev/comprehensive_format_test.py --step 3

# Step 4: Generate reports (fast)
uv run python3 scripts_dev/comprehensive_format_test.py --step 4
```

## Output Files

### Generated Samples

Location: `tests/samples/format_tests/`

Files: `test_0001_mp4_libx264_aac.mp4`, `test_0002_mkv_hevc_opus.mkv`, etc.

### Test Results

Location: `format_tests_results/`

- `comprehensive_test_results.json` - Complete test data
- `test_*.log` - Individual test logs
- `compatibility_summary.txt` - Text summary

### Reports

- `COMPATIBILITY_SHEET.md` - Main compatibility documentation
- `compatibility.json` - Machine-readable compatibility data
- `MISSING_FORMATS.md` - Gap analysis showing untested formats

### Internal Files

- `format_test_commands.json` - Generated ffmpeg commands
- `format_analysis/` - ffprobe output files

## Format Coverage

Current system generates:

| Category | Count | Examples |
|----------|-------|----------|
| **Video/Audio Combos** | 72 | MP4+H.264+AAC, MKV+HEVC+Opus, etc. |
| **Pixel Formats** | 10 | yuv420p, yuv422p, yuv420p10le, etc. |
| **Sample Rates** | 6 | 8kHz, 16kHz, 44.1kHz, 48kHz, 96kHz |
| **Image Formats** | 14 | PNG (various), JPEG (various), TIFF, WebP, etc. |
| **Total** | **~86+** | Expandable to hundreds |

## Extending the System

### Add More Formats

Edit `generate_all_format_commands.py`:

```python
# Add containers
common_containers = ['mp4', 'mkv', 'avi', 'YOUR_FORMAT']

# Add video codecs
common_video_codecs = ['libx264', 'libx265', 'YOUR_CODEC']

# Add audio codecs
common_audio_codecs = ['aac', 'mp3', 'YOUR_CODEC']
```

### Add Custom Test Cases

Add functions to `generate_all_format_commands.py`:

```python
def generate_custom_tests(input_file, output_dir):
    commands = []
    # Your custom ffmpeg commands
    return commands
```

Then integrate into `comprehensive_format_test.py`:

```python
custom_commands = generate_custom_tests(...)
self.commands.extend(custom_commands)
```

## Troubleshooting

### ffmpeg Not Found

```bash
brew install ffmpeg
```

### Samples Not Generating

Check `format_tests_results/generation_error_*.log` for ffmpeg errors.

Common issues:
- Codec not supported in container
- Missing codec libraries
- Invalid pixel format for codec

### Smart Media Manager Timeouts

Increase timeout in `comprehensive_format_test.py`:

```python
timeout=180  # Change to 300 or higher
```

### Out of Disk Space

Test samples can be large. Clean up with:

```bash
rm -rf tests/samples/format_tests/test_*
```

## Performance Tips

1. **Limit samples for testing**: Use `--max-samples 20` during development
2. **Skip existing**: Samples are skipped if they already exist
3. **Run steps separately**: Use `--step` to debug individual phases
4. **Parallel generation**: Future enhancement - generate samples in parallel

## Requirements

- Python 3.12+
- ffmpeg with common codec support
- Smart Media Manager installed
- macOS (for Apple Photos testing)
- ~5-10GB free disk space for full test suite

## License

Part of Smart Media Manager project.
