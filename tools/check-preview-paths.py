#!/usr/bin/env python3
"""Fails the build if a page preview can go back to showing nothing and never saying so.

The symptom this pins down: open a PDF, and the page area sits at its background colour -
near pure black in dark theme - until the screen is touched. Two separate causes:

  1. the render was wrapped in runCatching { ... }.getOrNull(), so a failure became a
     silent null, nothing was drawn, and nothing retried. PageRenderer.render never
     returns null; it throws. Every preview screen now goes through renderOrRetry and
     records a failure instead of hiding it.
  2. ZoomableImageView.apply() assigned the PREVIOUS matrix when the view had no size yet,
     which drew the new page at the old page's scale, and nothing corrected it.
"""
import pathlib
import re
import sys

K = pathlib.Path("app/src/main/java/com/kavopdf/app")
# the UI classes live one folder down; the screens sit at the top
WHERE = {
    "ViewerAdapter": "ui/ViewerAdapter.kt",
    "PageRenderer": "ui/PageRenderer.kt",
    "ZoomableImageView": "ui/ZoomableImageView.kt",
    "AnnotateActivity": "AnnotateActivity.kt",
    "CropActivity": "CropActivity.kt",
    "LinksActivity": "LinksActivity.kt",
    "RedactActivity": "RedactActivity.kt",
    "ViewerActivity": "ViewerActivity.kt",
}
PREVIEWS = ["ViewerAdapter", "AnnotateActivity", "CropActivity", "LinksActivity", "RedactActivity"]


def path_of(name):
    return K / WHERE[name]


fails = []
for name in PREVIEWS + ["PageRenderer", "ZoomableImageView", "ViewerActivity"]:
    if not path_of(name).exists():
        print(f"FAIL: {WHERE[name]} is missing")
        sys.exit(1)

# 1) every preview goes through the retrying render, and never swallows a null
for name in PREVIEWS:
    body = path_of(name).read_text(encoding="utf-8")
    if "renderOrRetry" not in body:
        fails.append(f"{name} does not use renderOrRetry - a failed render would be silent")
    if re.search(r"runCatching\s*\{[^}]*\.render\(", body):
        fails.append(f"{name} still wraps render() in runCatching - the failure would vanish")
    if "Page render failed" not in body:
        fails.append(f"{name} no longer records a failed render")

# 2) the helper must actually try twice
r = path_of("PageRenderer").read_text(encoding="utf-8")
m = re.search(r"fun renderOrRetry\([\s\S]{0,400}?\n    \}", r)
if not m:
    fails.append("PageRenderer.renderOrRetry is gone")
elif "repeat(2)" not in m.group(0):
    fails.append("renderOrRetry no longer retries")

# 3) no stale matrix, and a fit is requested once the size is known
z = path_of("ZoomableImageView").read_text(encoding="utf-8")
if "pendingFit" not in z:
    fails.append("ZoomableImageView lost pendingFit - a page drawn before layout would keep "
                 "the previous page's matrix")
apply_body = re.search(r"private fun apply\(\)[\s\S]*?\n    \}", z)
if apply_body and "imageMatrix = m" in apply_body.group(0).split("pendingFit = false")[0]:
    fails.append("apply() still assigns the stale matrix when the view has no size")
if "if (pendingFit || zoom <= 1.01f) reset()" not in z:
    fails.append("onSizeChanged no longer honours pendingFit")

# 4) the viewer must not fade a page in from a low alpha
v = path_of("ViewerAdapter").read_text(encoding="utf-8")
if "alpha = 0.3f" in v:
    fails.append("ViewerAdapter fades the page in from 0.3 alpha again - an interrupted "
                 "animator leaves the page nearly invisible")
if "renderedWidth[position] = baseWidth" not in v:
    fails.append("ViewerAdapter does not record the bind width, so every tap re-renders "
                 "the whole page")

# 5) the pager's item animation stays off (scroll stutter)
a = path_of("ViewerActivity").read_text(encoding="utf-8")
if "itemAnimator = null" not in a:
    fails.append("the pager's item animation is back on - it stutters a page rebind mid-swipe")

if fails:
    for f in fails:
        print("FAIL:", f)
    print("FAIL: a page preview can go blank and silent again")
    sys.exit(1)

print("PASS: every preview retries and reports, no stale matrix, no fade from near zero, "
      "no double render per tap")
