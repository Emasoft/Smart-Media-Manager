"""UUID generator for format identification with parameters.

Generates deterministic UUIDs based on format parameters:
- Codec (h264, hevc, vp9, etc.)
- Bit depth (8, 10, 12, 16)
- Pixel format (yuv420p, yuv422p, yuv444p, rgb24, etc.)
- Profile (high, main, main10, etc.)
- Sample rate (for audio)
- Sample format (for audio)
"""

import hashlib
from typing import Optional


def generate_video_uuid(
    codec: str,
    bit_depth: Optional[int] = None,
    pix_fmt: Optional[str] = None,
    profile: Optional[str] = None,
) -> str:
    """Generate a deterministic UUID for video format.

    Args:
        codec: Codec name (h264, hevc, vp9, av1, etc.)
        bit_depth: Bit depth (8, 10, 12, 16)
        pix_fmt: Pixel format (yuv420p, yuv422p, yuv444p, rgb24, etc.)
        profile: Codec profile (high, main, main10, etc.)

    Returns:
        UUID string in format: {hash}-{bitdepth}-{pixfmt}-{profile}-V

    Examples:
        >>> generate_video_uuid("h264", 8, "yuv420p", "high")
        'b2e62c4a-6122-548c-9bfa-0fcf3613942a-8bit-yuv420p-high-V'
    """
    # Use base codec UUID (for backward compatibility with existing UUIDs)
    base_uuids = {
        "h264": "b2e62c4a-6122-548c-9bfa-0fcf3613942a",
        "hevc": "faf4b553-de47-5bc8-80ea-d026a2571456",
        "av1": "c69693cd-1fcd-5608-a8df-9476a00cfa9b",
        "vp9": "4c9b19a7-ec9f-57c2-98ca-3ac8432b27cc",
    }

    base_uuid = base_uuids.get(codec.lower())
    if not base_uuid:
        # Generate deterministic UUID for unknown codec
        base_uuid = hashlib.sha256(codec.encode()).hexdigest()[:36]

    # If no parameters provided, return base UUID (backward compatibility)
    if not any([bit_depth, pix_fmt, profile]):
        return f"{base_uuid}-V"

    # Build parameter suffix
    params = []
    if bit_depth:
        params.append(f"{bit_depth}bit")
    if pix_fmt:
        params.append(pix_fmt)
    if profile:
        params.append(profile.lower())

    param_suffix = "-".join(params) if params else "default"
    return f"{base_uuid}-{param_suffix}-V"


def generate_audio_uuid(codec: str, sample_rate: Optional[int] = None, sample_fmt: Optional[str] = None) -> str:
    """Generate a deterministic UUID for audio format.

    Args:
        codec: Codec name (aac, opus, vorbis, etc.)
        sample_rate: Sample rate in Hz (44100, 48000, etc.)
        sample_fmt: Sample format (s16, s24, s32, f32, etc.)

    Returns:
        UUID string in format: {codec}-{samplerate}-{samplefmt}-A

    Examples:
        >>> generate_audio_uuid("aac", 48000, "s16")
        'aac-48000-s16-A'
    """
    params = [codec.lower()]
    if sample_rate:
        params.append(str(sample_rate))
    if sample_fmt:
        params.append(sample_fmt)

    return "-".join(params) + "-A"


def parse_video_uuid(uuid: str) -> dict:
    """Parse a video UUID to extract parameters.

    Args:
        uuid: Video UUID string

    Returns:
        Dict with keys: base_uuid, bit_depth, pix_fmt, profile

    Examples:
        >>> parse_video_uuid("b2e62c4a-6122-548c-9bfa-0fcf3613942a-8bit-yuv420p-high-V")
        {'base_uuid': 'b2e62c4a-6122-548c-9bfa-0fcf3613942a', 'bit_depth': 8,
         'pix_fmt': 'yuv420p', 'profile': 'high'}
    """
    parts = uuid.split("-")

    result: dict[str, str | int | None] = {"base_uuid": None, "bit_depth": None, "pix_fmt": None, "profile": None}

    # Extract base UUID (first 5 parts: xxxx-xxxx-xxxx-xxxx-xxxx)
    if len(parts) >= 5:
        result["base_uuid"] = "-".join(parts[:5])

    # Parse parameter suffix
    remaining = parts[5:] if len(parts) > 5 else []

    for param in remaining:
        if param.endswith("bit"):
            try:
                result["bit_depth"] = int(param[:-3])
            except ValueError:
                pass
        elif param.startswith("yuv") or param in ("rgb24", "rgba", "gray"):
            result["pix_fmt"] = param
        elif param not in ("V", "A", "I", "C", "R"):
            result["profile"] = param

    return result


if __name__ == "__main__":
    # Test UUID generation
    print("Video UUIDs:")
    print(f"  H.264 8-bit 4:2:0 High: {generate_video_uuid('h264', 8, 'yuv420p', 'high')}")
    print(f"  H.264 10-bit 4:2:0 High10: {generate_video_uuid('h264', 10, 'yuv420p', 'high10')}")
    print(f"  HEVC 8-bit 4:2:0 Main: {generate_video_uuid('hevc', 8, 'yuv420p', 'main')}")
    print(f"  HEVC 10-bit 4:2:0 Main10: {generate_video_uuid('hevc', 10, 'yuv420p', 'main10')}")

    print("\nAudio UUIDs:")
    print(f"  AAC 48kHz 16-bit: {generate_audio_uuid('aac', 48000, 's16')}")
    print(f"  AAC 6kHz 16-bit: {generate_audio_uuid('aac', 6000, 's16')}")

    print("\nParsing test:")
    uuid = generate_video_uuid("h264", 10, "yuv420p", "high10")
    print(f"  UUID: {uuid}")
    print(f"  Parsed: {parse_video_uuid(uuid)}")
