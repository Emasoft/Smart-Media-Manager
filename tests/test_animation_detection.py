"""
Unit tests for animation detection functions.

Tests cover:
- Animated GIF detection
- Animated PNG (APNG) detection
- Animated WebP detection
- PSD color mode detection
"""

from smart_media_manager.cli import (
    is_animated_gif,
    is_animated_png,
    is_animated_webp,
    get_psd_color_mode,
)


class TestAnimatedGifDetection:
    """Tests for is_animated_gif function."""

    def test_is_animated_gif_static(self, tmp_path):
        """Test is_animated_gif returns False for static GIF."""
        # Create minimal static GIF (GIF87a format)
        static_gif = tmp_path / "static.gif"
        static_gif.write_bytes(
            b"GIF87a"  # Header
            b"\x01\x00\x01\x00"  # Logical screen descriptor (1x1)
            b"\x00"  # No global color table
            b","  # Image separator
            b"\x00\x00\x00\x00"  # Image position
            b"\x01\x00\x01\x00"  # Image dimensions (1x1)
            b"\x00"  # No local color table
            b"\x02\x01\x01\x00"  # Image data
            b";"  # Trailer
        )
        assert is_animated_gif(static_gif) is False

    def test_is_animated_gif_animated(self, tmp_path):
        """Test is_animated_gif returns True for animated GIF."""
        # Create minimal animated GIF with 2 frames and NETSCAPE2.0 extension
        animated_gif = tmp_path / "animated.gif"
        animated_gif.write_bytes(
            b"GIF89a"  # Header (89a supports animation)
            b"\x01\x00\x01\x00"  # Logical screen descriptor (1x1)
            b"\x00"  # No global color table
            b"!"  # Extension introducer
            b"\xff"  # Application extension
            b"\x0b"  # Block size (11 bytes)
            b"NETSCAPE2.0"  # Application identifier (required for animation detection)
            b"\x03"  # Sub-block size
            b"\x01"  # Sub-block ID
            b"\x00\x00"  # Loop count (0 = infinite)
            b"\x00"  # Block terminator
            b"!"  # Extension introducer
            b"\xf9"  # Graphic control extension
            b"\x04"  # Block size
            b"\x00\x00\x00\x00\x00"  # Graphic control data
            b","  # Image separator (frame 1)
            b"\x00\x00\x00\x00"  # Image position
            b"\x01\x00\x01\x00"  # Image dimensions
            b"\x00"  # No local color table
            b"\x02\x01\x01\x00"  # Image data
            b"!"  # Extension introducer
            b"\xf9"  # Graphic control extension
            b"\x04"  # Block size
            b"\x00\x00\x00\x00\x00"  # Graphic control data
            b","  # Image separator (frame 2)
            b"\x00\x00\x00\x00"  # Image position
            b"\x01\x00\x01\x00"  # Image dimensions
            b"\x00"  # No local color table
            b"\x02\x01\x01\x00"  # Image data
            b";"  # Trailer
        )
        assert is_animated_gif(animated_gif) is True

    def test_is_animated_gif_nonexistent_file(self, tmp_path):
        """Test is_animated_gif handles nonexistent file."""
        nonexistent = tmp_path / "nonexistent.gif"
        # Should return False or raise appropriate error
        try:
            result = is_animated_gif(nonexistent)
            assert result is False
        except (FileNotFoundError, OSError):
            pass  # Expected behavior

    def test_is_animated_gif_not_gif_file(self, tmp_path):
        """Test is_animated_gif handles non-GIF file."""
        not_gif = tmp_path / "not_gif.txt"
        not_gif.write_text("This is not a GIF file")
        result = is_animated_gif(not_gif)
        assert result is False


class TestAnimatedPngDetection:
    """Tests for is_animated_png function."""

    def test_is_animated_png_static(self, tmp_path):
        """Test is_animated_png returns False for static PNG."""
        # Create minimal static PNG
        static_png = tmp_path / "static.png"
        static_png.write_bytes(
            b"\x89PNG\r\n\x1a\n"  # PNG signature
            b"\x00\x00\x00\x0dIHDR"  # IHDR chunk
            b"\x00\x00\x00\x01\x00\x00\x00\x01"  # 1x1 image
            b"\x08\x00\x00\x00\x00"  # 8-bit grayscale
            b"\x3a\x7e\x9b\x55"  # CRC
            b"\x00\x00\x00\x0aIDAT"  # IDAT chunk
            b"\x08\x1d\x01\x02\x00\xfd\xff\x02\x00\x00\x00"  # Image data
            b"\x57\xcd\x20\x5e"  # CRC
            b"\x00\x00\x00\x00IEND"  # IEND chunk
            b"\xae\x42\x60\x82"  # CRC
        )
        assert is_animated_png(static_png) is False

    def test_is_animated_png_animated(self, tmp_path):
        """Test is_animated_png returns True for APNG."""
        # Create minimal APNG with acTL chunk
        animated_png = tmp_path / "animated.png"
        animated_png.write_bytes(
            b"\x89PNG\r\n\x1a\n"  # PNG signature
            b"\x00\x00\x00\x08acTL"  # acTL chunk (animation control)
            b"\x00\x00\x00\x02"  # 2 frames
            b"\x00\x00\x00\x00"  # 0 loops (infinite)
            b"\x12\x34\x56\x78"  # CRC (dummy)
            b"\x00\x00\x00\x0dIHDR"  # IHDR chunk
            b"\x00\x00\x00\x01\x00\x00\x00\x01"  # 1x1 image
            b"\x08\x00\x00\x00\x00"  # 8-bit grayscale
            b"\x3a\x7e\x9b\x55"  # CRC
            b"\x00\x00\x00\x00IEND"  # IEND chunk
            b"\xae\x42\x60\x82"  # CRC
        )
        assert is_animated_png(animated_png) is True

    def test_is_animated_png_nonexistent_file(self, tmp_path):
        """Test is_animated_png handles nonexistent file."""
        nonexistent = tmp_path / "nonexistent.png"
        try:
            result = is_animated_png(nonexistent)
            assert result is False
        except (FileNotFoundError, OSError):
            pass  # Expected behavior

    def test_is_animated_png_not_png_file(self, tmp_path):
        """Test is_animated_png handles non-PNG file."""
        not_png = tmp_path / "not_png.txt"
        not_png.write_text("This is not a PNG file")
        result = is_animated_png(not_png)
        assert result is False


