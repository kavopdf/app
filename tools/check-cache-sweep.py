#!/usr/bin/env python3
"""Fails the build if the working cache can grow without bound again.

Everything the app works on is copied into cacheDir/work. It used to be cleaned only at
cold start, only if a file was over six hours old, and only inside work/ - so the link-icon
overlays written to the cache root were never removed at all, and a day of work could leave
gigabytes behind.

Pinned here:
  1. the age rule exists and is not a six-hour window,
  2. the sweep looks at the cache root as well as work/,
  3. a screen removes the files it made when it closes,
  4. a file the user shared or opened is spared, because another app may be reading it,
  5. the sweep actually runs on more than cold start.
"""
import pathlib
import re
import sys

POLICY = pathlib.Path("app/src/main/java/com/kavopdf/app/util/CachePolicy.java")
SWEEP = pathlib.Path("app/src/main/java/com/kavopdf/app/util/CacheSweep.kt")
ACT = pathlib.Path("app/src/main/java/com/kavopdf/app/PdfActivity.kt")
APP = pathlib.Path("app/src/main/java/com/kavopdf/app/KavoPdfApp.kt")

fails = []
for p in (POLICY, SWEEP, ACT, APP):
    if not p.exists():
        print(f"FAIL: {p} is missing")
        sys.exit(1)

policy = POLICY.read_text(encoding="utf-8")
sweep = SWEEP.read_text(encoding="utf-8")
act = ACT.read_text(encoding="utf-8")
app = APP.read_text(encoding="utf-8")

# 1) the age rule
m = re.search(r"MAX_AGE_MS\s*=\s*(\d+)L?\s*\*\s*([\d_]+)", policy)
if not m:
    fails.append("CachePolicy.MAX_AGE_MS not found")
else:
    minutes = int(m.group(1)) * (60_000 if int(m.group(2).replace("_", "")) == 60_000 else 0)
    if minutes == 0:
        fails.append("CachePolicy.MAX_AGE_MS is not expressed in minutes")
    elif minutes > 60 * 60_000:
        fails.append("CachePolicy.MAX_AGE_MS is an hour or more - the six-hour window is back")
m = re.search(r"ICON_AGE_MS\s*=\s*(\d+)L?\s*\*\s*60_000", policy)
if not m:
    fails.append("CachePolicy.ICON_AGE_MS not found - link icons would live for the full window")
if "link_shape_" not in policy:
    fails.append("CachePolicy no longer recognises the link-icon overlays")

# 2) the sweep must cover the cache root, not just work/
if '"work"' not in sweep:
    fails.append("CacheSweep no longer sweeps cacheDir/work")
if "context.cacheDir" not in sweep.replace('File(context.cacheDir, "work")', ""):
    fails.append("CacheSweep no longer sweeps the cache root - link icons would be missed again")
if "CachePolicy.isStale" not in sweep:
    fails.append("CacheSweep does not use the tested age rule")

# 3) a screen must delete what it made
if "override fun onDestroy()" not in act:
    fails.append("PdfActivity has no onDestroy, so a screen never removes its own cache files")
if "sessionFiles" not in act or "trackCacheFile" not in act:
    fails.append("PdfActivity no longer tracks the cache files it creates")
if "CacheSweep.deleteNow" not in act:
    fails.append("PdfActivity does not delete its tracked files when it closes")

# 4) a shared or opened file must be spared
if "keptFiles" not in act:
    fails.append("PdfActivity no longer spares the file the user shared or opened")
for handler in ("open.setOnClickListener", "share.setOnClickListener"):
    i = act.find(handler)
    if i < 0:
        fails.append(f"{handler} not found")
    elif "keptFiles.add" not in act[i:i + 300]:
        fails.append(f"{handler} does not mark the file as kept - Share/Open would break")

# 5) more than cold start
if "CacheSweep.sweep" not in app:
    fails.append("KavoPdfApp does not sweep")
if "cleanStaleCache" in app:
    fails.append("the old six-hour startup-only cleanup is still there")
if act.count("CacheSweep.sweep") < 1:
    fails.append("a screen closing does not trigger a sweep")

if fails:
    for f in fails:
        print("FAIL:", f)
    print("FAIL: the working cache can grow without bound")
    sys.exit(1)

print("PASS: cache files are removed when a screen closes and swept everywhere, with a tested age rule")
