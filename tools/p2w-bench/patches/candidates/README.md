# Candidate patches - built and measured in the 13-14 Nov era, never applied

**None of these is applied. None of these is verified against the current corpus.**

They were produced while a fleet of sub-agents was attacking the old pipeline, measured
against the **211-document corpus with the old instrument**, and then the pipeline was
rebuilt underneath them: new corpus (213), new instrument (`benchmarks/p2w.py`), new
round machine, new defect classes. The work is real; its numbers belong to a world that
no longer exists.

## Why they are here and not applied

Checked on 16 Nov:

    repo clean
    10 patches apply cleanly to the current tree (git apply --check)
    10 patches NOT already applied (0-7 of 46-201 distinctive added lines present in source)

So they are genuinely pending. They were **not** applied, for three reasons that all
point the same way:

1. **They cannot be verified right now.** Verification means building the engine and
   measuring 213 documents. The sandbox had no JDK and no corpus at the time of the check.
   Applying an engine patch without that is the unverified change the ratchet exists to stop.
2. **They carry their measurements from the old corpus.** A patch that read "32_stroke_lines
   11 -> 4" was measured with a different instrument on a different set of documents.
   The number does not transfer.
3. **The fixer holds the engine slot.** Changing the engine under a live fixer run makes
   its ratchet comparison meaningless.

## What they are

Six change what the app produces, four change only the advisory check tooling.

| patch | kind | +lines | touches |
|---|---|---|---|
| `ORDER-63-one-row-per-columns` | engine | 27 | DocxWriter - three-column pages written as one row per horizontal band; 63_three_column_brochure becomes a 2x3 grid |
| `colour-fixes-rebased` | engine | 141 | DocxWriter + PdfToWord - colour handling |
| `extra-gutter-band-projection` | engine | 179 | PdfToWord - extra gutter band projection |
| `FOUR-FIX-A2-free` | engine | 196 | PdfToWord |
| `rule-fix-2` | engine | 206 | DocxWriter + PdfToWord - `ownedByTable` wiring, stroke lines |
| `p2w-links-rebased` | engine | 484 | DocxWriter + PdfToWord + verify_google - hyperlinks |
| `36-underline-symmetric-2` | tooling | 244 | prove_checks + verify_google - underline symmetry |
| `47-margins-rebased` | tooling | 134 | verify_google - margins |
| `62_rule_weight` | tooling | 252 | verify_google - rule weight |
| `floors-211` | tooling | 55 | verify_google - check floors |

The four `tooling` patches change **checks, not output**. `verify_google.py` and
`prove_checks.py` are advisory in the current pipeline: `benchmarks/p2w.py` is the
authority and the 47 named checks do not decide a round. Patching them would move reported
check numbers without moving a single pixel of output, so they are the lowest value here
and the highest chance of confusing a reader.

## How to use them - one at a time, never as a stack

The stack of six engine patches is **1233 added lines across two files**. Applied together,
nothing can attribute a change to a cause: if the corpus moves, you will not know which
patch moved it, and if it regresses you will not know which one to drop. That is the exact
failure mode the 19-attempt ledger records.

    cd /scratch/work/base                      # a clean clone, phase must be 'fix'
    git apply --check tools/p2w-bench/patches/candidates/<one>.patch
    git apply        tools/p2w-bench/patches/candidates/<one>.patch
    ./tools/engine-verify/build-engine.sh      # or however the engine is built this round
    python3 benchmarks/p2w.py --budget 250     # measure
    # compare share@5px per document against benchmarks/RANKING.csv - the ratchet decides
    # keep only if no document regressed; record with attempt.py; revert otherwise

If a patch does not move the class it names, revert it and say so in ATTEMPTS.json - a
patch that does nothing is a finding, not a failure.

**Do not apply two of these in the same attempt.** The ledger has to be able to say which
one did what.

## Provenance

The reports that describe the work behind each patch were delivered with them and are not
in this repository: `36-underline-findings-2.md`, `SECTOR8-COLOUR-REBASE-REPORT.md`,
`RULE-WEIGHT-REPORT.md`, `SECTOR-11-links-rebase.md`, `ITEM20-report.md`,
`GRADIENT-REPORT-REBUILD.md`. Where a patch and a report disagree, trust neither: measure.
