#!/usr/bin/env python3
"""Fails the build if the launcher background is not the intended colour.

The adaptive icon takes its background from a colour resource, so a wrong value
is invisible in the file listing and only shows up on a phone. This decodes
resources.arsc out of the built APK and checks the value the launcher will draw.

Usage: verify-icon.py <path-to-apk>
"""
import sys, zipfile, struct

WANT = 0xFF15181D          # near-black, straight from values/launcher.xml
WRONG = 0xFF02A79F         # the old teal - must never come back

def main(path):
    with zipfile.ZipFile(path) as z:
        arsc = z.read("resources.arsc")
    le = lambda v: struct.pack("<I", v)
    want = arsc.count(le(WANT))
    wrong = arsc.count(le(WRONG))
    print(f"  resources.arsc        : {len(arsc)} bytes")
    print(f"  wanted #FF15181D      : {'present' if want else 'ABSENT'}  ({want})")
    print(f"  old teal #FF02A79F    : {'present <-- BAD' if wrong else 'absent'}  ({wrong})")
    ok = want > 0 and wrong == 0
    print()
    print("LAUNCHER BACKGROUND:", "PASS" if ok else "FAIL")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