class TestAnimatedWebPDetection:
    """Tests for is_animated_webp function."""

    def test_is_animated_webp_static(self, tmp_path):
        """Test is_animated_webp returns False for static WebP."""
        # Create minimal static WebP (VP8 bitstream)
        static_webp = tmp_path / "static.webp"
        static_webp.write_bytes(
            b"RIFF"  # RIFF header
            b"\x20\x00\x00\x00"  # File size (little-endian)
            b"WEBP"  # WebP signature
            b"VP8 "  # VP8 simple lossy format
            b"\x10\x00\x00\x00"  # Chunk size
            b"\x00" * 16  # Dummy VP8 data
        )
        assert is_animated_webp(static_webp) is False

    def test_is_animated_webp_animated(self, tmp_path):
        """Test is_animated_webp returns True for animated WebP."""
        # Create minimal animated WebP with ANIM chunk
        animated_webp = tmp_path / "animated.webp"
        animated_webp.write_bytes(
            b"RIFF"  # RIFF header
            b"\x30\x00\x00\x00"  # File size (little-endian)
            b"WEBP"  # WebP signature
            b"VP8X"  # Extended format
            b"\x0a\x00\x00\x00"  # Chunk size
            b"\x02\x00\x00\x00"  # Flags (bit 1 = animation)
            b"\x00\x00\x00\x00\x00\x00"  # Canvas size
            b"ANIM"  # Animation chunk
            b"\x06\x00\x00\x00"  # Chunk size
            b"\x00\x00\x00\x00"  # Background color
            b"\x00\x00"  # Loop count
        )
        assert is_animated_webp(animated_webp) is True

    def test_is_animated_webp_nonexistent_file(self, tmp_path):
        """Test is_animated_webp handles nonexistent file."""
        nonexistent = tmp_path / "nonexistent.webp"
        try:
            result = is_animated_webp(nonexistent)
            assert result is False
        except (FileNotFoundError, OSError):
            pass  # Expected behavior

    def test_is_animated_webp_not_webp_file(self, tmp_path):
        """Test is_animated_webp handles non-WebP file."""
        not_webp = tmp_path / "not_webp.txt"
        not_webp.write_text("This is not a WebP file")
        result = is_animated_webp(not_webp)
        assert result is False


class TestPsdColorModeDetection:
    """Tests for get_psd_color_mode function."""

    def test_get_psd_color_mode_rgb(self, tmp_path):
        """Test get_psd_color_mode detects RGB mode."""
        psd_rgb = tmp_path / "rgb.psd"
        psd_data = b"8BPS" + b"\x00\x01" + b"\x00" * 6 + b"\x00\x03" + b"\x00\x00\x00\x10" + b"\x00\x00\x00\x10" + b"\x00\x08" + b"\x00\x03"
        psd_rgb.write_bytes(psd_data)
        result = get_psd_color_mode(psd_rgb)
        assert result == "rgb"

    def test_get_psd_color_mode_cmyk(self, tmp_path):
        """Test get_psd_color_mode detects CMYK mode."""
        psd_cmyk = tmp_path / "cmyk.psd"
        psd_data = b"8BPS" + b"\x00\x01" + b"\x00" * 6 + b"\x00\x04" + b"\x00\x00\x00\x10" + b"\x00\x00\x00\x10" + b"\x00\x08" + b"\x00\x04"
        psd_cmyk.write_bytes(psd_data)
        result = get_psd_color_mode(psd_cmyk)
        assert result == "cmyk"

    def test_get_psd_color_mode_grayscale(self, tmp_path):
        """Test get_psd_color_mode detects grayscale mode."""
        psd_gray = tmp_path / "gray.psd"
        psd_data = b"8BPS" + b"\x00\x01" + b"\x00" * 6 + b"\x00\x01" + b"\x00\x00\x00\x10" + b"\x00\x00\x00\x10" + b"\x00\x08" + b"\x00\x01"
        psd_gray.write_bytes(psd_data)
        result = get_psd_color_mode(psd_gray)
        assert result == "grayscale"

    def test_get_psd_color_mode_invalid_file(self, tmp_path):
        """Test get_psd_color_mode handles invalid PSD."""
        invalid_psd = tmp_path / "invalid.psd"
        invalid_psd.write_text("Not a valid PSD file")
        result = get_psd_color_mode(invalid_psd)
        assert result is None

    def test_get_psd_color_mode_nonexistent_file(self, tmp_path):
        """Test get_psd_color_mode handles nonexistent file."""
        nonexistent = tmp_path / "nonexistent.psd"
        result = get_psd_color_mode(nonexistent)
        assert result is None

    def test_get_psd_color_mode_too_small(self, tmp_path):
        """Test get_psd_color_mode handles file that's too small."""
        tiny_psd = tmp_path / "tiny.psd"
        tiny_psd.write_bytes(b"8BPS")
        result = get_psd_color_mode(tiny_psd)
        assert result is None
