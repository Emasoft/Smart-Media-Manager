#!/usr/bin/env python3
"""
Test stem_needs_sanitization() and build_safe_stem() actual behavior.
Tests OBSERVABLE BEHAVIOR, not duplicated implementation logic.
"""

import sys
from pathlib import Path

# Add the module to path
sys.path.insert(0, str(Path(__file__).parent))

from smart_media_manager.cli import (
    stem_needs_sanitization,
    build_safe_stem,
)


def test_stem_needs_sanitization_safe_names():
    """Test that stem_needs_sanitization returns False for safe names."""
    print("\n" + "=" * 70)
    print("Testing stem_needs_sanitization() - Safe Names")
    print("=" * 70)

    safe_stems = [
        ("vacation_photo", "Normal safe name"),
        ("IMG_1234", "Camera filename"),
        ("2025-01-29_sunset", "Date prefix"),
        ("my_photo_2024", "Year suffix"),
        ("test123", "Alphanumeric"),
    ]

    passed = 0
    failed = 0

    for stem, description in safe_stems:
        # Call ACTUAL function
        result = stem_needs_sanitization(stem)

        if result == False:  # Expected: does NOT need sanitization
            passed += 1
            print(f"✓ {description}: '{stem}' - Safe (no sanitization needed)")
        else:
            failed += 1
            print(f"✗ {description}: '{stem}' - FAILED (should be safe)")

    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_stem_needs_sanitization_unsafe_names():
    """Test that stem_needs_sanitization returns True for unsafe names."""
    print("\n" + "=" * 70)
    print("Testing stem_needs_sanitization() - Unsafe Names")
    print("=" * 70)

    unsafe_stems = [
        ("", "Empty string"),
        ("  vacation  ", "Leading/trailing spaces"),
        ("photo/video", "Forward slash"),
        ("my:file", "Colon"),
        ("file|name", "Pipe character"),
        ("test<>file", "Angle brackets"),
        ("x" * 300, "Excessive length (300 chars)"),
        ("café_photo", "Non-ASCII (accented characters)"),
        ("日本語", "Non-ASCII (Japanese)"),
    ]

    passed = 0
    failed = 0

    for stem, description in unsafe_stems:
        # Call ACTUAL function
        result = stem_needs_sanitization(stem)

        if result == True:  # Expected: DOES need sanitization
            passed += 1
            print(f"✓ {description} - Correctly flagged as needing sanitization")
        else:
            failed += 1
            print(f"✗ {description} - FAILED (should need sanitization)")

    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_build_safe_stem_basic():
    """Test that build_safe_stem generates safe filenames."""
    print("\n" + "=" * 70)
    print("Testing build_safe_stem() - Basic Functionality")
    print("=" * 70)

    test_cases = [
        ("vacation_photo", "20250129_123456", 1, "Normal safe name"),
        ("café_photo", "20250129_123456", 2, "Accented characters"),
        ("my/bad/file", "20250129_123456", 3, "Slashes"),
        ("test<>file", "20250129_123456", 4, "Angle brackets"),
        ("", "20250129_123456", 5, "Empty string"),
    ]

    passed = 0
    failed = 0

    for original_stem, run_token, sequence, description in test_cases:
        # Call ACTUAL function
        result = build_safe_stem(original_stem, run_token, sequence)

        # Verify ACTUAL behavior - result should be safe
        needs_sanitization = stem_needs_sanitization(result)

        if not needs_sanitization:
            passed += 1
            print(f"✓ {description}")
            print(f"  Original: '{original_stem}'")
            print(f"  Safe:     '{result}'")
        else:
            failed += 1
            print(f"✗ {description} - Generated unsafe stem: '{result}'")
        print()

    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0


def test_build_safe_stem_uniqueness():
    """Test that build_safe_stem generates unique names for same input with different sequences."""
    print("\n" + "=" * 70)
    print("Testing build_safe_stem() - Uniqueness")
    print("=" * 70)

    original_stem = "vacation_photo"
    run_token = "20250129_123456"

    # Generate multiple safe stems with different sequences
    stems = []
    for i in range(1, 6):
        # Call ACTUAL function
        result = build_safe_stem(original_stem, run_token, i)
        stems.append(result)

    # Verify ACTUAL behavior - all should be unique
    unique_stems = set(stems)

    print(f"Generated {len(stems)} stems:")
    for i, stem in enumerate(stems, 1):
        print(f"  Sequence {i}: {stem}")

    if len(unique_stems) == len(stems):
        print(f"\n✓ All {len(stems)} stems are unique")
        return True
    else:
        print(f"\n✗ FAILED: Only {len(unique_stems)} unique stems from {len(stems)} generations")
        print(f"  Duplicates found!")
        return False


def test_build_safe_stem_length_limit():
    """Test that build_safe_stem respects maximum length limit."""
    print("\n" + "=" * 70)
    print("Testing build_safe_stem() - Length Limit")
    print("=" * 70)

    # Create a very long original stem
    long_stem = "x" * 500
    run_token = "20250129_123456"
    sequence = 1

    # Call ACTUAL function
    result = build_safe_stem(long_stem, run_token, sequence)

    # Verify ACTUAL behavior - should be truncated
    # Read MAX_SAFE_STEM_LENGTH from the module
    from smart_media_manager.cli import MAX_SAFE_STEM_LENGTH

    print(f"Original stem length: {len(long_stem)} chars")
    print(f"Safe stem length:     {len(result)} chars")
    print(f"Maximum allowed:      {MAX_SAFE_STEM_LENGTH} chars")
    print(f"Safe stem:            '{result}'")

    if len(result) <= MAX_SAFE_STEM_LENGTH:
        print(f"\n✓ Safe stem respects maximum length limit ({MAX_SAFE_STEM_LENGTH} chars)")
        return True
    else:
        print(f"\n✗ FAILED: Safe stem exceeds maximum length ({len(result)} > {MAX_SAFE_STEM_LENGTH})")
        return False


