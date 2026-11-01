#!/usr/bin/env python3
"""Guards the worker-thread rule: nothing inside a save producer may touch the UI.

A producer handed to runAndSave / runAndSaveAs runs on Dispatchers.IO. A toast there throws
"Can't toast on a thread that has not called Looper.prepare()" - which is exactly what shipped
once, logged as a NullPointerException in the activity log. This catches the next one.
"""
import pathlib, re, sys

ROOTS = [pathlib.Path("app/src/main/java")]
UI_CALLS = ("toast(", "showSuccess(", "AlertDialog", "setContentView", "binding.")
PRODUCERS = ("runAndSave(", "runAndSaveAs(")

problems = []

for root in ROOTS:
    for path in root.rglob("*.kt"):
        text = path.read_text(encoding="utf-8")
        for call in PRODUCERS:
            for match in re.finditer(re.escape(call), text):
                start = text.find("{", match.end())
                if start < 0:
                    continue
                depth, i = 0, start
                while i < len(text):
                    if text[i] == "{":
                        depth += 1
                    elif text[i] == "}":
                        depth -= 1
                        if depth == 0:
                            break
                    i += 1
                block = text[start:i]
                for line_no, line in enumerate(block.splitlines(), 1):
                    stripped = line.strip()
                    if stripped.startswith("//") or stripped.startswith("*"):
                        continue
                    if "runOnUiThread" in stripped or "withContext(Dispatchers.Main" in stripped:
                        continue
                    for ui in UI_CALLS:
                        if ui in stripped and "binding." not in ui:
                            problems.append(
                                f"{path.name}: '{stripped[:60]}' runs on a worker thread "
                                f"inside {call[:-1]}"
                            )

if problems:
    print("FAIL: " + "; ".join(sorted(set(problems))))
    sys.exit(1)
print("PASS: nothing inside a save producer touches the UI directly - toasts and dialogs are "
      "posted to the main thread")
