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

  Consistent and linear - and that reading was still only half the model. Those
  probes all used one face at 10-12 pt, where the ratio happens to be 0.95. Moving
  the size and the face as well (240/300/360/480/600 twips at 10 pt, the same
  probe at 14 pt and at 20 pt, and six faces at 10 pt) shows what the ratio is:

      rendered advance = (w:line / 240) * lineHeight(face, size)

  0.9583 at 10 pt Arial, 1.3417 at 14 pt, 1.9167 at 20 pt, and 1.049 / 1.170 /
  1.223 / 1.277 for Courier New / Times-Roman / Helvetica / Liberation Serif at
  10 pt. So w:line is a MULTIPLE of the face's line height, and no value of it
  places a baseline without knowing the substitute face. Do NOT write P / 0.95:
  that multiplier is one face at one size.

  What Google does honour exactly is w:before (20 pt came back 20 pt, 160 pt came
  back 160 pt), and with the box cut to a hairline the advance is
  before + 0.069 * size whichever face is substituted (0.069 em to 0.01 pt over
  8/10/14/20 pt Arial and 10 pt Courier New and Times New Roman). That is the
  construct to build on; see REMAINING-DEFECTS.md, class 20_within_10pt.

HOW TO USE IT
  When a class looks unfixable because "Docs does not support X", build the
  smallest document that isolates X, run it through Drive, and measure. Only then
  is it a limit. Record the measurement in the commit message either way - a
  failed experiment is still evidence, and it stops the next run repeating it.

  python3 calibrate.py <a.pdf> <b.pdf> ...     # compare pitches of several exports

  A probe worth rebuilding: one paragraph style, one face, 8 identical lines,
  zero margins, w:line = 240/300/360/480/600 with lineRule="exact". Then repeat
  it at another size, at another face, with w:line="1" plus a w:before, and with
  a mixed mark/run size. Those four runs are what the numbers above come from.
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
