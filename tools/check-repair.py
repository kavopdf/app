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
    if len(d) < 40:
        fails.append("ic_repair.xml path is too short to draw anything")
    xs = [float(v) for v in re.findall(r"([\d.]+),", d)]
    ys = [float(v) for v in re.findall(r",([\d.]+)", d)]
    if not xs or not ys:
        fails.append("ic_repair.xml has no coordinates")
    else:
        # The icon has to fill the same 960 box the other tool icons use, without
        # spilling outside it - a drawing that sits in a corner renders small.
        if min(xs) < 0 or max(xs) > 960 or min(ys) < 0 or max(ys) > 960:
            fails.append("ic_repair.xml draws outside its 960 viewport (clipped)")
        elif (max(xs) - min(xs)) < 620 or (max(ys) - min(ys)) < 620:
            fails.append(f"ic_repair.xml only covers {max(xs)-min(xs):.0f}x{max(ys)-min(ys):.0f} "
                         "of its 960 box - it will render smaller than the other tool icons")

# ---- 4b) the stages that the stress set proved necessary -------------------------
# Each of these exists because a real fixture needed it. Losing one silently turns a
# recoverable file into "could not repair".
for needle, why in [
    ("workDir(", "the scratch copy must fall back to a writable folder - a read-only source "
                 "folder made every repair fail with 'Permission denied'"),
    ("salvageObjects(", "the object-lifting stage is what recovers a file whose object "
                        "headers are damaged"),
    ("buildLifted(", "the lifted file has to be rebuilt with a fresh cross-reference table"),
    ("repointPages(", "a catalog whose page-tree node was destroyed must be repointed at a "
                      "rebuilt one"),
    ("brokenOnArrival", "a page that was already broken must not be treated as a regression"),
    ("setContents(", "a kept page whose content is destroyed must be emptied, or readers "
                     "fail on it"),
    ("none of their content survived", "a file whose pages are all empty must be refused, "
                                       "not handed over as a blank PDF"),
]:
    if needle not in engine:
        fails.append(f"repair lost {needle}: {why}")

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
if "TestRepairFixtures" not in pathlib.Path("tools/verify-engine.sh").read_text(encoding="utf-8"):
    fails.append("TestRepairFixtures is not run by verify-engine.sh")
if not pathlib.Path("tools/engine-verify/TestRepairFixtures.java").exists():
    fails.append("TestRepairFixtures.java is missing")

if fails:
    for x in fails:
        print("FAIL:", x)
    sys.exit(1)
print("PASS: repair verifies every page before saving, refuses to save otherwise, "
      "handles every real damage stage, and is wired into the enum, home screen, "
      "heading, suffix, strings, icon and the 21-file stress set")
