# The .txt half

Everything here belongs to the .txt output. Nothing in the .docx path reads these files, and nothing
in the .docx path writes them, so a txt run cannot move a docx number by accident and a docx run
cannot hide behind a txt score.

    RANKING-TXT.csv      one row per document: applicable, passed, failed, abstained, failed_ids
    STATE-TXT.json       the txt state - scored, clean, failing, and the docx hash at the last gate
    HISTORY-TXT.jsonl    one line per gate run

## What the two formats actually share

**Three files, three jobs:**

    PdfToWord.java    9677 lines   MODEL + TXT - convert() builds the model both writers read, and
                                                writeTxt() writes the .txt itself (line 9674)
    DocxWriter.java   7219 lines   DOCX        - write() writes the .docx (line 701)
    TxtWriter.java     568 lines   TXT         - write() writes the .txt (line 59)

  PdfToWord does NOT write a .docx: it has no w:document, no word/document.xml, no ZipOutputStream,
  no ZipEntry, and its DocxWriter references are comments or model types (DocxWriter.Shape,
  DocxWriter.Picture), never a call to DocxWriter.write().

The pipeline, from ReadingOrder.java:24-30:

    Result r = PdfToWord.convert(pdf, "", null);   // the model
    PdfToWord.classifyHeadings(r);
    ReadingOrder.apply(r);                          // one order, for every consumer
    DocxWriter.write(r, docx);                      // reads it        -> .docx
    PdfToWord.writeTxt(r, txt);                     // reads the same  -> .txt

`PdfToWord.writeTxt()` is the txt's entry point (line 9674); `TxtWriter.write()` is what it calls.
ToolsActivity:600 calls `TxtWriter.write()` directly for the same result.

**So `PdfToWord` feeds both outputs and writes one of them.** It builds the model the .docx is made
from, and it writes the .txt. The .docx itself is written by `DocxWriter.write()`; the .txt by
`TxtWriter.write()`, which `PdfToWord.writeTxt()` calls.

What that means for a change:

    a change in DocxWriter.java   moves the .docx only
    a change in TxtWriter.java    moves the .txt only
    a change in PdfToWord.java    moves BOTH - it owns convert() and writeTxt()

Two facts from the source that hold the isolation in place:

  * PdfToWord.java:139-140, on the lineX/lineY fields: "Keeping the raw numbers here means that work
    happens in writeTxt() and nowhere else - the .docx path reads runs and never touches any of these,
    so the document output cannot change."
  * PdfToWord.java:730-735, on the five layout stats: "NO LONGER WRITTEN HERE. These five were filled
    by DocxWriter.write into this object - a field of the conversion, shared by every consumer of the
    same Result - so a .txt written after a .docx described a document whose report carried numbers
    only the .docx writer could produce. They are measurements of the .docx layout and are returned by
    that call as DocxWriter.Stats."

The second one is the bug that made the two outputs disagree: the docx writer wrote into the shared
Result and the txt then described the docx's numbers. It was fixed by returning those stats instead of
storing them. ReadingOrder.java:15-22 records the same lesson about page.blocks: the ordering decision
was moved out of DocxWriter.write into ReadingOrder so it happens once, before either writer.

That is why `txt_gate.py` records the SHA-256 of `benchmarks/RANKING.csv` when it starts and checks it
again at the end:

  * unchanged  -> the txt work did not touch the docx, and the gate says so
  * changed    -> the gate fails and names both hashes. The docx ratchet still decides whether the
                  change may be kept; the gate's job is only to make sure nobody can claim a txt
                  result while a docx number moved underneath it.

**AND THE OTHER DIRECTION MATTERS TOO.** `DocxWriter.orderStamps()` mutates page.blocks - line 4757
is `blocks.removeAll(stamps)`, and there are two mutation sites in that method against zero in
`DocxWriter.write()` - and TxtWriter walks page.blocks, so a docx-motivated change can move the txt. `txt_gate.py --watch-docx` records the SHA-256 of
RANKING-TXT.csv before a docx change and checks it after, exactly as the docx hash is checked after a
txt change. One direction is not enough: the shared model makes the dependency two-way even though
only one writer writes it.

## The 99% bar

A document passes when EVERY applicable check passes. `abstained` is never counted as a pass - a
check that did not run is not a check that passed.

## Commands

    python3 tools/p2w-bench/txt_rank.py --limit 40     # score the next 40 unscored documents
    python3 tools/p2w-bench/txt_gate.py --score 40     # score, then gate and write STATE-TXT.json
    python3 tools/p2w-bench/txt_gate.py --gate         # gate only

## What was here before

On 17 Nov a store very like this one was deleted - 327 lines across five files - on the belief that
`RANKING.csv`'s `text_recall` covered the txt. It did not: `text_recall` compares the RENDERED DOCX's
text with the source, and no tool opened the .txt at all. The corpus sat at "0 of 213" for a day with
213 txt files on disk. This directory is that store rebuilt, and the separation is the part that
keeps it from being forgotten again.
