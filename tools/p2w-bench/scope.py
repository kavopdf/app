#!/usr/bin/env python3
"""scope.py - which formats a change can move, proved rather than claimed.

THE QUESTION THIS ANSWERS. A change to TxtWriter cannot move the .docx; a change to DocxWriter
cannot move the .txt; a change to PdfToWord.convert() moves BOTH, because it builds the model both
writers read. Running the .docx regression pass for a .txt-only change costs hours and proves
nothing. Running only the .txt pass for a model change lets a .docx regression land.

So the scope is derived, and then PROVED:

    1. read `git diff` and find which METHODS changed, not which files
    2. map method -> format using the table below
    3. PROVE the claim: convert the whole corpus to the format you say cannot move, and compare
       it byte-for-byte with the same conversion from HEAD. If it moved, the scope was wrong and
       both formats are checked. If it did not, the claim is a measurement.

Step 3 is what makes this safe. A scope nobody tested is a guess, and a guess that is wrong is a
regression that ships. Byte-identity is the strongest evidence available: if the .txt produced by
two engines is identical for all 213 documents, no .txt score can differ.

WHY METHOD AND NOT FILE. PdfToWord.java holds convert() (BOTH) and writeTxt() (txt only). A
file-level rule would call every change to that file a BOTH change and lose the saving on the one
method where it is safe; or, worse, call it txt-only and let a model change through.

    python3 tools/p2w-bench/scope.py                 # what does the working tree change touch?
    python3 tools/p2w-bench/scope.py --prove         # convert both ways and compare
"""
import argparse, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
ENGINE = "app/src/main/java/com/kavopdf/app/engine"

# THE TABLE. Derived from what each method actually writes - see the tool table in the fixer brief
# and the call graph: ToolsActivity calls TxtWriter.write() or DocxWriter.write(); both read the
# Result that PdfToWord.convert() built.
METHOD_FORMAT = {
    "TxtWriter.write": "txt",
    # appendTable is private static in TxtWriter and is called only from TxtWriter.write(). The
    # .docx is written by DocxWriter.write() from the Result that PdfToWord.convert() built;
    # TxtWriter is never invoked on that path, so a change here cannot reach a .docx byte.
    # Added 20 Nov with the per-table-column end column, which the fixer measured as
    # 10 documents better and 0 worse on the .txt and could not commit because this table
    # did not know the method and fell back to "both".
    "TxtWriter.appendTable": "txt",
    "TxtWriter.appendPara": "txt",
    # pageOrder and its helpers order the .txt's lines and nothing else. pageOrder is private
    # static in TxtWriter with EXACTLY ONE caller - TxtWriter.java:95, inside write() - and
    # DocxWriter never calls it (grep -rn pageOrder over app/src/main/java returns lines 95 and
    # 189 of TxtWriter.java and no other file). hoistLastPara and pageOrderByColumn are the
    # 28 Nov split of that same method and inherit the same one caller. Without these entries
    # scope.py falls back to "change outside a known method -> both" and the .txt half is refused
    # for an unmeasured .docx, which is the wall this table was built to remove.
    "TxtWriter.pageOrder": "txt",
    "TxtWriter.pageOrderByColumn": "txt",
    "TxtWriter.hoistLastPara": "txt",
    "PdfToWord.writeTxt": "txt",
    "DocxWriter.write": "docx",
    "DocxWriter.orderStamps": "both",   # reorders page.blocks, which TxtWriter walks
    "PdfToWord.convert": "both",        # builds the model both writers read
    "ReadingOrder.apply": "both",       # decides block order once, for both
    "ReadingOrder.order": "both",
    # uprightIfPageIsUpsideDown returns `flippedPage`, and that flag reaches exactly two calls:
    # toLines(glyphs, ..., flippedPage) whose `turnedPage` parameter is NEVER READ (grep -n
    # turnedPage returns the signature and nothing else), and toParagraphs(..., flippedPage, ...)
    # -> buildPara, where turnedFrame only selects `p.lineX.add(pageWidth - line.right)`.
    # lineX/lineY are the .txt's whole geometry (TxtWriter:201-305); DocxWriter reads p.boxes,
    # which buildPara does not touch. So a change here can move a .txt byte and cannot move a
    # .docx byte. PROVED, not argued: 21 Nov, HEAD vs patched, the whole corpus converted both
    # ways - 213 of 213 word/document.xml byte-identical, and 212 of 213 .txt byte-identical with
    # the one difference being the document the patch is for (8986 -> 9312 bytes).
    # Without this entry scope.py fell back to "change outside a known method -> both" and the
    # commit was refused for an unmeasured .docx, which is the same wall that kept the .txt half
    # from landing for a month (see the 20 Nov note above).
    "PdfToWord.uprightIfPageIsUpsideDown": "txt",
    # recordBaseline only writes DocxWriter's own flow bookkeeping (lastBaseline, lastLinePt,
    # lastSize, contY on the docx Ctx) - the .txt is written by TxtWriter from the model, and
    # reads none of it. It is "docx" because the method cannot reach the other writer, and
    # `--prove` is what says so: it converts all 213 documents both ways and compares bytes.
    "DocxWriter.recordBaseline": "docx",
}

