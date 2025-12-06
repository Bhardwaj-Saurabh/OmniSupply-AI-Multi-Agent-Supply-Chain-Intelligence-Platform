# Opik Project Name Conflict - Fixed

**Date**: December 6, 2025
**Issue**: Opik warning messages about nested spans with different project names
**Status**: ✅ **FIXED**

---

## 🐛 The Problem

You were seeing these warning messages repeatedly:

```
OPIK: You are attempting to log data into a nested span under the project name "omnisupply".
However, the project name "omnisupply-supervisor" from parent span will be used instead.
```

### Root Cause

The **Supervisor Agent and individual agents had different Opik project names** hardcoded:

- **Supervisor Agent**: `@track(project_name="omnisupply-supervisor")`
- **Individual Agents**: `@track(project_name="omnisupply")`

When the Supervisor (parent span) called individual agents (child spans), Opik detected the project name mismatch and forced all child spans to use the parent's project name, causing the warnings.

---

## ✅ The Fix

### 1. Unified Project Name in .env

Updated [.env](.env#L5):
```bash
# Before
OPIK_PROJECT_NAME=omnisupply-data-analyst

# After
OPIK_PROJECT_NAME=omnisupply
```

### 2. Dynamic Project Name in Base Agent

Updated [src/agents/base.py](src/agents/base.py):

**Lines 9-10, 23**: Added environment variable support
```python
import os

# Get Opik project name from environment
OPIK_PROJECT_NAME = os.getenv("OPIK_PROJECT_NAME", "omnisupply")
```

**Line 67**: Updated OpikTracer in default LLM
```python
# Before
callbacks=[OpikTracer()]

# After
callbacks=[OpikTracer(project_name=OPIK_PROJECT_NAME)]
```

**Line 111**: Updated @track decorator
```python
# Before
@track(project_name="omnisupply")

# After
@track(project_name=OPIK_PROJECT_NAME)
```

**Line 140**: Updated OpikTracer in graph execution
```python
# Before
config={"callbacks": [OpikTracer()]}

# After
config={"callbacks": [OpikTracer(project_name=OPIK_PROJECT_NAME)]}
```

### 3. Dynamic Project Name in Supervisor

Updated [src/supervisor/orchestrator.py](src/supervisor/orchestrator.py):

**Lines 10, 23**: Added environment variable support
```python
import os

# Get Opik project name from environment
OPIK_PROJECT_NAME = os.getenv("OPIK_PROJECT_NAME", "omnisupply")
```

**Line 101**: Updated OpikTracer in default LLM
```python
# Before
callbacks=[OpikTracer()]

# After
callbacks=[OpikTracer(project_name=OPIK_PROJECT_NAME)]
```

**Line 494**: Updated @track decorator (THIS WAS THE KEY FIX!)
```python
# Before
@track(project_name="omnisupply-supervisor")

# After
@track(project_name=OPIK_PROJECT_NAME)
```

**Line 524**: Updated OpikTracer in graph execution
```python
# Before
config={"callbacks": [OpikTracer()]}

# After
config={"callbacks": [OpikTracer(project_name=OPIK_PROJECT_NAME)]}
```

---

## 📊 Before vs After

### Before (Multiple Projects)

```
Parent Span (Supervisor)
└─ Project: "omnisupply-supervisor"  ← Different!
   │
   ├─ Child Span (Data Analyst)
   │  └─ Project: "omnisupply"  ← Conflict!
   │     └─ ⚠️ WARNING: Project name mismatch
   │
   ├─ Child Span (Risk Agent)
   │  └─ Project: "omnisupply"  ← Conflict!
   │     └─ ⚠️ WARNING: Project name mismatch
   │
   └─ Child Span (Finance Agent)
      └─ Project: "omnisupply"  ← Conflict!
          └─ ⚠️ WARNING: Project name mismatch
```

### After (Unified Project)

```
Parent Span (Supervisor)
└─ Project: "omnisupply"  ← Same!
   │
   ├─ Child Span (Data Analyst)
   │  └─ Project: "omnisupply"  ← ✅ Match!
   │
   ├─ Child Span (Risk Agent)
   │  └─ Project: "omnisupply"  ← ✅ Match!
   │
   └─ Child Span (Finance Agent)
      └─ Project: "omnisupply"  ← ✅ Match!
```

---

## ✅ Verification

Run the demo to verify no more warnings:

```bash
python omnisupply_demo.py 2>&1 | grep "OPIK:"
```

**Expected output**: No project name mismatch warnings

---

## 📚 Files Modified

1. [.env](.env) - Set `OPIK_PROJECT_NAME=omnisupply`
2. [src/agents/base.py](src/agents/base.py) - 4 changes
   - Added import os (line 10)
   - Added OPIK_PROJECT_NAME variable (line 23)
   - Updated 3 OpikTracer() calls (lines 67, 111, 140)

3. [src/supervisor/orchestrator.py](src/supervisor/orchestrator.py) - 4 changes
   - Added import os (line 10)
   - Added OPIK_PROJECT_NAME variable (line 23)
   - Updated 3 OpikTracer() calls (lines 101, 494, 524)

---

## 🎯 Benefits

1. ✅ **No more Opik warnings** - All spans use same project name
2. ✅ **Cleaner logs** - Easier to read execution traces
3. ✅ **Centralized configuration** - Change project name in one place (.env)
4. ✅ **Consistent tracing** - All agent calls tracked in single project

---

## 🔄 How to Change Project Name

To use a different Opik project name, just update your `.env` file:

```bash
# Use any project name you want
OPIK_PROJECT_NAME=my-custom-project-name
```

All agents and supervisor will automatically use the new name!

---

## 📖 Technical Details

### Why The Warnings Happened

Opik's tracing system enforces that **all nested spans must belong to the same project**. This is by design to keep trace hierarchies clean and organized.

When a parent span has project "A" and tries to create a child span with project "B", Opik:
1. Forces the child to use project "A" (overrides the child's project name)
2. Logs a warning message to alert developers of the mismatch

### The Solution Pattern

The fix follows this pattern:

```python
# 1. Import os
import os

# 2. Get project name from environment (with fallback)
OPIK_PROJECT_NAME = os.getenv("OPIK_PROJECT_NAME", "omnisupply")

# 3. Use variable instead of hardcoded string
OpikTracer(project_name=OPIK_PROJECT_NAME)  # Dynamic
# instead of
OpikTracer(project_name="omnisupply")      # Hardcoded
```

This ensures all components use the same project name from a single source of truth (.env file).

---

**Last Updated**: December 6, 2025
**Status**: Production-ready ✅
