# The real cost of an engine attempt, measured: one edit invalidates 213 documents

**27 Nov 2026, fixer run.** Written after the per-document corpus cache landed (`87a3d4ef`) and the
corpus was stamped 213/213 on engine `d28ca7516c3f9165`.

## The number

The cache key for each document is `{engine fingerprint, sha256 of the source PDF, .docx size}`. That is
what makes it trustworthy - a `.docx` from another engine is never mistaken for this build's output. It
also means the engine fingerprint is in every one of the 213 keys:

    $ python3 -c "... len(os.listdir(cc.KEYS))"
    213

So **any edit to `app/src/main/java` stales all 213 keys at once**, and the first measurement of an engine
attempt has to wait for a full rebuild. Measured on this pod: 213 documents at ~4.6 s/doc of wall time,
`-j 4`, CPU-bound on two cores (`-j 2` gave the same 4.5 s/doc) = **~16.4 minutes**, or five 240 s slices.

That is the structural reason a 90-minute run does not make four to six attempts. An attempt is not
"edit, measure, decide". It is:

| step | cost |
|:--|:--|
| edit one constant in `DocxWriter.java` | seconds |
| `javac` the engine | ~2-3 min |
| rebuild the corpus so anything can be compared | ~16.4 min |
| render + score the documents the attempt touches | minutes |
| revert, and rebuild again to get back to a measurable baseline | ~16.4 min |

**One attempt costs ~35 minutes and two full corpus rebuilds.** Two attempts fill the slot. The median
31-run history of 36 minutes is not a discipline problem; it is one attempt plus its revert.

## What would change it, and what would not

Not: keeping the old `.docx` when the engine moves. That is the fossil the 24 Nov incident was made of -
a corpus that was a mix of two engines, certified by one stamp.

Yes: **convert only what the attempt needs, against a stated baseline.** The corpus already has
`ConvertOne.java`. A document-level rebuild of the 5 documents a class is measured on is ~25 s, not 16.4
minutes, and it is enough to answer "did this make these documents better or worse". The full 213-document
rebuild is only needed at commit time, where the gate runs it anyway.

The gap is that nothing exposes that path to a fixer run: `corpus-slice.py` walks the whole corpus, and
there is no `--only <stem>` and no way to score a subset against the committed baseline. That is the next
instrument change, and it is smaller than the one in this slot.

## Also true, and worth not re-deriving

`measure_gate.py` reports `READY - every document measured`, `docx 212/212 scored`, engine
`d28ca7516c3f9165` matching the tree. The "211 of 212 on an older engine" line in the report is the
**Google** (`gverify`) table, not the docx table - the two are different measurements and only the Google
one is stale. Anyone reading "211 on an older engine" as "the docx scores are stale" is reading the wrong
table.
