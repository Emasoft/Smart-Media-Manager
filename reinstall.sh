#!/usr/bin/env bash
# Development script: Bumps version, builds wheel, and reinstalls as uv tool
# Usage: ./reinstall.sh
#
# This script is for DEVELOPERS ONLY. End users should install via:
#   uv tool install smart-media-manager
#
set -euo pipefail

echo ""
echo "=== Smart Media Manager Development Reinstall ==="
echo ""

# Bump patch version
echo "[1/4] Bumping patch version..."
uv version --bump patch --bump alpha

# Sync dependencies
echo "[2/4] Syncing dependencies..."
uv sync

# Build wheel
echo "[3/4] Building wheel..."
uv build --wheel --clear --quiet

# Find the latest wheel
WHEEL_PATH="$(ls -t dist/*.whl 2>/dev/null | head -n1)"
if [[ -z "$WHEEL_PATH" ]]; then
    echo "ERROR: No wheel found in dist/"
    exit 1
fi
echo "    Built: $WHEEL_PATH"

# Reinstall as uv tool
echo "[4/4] Reinstalling as uv tool..."
uv tool uninstall smart-media-manager 2>/dev/null || true
uv tool install "$WHEEL_PATH" --python 3.12

echo ""
echo "=== Done ==="
echo ""
smart-media-manager --version
