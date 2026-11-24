# The .txt half

Everything here belongs to the .txt output. Nothing in the .docx path reads these files, and nothing
in the .docx path writes them, so a txt run cannot move a docx number by accident and a docx run
cannot hide behind a txt score.

    RANKING-TXT.csv      one row per document: applicable, passed, failed, abstained, failed_ids
    STATE-TXT.json       the txt state - scored, clean, failing, and the docx hash at the last gate
    HISTORY-TXT.jsonl    one line per gate run

## The .txt grades itself against its own records, and nothing else

Every file here, all inside this directory. Nothing on the .docx side reads or writes any of them, and
`txt_gate.py` proves that per run by hashing `benchmarks/RANKING.csv` before and after.

The .docx keeps a set of records that turn a score table into something a fixer can act on. The .txt
now keeps the same set, one directory over, and no file on either side is read or written by the
other.

| .docx | .txt | what it is | who writes it |
|---|---|---|---|
| `benchmarks/RANKING.csv` | `RANKING-TXT.csv` | the current scores, one row per document | scoring |
| `benchmarks/RANKING-BASELINE.csv` | `RANKING-TXT-BASELINE.csv` | the reference table | `txt_rank.py --baseline`, once. Scoring never touches it. |
| `tools/p2w-bench/RATCHET.json` | `RATCHET-TXT.json` | the best each document has reached, and the universe it reached it under | `txt_rank.py`, only when a document improves |
| - | `DOCX-WATCH.json`, `BOTH-WATCH.json` | the hashes `--watch-docx` and `--snapshot` recorded, for the comparison after the change | `txt_gate.py` |
| `benchmarks/STATE.json` | `STATE-TXT.json` | the last gate state | `txt_gate.py` |
| `tools/p2w-bench/RESULTS.jsonl` | `HISTORY-TXT.jsonl` | one line per gate run | `txt_gate.py` |
| `benchmarks/DEFECT-CLASSES.md` | `DEFECT-CLASSES-TXT.md` | the classes, ranked by how many documents each holds | `classify_txt.py` |
| `benchmarks/CENSUS.csv` | `CENSUS-TXT.csv` | one row per document with its cause and its baseline | `classify_txt.py` |
| `tools/p2w-bench/CAUSES.json` | `CAUSES-TXT.json` | what causes each document's damage | `classify_txt.py` |
| `tools/p2w-bench/UNMEASURED.json` | `UNMEASURED-TXT.json` | what was not compared, and why | `classify_txt.py` |

`tools/p2w-bench/RATCHET.json` is named above as the .docx counterpart and **does not currently
exist**: the .docx ratchet was reset on the drift described in `ratchet.py`'s own output, and no
fresh marks have been taken since. The .txt has its marks. That asymmetry is real and is a .docx
problem, not a .txt one - the .txt gate does not depend on it.

Two tools mirror the .docx's as well:

    step_txt.py       what to fix, worst class first, with the commands - the .txt's step.py
    classify_txt.py   rebuilds the four records from RANKING-TXT.csv and nothing else

**`classify_txt.py` never reads a .docx file.** A cause is derived from the check ids that failed:
one check names its own cause, and checks that move together (position with line order, word
accuracy with word invention) are named for the group, because they are one displacement seen
twice. It also reports every document that is scored but absent from the baseline or the marks,
which is the only way a gap in the records becomes visible rather than assumed away.

**The ratchet compares a score against `RATCHET-TXT.json`, never against `RANKING-TXT.csv`.** That
distinction is the whole point. Comparing against the score file means the store grades itself, and
it fails in the one case that matters: delete or reset the store and every document becomes a first
score, nothing is compared, and the ratchet prints "no document got worse" over an empty table.

Three verdicts, and only one of them is a pass:

    exit 0   every mark held
    exit 1   a document is worse than its best - a real regression
    exit 3   nothing was compared: the marks are empty (UNMEASURED) or were stamped under a
             different set of checks (STALE). Not a pass, not a regression - a gate that cannot speak.

`txt_gate.py --gate` refuses the same two cases rather than printing `0 of 0 clean (0.0%)`, and it
also refuses when the scores exist but the marks or the baseline do not.

**A mark is raised only when a document improves**, so `RATCHET-TXT.json` records the best each
document has ever reached rather than the last thing that happened to be measured. Marks stamped
under a different check universe are not compared, not carried forward and not replaced.

---

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
    python3 tools/p2w-bench/txt_gate.py --score 60     # score, then gate and write STATE-TXT.json
    python3 tools/p2w-bench/txt_gate.py --gate         # gate only

## What was here before

On 17 Nov a store very like this one was deleted - 327 lines across five files - on the belief that
`RANKING.csv`'s `text_recall` covered the txt. It did not: `text_recall` compares the RENDERED DOCX's
text with the source, and no tool opened the .txt at all. The corpus sat at "0 of 213" for a day with
213 txt files on disk. This directory is that store rebuilt, and the separation is the part that
keeps it from being forgotten again.
