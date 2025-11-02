#!/usr/bin/env bash
set -euo pipefail
echo ""
echo "Attempting to reinstall smart-media-manager..."
echo ""
uv version --bump patch --bump alpha
uv sync
uv build --wheel --clear --quiet
WHEEL_PATH="$(ls -t dist/*.whl | head -n1)"
echo ""
uv tool uninstall smart-media-manager
uv tool install "$WHEEL_PATH"
echo ""
echo "Done reinstalling smart media manager"
echo ""
