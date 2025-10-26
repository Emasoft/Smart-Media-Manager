"""smart_media_manager package metadata."""

from importlib import metadata


def _detect_version() -> str:
    try:
        return metadata.version("smart-media-manager")
    except metadata.PackageNotFoundError:
        return "0.0.0"


__version__ = _detect_version()

__all__ = ["__version__"]
