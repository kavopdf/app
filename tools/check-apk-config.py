#!/usr/bin/env python3
"""Fails the build if the APK starts carrying things it can never use.

Two pins:

1. LOCALES. res/ has only values and values-night - the app is English - but
   resources.arsc was carrying about 120 languages of library strings from material,
   appcompat and the rest. resConfigs "en" drops them, which changes nothing that is
   displayed. The trap: if a translation folder is ever added and resConfigs is not
   updated, that language would silently never appear. This catches that.

2. ABIs. Both arm64-v8a and armeabi-v7a are shipped on purpose - a lot of budget phones
   are still 32-bit. Dropping one would halve the native libs and break those phones.
"""
import pathlib
import re
import sys

GRADLE = pathlib.Path("app/build.gradle")
RES = pathlib.Path("app/src/main/res")

fails = []
if not GRADLE.exists():
    print("FAIL: app/build.gradle is missing")
    sys.exit(1)
g = GRADLE.read_text(encoding="utf-8")

# 1) resConfigs must be present
m = re.search(r'resConfigs\s+"([^"]+)"', g)
if not m:
    fails.append('resConfigs is gone - about 120 unused languages would come back')
else:
    kept = {x.strip() for x in m.group(1).split(",")}
    if "en" not in kept:
        fails.append('resConfigs no longer keeps "en"')
    # every translation folder in the source must be listed, or it silently disappears
    if RES.exists():
        for d in sorted(RES.glob("values-*")):
            suffix = d.name[len("values-"):]
            # night, v23, land, sw600dp and friends are config qualifiers, not languages
            if re.fullmatch(r"[a-z]{2,3}(-r[A-Z]{2})?", suffix) and suffix not in kept:
                fails.append(f"res/values-{suffix} is a translation folder but resConfigs "
                             f"does not list it - that language would never show")

# 2) both ABIs
m = re.search(r"abiFilters\s+([^\n]+)", g)
if not m:
    fails.append("abiFilters is gone - the APK would carry every ABI")
else:
    abis = set(re.findall(r"'([^']+)'", m.group(1)))
    for need in ("arm64-v8a", "armeabi-v7a"):
        if need not in abis:
            fails.append(f"{need} was dropped from abiFilters - phones using it cannot install")

# 3) sharing: the app must be able to RECEIVE a shared PDF
#    "Open with" (ACTION_VIEW) and the share sheet (ACTION_SEND) are separate filters in
#    Android. KavoPDF only had VIEW, so it never appeared in a share sheet at all.
MANIFEST = pathlib.Path("app/src/main/AndroidManifest.xml")
if not MANIFEST.exists():
    fails.append("AndroidManifest.xml is missing")
else:
    mf = MANIFEST.read_text(encoding="utf-8")
    if "android.intent.action.SEND" not in mf:
        fails.append("no ACTION_SEND filter - KavoPDF would not appear in any share sheet")
    else:
        i = mf.find("android.intent.action.SEND")
        block = mf[max(0, i - 200):i + 400]
        if "application/pdf" not in block:
            fails.append("the ACTION_SEND filter is not for application/pdf")
    if "android.intent.action.VIEW" not in mf:
        fails.append("the ACTION_VIEW filter is gone - tapping a PDF would stop opening it")

VIEWER = pathlib.Path("app/src/main/java/com/kavopdf/app/ViewerActivity.kt")
if not VIEWER.exists():
    fails.append("ViewerActivity.kt is missing")
else:
    v = VIEWER.read_text(encoding="utf-8")
    if "EXTRA_STREAM" not in v:
        fails.append("ViewerActivity does not read EXTRA_STREAM - a shared PDF would open "
                     "nothing even with the filter in place")
    if "clipData" not in v:
        fails.append("ViewerActivity does not fall back to clipData")
    if "intent?.data" in v and "incomingUri" not in v:
        fails.append("ViewerActivity went back to reading only intent.data")

# 4) the whole display, camera cutout included
#    Without windowLayoutInDisplayCutoutMode a phone with a notch treats the app as
#    "fit to screen" and keeps a black band along the edge, so every other app looked
#    full screen and this one did not.
THEMES = pathlib.Path("app/src/main/res/values/themes.xml")
if not THEMES.exists():
    fails.append("values/themes.xml is missing")
else:
    th = THEMES.read_text(encoding="utf-8")
    if "android:windowLayoutInDisplayCutoutMode" not in th:
        fails.append("the theme no longer asks for the display cutout - a notched phone "
                     "would letterbox the app again")
    elif "shortEdges" not in th:
        fails.append("windowLayoutInDisplayCutoutMode is not shortEdges")

UI = pathlib.Path("app/src/main/java/com/kavopdf/app/util/Ui.kt")
if not UI.exists():
    fails.append("util/Ui.kt is missing")
elif "applyCutoutInsets" not in UI.read_text(encoding="utf-8"):
    fails.append("applyCutoutInsets is gone - content would sit under the punch-hole in "
                 "landscape")

for name in ("PdfActivity", "MainActivity"):
    f = pathlib.Path(f"app/src/main/java/com/kavopdf/app/{name}.kt")
    if not f.exists():
        fails.append(f"{name}.kt is missing")
    elif "applyCutoutInsets" not in f.read_text(encoding="utf-8"):
        fails.append(f"{name} does not apply the cutout insets")

if fails:
    for f in fails:
        print("FAIL:", f)
    print("FAIL: the APK configuration is wrong")
    sys.exit(1)

print("PASS: locales are limited to English, no translation folder is orphaned, both ABIs ship")
