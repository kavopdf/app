#!/usr/bin/env python3
"""Which documents actually need a Google measurement, and which LibreOffice already answers.

A Google restamp is ~54 minutes because every document is uploaded. LibreOffice is local, all 213, and
about two minutes. The question is what LO can settle on its own.

LO is the PERMISSIVE renderer on 33 of the 34 checks: it passes 125 of 191 where Google passes 36. So
a document LO fails is failing something Google also fails, and it cannot be clean - no upload needed
to know that. Only the documents LO passes need the strict renderer to decide.

MEASURED on the committed stores: 66 of 191 LO-fail (35% that need no Google), 125 LO-pass.

ONE EXCEPTION, and it is why this is not a blanket rule. The capability matrix says LibreOffice is
STRICTER on exactly one check, 14_filled_shapes - so an LO failure there proves nothing about Google.
A document whose only LO failure is that check still needs the upload.

  --need    the documents that need a Google verdict, one per line
  --settled the documents LO already settles, one per line
  --status  the counts and the saving

Nothing is written and nothing is skipped automatically: this reports, and the run decides.
"""
import json
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
GV = os.path.join(ROOT, "benchmarks", "gverify")
LO = os.path.join(ROOT, "benchmarks", "gverify-lo")

# The one check where LibreOffice is stricter than Google, so an LO failure proves nothing.
LO_STRICTER = {"14_filled_shapes"}


def _failed(path):
    try:
        d = json.load(open(path, encoding="utf-8"))
    except Exception:
        return None
    if d.get("status") == "page_count_refused":
        return None
    return set(d.get("failed") or [])


def split():
    lo = {}
    for f in glob.glob(os.path.join(LO, "*.json")):
        r = _failed(f)
        if r is not None:
            lo[os.path.basename(f)[:-5]] = r
    google = set()
    for f in glob.glob(os.path.join(GV, "*.json")):
        try:
            if json.load(open(f, encoding="utf-8")).get("status") != "page_count_refused":
                google.add(os.path.basename(f)[:-5])
        except Exception:
            pass
    need, settled = [], []
    for name in sorted(google):
        if name not in lo:
            need.append(name)                     # no LO render: nothing settles it
            continue
        decisive = lo[name] - LO_STRICTER
        (settled if decisive else need).append(name)
    return need, settled, len(google), len(lo)


def main(argv):
    need, settled, n_g, n_lo = split()
    if "--need" in argv:
        for n in need:
            print(n)
        return 0
    if "--settled" in argv:
        for n in settled:
            print(n)
        return 0
    print("  scored in Google : %d" % n_g)
    print("  rendered in LO   : %d" % n_lo)
    print("  LO settles       : %d  - LO fails a check Google also fails, so not clean" % len(settled))
    print("  need Google      : %d" % len(need))
    if n_g:
        print("  saving           : %.0f%% of the uploads" % (100.0 * len(settled) / n_g))
    print("  exception        : a document whose only LO failure is %s still needs Google"
          % ", ".join(sorted(LO_STRICTER)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
