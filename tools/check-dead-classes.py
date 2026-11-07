#!/usr/bin/env python3
"""Nothing ships in the APK that the APK does not use.

WHY
    Everything under app/src/main is compiled into the APK. A class nobody calls is
    weight on every phone and, worse, a claim: Display.kt's own comment said "Called
    from every screen" and nothing called it, so a reader believed the work was done.
    ViewMapping.kt had no reference in any java, kotlin, layout or manifest file and
    shipped in every build.

WHAT COUNTS AS A REFERENCE
    A class is used if its name appears in another .java or .kt file, in a layout or
    other .xml, in AndroidManifest.xml, or in a proguard rule. All four are checked,
    because a custom View is named only in a layout and an Activity only in the
    manifest - searching the code alone reports both as dead.

WHAT IS NOT REPORTED
    Anything named in a proguard keep rule is skipped: the build is being told to keep
    it, so it is reachable by a route this script cannot see.
    R and BuildConfig are generated, not written.

EXIT
    0  every class is referenced somewhere
    1  at least one class is referenced nowhere - do not ship it
"""

import os
import re
import sys

ROOT = "app/src/main"
SKIP = {"R", "BuildConfig"}


def read(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def main():
    if not os.path.isdir(ROOT):
        print("no %s - run this from the repo root" % ROOT)
        return 2

    sources = {}
    xml = {}
    for base, _dirs, files in os.walk(ROOT):
        for name in files:
            path = os.path.join(base, name)
            if name.endswith((".java", ".kt")):
                sources[path] = read(path)
            elif name.endswith(".xml"):
                xml[path] = read(path)

    # proguard keeps: anything named there is reachable by a route we cannot see
    kept = ""
    for candidate in ("app/proguard-rules.pro", "proguard-rules.pro"):
        if os.path.exists(candidate):
            kept += read(candidate)

    code = "\n".join(sources.values())
    markup = "\n".join(xml.values())

    dead = []
    for path, body in sources.items():
        name = os.path.basename(path).rsplit(".", 1)[0]
        if name in SKIP:
            continue
        pattern = re.compile(r"\b" + re.escape(name) + r"\b")
        others = "\n".join(v for k, v in sources.items() if k != path)
        if pattern.search(others) or pattern.search(markup) or pattern.search(kept):
            continue
        dead.append(path)

    if not dead:
        print("PASS: all %d classes under %s are referenced somewhere" % (len(sources), ROOT))
        return 0

    print("FAIL: %d class(es) under %s are referenced by nothing and would ship:" %
          (len(dead), ROOT))
    for path in sorted(dead):
        print("   " + path)
    print("")
    print("Each one is compiled into every APK and never called. Either wire it up, or")
    print("delete it. If it is reached by reflection, name it in a proguard keep rule so")
    print("this check can see that it is deliberate.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
