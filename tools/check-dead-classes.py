#!/usr/bin/env python3
"""Nothing ships in the APK that the APK does not use.

WHY
    Everything under app/src/main is compiled into the APK. A class nobody calls is
    weight on every phone and, worse, a claim: a comment that says "called from every
    screen" on a function nothing calls makes a reader believe the work is done.

WHAT COUNTS AS A REFERENCE
    A file is used if ANY name it declares appears in another .java or .kt file, in a
    layout or other .xml, in AndroidManifest.xml, or in a proguard rule.

    That "any name" is the whole point. A Kotlin file called Display.kt can declare a
    top-level function called useHighestRefreshRate, and the caller imports the FUNCTION,
    not the file. Checking only the file name reports that file dead while it is called
    from two screens. This guard made exactly that mistake on its first run and it got
    app/src/main/java/com/kavopdf/app/ui/ViewMapping.kt deleted, whose drawnImageRect()
    is called from CropView.kt:63 and RedactView.kt:70. Both names are checked now.

WHAT IS NOT REPORTED
    Anything named in a proguard keep rule is skipped: the build is being told to keep
    it, so it is reachable by a route this script cannot see.
    R and BuildConfig are generated, not written.

EXIT
    0  every file is referenced somewhere
    1  at least one file is referenced nowhere - do not ship it
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


def declared_names(path, body):
    """Every name this file declares that another file could refer to."""
    names = set()
    names.add(os.path.basename(path).rsplit(".", 1)[0])
    if path.endswith(".kt"):
        for m in re.finditer(
                r"^\s*(?:@\w+\s+)*(?:(?:internal|private|public|protected|open|abstract"
                r"|sealed|data|enum|annotation|value|inline|suspend|override)\s+)*"
                r"(?:class|object|interface|fun|val|var)\s+(?:<[^>]*>\s*)?"
                r"(?:[\w.]+\.)?(\w+)", body, re.M):
            names.add(m.group(1))
        for m in re.finditer(r"\bfun\s+[\w.]+\.(\w+)\s*\(", body):
            names.add(m.group(1))
    else:
        for m in re.finditer(r"\b(?:class|interface|enum)\s+(\w+)", body):
            names.add(m.group(1))
        for m in re.finditer(r"\bstatic\s+[\w<>\[\], ]+\s+(\w+)\s*\(", body):
            names.add(m.group(1))
    return {n for n in names if n and n not in SKIP and len(n) > 2}


def main():
    if not os.path.isdir(ROOT):
        print("no %s - run this from the repo root" % ROOT)
        return 2

    sources, xml = {}, {}
    for base, _dirs, files in os.walk(ROOT):
        for name in files:
            path = os.path.join(base, name)
            if name.endswith((".java", ".kt")):
                sources[path] = read(path)
            elif name.endswith(".xml"):
                xml[path] = read(path)

    kept = ""
    for candidate in ("app/proguard-rules.pro", "proguard-rules.pro"):
        if os.path.exists(candidate):
            kept += read(candidate)

    markup = "\n".join(xml.values())

    dead = []
    for path, body in sources.items():
        names = declared_names(path, body)
        others = "\n".join(v for k, v in sources.items() if k != path)
        haystack = others + "\n" + markup + "\n" + kept
        if any(re.search(r"\b" + re.escape(n) + r"\b", haystack) for n in names):
            continue
        dead.append((path, sorted(names)))

    if not dead:
        print("PASS: all %d files under %s declare something another file refers to"
              % (len(sources), ROOT))
        return 0

    print("FAIL: %d file(s) under %s declare nothing that anything refers to:"
          % (len(dead), ROOT))
    for path, names in sorted(dead):
        print("   " + path)
        print("      declares: " + ", ".join(names[:8]))
    print("")
    print("Each one is compiled into every APK and never used. Either wire it up, or")
    print("delete it. If it is reached by reflection, name it in a proguard keep rule so")
    print("this check can see that it is deliberate.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
