#!/usr/bin/env python3
"""Fails the build if the repair tool could ever hand the user a file it did not verify.

Repair is the one feature whose failure mode is silent: a half-rebuilt PDF opens, looks
plausible, and is missing pages. So the rules are pinned here rather than trusted:

  * the engine must reopen and walk every page before it calls a repair a success
  * a repair that does not pass that check must delete its output
  * the screen must refuse to save when the engine says it did not verify
  * the tool must be wired everywhere a tool has to be (enum, home screen, heading,
    file suffix, run branch, strings, icon) - a missing branch is how a screen ends up
    titled with the app name
"""
import pathlib
import re
import sys

KT = pathlib.Path("app/src/main/java/com/kavopdf/app")
ENGINE = KT / "engine/PdfRepair.java"
ACT = KT / "ToolsActivity.kt"
MAIN = KT / "MainActivity.kt"
TOOL = KT / "model/ToolItem.kt"
STRINGS = pathlib.Path("app/src/main/res/values/strings.xml")
ICON = pathlib.Path("app/src/main/res/drawable/ic_repair.xml")

fails = []
need = [ENGINE, ACT, MAIN, TOOL, STRINGS, ICON]
for f in need:
    if not f.exists():
        fails.append(f"{f} is missing")
if fails:
    for x in fails:
        print("FAIL:", x)
    sys.exit(1)

engine = ENGINE.read_text(encoding="utf-8")
act = ACT.read_text(encoding="utf-8")
main = MAIN.read_text(encoding="utf-8")
tool = TOOL.read_text(encoding="utf-8")
strings = STRINGS.read_text(encoding="utf-8")
icon = ICON.read_text(encoding="utf-8")

# ---- 1) the engine verifies before it claims success -------------------------------
body = engine[engine.index("public static Report repair("):]
body = body[: body.index("//  Stage 1 - the bytes themselves") if "//  Stage 1" in body else len(body)]
if "verify(out, pw, r)" not in body:
    fails.append("repair() no longer verifies its own output")
if not re.search(r"if \(!r\.verified \|\| r\.pagesAfter <= 0\)", body):
    fails.append("repair() no longer refuses to accept an unverified result")
if body.count("out.delete()") < 2:
    fails.append("repair() does not delete the output when it fails")
if "new PDFStreamParser(page).parse()" not in engine:
    fails.append("the page content is no longer walked - presence is not proof")
if "keepProtection" not in engine:
    fails.append("repairing an encrypted file would strip its protection")

# ---- 2) the screen must not save an unverified repair -----------------------------
if "if (!rep.readable || !rep.verified)" not in act:
    fails.append("ToolsActivity would save a repair the engine did not verify")
if "throw IllegalStateException" not in act:
    fails.append("the repair branch no longer aborts the save on failure")

# ---- 3) the tool is wired everywhere ---------------------------------------------
if not re.search(r"\bREPAIR\b", tool):
    fails.append("Action.REPAIR is not in the enum")
if "Action.REPAIR" not in main:
    fails.append("Repair is not on the home screen")
if not re.search(r"Action\.REPAIR\s*->\s*R\.string\.tool_repair", act):
    fails.append("applyToolChrome has no Repair heading - the screen would show the app name")
if not re.search(r"Action\.REPAIR\s*->\s*\"_repaired\"", act):
    fails.append("the repaired file has no suffix")
if not re.search(r"Action\.REPAIR\s*->\s*\{", act):
    fails.append("onRun has no Repair branch")
for s in ("tool_repair", "tool_repair_desc", "repair_run", "repair_failed_title",
          "repair_section_found", "repair_section_done", "repair_label_pages"):
    if f'name="{s}"' not in strings:
        fails.append(f"string {s} is missing")

# ---- 4) the icon is a real vector, not an empty file -----------------------------
if "<vector" not in icon or "pathData" not in icon:
    fails.append("ic_repair.xml is not a vector drawable with a path")
elif len(re.search(r'android:pathData="([^"]+)"', icon).group(1)) < 40:
    fails.append("ic_repair.xml path is too short to draw anything")

# ---- 5) the tests exist and actually run -----------------------------------------
test = pathlib.Path("tools/engine-verify/TestRepair.java")
if not test.exists():
    fails.append("TestRepair.java is missing")
elif "TestRepair" not in pathlib.Path("tools/verify-engine.sh").read_text(encoding="utf-8"):
    fails.append("TestRepair is not run by verify-engine.sh")
else:
    t = test.read_text(encoding="utf-8")
    for case in ("truncate(", "wipeXref(", "removeEof(", "mutateStartxref(", "junkPrefix(",
                 "junkSuffix(", "removeHeader(", "breakPageTree(", "corruptStream(",
                 "breakPageContent("):
        if case not in t:
            fails.append(f"TestRepair no longer covers {case}")

if fails:
    for x in fails:
        print("FAIL:", x)
    sys.exit(1)
print("PASS: repair verifies every page before saving, refuses to save otherwise, "
      "and is wired into the enum, home screen, heading, suffix, strings and icon")
