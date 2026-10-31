#!/usr/bin/env python3
"""Fails the build if the app starts doing needless repeated work or needless wakeups.

Two things were found in a deep audit and fixed once; this keeps them fixed.

1. Redaction called the engine once per page. The engine reloads and rewrites the whole
   document on every call, so twenty redactions on a two-hundred page file meant twenty
   full loads and twenty full saves, plus a temp copy per step. redactPagesLazy() asks for
   one painted page at a time instead, so memory stays at one bitmap while the document is
   opened and saved once.

2. The ANR watchdog ticked the main thread every 500 ms for the life of the process,
   including while the app sat behind another app doing nothing. It now backs off to 5 s
   when the app is not in front. The detector is not removed.
"""
import pathlib
import re
import sys

KT = pathlib.Path("app/src/main/java/com/kavopdf/app")
REDACT = KT / "RedactActivity.kt"
ENGINE = KT / "engine/PdfEngine.java"
CRASH = KT / "util/CrashGuard.kt"
STALLS = KT / "engine/Stalls.java"

fails = []


def read(p):
    if not p.exists():
        fails.append(f"{p} is missing")
        return ""
    return p.read_text(encoding="utf-8")


redact = read(REDACT)
engine = read(ENGINE)
crash = read(CRASH)
stalls = read(STALLS)

# --- redaction: one open, one save ---
if "redactPagesLazy(" not in redact:
    fails.append("RedactActivity no longer uses redactPagesLazy - it would reload and "
                 "rewrite the whole document once per redacted page")
if re.search(r"PdfEngine\.redactPages\(", redact):
    fails.append("RedactActivity calls the array version of redactPages again - that is "
                 "the per-page reload")
if "public static void redactPagesLazy(" not in engine:
    fails.append("PdfEngine.redactPagesLazy is gone")
if "interface PagePainter" not in engine:
    fails.append("the one-page-at-a-time painter is gone - redaction would have to hold "
                 "every full-page bitmap at once")
# the loop must still ask for one page at a time, not build a list of bitmaps
if re.search(r"map\s*\{[^}]*paintBlack", redact):
    fails.append("RedactActivity builds a list of painted bitmaps - that is a full page "
                 "per redaction held in memory at once")
if "redact_step_" in redact:
    fails.append("the per-step temp file is back - the document is being saved more than once")

# --- the stall ticker must back off in the background ---
if "Stalls.IDLE_MS" not in crash:
    fails.append("the ANR watchdog ticks at the foreground rate even in the background")
if "IDLE_MS" not in stalls:
    fails.append("Stalls.IDLE_MS is missing")
else:
    m = re.search(r"IDLE_MS\s*=\s*([\d_]+)L", stalls)
    tick = re.search(r"TICK_MS\s*=\s*([\d_]+)L", stalls)
    if m and tick:
        idle = int(m.group(1).replace("_", ""))
        fast = int(tick.group(1).replace("_", ""))
        if idle < fast * 4:
            fails.append(f"IDLE_MS ({idle}) is not a real back-off from TICK_MS ({fast})")

if fails:
    for f in fails:
        print("FAIL:", f)
    print("FAIL: needless repeated work or needless wakeups came back")
    sys.exit(1)

print("PASS: redaction opens the document once, and the watchdog backs off when the app "
      "is not in front")