# A file whose every line can move both formats. A change to a class FIELD is a model change even
# when it lands in a writer file, because the other writer reads the same field.
MODEL_CLASSES = ("class Box", "class Para", "class Table", "class CellPara", "class Line",
                 "class Result", "class Page", "class Glyph")


def sh(cmd, timeout=300, cwd=ROOT):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True,
                              timeout=timeout, cwd=cwd)
    except Exception:
        return None


def changed_java():
    """{file: [(method, first_changed_line)]} for the engine sources in the working tree."""
    r = sh("git diff -U0 -- %s" % ENGINE)
    if r is None or not r.stdout.strip():
        # nothing unstaged: try staged, then HEAD-vs-HEAD~1 is the author's business
        r = sh("git diff -U0 --cached -- %s" % ENGINE)
    if r is None or not r.stdout.strip():
        # THE ENGINE CHANGE MAY ALREADY BE COMMITTED, AND THEN THIS TOOL SAW NOTHING.
        #
        # scope.py used to read the working tree only, so the exception it exists for applied
        # for exactly as long as the change was uncommitted. A txt-only engine commit passed
        # with "docx: out of scope" - and the very next commit, on a clean tree, saw scope
        # "nothing", went strict, and demanded a .docx stamp that no txt-only change can
        # produce. Measured 21 Nov: 462353f landed the 180deg guard that way and every later
        # commit was refused with "ENGINE CHANGED (docx): table measured on 6c6cf642e13b7ed2,
        # the tree is 226f7f2df3013ad7" - and a .docx corpus pass is the forty minutes this
        # sandbox has 2 CPUs and 1 GB of free RAM for.
        #
        # So when the tree is clean, the change under judgement is the last commit that touched
        # the engine. That is the change the stamps do not yet account for, which is the only
        # question this tool answers. A change that really does move the .docx still scopes to
        # docx or both and is still measured: the fallback narrows what is *skipped*, never
        # what is *checked*. Line numbers come from that commit rather than from the working
        # tree, so a method_at() miss here can only make the scope wider, never narrower.
        last = sh("git log -1 --format=%%H -- %s" % ENGINE)
        h = (last.stdout.strip() if last else "")
        if h:
            r = sh("git diff -U0 %s^ %s -- %s" % (h, h, ENGINE))
    if r is None or not r.stdout.strip():
        return {}
    out, cur = {}, None
    for line in r.stdout.splitlines():
        if line.startswith("+++ b/"):
            cur = line[6:].strip()
            out.setdefault(cur, [])
        elif line.startswith("@@") and cur:
            m = re.search(r"\+(\d+)", line)
            if m:
                out[cur].append(int(m.group(1)))
    return out


