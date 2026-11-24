#!/usr/bin/env python3
"""Assemble /tmp/report.md from report.py's own body plus this run's prose, in one pass.

The generator owns every number; this only inserts prose between the header and `## Progress`.
Kept separate so the beats counter does not move between generation and validation.
"""
import re
import sys

s = open("tools/p2w-bench/REPORT.md").read()
m = re.search(r"```\n(# P2W Fixer.*?)\n```", s, re.S)
if not m:
    sys.exit("REPORT.md has no fenced body - report.py changed shape")
body = m.group(1)
lines = body.split("\n")
title = lines[0]
hdr = [l for l in lines[:4] if l.startswith("**24 Nov")][0]
rest = body[body.index("## Progress"):]
mine = open("/tmp/mine.md").read()
out = title + "\n\n" + hdr + "\n\n" + mine + rest
open("/tmp/report.md", "w").write(out)
print("wrote /tmp/report.md (%d bytes)" % len(out))
