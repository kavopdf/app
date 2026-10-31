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

if fails:
    for f in fails:
        print("FAIL:", f)
    print("FAIL: the APK configuration is wrong")
    sys.exit(1)

print("PASS: locales are limited to English, no translation folder is orphaned, both ABIs ship")
