# Root Cause Tracing

Adapted from Superpowers `systematic-debugging/root-cause-tracing.md` (MIT License).

## Overview

Bugs often manifest deep in the call stack (wrong directory, wrong file path, wrong parameter value). Your instinct is to fix where the error appears, but that's treating a symptom.

**Core principle:** Trace backward through the call chain until you find the original trigger, then fix at the source.

## When to Use

- Error happens deep in execution (not at entry point)
- Stack trace shows long call chain
- Unclear where invalid data originated
- Need to find which test/code triggers the problem

## The Tracing Process

### 1. Observe the Symptom
```
Error: file not found at /wrong/path/config.json
```

### 2. Find Immediate Cause
**What code directly causes this?**
```python
config = load_config(config_path)  # config_path is "/wrong/path"
```

### 3. Ask: What Called This?
```
load_config(config_path)
  ← called by initialize_app(config_path)
  ← called by main("--config", "/wrong/path")
  ← called by test setup with hardcoded path
```

### 4. Keep Tracing Up
**What value was passed?**
- `config_path = "/wrong/path"` (hardcoded in test!)
- Test setup doesn't use temp directory

### 5. Find Original Trigger
**Where did wrong value come from?**
```python
# In test fixture:
config_path = "/wrong/path/config.json"  # Should use tmpdir
```

## Adding Stack Traces

When you can't trace manually, add instrumentation:

```python
import traceback

def load_config(path):
    print(f"DEBUG load_config: path={path}, cwd={os.getcwd()}", file=sys.stderr)
    print(f"  Callers: {''.join(traceback.format_stack()[-4:-1])}", file=sys.stderr)
    # ... proceed with load
```

**Critical:** Use stderr in tests (stdout may be captured).

**Run and capture:**
```bash
pytest tests/ 2>&1 | grep 'DEBUG load_config'
```

**Analyze stack traces:**
- Look for test file names
- Find the line number triggering the call
- Identify the pattern (same test? same parameter?)

## Key Principle

**NEVER fix just where the error appears.** Trace back to find the original trigger.

Fix at source, then add validation at each layer data passes through. See `defense-in-depth.md` for the complete pattern.
