#!/usr/bin/env python3
"""anchors.py - how much of the corpus's text is inside an anchored DrawingML text box.

WHY THIS EXISTS.

The 24 Nov root-cause pass named one construct as the largest engine defect anyone had found:
`DocxWriter` routes body text into a `<wps:txbx>` inside a `<wp:anchor>`, and Google Docs
rasterises every anchored box on import, so that text leaves the exported text layer. The
charter's summary put it at ~166 document-failures across five checks.

Nobody had measured the population. The engine has a census (`-Dp2w.census=<file>`) that counts
WRITER CALLS, but that is not the same question: a stamp also writes a text box, and a page that
is merely in `positioned` mode writes boxes the census files under a different counter. This tool
measures the OUTPUT - the characters that are actually inside a `w:txbxContent` in the `.docx` -
which is the population that can lose text in Google, whoever wrote it.

Measured on engine 981ff1fa35e2cf67, 25 Nov: 47 of 213 documents carry boxed text, and those
boxes hold 27,501 of 463,228 characters (5.94 % of the corpus). The gap threshold itself
(`GAP_CAP_TW`, the `anchorRule` counter) writes 13 boxes in the whole corpus.

USAGE

    python3 tools/p2w-bench/anchors.py <docx-dir>            # per-document table, worst first
    python3 tools/p2w-bench/anchors.py <dirA> --vs <dirB>    # A/B: what a change moved
    python3 tools/p2w-bench/anchors.py <dir> --json out.json # machine-readable
    python3 tools/p2w-bench/anchors.py <dir> --min-chars 1   # only documents with boxed text

The A/B mode compares `word/document.xml`, never the `.docx` bytes: the archive is not
byte-deterministic across runs (zip timestamps), so a byte diff reports every document as changed
even when the engine wrote the same document. Measured 25 Nov: 213 of 213 differ at the byte
level and 0 of 213 differ in `document.xml`.

Exit codes: 0 read everything, 1 a document could not be read.
"""
import argparse
import hashlib
import json
import os
import re
import sys
import zipfile

TXBX = re.compile(r"<w:txbxContent>(.*?)</w:txbxContent>", re.S)
WT = re.compile(r"<w:t(?:\s[^>]*)?>(.*?)</w:t>", re.S)


def _text(xml):
    return "".join(WT.findall(xml))


def measure(docx_dir):
    """{name: {chars, boxed, xml_sha}} for every .docx in the directory."""
    out, errors = {}, []
    for f in sorted(os.listdir(docx_dir)):
        if not f.endswith(".docx"):
            continue
        path = os.path.join(docx_dir, f)
        try:
            xml = zipfile.ZipFile(path).read("word/document.xml").decode("utf-8", "replace")
        except Exception as e:                       # a half-written or odd archive
            errors.append((f, str(e)))
            continue
        boxed = "".join(TXBX.findall(xml))
        out[f[:-5]] = {
            "chars": len(_text(xml)),
            "boxed": len(_text(boxed)),
            "xml_sha": hashlib.sha256(xml.encode("utf-8")).hexdigest(),
        }
    return out, errors


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("dir")
    ap.add_argument("--vs", metavar="DIR", help="compare against a second directory")
    ap.add_argument("--json", metavar="FILE", help="write the measurement here")
    ap.add_argument("--min-chars", type=int, default=0,
                    help="only list documents with at least this many boxed characters")
    a = ap.parse_args(argv)

    A, ea = measure(a.dir)
    if not A:
        print("no .docx in %s" % a.dir)
        return 1
    tot = sum(v["chars"] for v in A.values())
    box = sum(v["boxed"] for v in A.values())
    withbox = [k for k, v in A.items() if v["boxed"] > 0]
    print("documents      : %d" % len(A))
    print("characters     : %d" % tot)
    print("boxed          : %d  (%.2f %%)" % (box, 100.0 * box / max(1, tot)))
    print("documents with any boxed text : %d" % len(withbox))

    rows = [(k, v) for k, v in A.items() if v["boxed"] >= max(1, a.min_chars)]
    if rows:
        print()
        print("%-52s %8s %8s %7s" % ("document", "chars", "boxed", "share"))
        for k, v in sorted(rows, key=lambda r: -r[1]["boxed"]):
            print("%-52s %8d %8d %6.1f%%"
                  % (k[:52], v["chars"], v["boxed"], 100.0 * v["boxed"] / max(1, v["chars"])))

    result = {"dir": a.dir, "documents": len(A), "chars": tot, "boxed": box,
              "docs_with_boxed": len(withbox), "errors": ea, "docs": A}

    if a.vs:
        B, eb = measure(a.vs)
        changed = [k for k in A if B.get(k, {}).get("xml_sha") != A[k]["xml_sha"]]
        moved = [(k, A[k]["boxed"], B[k]["boxed"], A[k]["chars"], B[k]["chars"])
                 for k in A if k in B and (A[k]["boxed"] != B[k]["boxed"]
                                           or A[k]["chars"] != B[k]["chars"])]
        tb = sum(v["boxed"] for v in B.values())
        tc = sum(v["chars"] for v in B.values())
        print()
        print("A/B against %s" % a.vs)
        print("  document.xml changed : %d of %d" % (len(changed), len(A)))
        print("  boxed characters     : %d -> %d (%+d)" % (box, tb, tb - box))
        print("  total characters     : %d -> %d (%+d)" % (tot, tc, tc - tot))
        if moved:
            print()
            print("  %-52s %7s %7s %9s %9s" % ("document", "boxedA", "boxedB", "charsA", "charsB"))
            for k, b1, b2, c1, c2 in sorted(moved, key=lambda r: -(r[1] - r[2])):
                print("  %-52s %7d %7d %9d %9d" % (k[:52], b1, b2, c1, c2))
        result["vs"] = {"dir": a.vs, "xml_changed": len(changed),
                        "boxed": tb, "chars": tc, "moved": moved}

    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=1, sort_keys=True)
        print()
        print("written to %s" % a.json)

    return 1 if ea else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
