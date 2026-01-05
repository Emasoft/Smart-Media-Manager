#!/usr/bin/env bash
# Validate samples/ folder for CI/CD compliance
#
# Checks:
# 1. Total size is under 3MB (CI limit)
# 2. All media files are registered in test_set.yaml
# 3. README.md exists with license information
#
# Usage:
#   ./scripts/validate_samples.sh          # Validate samples/
#   ./scripts/validate_samples.sh --strict # Also check file integrity

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SAMPLES_DIR="$PROJECT_ROOT/samples"
TEST_SET_YAML="$SAMPLES_DIR/test_set.yaml"
MAX_SIZE_BYTES=3145728  # 3MB

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

STRICT_MODE=false
ERRORS=0
WARNINGS=0

# Parse arguments
for arg in "$@"; do
    case $arg in
        --strict)
            STRICT_MODE=true
            ;;
    esac
done

echo "Validating samples/ folder..."
echo "================================"

# Check 1: samples directory exists
if [ ! -d "$SAMPLES_DIR" ]; then
    echo -e "${RED}ERROR: samples/ directory not found${NC}"
    exit 1
fi

# Check 2: test_set.yaml exists
if [ ! -f "$TEST_SET_YAML" ]; then
    echo -e "${RED}ERROR: samples/test_set.yaml not found${NC}"
    ((ERRORS++))
else
    echo -e "${GREEN}OK: test_set.yaml exists${NC}"
fi

# Check 3: README.md exists
if [ ! -f "$SAMPLES_DIR/README.md" ]; then
    echo -e "${YELLOW}WARNING: samples/README.md not found (should document license)${NC}"
    ((WARNINGS++))
else
    echo -e "${GREEN}OK: README.md exists${NC}"
fi

# Check 4: Total size under limit
TOTAL_SIZE=$(du -sb "$SAMPLES_DIR" 2>/dev/null | cut -f1 || du -sk "$SAMPLES_DIR" | awk '{print $1 * 1024}')
if [ "$TOTAL_SIZE" -gt "$MAX_SIZE_BYTES" ]; then
    TOTAL_MB=$(echo "scale=2; $TOTAL_SIZE / 1048576" | bc)
    MAX_MB=$(echo "scale=2; $MAX_SIZE_BYTES / 1048576" | bc)
    echo -e "${RED}ERROR: samples/ size (${TOTAL_MB}MB) exceeds limit (${MAX_MB}MB)${NC}"
    ((ERRORS++))
else
    TOTAL_KB=$(echo "scale=1; $TOTAL_SIZE / 1024" | bc)
    echo -e "${GREEN}OK: Total size ${TOTAL_KB}KB (under 3MB limit)${NC}"
fi

# Check 5: Required subdirectories exist
for subdir in images videos raw; do
    if [ ! -d "$SAMPLES_DIR/$subdir" ]; then
        echo -e "${YELLOW}WARNING: samples/$subdir/ directory not found${NC}"
        ((WARNINGS++))
    fi
done

# Check 6: Core sample files exist (required for CI)
REQUIRED_FILES=(
    "images/test_pattern.jpg"
    "videos/test_video.mp4"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$SAMPLES_DIR/$file" ]; then
        echo -e "${RED}ERROR: Required file samples/$file not found${NC}"
        ((ERRORS++))
    else
        echo -e "${GREEN}OK: Required file $file exists${NC}"
    fi
done

# Check 7: No large individual files (>300KB each for CI)
echo ""
echo "Checking individual file sizes..."
while IFS= read -r -d '' file; do
    SIZE=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo 0)
    if [ "$SIZE" -gt 307200 ]; then
        RELATIVE="${file#$SAMPLES_DIR/}"
        SIZE_KB=$(echo "scale=1; $SIZE / 1024" | bc)
        echo -e "${YELLOW}WARNING: $RELATIVE is ${SIZE_KB}KB (>300KB)${NC}"
        ((WARNINGS++))
    fi
done < <(find "$SAMPLES_DIR" -type f -not -name "*.yaml" -not -name "*.md" -print0)

# Check 8 (strict mode): Verify all media files are in test_set.yaml
if [ "$STRICT_MODE" = true ]; then
    echo ""
    echo "Strict mode: Checking file registration..."
    while IFS= read -r -d '' file; do
        RELATIVE="${file#$SAMPLES_DIR/}"
        if ! grep -q "$RELATIVE" "$TEST_SET_YAML" 2>/dev/null; then
            echo -e "${YELLOW}WARNING: $RELATIVE not registered in test_set.yaml${NC}"
            ((WARNINGS++))
        fi
    done < <(find "$SAMPLES_DIR" \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" -o -name "*.gif" -o -name "*.webp" -o -name "*.bmp" -o -name "*.tiff" -o -name "*.heic" -o -name "*.apng" -o -name "*.mp4" -o -name "*.mov" \) -print0)
fi

# Summary
echo ""
echo "================================"
if [ "$ERRORS" -gt 0 ]; then
    echo -e "${RED}FAILED: $ERRORS error(s), $WARNINGS warning(s)${NC}"
    exit 1
elif [ "$WARNINGS" -gt 0 ]; then
    echo -e "${YELLOW}PASSED with $WARNINGS warning(s)${NC}"
    exit 0
else
    echo -e "${GREEN}PASSED: All checks passed${NC}"
    exit 0
fi
