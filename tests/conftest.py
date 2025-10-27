"""Pytest configuration and fixtures for Smart Media Manager tests."""

import shutil
from datetime import datetime
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture(autouse=True)
def preserve_test_logs(request: pytest.FixtureRequest, tmp_path: Path) -> Generator[None, None, None]:
    """Preserve test logs with timestamps after each test completes.

    This fixture automatically runs for every test and:
    1. Lets the test run
    2. After test completes, searches for log files in tmp_path
    3. Copies any logs to tests/results/logs/ with timestamped names
    4. Preserves logs even if the test fails

    Log naming format: {test_name}_{timestamp}_{original_name}.log
    Example: test_mp4_video_detection_20251027_160000_skip.log
    """
    yield  # Let the test run

    # After test completes, preserve any logs
    test_name = request.node.name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create results directory
    results_dir = Path(__file__).parent / "results" / "logs"
    results_dir.mkdir(parents=True, exist_ok=True)

    # Find and copy log files from tmp_path
    if tmp_path.exists():
        for log_file in tmp_path.rglob("*.log"):
            # Create timestamped filename
            new_name = f"{test_name}_{timestamp}_{log_file.name}"
            dest = results_dir / new_name

            try:
                shutil.copy2(log_file, dest)
            except Exception as e:
                # Don't fail the test if log preservation fails
                print(f"Warning: Failed to preserve log {log_file}: {e}")

        # Also look for .smm_logs directories
        for smm_logs_dir in tmp_path.rglob(".smm_logs"):
            if smm_logs_dir.is_dir():
                for log_file in smm_logs_dir.glob("*.log"):
                    new_name = f"{test_name}_{timestamp}_{log_file.name}"
                    dest = results_dir / new_name

                    try:
                        shutil.copy2(log_file, dest)
                    except Exception as e:
                        print(f"Warning: Failed to preserve log {log_file}: {e}")
