# 18_displacement — the spacer+dither patch, Google-confirmed on a third document

**Run:** relay 15:17, 22 Nov 2026. **Engine:** HEAD `269de8a` + `patches/18-displacement-SPACER-BEFORE-plus-ROW-PITCH-DITHER.patch`
applied to the working tree (uncommitted — the corpus was not ratcheted in this slot).

## What this slot did

1. Applied the 13:56 slot's patch to `app/src/main/java/com/kavopdf/app/engine/DocxWriter.java`
   (spacer gap moved from `w:line` to `w:before` with a hairline `w:line="1"`; row pitch diffused onto
   the measured 0.75 pt grid). `git apply --check` clean; build 45 s; **213/213 documents converted**
   with the patched engine in 1 m 40 s (`ConvertAll`, `-Xmx900m` — the pod has 2 GB and `-Xmx2g` dies
   with "Could not reserve enough space for 2097152KB object heap").
2. Confirmed the construct is really in the output: `w:line="1"` appears 3× in
   `table-with-no-header-row.docx` and 6× in `362_price_list_dense.docx`.

## The measurement — two documents from the 16 that fail 18_displacement and nothing else

Both uploaded as `.docx` to `KavoPDF-Verify`, converted to a Google Doc, exported as PDF, compared with
`verify_google.py --docx`, and the Google Doc deleted afterwards. Nothing left in Drive.

| document | before (benchmarks/gverify, HEAD) | after (this engine, live round trip) |
|:--|:--|:--|
| `table-with-no-header-row` | 41/42, failed `18_displacement` only | **47/47 PASS — CLEAN** |
| `362_price_list_dense` | 41/42, failed `18_displacement` only | 41/42, still `18_displacement` (source=0 render=1) |

The denominator is 47 on the first and 42 on the second: `verify_google.py` scores only the checks that
apply to the document, so a total is never comparable across documents — only a PASS/FAIL verdict is.

**So the patch does reach the class it was aimed at, and it converts at least one of the 16 into a clean
document.** It is not a universal fix for the class: the price list is still displaced, so the class
still has an open document after the patch and its leverage does not fall to zero.

## Why the corpus was not ratcheted — measured, not guessed

`p2w.py --budget 240` measured **41 of 212 documents in 240 s** (6.0 s/document including the 80 s
soffice start, batched 12 per launch). 171 remaining is **~17 min** of measurement, plus a build and the
ratchet/gate/commit/report sequence — more than the slot had left when the throughput was known. The
brief's rule stands: never start a corpus pass you cannot finish. The 41 rows it produced are in
`RANKING.partial.csv` and the published `RANKING.csv` was not touched.

## THE TRAP THAT MADE THOSE 41 ROWS WORTHLESS — read this before the next corpus pass

`benchmarks/p2w.py:70` sets `REPO = ROOT + "/repo"` and `:82` sets
`ENGINE_SRC = os.environ.get("P2W_ENGINE_SRC") or REPO`. With `P2W_ENGINE_SRC` unset — which is how a
fixer run naturally calls it — **p2w.py builds and measures `/scratch/work/p2w/repo`, a fresh clone of
HEAD, not the working tree.** The log says so (`engine -- building from /scratch/work/p2w/repo`) and
that clone is at `269de8a` with none of the patch in it.

A fixer that runs `p2w.py --budget N` to ratchet its own change therefore measures the *unpatched*
engine, writes a table stamped with HEAD's fingerprint, and reports "nothing moved" about a change that
was never converted. That is a false negative that costs a whole slot and looks like evidence.

**The next run must pass `P2W_ENGINE_SRC=<its own clone>`,** e.g.

    P2W_ENGINE_SRC=/scratch/work/CS python3 benchmarks/p2w.py --budget 240

and check the first line of the log reads its own path before spending anything on the pass.

## The next move

Apply the patch (it is in `patches/`, uncommitted by design) and run the corpus pass with
`P2W_ENGINE_SRC` set to the patched clone, then `ratchet.py` and `commit-gate.sh`. Expected prize: up to
the 16 documents that fail `18_displacement` and nothing else, of which at least one
(`table-with-no-header-row`) is now measured clean. The residual `362_price_list_dense` displacement is
the small-spacer over-charge the 13:56 run identified (`mobile-bill`'s 128/124 tw spacers charged in
full where Google charged ~0) and it is still open.

---

## CONTRADICTION, RECORDED — the concurrent 15:34 run refuted this patch

While this slot was measuring, a second fixer (commit `1085564c`, "fixer 15:34") put the same patch
through Google on two other documents and found it **refutes itself**:

    two-tables-stacked-with-no-gap   46/47 in Google, failing the same check as baseline
    mobile-bill                      46/47 -> 43/47, and an extra page

That is a stronger result than the two documents this slot measured, because it includes a document the
patch makes **worse** (an extra page on `mobile-bill`), and a patch that damages one document is not a
fix. Its measured law — `w:before` is charged by Google as exactly V/20 pt — explains both: the spacer
is now charged in full where Google charged ~0, which is fine for a 12.35 pt table gap and wrong for a
6.4 pt one.

So the honest reading of this slot's two round trips:

* `table-with-no-header-row` 41/42 -> **47/47 PASS** is a real measurement and it stands. One document
  in this class does become clean under the patch.
* `362_price_list_dense` unchanged is also real.
* Neither is enough to keep the patch. Two documents that improve do not pay for one that gains a page.
  The patch stays in `patches/` as a refuted idea, not a lead.

The trap below is unaffected and is the part of this run worth keeping.
