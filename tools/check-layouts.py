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

print(f"layouts checked: {len(glob.glob('app/src/main/res/layout/*.xml'))}")
if bad:
    for f, why in bad:
        print(f"FAIL {f}: {why}")
    sys.exit(1)
print("PASS: every layout is well-formed and namespaced correctly")