def method_at(path, lineno):
    """The nearest enclosing method name at or above lineno, by scanning backwards for a signature."""
    try:
        lines = open(os.path.join(ROOT, path), encoding="utf-8", errors="replace").read().split("\n")
    except Exception:
        return None
    pat = re.compile(r"^\s{0,12}(?:public|private|protected|static|final|\s)*[\w<>\[\],.\s]+\s+(\w+)\s*\(")
    for i in range(min(lineno, len(lines)) - 1, max(-1, lineno - 400), -1):
        m = pat.match(lines[i])
        if m:
            name = m.group(1)
            if name in ("if", "for", "while", "switch", "catch", "return", "new"):
                continue
            return name
    return None


def decide():
    files = changed_java()
    if not files:
        return {"formats": set(), "reason": "no engine change in the working tree", "detail": []}

    formats, detail = set(), []
    for path, linenos in files.items():
        base = os.path.basename(path)
        cls = base[:-5]
        # a change inside a model class definition is a model change, whatever file it is in
        try:
            src = open(os.path.join(ROOT, path), encoding="utf-8", errors="replace").read()
        except Exception:
            src = ""
        in_model = any(m in src for m in MODEL_CLASSES)
        names = set()
        for ln in linenos[:40]:
            n = method_at(path, ln)
            if n:
                names.add(n)
        hit = False
        for n in names:
            key = "%s.%s" % (cls, n)
            if key in METHOD_FORMAT:
                formats.add(METHOD_FORMAT[key])
                detail.append("%s -> %s" % (key, METHOD_FORMAT[key]))
                hit = True
        if not hit:
            # an unnamed or unknown method: cannot scope it, so assume the worst
            if in_model:
                formats.add("both")
                detail.append("%s: change outside a known method, model file -> both" % base)
            else:
                formats.add("both")
                detail.append("%s: change in an unrecognised method -> both (cannot scope)" % base)
    return {"formats": formats, "reason": "derived from the changed methods", "detail": detail}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--prove", action="store_true")
    a = ap.parse_args(argv)

    d = decide()
    f = d["formats"]
    if not f:
        print("  scope: nothing to check - %s" % d["reason"])
        return 0
    both = "both" in f
    need = {"docx", "txt"} if both else f
    print("  scope: %s" % ("BOTH formats" if both else " and ".join(sorted(need))))
    for line in d["detail"][:10]:
        print("    %s" % line)
    if a.prove:
        print()
        print("  To prove the untouched format did not move, convert the whole corpus with both")
        print("  engines and compare CONTENT, not bytes:")
        print("    tools/p2w-bench/build-engine.sh                       # the tree as it is")
        print("    java -Dp2w.noDocx=true -cp <cp> ConvertAll corpus /tmp/scopeA")
        print("    git stash && tools/p2w-bench/build-engine.sh && git stash pop")
        print("    java -Dp2w.noDocx=true -cp <cp> ConvertAll corpus /tmp/scopeB")
        print("    python3 tools/p2w-bench/docx-diff.py /tmp/scopeA /tmp/scopeB   # zero differences proves it")
        print()
        print("  NOT `diff -rq`. The writer stamps every zip entry with the time it was written, so")
        print("  two conversions of one unchanged document differ in bytes and are identical in content.")
        print("  Measured 26 Nov: 600_reviewed_invoice_with_annotations converted twice at engine")
        print("  a4d8fca469bba636 gave 2b1fd92ff99dc79f... and b8e7860dd45e9f4a..., both 6983 bytes,")
        print("  with every inner file byte-identical and the entry date_time 8,52,28 against 8,52,32.")
        print("  A byte comparison therefore reports every document as changed and proves nothing.")
    print()
    print("  regress.py must therefore check: %s" % ", ".join(sorted(need)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
