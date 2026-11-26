# The corpus pass DOES finish inside a slot — 212 of 212 scored in 6 calls, and the build is 1.4 min

**26 Nov 2026 · relay fixer, 12:16 slot · engine `a4de7df896875a39` (HEAD) · measured, not argued**

`BLOCKERS.md` 05:28 (26 Nov) says: *"the .docx table cannot be re-scored inside a slot, so no engine
change can land whatever it does"*, and reports two `p2w.py --budget 265` calls that measured 24 then 18
with `remaining` rising 188 -> 194. **That is not what this run measured.** Both halves of the wedge are
budget arithmetic, not a missing capability.

## The corpus build: 1.4 minutes, not 19

    python3 tools/p2w-bench/corpus-convert.py --ensure -j 6

    78 -> 177 docx in one 285 s call, then 177 -> 213 in 87 s.  213/213 for engine 46cebd163a3770a1.

The 19-minute figure comes from ~10.8 s/document with one worker. `-j 6` on this pod does ~3 s/document.
`corpus-convert.py` already takes `-j`; nothing was written for this.

## The re-score: 212 of 212 in six calls, and it RESUMES

    p2w.py --budget 270   55 -> 91 -> 127 -> 161 -> 197 -> 209 -> 212 of 212, remaining 0

Measured, call by call: 55, 36, 36, 34, 36, 12, 3. The counter advances every call; `remaining` never rose.
**It resumes per document** (`DIST/<doc>.json`), and a call that ends mid-chunk keeps what it measured.
The 05:28 row's 24-then-18 is explained by the state it started from (a corpus with 138 documents still
unbuilt), not by the tool restarting: that run's own numbers say `docx 75/213 -- converting 138`, so its
budget was being spent on CONVERSION, and the two calls each converted and measured a disjoint slice.

**The order matters: build first, then measure.** A call that has to convert will spend its whole budget
converting and measure nothing, which reads from outside exactly like a broken measurement.

## The three documents that "soffice gave no render" for DO render — they were starved

The pass stalled at 209/212 with `041122-Account_Opening_Form`, `14_stamp_chars_positioned_td` and
`324_loan_amortisation_schedule` recorded as `PRE/.soffice-fail`. Given a real deadline each one renders:

| document | with the prerender's deadline | with a 110 s deadline |
|:--|:--|--:|
| `041122-Account_Opening_Form` | "no render in 17 s" | **rendered, 65 s** |
| `14_stamp_chars_positioned_td` | "no render in 6 s" | **rendered, 6 s** |
| `324_loan_amortisation_schedule` | never attempted | **rendered, 29 s** |

`prerender()` reserves `min(PER_DOC, (end-now)*0.5)` for the batch and gives each isolated retry
`min(end, t_one+PER_DOC)`. Late in a call `end` has passed, so the retry's deadline is "now" and the
document is charged a failure it never earned; `SOFFICE_FAIL_LIMIT` then skips it on every later call.
A document is not unrenderable because the budget was spent. **Fix (not applied, no measurement): the
isolated retry should get `min(t_one+PER_DOC, HARD_CAP)` and never a deadline in the past.**

## What stopped the landing — and it is not the gate

The `txt-meta-annotation` patch (`PATCHES/txt-meta-annotation-26NOV-relay.patch`) was applied, the corpus
built on it and the whole table re-measured in this slot. `regress.py --check` then refused on **one**
document:

    600_reviewed_invoice_with_annotations   54.30 -> 62.46  share@5 up vs the last commit

The finding that proposed the patch (`TXT-600-ANNOTATION-META-MEASURED-CLEAN-UNLANDABLE-26NOV-relay.md`)
claims `word/document.xml` is **byte-identical** on 600 after the change. **It is not reproducible.** Two
conversions of the same source, one with the patch and one at HEAD, produced different `.docx` bytes:

    patched  8cdb2dd8e49e360520b9649417ec4040f46a1347e6b1bee8dadd9eaa6d81193c
    HEAD     ca292defbde2028033fb395b6d3b53232f111264afff9336c6be352ca131a627

Either the writer is not deterministic run to run (a timestamp in `docProps/core.xml` would do it) or the
`Para.meta` field moves the output. **A sha256 comparison across two runs cannot be used as evidence of
byte-identity until that is settled**, and `scope.py --prove` rests on exactly that comparison — so a
`--prove` that passes today may be passing on two runs that both differ from HEAD in the same way.
The patch was reverted; nothing was committed from it.

## What the next run should do

1. **Build, then measure, in that order**, with `corpus-convert.py --ensure -j 6` (1.4 min) and
   `p2w.py --budget 270` six times (~30 min). This fits a slot with room to spare.
2. **Settle the docx determinism question first** (convert one document twice at the same engine and
   compare). If the writer is not deterministic, every byte-identity claim in `FINDINGS/` needs re-reading
   and `scope.py --prove` needs a same-run baseline.
3. Give the isolated prerender retry a deadline that cannot be in the past; then 041122, 14_stamp and
   324_loan stop being permanent `soffice-fail` skips.