def test_build_safe_stem_empty_input():
    """Test that build_safe_stem handles empty input gracefully."""
    print("\n" + "=" * 70)
    print("Testing build_safe_stem() - Empty Input")
    print("=" * 70)

    # Call ACTUAL function with empty stem
    result = build_safe_stem("", "20250129_123456", 1)

    # Verify ACTUAL behavior - should generate a valid stem
    needs_sanitization = stem_needs_sanitization(result)

    print(f"Empty input result: '{result}'")

    if not needs_sanitization and len(result) > 0:
        print(f"✓ Empty input handled gracefully, generated safe stem")
        return True
    else:
        print(f"✗ FAILED: Empty input produced invalid result")
        return False


def test_build_safe_stem_ascii_conversion():
    """Test that build_safe_stem converts non-ASCII to ASCII."""
    print("\n" + "=" * 70)
    print("Testing build_safe_stem() - ASCII Conversion")
    print("=" * 70)

    non_ascii_stems = [
        ("café", "French accents"),
        ("naïve", "Diaeresis"),
        ("日本語", "Japanese"),
        ("Москва", "Cyrillic"),
        ("Tëst", "Mixed accents"),
    ]

    passed = 0
    failed = 0

    for original_stem, description in non_ascii_stems:
        # Call ACTUAL function
        result = build_safe_stem(original_stem, "20250129", 1)

        # Verify ACTUAL behavior - should be ASCII only
        is_ascii = all(ord(c) < 128 for c in result)

        if is_ascii:
            passed += 1
            print(f"✓ {description}: '{original_stem}' → '{result}' (ASCII)")
        else:
            failed += 1
            print(f"✗ {description}: '{original_stem}' → '{result}' (NOT ASCII)")

    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_build_safe_stem_run_token_fragment():
    """Test that build_safe_stem incorporates run token fragment."""
    print("\n" + "=" * 70)
    print("Testing build_safe_stem() - Run Token Fragment")
    print("=" * 70)

    original_stem = "photo"
    run_token1 = "20250129_123456"
    run_token2 = "20250129_654321"
    sequence = 1

    # Call ACTUAL function with different run tokens
    result1 = build_safe_stem(original_stem, run_token1, sequence)
    result2 = build_safe_stem(original_stem, run_token2, sequence)

    print(f"Same stem '{original_stem}', same sequence {sequence}:")
    print(f"  Run token 1: {run_token1} → '{result1}'")
    print(f"  Run token 2: {run_token2} → '{result2}'")

    # Verify ACTUAL behavior - different run tokens should produce different results
    if result1 != result2:
        print(f"\n✓ Different run tokens produce unique stems")
        return True
    else:
        print(f"\n✗ FAILED: Different run tokens produced same stem")
        return False


def main():
    print("=" * 70)
    print("Filename Sanitization Behavior Tests")
    print("=" * 70)

    results = []

    # Run all tests
    try:
        results.append(("stem_needs_sanitization - Safe names", test_stem_needs_sanitization_safe_names()))
    except Exception as e:
        print(f"\n✗ Safe names test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("stem_needs_sanitization - Safe names", False))

    try:
        results.append(("stem_needs_sanitization - Unsafe names", test_stem_needs_sanitization_unsafe_names()))
    except Exception as e:
        print(f"\n✗ Unsafe names test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("stem_needs_sanitization - Unsafe names", False))

    try:
        results.append(("build_safe_stem - Basic functionality", test_build_safe_stem_basic()))
    except Exception as e:
        print(f"\n✗ Basic functionality test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("build_safe_stem - Basic functionality", False))

    try:
        results.append(("build_safe_stem - Uniqueness", test_build_safe_stem_uniqueness()))
    except Exception as e:
        print(f"\n✗ Uniqueness test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("build_safe_stem - Uniqueness", False))

    try:
        results.append(("build_safe_stem - Length limit", test_build_safe_stem_length_limit()))
    except Exception as e:
        print(f"\n✗ Length limit test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("build_safe_stem - Length limit", False))

    try:
        results.append(("build_safe_stem - Empty input", test_build_safe_stem_empty_input()))
    except Exception as e:
        print(f"\n✗ Empty input test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("build_safe_stem - Empty input", False))

    try:
        results.append(("build_safe_stem - ASCII conversion", test_build_safe_stem_ascii_conversion()))
    except Exception as e:
        print(f"\n✗ ASCII conversion test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("build_safe_stem - ASCII conversion", False))

    try:
        results.append(("build_safe_stem - Run token fragment", test_build_safe_stem_run_token_fragment()))
    except Exception as e:
        print(f"\n✗ Run token fragment test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("build_safe_stem - Run token fragment", False))

    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)

    all_passed = True
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False

    print("=" * 70)

    if all_passed:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
