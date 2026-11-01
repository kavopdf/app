#!/usr/bin/env python3
"""Fails the build if a layout is malformed.

Two things this catches, both of which would break the app silently until someone
opened the screen:
  * a layout that does not parse
  * a layout whose attributes lost their namespace prefix (e.g. written back as
    ns0:id instead of android:id) - which happens when a layout is rewritten by a
    generic XML tool rather than edited as text.
"""
import glob
import re
import sys
import xml.etree.ElementTree as ET

bad = []
for f in sorted(glob.glob("app/src/main/res/layout/*.xml")):
    s = open(f, encoding="utf-8").read()
    m = re.search(r'\bns\d+:', s)
    if m:
        bad.append((f, f"attribute written as {m.group(0)}... instead of android:/app:"))
        continue
    try:
        ET.parse(f)
    except Exception as e:
        bad.append((f, str(e)))
    # an id must be declared with the android namespace
    if 'android:id=' not in s and '@+id/' in s:
        bad.append((f, "ids present but no android:id= attributes"))

# Page arrows sit on the page area, which is dark in BOTH themes (viewer_bg is #2B2D33
# by day and #0B0C0F by night). Tinting them with ?attr/colorOnPrimary looked right
# because that colour is chosen to sit on the toolbar, but the Amber theme's
# colorOnPrimary is #FF241A00 - near black on near black, which is why the Redact
# screen's arrows were invisible. On this background they must be white.
DARK_BG_SCREENS = {"activity_redact.xml": "@color/white"}
for name, want in DARK_BG_SCREENS.items():
    f = f"app/src/main/res/layout/{name}"
    try:
        s = open(f, encoding="utf-8").read()
    except FileNotFoundError:
        bad.append((f, "missing"))
        continue
    for arrow in ("prevPage", "nextPage"):
        m = re.search(r'android:id="@\+id/' + arrow + r'"[\s\S]{0,600}?app:tint="([^"]+)"', s)
        if not m:
            bad.append((f, f"{arrow} has no app:tint"))
        elif m.group(1) != want:
            bad.append((f, f"{arrow} is tinted {m.group(1)}, must be {want} on the dark "
                           "page area"))

# and no page arrow anywhere may use a colour meant for the toolbar
for f in sorted(glob.glob("app/src/main/res/layout/*.xml")):
    s = open(f, encoding="utf-8").read()
    for arrow in ("prevPage", "nextPage"):
        m = re.search(r'android:id="@\+id/' + arrow + r'"[\s\S]{0,600}?app:tint="([^"]+)"', s)
        if m and "colorOnPrimary" in m.group(1):
            bad.append((f, f"{arrow} is tinted with colorOnPrimary - that colour belongs "
                           "on the toolbar, not on the page area"))

print(f"layouts checked: {len(glob.glob('app/src/main/res/layout/*.xml'))}")
if bad:
    for f, why in bad:
        print(f"FAIL {f}: {why}")
    sys.exit(1)
print("PASS: every layout is well-formed and namespaced correctly")
