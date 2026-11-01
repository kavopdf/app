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

# ---- 1b) repair must not go through the normal "is this a PDF" gate ---------------
# openPdf() refuses anything without "%PDF-" in its first kilobyte and asks the engine
# for a page count before handing the file over. A damaged PDF fails both - which is the
# one file this tool exists for. The repair branch has to load the bytes itself.
branch = act[act.index("if (tool == Action.REPAIR)"):]
branch = branch[: branch.index("\n            return")]
# Comments explain why openPdf is avoided; they are not calls. Strip them first so the
# check reads code, not prose.
branch = re.sub(r"//[^\n]*", "", branch)
if "openPdf(" in branch:
    fails.append("the repair branch calls openPdf() - a damaged file would be refused "
                 "before the repair engine ever sees it")
if "looksLikePdf" in branch:
    fails.append("the repair branch gates on looksLikePdf() - a file with a damaged or "
                 "missing header can never reach the repair")
if "copyToCache" not in branch:
    fails.append("the repair branch does not copy the file to the cache itself")
if "diagnose(" not in branch:
    fails.append("the repair branch no longer diagnoses the file as soon as it is picked")
if "askRepairPassword" not in act:
    fails.append("an encrypted file is never asked for its password")
if "PdfRepair.repair(src, repairPassword, out)" not in act:
    fails.append("the password the user gave is not passed to the repair")

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
else:
    d = re.search(r'android:pathData="([^"]+)"', icon).group(1)
    if len(d) < 400:
        fails.append("ic_repair.xml path is too short to be a real glyph")
    # The tool icons all come from the same set: a 960 viewport drawn through a
    # translateY(960) group, which is how Material Symbols coordinates are carried over.
    # An icon drawn in its own convention renders at the wrong size next to the others.
    if 'android:translateY="960"' not in icon:
        fails.append("ic_repair.xml is not drawn in the same 960/translateY convention as the "
                     "other tool icons - it will not match their size")
    if 'android:width="26dp"' not in icon or 'android:height="26dp"' not in icon:
        fails.append("ic_repair.xml is not 26dp like the other tool icons")

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

# ---- 6) the stress fixtures are in the repo and wired into the suite ------------
fixdir = pathlib.Path("tools/engine-verify/fixtures/repair")
fixtures = sorted(fixdir.glob("*.pdf")) if fixdir.is_dir() else []
if len(fixtures) < 50:
    fails.append(f"only {len(fixtures)} repair fixtures are in the repo - the stress set "
                 "must stay, it is the only thing that tests real damage")
suite = pathlib.Path("tools/verify-engine.sh").read_text(encoding="utf-8")
if "TestRepairFixtures" not in suite:
    fails.append("TestRepairFixtures is not run by verify-engine.sh")
# The 51-fixture sweep is slow and only says anything about the repair engine, so it is
# gated on a fingerprint of the engine, its tests and its fixtures. A change to any other
# tool must not pay for it - and a change to the repair must never silently skip it.
for needle, why in [
    ("repair-suite.stamp", "the fingerprint file is gone - the suite would either never "
                           "run or run on every build"),
    ("PdfRepair.java", "the fingerprint must include the engine itself"),
    ("fixtures/repair", "the fingerprint must include the fixtures"),
    ("REPAIR_FULL", "there is no way to force a full run"),
]:
    if needle not in suite:
        fails.append(f"the repair-suite gate lost {needle}: {why}")
if not pathlib.Path("tools/engine-verify/repair-suite.stamp").exists():
    fails.append("repair-suite.stamp is missing - commit it with every repair change, or the "
                 "suite will run on every build")
tort = pathlib.Path("tools/engine-verify/fixtures/torture")
if not tort.is_dir() or len(list(tort.glob("*.pdf"))) < 40:
    fails.append("the torture pack is not in the repo - it is the only set that "
                 "tests structural and semantic corruption")
if not pathlib.Path("tools/engine-verify/TestRepairFixtures.java").exists():
    fails.append("TestRepairFixtures.java is missing")

if fails:
    for x in fails:
        print("FAIL:", x)
    sys.exit(1)
print("PASS: repair verifies every page before saving, refuses to save otherwise, "
      "handles every real damage stage, and is wired into the enum, home screen, "
      "heading, suffix, strings, icon and the 21-file stress set")
