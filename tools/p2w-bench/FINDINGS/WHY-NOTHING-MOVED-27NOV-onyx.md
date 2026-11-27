# Why nothing moved

Because the class I took is not blocked on an engine change. It is blocked on a **renderer that has no
cache**, and this run spent its slot proving that rather than assuming it.

## 1. The measurement that decided the run

I did not take `18_displacement` because the tool printed it. I took it because it is the largest single
blocker in the store and the reason is checkable in one query:

    40 documents fail exactly ONE check
    30 of those 40 fail ONLY 18_displacement
    18_displacement fails on 119 of 211 scored documents
    60_text_column_right_edge, the next largest, fails on 63

So the class is worth up to 30 clean documents from one construct, and `classpick --leverage` puts its
worth at 54.6. The rotation said `18_displacement` too. That is a reason; it is not the tool's print.

## 2. What the two agents settled, before I touched the engine

**Agent A — the small-dy cluster of 15 documents (each fails only this check).**
It converted all 15, rendered them through LibreOffice, and scored them with `verify_google.py` itself,
twice: at HEAD, and with `dy` taken from the baseline origin instead of the bbox top.

- The baseline-in-line site is **arithmetically excluded**. Its whole lever is `LINE_BASE × hairlinePt(size)`,
  and `hairlinePt` caps the box at 0.6485 pt, so the entire term is ≤ **0.52 pt**. The observed charge is
  1.6–3.0 pt and **sign-mixed (8 positive, 7 negative)**. A lever that cannot change sign cannot explain a
  population that does. That is why the `BASELINE_EM` swap moved `31_times` 1.04 pt where it predicted 2.76.
- 11 of the 15 **pass under LibreOffice**. Their `.docx` already puts every line where the page put it as far
  as any renderer honouring Word's spacing model is concerned; the residual is Google's layout of the same
  construct.
- 4 of the 15 are wrong in **both** renderers (`table-with-no-header-row` −5.0 pt, `worst_dy` 101.4;
  `two-tables-stacked-with-no-gap` −2.5 / 5.6; `71_invoice_space_aligned_no_rules` +1.5 / 8.7;
  `balance-sheet-two-columns-of-figures` +0.0 / 3.5). Those are genuine engine faults and they are the
  table-row class, not the baseline class.

**Agent B — the previous run's txt lead.** Closed, with a fixture rather than an argument: the form-feed bug
was real, is already fixed at `verify_txt.py:944` (commit `0d45ff6`), is **not** a writer bug, and clears
**0** documents under A/B on the same files. The premise was stale: the `.txt` half has read **205 clean /
8 failing** since 26 Nov, not the 186/27 the hand-off quotes.

## 3. The one attempt I made, and what it found

`table-with-no-header-row` is the document where the engine is wrong in both renderers, so it is the one
that can be validated **without** Google. I converted it, rendered it, scored it: `41/42`, `18_displacement`
the only failure, `med_dy -4.9`, `worst_dy 101.4`, 215 runs — the same run count as the recorded Google row.

Then I extracted both pages' row grids. Both have 32 rows. **Source pitch 18.4 pt, render pitch 17.9 pt, on
26 consecutive gaps.** The charge is a **linear ramp of 0.44 pt per row, 0.7 → 12.0 pt over 27 rows** — not
a constant offset. `med_dy` is just the value at the middle of the ramp and has no independent meaning.

And `worst_dy 101.4` is not a displacement at all. The largest pair is `'Diesel'`, source row 130.4 → render
29.1, and the same source row's other cells pair to 100.7 and 118.6 — **one source row claimed by three
render rows 5.5 rows apart**. That is the greedy assignment claiming the nearest *unused* occurrence of a
normalised string on a header-less table of short numeric cells. It changes no verdict here (the page fails
on the count clause anyway), but prior work in this class fitted corrections to `worst_dy` by document. If
`worst_dy` can carry a 5.5-row pairing error, those fits were fitting noise.

## 4. Why that is a lead and not a kept change

The ramp is confirmed in **one renderer on one document**. To fix it I would have to change how the row's
laid pitch is written, then prove it on the corpus. That needs two things this slot did not have:

1. **A corpus rebuild.** `corpus-convert.py` keys every document on the engine source hash; one line under
   `app/src/main/java` invalidates all 213 keys and `regress.py --check` refuses to stamp until they are
   rebuilt — ~27 min, and a rebuild I cannot finish is a corpus with no stamp, worse than the one I had.
2. **A Google render.** The only renderer that sees this cluster is Google, and there is **no cached Google
   export on the pod** — `/scratch/work/p2w/gverify/gd` is empty, and `/scratch/work` does not survive a run.
   Every measurement of this class costs a Drive round trip, which is why 57 attempts have steered by
   `med_dy` alone.

I chose to land the measurement rather than a patch I could not verify. The pod was warm this run (corpus,
JDK and engine all present), so the 32 minutes the last run spent building it went into the agents and the
probe instead — and that is what produced the two findings and the closed lead.

## 5. What the next run should do first

1. **Read `med_dy` as a ramp for any table document.** The store carries no per-row data, so the ramp is
   invisible in it. That gap is the highest-value instrument change available to this class.
2. **Do not fit a correction to `worst_dy` alone.** Guard first: a pair whose `|dy|` exceeds 2× the page's own
   row pitch is more likely a mis-pair than a displacement.
3. **The 4 Group-1 documents are the only ones in this cluster that can be validated without Google.** Start
   there; a fix that moves them is measurable in the slot.
