#!/usr/bin/env python3
"""Fails the build if a file is named something other than what it holds.

Ui.kt held one thing - class Busy - long after the rest of it moved out, so the name
pointed at nothing. That is how a file ends up being opened, misread and edited by
mistake. This pins the convention down:

  * a Kotlin/Java file must be named after one of the classes it declares
  * a resource file must be lowercase snake_case
  * no path may carry an old project name
"""
import glob
import os
import re
import sys

OLD = re.compile(r"(vk0627773|vk062777|novapdf|pdfnova|pdfsmith|vellara|codexa)", re.I)
fails = []

# 1) code files named after a class they declare
for f in sorted(glob.glob("app/src/main/java/**/*.kt", recursive=True)):
    base = os.path.basename(f)[:-3]
    s = open(f, encoding="utf-8", errors="replace").read()
    names = set(re.findall(r"^(?:@\w+(?:\([^)]*\))?\s*)*(?:public |internal |private |abstract |open |final |sealed |data |enum |annotation )*(?:class|object|interface)\s+(\w+)", s, re.M))
    if names and base not in names:
        fails.append(f"{f}: holds {sorted(names)} but the file is called {base}")

for f in sorted(glob.glob("app/src/main/java/**/*.java", recursive=True)):
    base = os.path.basename(f)[:-5]
    s = open(f, encoding="utf-8", errors="replace").read()
    names = set(re.findall(r"^\s*(?:public\s+|final\s+|abstract\s+)*(?:class|interface|enum)\s+(\w+)", s, re.M))
    if names and base not in names:
        fails.append(f"{f}: holds {sorted(names)} but the file is called {base}")

# 2) resource file names
for f in sorted(glob.glob("app/src/main/res/**/*", recursive=True)):
    if os.path.isdir(f):
        continue
    name = os.path.basename(f)
    if not re.fullmatch(r"[a-z0-9_]+(\.[a-z0-9]+)?", name):
        fails.append(f"{f}: resource file names must be lowercase snake_case")

# 3) no old project names in any path
for root in ("app", "tools", "docs", ".github"):
    for dirpath, dirnames, filenames in os.walk(root):
        for n in dirnames + filenames:
            rel = os.path.join(dirpath, n)
            if OLD.search(rel):
                fails.append(f"{rel}: carries an old project name")

if fails:
    for x in fails:
        print("FAIL:", x)
    sys.exit(1)
print("PASS: every file is named after what it holds, resources are snake_case, no old names")
