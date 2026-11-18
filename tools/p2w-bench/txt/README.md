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

**The isolation runs ONE way, not two.**

    a change to TxtWriter.java    CANNOT move a docx number - it reads the model and writes nothing
                                  back to it ("nothing here writes back to the model", line 17)
    a change to DocxWriter.java   CAN move a txt number - it MUTATES page.blocks, and TxtWriter
                                  walks page.blocks. This is not theory: DocxWriter used to call
                                  orderStamps(page, ...) on the page itself, which moved a stamp's
                                  paragraphs inside page.blocks, and the .txt therefore changed
                                  according to whether the .docx had been written first - 11 of 211
                                  documents. The comment at DocxWriter.java:1119-1126 calls it SECTOR
                                  19 and says the fix was to move the ordering decision out to
                                  ReadingOrder, decided once on the document, so neither writer
                                  mutates order.
    a change to PdfToWord.java    CAN move BOTH - it builds the model both writers read

So the txt is the fragile side: anything that mutates the model before TxtWriter walks it changes the
txt, and DocxWriter is such a mutator. That is why the gate is symmetric (below).

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
