"""Pytest configuration and fixtures for Smart Media Manager tests."""

import os
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Generator

import pytest
import yaml


# =============================================================================
# Test Set Configuration
# =============================================================================


@dataclass
class TestSetConfig:
    """Configuration loaded from test_set.yaml files.

    Provides access to sample files for tests based on the configured test set.
    Default: samples/test_set.yaml (public, minimal samples for CI)
    Local: samples_dev/test_set.yaml (comprehensive samples for local testing)
    """

    name: str
    description: str
    base_path: Path
    samples: dict[str, dict[str, str | None]] = field(default_factory=dict)
    test_overrides: dict[str, dict[str, str]] = field(default_factory=dict)
    skip_markers: list[str] = field(default_factory=list)
    include_markers: list[str] = field(default_factory=list)
    max_total_size_bytes: int | None = None

    def get_sample(self, category: str, format_key: str = "default") -> Path | None:
        """Get path to a sample file by category and format.

        Args:
            category: Sample category (image, video, animated, raw)
            format_key: Specific format within category (jpeg, png, mp4_h264, etc.)
                       Use "default" for the default format in that category.

        Returns:
            Path to the sample file, or None if not available.
        """
        if category not in self.samples:
            return None
        category_samples = self.samples[category]
        if format_key not in category_samples:
            format_key = "default"
        if format_key not in category_samples:
            return None
        sample_path = category_samples[format_key]
        if sample_path is None:
            return None
        full_path = self.base_path / sample_path
        if full_path.exists():
            return full_path
        return None

    def get_test_sample(self, test_file: str, category: str) -> Path | None:
        """Get sample path for a specific test file with optional override.

        Args:
            test_file: Test file name (e.g., "test_minimal_ci")
            category: Sample category to retrieve

        Returns:
            Path to sample, using test-specific override if configured.
        """
        if test_file in self.test_overrides:
            overrides = self.test_overrides[test_file]
            if category in overrides:
                return self.base_path / overrides[category]
        return self.get_sample(category)

    def should_skip_marker(self, marker: str) -> bool:
        """Check if tests with given marker should be skipped."""
        return marker in self.skip_markers


def load_test_set_config(config_path: Path) -> TestSetConfig:
    """Load test set configuration from YAML file.

    Args:
        config_path: Path to test_set.yaml file

    Returns:
        TestSetConfig instance with loaded configuration
    """
    with open(config_path) as f:
        data: dict[str, Any] = yaml.safe_load(f)

    base_path = config_path.parent / data.get("base_path", ".")

    return TestSetConfig(
        name=data.get("name", "unknown"),
        description=data.get("description", ""),
        base_path=base_path.resolve(),
        samples=data.get("samples", {}),
        test_overrides=data.get("test_overrides", {}),
        skip_markers=data.get("skip_markers", []),
        include_markers=data.get("include_markers", []),
        max_total_size_bytes=data.get("max_total_size_bytes"),
    )


def get_default_test_set_path() -> Path:
    """Get the default test set config path.

    Checks TEST_SET_CONFIG environment variable first,
    then falls back to samples/test_set.yaml.
    """
    env_path = os.environ.get("TEST_SET_CONFIG")
    if env_path:
        return Path(env_path)
    project_root = Path(__file__).parent.parent
    return project_root / "samples" / "test_set.yaml"


# =============================================================================
# Pytest Hooks and Options
# =============================================================================


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add custom command-line options for test set configuration."""
    parser.addoption(
        "--test-set",
        action="store",
        default=None,
        help="Path to test_set.yaml configuration file. "
        "Default: samples/test_set.yaml or TEST_SET_CONFIG env var.",
    )


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with test set markers."""
    config.addinivalue_line(
        "markers", "minimal: Minimal tests for CI with small samples"
    )
    config.addinivalue_line(
        "markers", "requires_raw: Tests requiring RAW camera samples"
    )
    config.addinivalue_line(
        "markers", "requires_large: Tests requiring large media files"
    )
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "slow: Slow tests (may be skipped in CI)")


# =============================================================================
# Test Set Fixtures
# =============================================================================


@pytest.fixture(scope="session")
def test_set_config(request: pytest.FixtureRequest) -> TestSetConfig:
    """Load test set configuration for the test session.

    The config path can be specified via:
    1. --test-set command line option
    2. TEST_SET_CONFIG environment variable
    3. Default: samples/test_set.yaml
    """
    config_path_opt = request.config.getoption("--test-set")
    if config_path_opt:
        config_path = Path(config_path_opt)
    else:
        config_path = get_default_test_set_path()

    if not config_path.exists():
        pytest.skip(f"Test set config not found: {config_path}")

    return load_test_set_config(config_path)


@pytest.fixture(scope="session")
def sample_image(test_set_config: TestSetConfig) -> Path | None:
    """Get default image sample path."""
    return test_set_config.get_sample("image")


@pytest.fixture(scope="session")
def sample_video(test_set_config: TestSetConfig) -> Path | None:
    """Get default video sample path."""
    return test_set_config.get_sample("video")


@pytest.fixture(scope="session")
def sample_animated_gif(test_set_config: TestSetConfig) -> Path | None:
    """Get animated GIF sample path."""
    return test_set_config.get_sample("animated", "gif")


@pytest.fixture(scope="session")
def sample_raw(test_set_config: TestSetConfig) -> Path | None:
    """Get RAW camera format sample path."""
    return test_set_config.get_sample("raw")


@pytest.fixture
def skip_if_no_sample(test_set_config: TestSetConfig) -> Callable[[str, str], Path]:
    """Skip test if required sample is not available in current test set.

    Returns a function that takes (category, format_key) and either returns
    the sample Path or skips the test if the sample is not available.
    """

    def _skip_if_no_sample(category: str, format_key: str = "default") -> Path:
        sample = test_set_config.get_sample(category, format_key)
        if sample is None:
            pytest.skip(
                f"Sample not available: {category}/{format_key} (using {test_set_config.name} test set)"
            )
        return sample

    return _skip_if_no_sample


@pytest.fixture(autouse=True)
def preserve_test_logs(
    request: pytest.FixtureRequest, tmp_path: Path
) -> Generator[None, None, None]:
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
