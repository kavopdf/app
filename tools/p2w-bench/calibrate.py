#!/usr/bin/env python3
"""
calibrate.py - measure what Google Docs actually does, before blaming it.

WHY THIS EXISTS
  On 10 Nov the class fixer closed 20_within_10pt - the largest class in the
  corpus, 36 of 41 measured documents - as CLOSED-UNFIXABLE with the reason
  "Google Docs has no exact line spacing". That was not true. Three documents
  with w:line set to 240, 360 and 480 twips came back from Drive with pitches of
  11.3, 17.1 and 22.8 pt: proportional, monotonic, and honoured. The class was
  closed on an assumption, and 36 documents were written off with it.

  A renderer limit is a real thing and worth recording. An assumption that a
  renderer has a limit is not. The difference is one experiment, and this file
  is that experiment.

WHAT IT FOUND
  Google Docs renders w:line at about 95 % of the value asked for:

      asked 12 pt -> 11.3 measured   ratio 0.942
      asked 18 pt -> 17.1 measured   ratio 0.950
      asked 24 pt -> 22.8 measured   ratio 0.950

  Consistent and linear. So exact line spacing is available, just scaled, and an
  engine that wants a pitch of P should write P / 0.95. That is a multiplier, not
  a redesign, and it is the single largest position defect in the corpus.

HOW TO USE IT
  When a class looks unfixable because "Docs does not support X", build the
  smallest document that isolates X, run it through Drive, and measure. Only then
  is it a limit. Record the measurement in the commit message either way - a
  failed experiment is still evidence, and it stops the next run repeating it.

  python3 calibrate.py <a.pdf> <b.pdf> ...     # compare pitches of several exports
"""
import sys
import warnings

warnings.filterwarnings("ignore")

try:
    import fitz
except ImportError:
    print("PyMuPDF not installed", file=sys.stderr)
    sys.exit(2)


def pitches(path):
    """Baseline-to-baseline gaps on page 1, and the distinct sizes seen."""
    doc = fitz.open(path)
    page = doc[0]
    ys, sizes = [], set()
    for block in page.get_text("dict")["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                if not span.get("text", "").strip():
                    continue
                ys.append(round(span["bbox"][1], 2))
                sizes.add(round(span["size"], 1))
    ys = sorted(set(ys))
    gaps = [round(b - a, 2) for a, b in zip(ys, ys[1:]) if 1 < b - a < 200]
    gaps.sort()
    doc.close()
    return (gaps[len(gaps) // 2] if gaps else 0.0), len(ys), sorted(sizes)


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    for path in argv[1:]:
        try:
            pitch, lines, sizes = pitches(path)
            print("%-46s pitch %6.2f pt   lines %3d   sizes %s" % (
                path.split("/")[-1][:46], pitch, lines, sizes))
        except Exception as exc:
            print("%-46s could not read: %s" % (path.split("/")[-1][:46], exc))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
