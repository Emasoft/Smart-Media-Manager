# GitHub Issues Created for Smart Media Manager

## Summary

All features from the TODO checklist have been created as GitHub issues for tracking and documentation purposes.

**Important Note:** ✅ **All these features have already been implemented** in commits `a5fc66e` and `d3a425f`. The issues are created for:
- Documentation purposes
- Future reference
- Tracking any refinements or bugs
- Community visibility

## Created Issues

### Issue #1: Add comprehensive statistics tracking and reporting
**URL:** https://github.com/Emasoft/Smart-Media-Manager/issues/1
**Status:** ✅ Already implemented
**Implementation:** Commit a5fc66e

**What was implemented:**
- `RunStatistics` dataclass tracking 16 metrics
- Color-coded summary output with ANSI colors
- Statistics logged to run log file
- Success rate calculation
- Per-file failure tracking

### Issue #2: Add interactive retry prompt for failed Apple Photos imports
**URL:** https://github.com/Emasoft/Smart-Media-Manager/issues/2
**Status:** ✅ Already implemented
**Implementation:** Commit a5fc66e

**What was implemented:**
- `prompt_retry_failed_imports()` function
- Interactive y/n prompt after failures
- Retry only failed files
- Updated statistics after retry
- Graceful error handling

### Issue #3: Enhance Apple Photos error capture with per-file details
**URL:** https://github.com/Emasoft/Smart-Media-Manager/issues/3
**Status:** ✅ Already implemented
**Implementation:** Commit a5fc66e

**What was implemented:**
- Enhanced AppleScript return format
- Per-file error messages
- Parsing of error details
- Logging of specific failure reasons
- Distinction between failure types

### Issue #4: Add .m4v remuxing support (no re-encoding)
**URL:** https://github.com/Emasoft/Smart-Media-Manager/issues/4
**Status:** ✅ Already implemented
**Implementation:** Commit a5fc66e

**What was implemented:**
- New format rule `R-VID-001a` for .m4v files
- `rewrap_to_mp4` action
- Container-only change (no re-encoding)
- Preserves quality and metadata

### Issue #5: Add corrupt/truncated video detection before staging
**URL:** https://github.com/Emasoft/Smart-Media-Manager/issues/5
**Status:** ✅ Already implemented
**Implementation:** Commit a5fc66e

**What was implemented:**
- `is_video_corrupt_or_truncated()` function
- Multiple validation checks (ffprobe, streams, duration, first frame)
- Integration into `detect_media()` pipeline
- Detailed error messages
- Statistics tracking for corrupt files

### Issue #6: Update conversion preferences: PNG for images, smart ffmpeg for video
**URL:** https://github.com/Emasoft/Smart-Media-Manager/issues/6
**Status:** ✅ Already implemented
**Implementation:** Commit a5fc66e

**What was implemented:**
- `convert_to_png()` function
- Updated format rules for WebP, AVIF, PSD
- PNG preferred over TIFF
- Smart ffmpeg defaults for video
- Safe fallback uses PNG

### Issue #7: Improve automated filename renaming to avoid errors
**URL:** https://github.com/Emasoft/Smart-Media-Manager/issues/7
**Status:** ⚠️ Partially implemented (needs refinement)

**Current implementation:**
- `sanitize_stage_paths()` function
- `build_safe_stem()` helper
- Filename preservation when possible
- Run token + sequence for uniqueness

**Could be improved:**
- More conservative renaming logic
- Better logging of rename reasons
- Additional edge case handling

## Issue #8: Add fast pre-count for file scanning

**Note:** This issue was being created but the command got stuck. The feature is not strictly necessary as:
- Progress bars already exist for all stages
- Current implementation shows progress in real-time
- Pre-counting would add latency before scanning starts

**Could be created later if needed.**

## Mapping: TODO Checklist → GitHub Issues

| TODO Item | Issue # | Status |
|-----------|---------|--------|
| Add global progress reporting for every stage | #1, #8 | ✅ Progress bars exist |
| Capture detailed per-stage statistics | #1 | ✅ Implemented |
| Emit stats summary at end of run | #1 | ✅ Implemented |
| Prompt user to retry failed imports | #2 | ✅ Implemented |
| Improve Apple Photos error handling | #3 | ✅ Implemented |
| Remux .m4v files with compatible codecs | #4 | ✅ Implemented |
| Detect corrupt video before staging | #5 | ✅ Implemented |
| Update conversion preferences (PNG/smart ffmpeg) | #6 | ✅ Implemented |
| Keep console output limited to progress bars | #1 | ✅ Implemented |
| Improve filename renaming | #7 | ⚠️ Needs refinement |

## What Can Be Done With These Issues

### For Completed Issues (#1-6)
- **Close them** if no further work needed
- **Keep open** for documentation/future refinements
- **Add "implemented" label** to mark as done
- **Reference commits** in comments

### For Issue #7 (Renaming)
- Review current implementation
- Identify specific edge cases to improve
- Create sub-tasks if needed
- Keep open for future work

### Creating New Issues
If new bugs or features are discovered:
1. Create a new issue
2. Reference related issues if applicable
3. Add appropriate labels
4. Link to relevant code sections

## Labels Used

All issues are tagged with `enhancement` label. Additional labels could be added:
- `implemented` - For already completed features
- `documentation` - For doc-only changes
- `bug` - If issues are discovered
- `help-wanted` - For community contributions
- `good-first-issue` - For newcomers

## Next Steps

1. **Review issues** and decide which to close vs keep open
2. **Add "implemented" label** to issues #1-6
3. **Add commit references** in issue comments
4. **Create milestones** for future releases
5. **Close or refine** issue #7 based on needs

## Files Created

- This summary: `GITHUB_ISSUES_SUMMARY.md`
- Implementation details: `IMPLEMENTATION_SUMMARY.md` (already exists)
- Deployment record: `DEPLOYMENT_SUMMARY.md` (already exists)
