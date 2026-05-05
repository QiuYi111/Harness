# Defense-in-Depth Validation

Adapted from Superpowers `systematic-debugging/defense-in-depth.md` (MIT License).

## Overview

When you fix a bug caused by invalid data, adding validation at one place feels sufficient. But that single check can be bypassed by different code paths, refactoring, or mocks.

**Core principle:** Validate at EVERY layer data passes through. Make the bug structurally impossible.

## Why Multiple Layers

Single validation: "We fixed the bug"
Multiple layers: "We made the bug impossible"

Different layers catch different cases:
- Entry validation catches most bugs
- Business logic catches edge cases
- Environment guards prevent context-specific dangers
- Debug logging helps when other layers fail

## The Four Layers

### Layer 1: Entry Point Validation
**Purpose:** Reject obviously invalid input at API boundary

```python
def create_project(name: str, working_dir: str):
    if not working_dir or not working_dir.strip():
        raise ValueError("working_dir cannot be empty")
    if not os.path.exists(working_dir):
        raise FileNotFoundError(f"working_dir does not exist: {working_dir}")
    if not os.path.isdir(working_dir):
        raise NotADirectoryError(f"working_dir is not a directory: {working_dir}")
    # ... proceed
```

### Layer 2: Business Logic Validation
**Purpose:** Ensure data makes sense for this operation

```python
def initialize_workspace(project_dir: str, session_id: str):
    if not project_dir:
        raise ValueError("project_dir required for workspace initialization")
    # ... proceed
```

### Layer 3: Environment Guards
**Purpose:** Prevent dangerous operations in specific contexts

```python
import os, tempfile

def git_init(directory: str):
    if os.environ.get("TESTING"):
        norm = os.path.normpath(os.path.abspath(directory))
        tmp = os.path.normpath(tempfile.gettempdir())
        if not norm.startswith(tmp):
            raise RuntimeError(f"Refusing git init outside temp dir during tests: {directory}")
    # ... proceed
```

### Layer 4: Debug Instrumentation
**Purpose:** Capture context for forensics

```python
import traceback, logging

def git_init(directory: str):
    stack = ''.join(traceback.format_stack())
    logging.debug(f"About to git init: directory={directory}, cwd={os.getcwd()}, stack={stack}")
    # ... proceed
```

## Applying the Pattern

When you find a bug:

1. **Trace the data flow** — Where does bad value originate? Where used?
2. **Map all checkpoints** — List every point data passes through
3. **Add validation at each layer** — Entry, business, environment, debug
4. **Test each layer** — Try to bypass layer 1, verify layer 2 catches it

## Key Insight

All four layers are necessary. During testing, each layer catches bugs the others missed:
- Different code paths bypassed entry validation
- Mocks bypassed business logic checks
- Edge cases on different platforms needed environment guards
- Debug logging identified structural misuse

**Don't stop at one validation point.** Add checks at every layer.
