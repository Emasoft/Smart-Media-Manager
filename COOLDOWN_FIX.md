# Apple Photos Import Cooldown Strategy

## Problem
When importing thousands of files, Apple Photos can become resource-exhausted and reject all subsequent imports with "unknown error" dialogs. This occurred after ~1800 files in user testing.

## Solution: Progressive Cooldown Strategy

### 1. Increased Base Delay
**Previous**: 3 seconds → 5 seconds (v0.4.2) → 10 seconds (v0.4.4)
**Current**: 10 seconds between batches
**Configurable**: `SMM_BATCH_DELAY` environment variable

```bash
# Override batch delay (default: 10 seconds)
export SMM_BATCH_DELAY=15
smart-media-manager --path /path/to/media
```

### 2. Extended Pause Every N Batches
**Frequency**: Every 3 batches (v0.4.4: 150 files per pause, changed from every 5 batches)
**Batch size**: 50 files per batch (v0.4.4: reduced from 100 for more granular control)
**Duration**: 30 seconds additional pause (v0.4.4: doubled from 15s)
**Purpose**: Let Photos catch up with:
- Database writes
- Thumbnail generation
- iCloud sync queue
- Memory management

**Log output**:
```
Batch 3/90: 50 imported, 0 failed
Taking extended pause (30s) to let Apple Photos process backlog...
```

### 3. Failure Recovery Delay
**Trigger**: When entire batch fails (0 imports, 100% failures)
**Duration**: 30 seconds additional pause
**Purpose**: Give Photos time to recover from errors

**Log output**:
```
Batch 19/90: 0 imported, 50 failed
Batch 19 failed completely (50 files). Waiting 30s before continuing...
```

## Expected Behavior

For a 4477-file import (90 batches @ 50 files/batch):

**Timeline (v0.4.4)**:
- **Batches 1-2**: 10s delay each = 20s total
- **Batch 3**: 10s + 30s extended pause = 40s
- **Batches 4-5**: 10s delay each = 20s total
- **Batch 6**: 10s + 30s extended pause = 40s
- **Pattern repeats every 3 batches**

**Total additional time**: ~30 minutes of cooldown
- Base delays: 89 intervals × 10s = ~15 minutes
- Extended pauses: 30 pauses × 30s = 15 minutes
- Trade-off: Slower but reliable vs. fast catastrophic failure

**Benefits**:
- Photos has regular breathing room every 150 files (vs. 500 in v0.4.2)
- Prevents resource exhaustion with more frequent, longer pauses
- Allows iCloud sync to catch up
- Enables memory cleanup
- Smaller batches (50 vs. 100) reduce per-batch load

## Constants (in smart_media_manager/cli.py)

```python
MAX_APPLESCRIPT_ARGS = 50  # Batch size (reduced from 100 in v0.4.4)
PHOTOS_BATCH_DELAY = int(os.getenv("SMM_BATCH_DELAY", "10"))  # Base delay (increased from 5s in v0.4.4)
PHOTOS_EXTENDED_PAUSE_INTERVAL = 3  # Extended pause every N batches (reduced from 5 in v0.4.4)
PHOTOS_EXTENDED_PAUSE_DURATION = 30  # Extended pause duration (doubled from 15s in v0.4.4)
PHOTOS_FAILURE_RECOVERY_DELAY = 30  # Delay after batch failures (seconds)
```

## Tuning Recommendations

### If imports still fail after ~2000 files (v0.4.4):
```bash
# Increase base delay to 15 seconds
export SMM_BATCH_DELAY=15
```
Note: Batch size is already at 50 files (reduced from 100). If failures persist, consider:
- Reducing batch size further in code (MAX_APPLESCRIPT_ARGS to 25)
- Increasing extended pause duration to 45s

### If you have fast iCloud sync and powerful Mac:
```bash
# Decrease to 7 seconds (faster but riskier)
export SMM_BATCH_DELAY=7
```
Note: Do NOT go below 5s without extensive testing

### If Photos.app becomes unresponsive:
- v0.4.4 already has aggressive settings (50 files/batch, 30s pauses every 3 batches)
- If still unresponsive, your Mac may lack sufficient resources for Photos.app
- Consider importing in smaller chunks (e.g., 1000 files at a time)

## Comparison: Version History

### v0.4.0-0.4.1 (3s delay, 100 files/batch):
- Batch 1-18: Success (1800 files in ~4 minutes)
- Batch 19+: **All failed** (Photos overwhelmed)
- Result: 40% success rate, catastrophic failure

### v0.4.2-0.4.3 (5s delay, 15s pause every 5 batches, 100 files/batch):
- Batch 1-19: Success (1900 files)
- Batch 20+: **Most failed** (Photos still overwhelmed)
- Result: ~42% success rate, still failed

### v0.4.4 (10s delay, 30s pause every 3 batches, 50 files/batch):
- Doubled base delay: 5s → 10s
- More frequent pauses: every 5 batches → every 3 batches
- Longer pauses: 15s → 30s
- Smaller batches: 100 → 50 files
- Expected result: **100% success rate** with ~30 min cooldown time
- Total time: ~60 minutes for 4477 files (slow but reliable)

**Trade-off**: 15× slower than v0.4.0, but **reliable** vs catastrophic failure

## Monitoring

Watch the logs for these patterns (v0.4.4 with 50 files/batch):

**✓ Healthy import**:
```
Batch 6/90: 50 imported, 0 failed
Taking extended pause (30s) to let Apple Photos process backlog...
Batch 7/90: 50 imported, 0 failed
```

**⚠️ Photos struggling** (but recovering):
```
Batch 40/90: 47 imported, 3 failed
Batch 41/90: 50 imported, 0 failed  # Recovered!
```

**✗ Photos exhausted** (failure recovery kicks in):
```
Batch 50/90: 0 imported, 50 failed
Batch 50 failed completely (50 files). Waiting 30s before continuing...
Batch 51/90: 50 imported, 0 failed  # Recovery successful!
```

## Future Improvements

1. **Adaptive delays**: Detect import slowdown and automatically increase delays
2. **Photos.app health check**: Monitor CPU/memory and pause if stressed
3. **Smaller batches**: Reduce from 100 to 50 files per batch for more granular control
4. **User notifications**: Show macOS notification when pausing for extended periods
