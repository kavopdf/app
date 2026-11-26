# The docx corpus re-measure does not fit in a 90-minute slot, and it is why the gate stays NOT READY

Measured 26 Nov 2026, fixer slot 16:56 IST, on the tree at `6ee2cd00`.

## What the gate says, and what the two instruments disagree about

    measure_gate.py   RANKING.csv measured on docx engine a4de7df896875a39, tree is 7e0de1abdeb221ae -> NOT READY
    regress.py --check  ENGINE CHANGED (docx): table measured on a4de7df896875a39, the tree is 7e0de1abdeb221ae
                        engine fingerprint (all java): 025fe9deda5ac7b1

Three engine ids for one tree. They are not in conflict once you read `engine_fingerprint()`:
the `docx` form hashes the `*.java` set minus `DOCX_EXCLUDES`, and the bare call hashes all of
them. So `025fe9deda5ac7b1` is the whole-engine id the previous run's report quotes and
`7e0de1abdeb221ae` is the docx-scoped id the table must be stamped with. **A run that quotes the
all-java id as the engine it measured on will believe the corpus is current when it is not.** The
table has not been measured on the docx engine since `a4de7df896875a39`.

## The measurement, three slices of `benchmarks/p2w.py --force --budget 240`

| slice | measured | converted .docx | remaining |
|:--|--:|--:|--:|
| 1 (12:23-12:26) | 12 of 224 | - | - |
| 2 (12:27-12:31) | 31 of 212 | 146 of 213 | 181 |
| 3 (12:32-12:36) | **43 of 212** | **146 of 213** | **169** |

Rate: 12 documents in the last 240 s budget, i.e. **3 documents a minute**, dominated by
`prerender ... in soffice batches of 12`. 169 remaining is therefore **about 50 minutes of
measuring on top of the conversion**, and the conversion itself is stuck: the .docx count did not
move from 146 across slices 2 and 3, so 67 documents have no output for the pass to score.

`p2w.py` writes `/scratch/output/RANKING.partial.csv` (43 rows) and leaves the published
`benchmarks/RANKING.csv` untouched while incomplete. So a run that spends its whole slot here
credits nothing: the gate still refuses, and no document moves.

## Why this is the blocker and not an excuse

Every commit since the engine last changed is refused by the same sentence. The previous run's
kept page-top fix (`aa496eb`, Google 42/47 -> 46/47 and 45/47) is in the tree and in the table's
engine is not. Until the pass completes, `regress.py --stamp` cannot run, the three
`[ratchet]` pending rows (`05_chars_extra`, `32_stroke_lines`, `47_margins`) cannot be closed, and
`attempt.py` will not credit a moved count measured on this tree.

## What the next run should do about it, in order

1. **Find why the .docx count stops at 146.** 67 documents have no output and every slice spends
   its prerender budget on them again. `ls /scratch/work/p2w/pre/*.soffice-fail` and the
   `prerender: N document(s) skipped` log line name them. A document that cannot render must be
   marked exempt or failed, not re-attempted every slice: that is where the 3-documents-a-minute
   rate comes from.
2. **Then run the pass to completion** with the prerender no longer poisoned. At 12 a slice it is
   14 slices; with 67 dead documents removed it is 8.
3. **Only then** `regress.py --stamp`, and the three ratchet rows close in the same pass.

The number to beat: **43 of 212 measured on `7e0de1abdeb221ae`, 169 to go.** Partial output is at
`/scratch/work/keep/RANKING.partial.csv` in the run's sandbox (not committed: it is a partial
table and publishing it is the failure mode `p2w.py` was written to prevent).
