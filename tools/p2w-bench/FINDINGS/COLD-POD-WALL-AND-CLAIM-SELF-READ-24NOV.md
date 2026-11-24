# A cold pod is why a slot lands nothing - measured, with the three walls and their costs

**Run: 24 Nov 2026, fixer slot 18:59 IST.** Nothing in this file is a theory about the engine. It is
four measurements of the *pipeline*, and the first one explains why previous slots ended with an
unlandable patch and an empty report.

---

## What I believed

That a fixer slot that lands nothing has been beaten by the engine: a construct Google will not honour,
a check that fails a document against itself, a class with no verdict.

## What I measured

On a **fresh pod**, in the order the walls appear:

| # | wall | what it looks like | measured cost |
|---|---|---|---|
| 1 | the corpus PDFs are not in the repo | `corpus-convert.py --ensure` -> `no corpus PDFs found` (exit 3) | `corpus-fetch.sh` fetched **213 PDFs**, 212 scored, 0 missing |
| 2 | no JDK, and the engine is not compiled | every document fails `ClassNotFoundException: ConvertAll` | `jdk-fetch.sh` + 4 jars + `javac` = the engine and `ConvertAll.class` |
| 3 | the corpus `.docx` cache cannot be built in one call | `corpus-convert.py --ensure` converts all 213 in one call; **4.4 s/doc wall with 6 workers = 15 min**, the platform kills a call at 290 s | four slices: **68 + 51 + 51 + 43 = 213**, 0 failures |

**The consequence is the point.** `regress.py --check` is the pre-commit hook. It cannot run without
the corpus. So on a fresh pod **no commit of any kind could land - including the fixer's own claim.**
`round.py --claim-fixer` commits `ROUND.json` and pushes it, and the gate refused that commit. A slot
that cannot claim cannot work, and a run that cannot claim reports nothing.

**Measured after the three walls were cleared:** `regress.py --check` -> `PASS` in **11.4 s**.

So the pipeline was not dead and the engine was not blocking. It was **cold**, and every fixer run was
paying 15 minutes of invisible set-up cost it had not budgeted, then reporting a slot's worth of nothing.

## What is now true

- `tools/p2w-bench/corpus-slice.py` (new) builds the cache in slices that each fit one call, converts
  **only** documents with no `.docx` on disk, and the last slice writes the stamp with
  `corpus-convert.py`'s own `write_stamp()`, so `--ensure` then reads WARM. Nothing is deleted and no
  document is converted twice.
- The slice size is a measurement, not a guess: the first version divided the 11 s/doc *single-document*
  cost by the worker count and asked for 109 documents in a 200 s budget; the call was killed at 300 s
  having done 68. The cost that matters is wall time per document at this worker count, and it is not
  linear in workers. **4.5 s/doc** is the number to size against.

## What would prove this wrong

A pod that arrives with `/scratch/work/p2w/corpus` populated, a JDK and a compiled engine already, where
`corpus-convert.py --ensure` prints `corpus is warm` and `regress.py --check` passes in seconds without
any of the above. Then this file describes one pod, not the pipeline. Check
`corpus-convert.py --status` first; it says WARM or COLD and the reason.

---

# The claim read its own claim as a rival's - measured, fixed, pinned

**Second wall, and the one that looks like a live run and is not.**

`round.py --claim-fixer` decides "is someone else in the slot" from `load()` - this sandbox's working
copy. Every tool in the directory writes `ROUND.json` and `RUN.json`, so that file is dirty the moment
anything runs, and the `git pull --rebase` meant to refresh it **fails on that dirt**. The claim then
read the file it had itself just written seconds earlier, saw a claim of age 0, and stood down.

**Measured 24 Nov 18:59 IST, this run:**

```
--claim-fixer             fixer busy - another run claimed and pushed first (no detail). Standing down.
git show origin/main:...  "fixer_started": 0
```

The slot was free. This run continued only because a reader disbelieved the tool. **A run that stands
down reports nothing**, so the loss is silent - the report says "nothing to report" and the slot is gone.

