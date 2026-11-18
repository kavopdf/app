# The .txt half

Everything here belongs to the .txt output. Nothing in the .docx path reads these files, and nothing
in the .docx path writes them, so a txt run cannot move a docx number by accident and a docx run
cannot hide behind a txt score.

    RANKING-TXT.csv      one row per document: applicable, passed, failed, abstained, failed_ids
    STATE-TXT.json       the txt state - scored, clean, failing, and the docx hash at the last gate
    HISTORY-TXT.jsonl    one line per gate run

## What the two formats actually share

**They do not share a writer.** The conversion is a three-way split:

    PdfToWord.parse()  ->  result (the model)
                              |
                              +-- asTxt ? TxtWriter.write(result, out)
                                         : DocxWriter.write(result, out)

    ToolsActivity.kt:600    if (asTxt) TxtWriter.write(result, out) else DocxWriter.write(result, out)

One or the other, never both. `TxtWriter.java` is 568 lines and standalone - it references
`DocxWriter`, `ReadingOrder` and `NormStore` nowhere and imports only `java.io` and `java.util`.
`DocxWriter.java` is 7196 lines and never touches the txt.

**The isolation runs ONE way, and it depends on WHICH METHOD in the file you touch.**

`DocxWriter.java` is not only a writer. It is a writer plus two static helpers that the model uses:

    DocxWriter.write()         does NOT mutate the model. Verified: zero writes to page.blocks in
                               the whole file. A change here cannot move a txt number.
    DocxWriter.orderStamps()   DOES mutate it. Line 4757 is `blocks.removeAll(stamps)` followed by a
                               re-insert at the position each stamp's own y falls. Its own comment
                               (4745-4748) records the effect: "That reorders page.blocks itself,
                               which both outputs read ... the .txt changed with it (318: 81 -> 90
                               lines)."
    DocxWriter.stampFrames()   folds a stamp's frame rules into one shape before anything is written.

`ReadingOrder` calls both helpers, and `ReadingOrder` runs BEFORE either writer:

    ReadingOrder.java:61       DocxWriter.orderStamps(page, outlines);

That placement used to live inside `DocxWriter.write()` itself, and ReadingOrder.java:15-22 explains
why it was moved: "The .txt writer then walked the same list, so the .txt described a page whose stamp
paragraphs had been moved by the .docx writer ... the same PDF gave two different .txt files depending
on call order, and no check could see it because every text check pairs by text, and a reordering of
lines pairs just as well one way as the other."

So:

    a change to TxtWriter.java           cannot move a docx number - it reads the model and writes
                                         nothing back to it ("nothing here writes back to the model")
    a change to DocxWriter.write()       cannot move a txt number - it does not mutate the model
    a change to DocxWriter.orderStamps() CAN move a txt number - it reorders page.blocks, which the
                                         txt then walks
    a change to PdfToWord.java           can move both - it builds the model both writers read

The file name is not the unit of risk; the method is. That is why the gate is symmetric (below).

That is why `txt_gate.py` records the SHA-256 of `benchmarks/RANKING.csv` when it starts and checks it
again at the end:

  * unchanged  -> the txt work did not touch the docx, and the gate says so
  * changed    -> the gate fails and names both hashes. The docx ratchet still decides whether the
                  change may be kept; the gate's job is only to make sure nobody can claim a txt
                  result while a docx number moved underneath it.

**AND THE OTHER DIRECTION MATTERS TOO.** DocxWriter mutates page.blocks, which is what TxtWriter
walks, so a docx-motivated change can move the txt. `txt_gate.py --watch-docx` records the SHA-256 of
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
