#!/usr/bin/env python3
"""Fails the build if the crash / stall detectors start crying wolf, or if a drawn line
goes back to being a polygon.

Both rules come from a real activity log:

  * every "Main thread blocked for 5001ms" entry was the ticker's own 5-second idle
    interval being read as a freeze. The detector must be told how long it asked for.
  * every "Previous launch crashed" entry carried uptime=0s and a near-empty heap - a
    process that ended normally. A kill in the background is not a crash.
  * every "AnnotateActivity took 4267ms, normal is 176ms" was an export compared against
    the norm of opening the file, because one screen shared one history.
"""
import pathlib
import re
import sys

K = pathlib.Path("app/src/main/java/com/kavopdf/app")
STALLS = K / "engine/Stalls.java"
CRASH = K / "util/CrashGuard.kt"
ACT = K / "PdfActivity.kt"
REND = K / "ui/AnnotRenderer.kt"
OVER = K / "ui/OverlayView.kt"

fails = []
for p in (STALLS, CRASH, ACT, REND, OVER):
    if not p.exists():
        print(f"FAIL: {p} is missing")
        sys.exit(1)

stalls = STALLS.read_text(encoding="utf-8")
crash = CRASH.read_text(encoding="utf-8")
act = ACT.read_text(encoding="utf-8")
rend = REND.read_text(encoding="utf-8")
over = OVER.read_text(encoding="utf-8")


def body(text, start_re):
    m = re.search(start_re, text)
    if not m:
        return None
    i = m.start()
    j = text.index("{", i)
    depth, k = 0, j
    while k < len(text):
        if text[k] == "{":
            depth += 1
        elif text[k] == "}":
            depth -= 1
            if depth == 0:
                return text[i:k + 1]
        k += 1
    return None


# 1) Stalls must be told the interval it asked for
if not re.search(r"long onTick\(long nowMs,\s*long expectedMs\)", stalls):
    fails.append("Stalls.onTick lost its expectedMs parameter - a scheduled 5s idle gap "
                 "would be reported as a 5s freeze again")
if not re.search(r"Math\.max\(0L,\s*expectedMs\)", stalls):
    fails.append("Stalls no longer subtracts the expected interval")

# 2) the ticker must pass the interval it actually scheduled, and reset across a switch
tick = body(crash, r"val tick = object : Runnable")
if tick is None:
    fails.append("the stall ticker is gone")
else:
    # the call nests elapsedRealtime(), so match the tail rather than the arguments
    if not re.search(r"stalls\.onTick\([\s\S]{0,80}?,\s*expected\s*\)", tick):
        fails.append("the ticker does not pass the interval it scheduled to Stalls.onTick")
    if "stalls.reset()" not in tick:
        fails.append("the ticker does not reset the beat when the app changes foreground state")
    if "startedInFront" not in tick and "wasForeground" not in tick:
        fails.append("the ticker does not remember whether the gap started in front of the user")

# 3) "previous launch crashed" must be lifecycle-driven, not a 5-second timer
boot = body(crash, r"// B7:")
if boot is None:
    fails.append("the previous-launch check is gone")
else:
    if "registerActivityLifecycleCallbacks" not in boot:
        fails.append("the previous-launch flag is not driven by the activity lifecycle - "
                     "a normal background kill would be reported as a crash")
    if re.search(r"postDelayed\([\s\S]{0,400}?5000", boot):
        fails.append("the old five-second timer is back - a launch closed quickly would "
                     "be reported as a crash")

# 4) one norm per operation, not one per screen
key = body(act, r"private fun taskKey\(status: String\)")
if key is None:
    fails.append("PdfActivity.taskKey is gone")
elif not re.search(r"tool\s*\+\s*\":\"\s*\+\s*op", key) and "op" not in key:
    fails.append("taskKey ignores the operation - an export would be judged against the "
                 "norm of opening the file")

# 5) a drawn line must be a curve
if "fun strokePath(" not in rend:
    fails.append("AnnotRenderer.strokePath is gone - freehand strokes would be polygons again")
else:
    if "quadTo" not in rend:
        fails.append("strokePath no longer uses quadTo")
    stroke = body(rend, r"is Annot\.Stroke ->")
    if stroke is None:
        fails.append("the Annot.Stroke branch is gone")
    elif "strokePath(" not in stroke:
        fails.append("the exported stroke does not use strokePath")
    elif "lineTo" in stroke:
        fails.append("the exported stroke still joins raw points with lineTo")
if "strokePath(" not in over:
    fails.append("the live preview does not use strokePath - preview and export would differ")
else:
    pen = body(over, r"if \(tool == Tool\.PEN")
    if pen is not None and "lineTo" in pen:
        fails.append("the live preview still joins raw points with lineTo")

if fails:
    for f in fails:
        print("FAIL:", f)
    print("FAIL: the detectors or the ink path regressed")
    sys.exit(1)

print("PASS: stalls are measured against the interval asked for, a background kill is not a "
      "crash, each operation has its own norm, and drawn lines are curves")