**Second half, quieter:** the old code printed `claimed at HH:MM` after a **rejected** push, so a run
believed it held a slot the other fixer could not see. Two runs then edit the engine at once - the 17 Nov
whole-file revert.

**Now:** fetch, read the rival claim out of `origin/main` (the only state both sandboxes share), treat an
identical value as our own claim, and refuse to claim at all if the claim never reaches origin.

`test_claim_remote.py` (new) pins five cases. **Measured before the change: 3 of 5 failed.** After: 5 of 5
agree. Live after the fix: `--claim-fixer` -> `fixer claimed at 19:49`.

---

# The anchored-box lead: the patch is written and measured, and the risk model in it is wrong

Carried into this run and measured by a sub-agent; recorded here so the next run does not rebuild it.

**The patch** (`DocxWriter.java`, seven edits): `para()` stops routing a positioned page's lines into
anchored DrawingML boxes; `flowFromBox`/`flowRow` turn the after-table and pitch gaps into `w:before`
clamped by `fitPage`; the two zero-gap branches **rewind the flow** to the line's own baseline instead of
anchoring it.

**Measured on 8 real documents, from `word/document.xml`:**

| | HEAD | patched |
|---|---:|---:|
| anchored boxes | 381 | **6** (-98.4 %) |
| non-space chars in boxes | 11,180 | **376** (-96.6 %) |
| `041122-Account_Opening_Form` boxes | 189 | 3 |

**No text lost:** character multiset identical - `041122` 42,319 -> 42,319 (0 lost, 0 gained); `311` 1,183
-> 1,183; the filled twin 42,398 -> 42,398. The 3 survivors are `pinnedBoxes` signature lines, a different
construct.

**The agent's own risk note says page count is the unmeasured danger, and cites the 7 Nov revert. That is
the wrong risk, and the repository already measured it:**
`FINDINGS/ANCHORED-BOX-CENSUS-CAP-IS-16PCT-24NOV.md` - "page-count changes (soffice, all 23 changed
documents): **0**. Page counts hold on all 23 changed documents, so pagination is not what refutes it.
**Displacement is.**" The spend-always experiment cost `330_cad_drawing_sheet` a median displacement of
3.14 -> 16.77 pt and `table-inside-two-column-page` a max of 9.17 -> 92.01 pt, because a gap the page
cannot afford enters the flow as `w:before` and the squeeze pulls the whole page up.

**And the census says the same patch is not sufficient on its own:** spending every gap removes 3,770 of
23,794 box characters (15.9 %); the `PAGE_POSITION_ON_ANCHOR` cascade removes 4,037 (17.0 %); **neither
empties a single document**, because after the flow resyncs the next line reaches its own negative gap and
anchors by itself. The census's own conclusion is a per-line rule - a line the flow cannot reach is
written into the flow **at the position the page drew**, as `w:before`, not as a box - and records it as
**a proposal, not a result**.

## So the next run's first measurement is not "does the box count fall"

It does, by 98 %. It is **displacement on the 23 changed documents**, because that is the number the
repository already measured as the refuter. Concretely:

1. apply the patch, rebuild the engine, and re-convert the corpus (`corpus-slice.py`, ~16 min);
2. `regress.py --check` - it refuses a Google regression too, so this is the first honest filter;
3. on the documents the census names, compare displacement HEAD vs patched, expecting the `330` and
   `table-inside-two-column-page` signature if the `w:before` is spent unclamped;
4. only then Google, on the hardest document where boxes are the whole defect (`041122`, 189 boxes).

## What would prove this wrong

If the patched build holds displacement at or below HEAD's on all 23 changed documents, the census's
"displacement is what refutes it" is refuted and the box construct can be removed in one change - which
would touch `04_chars_missing`, `45_char_accuracy`, `13_text_colours`, `44_header_footer` and
`17_matched_runs` at once. If it does not, the per-line `w:before` rule is the only route and the rewind
in `flowRow` is the wrong shape for it.
