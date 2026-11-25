# 18_displacement: mechanism, minimal patches, discriminating test - PROPOSED, NOT MEASURED

**25 Nov 2026, 09:20-09:30 IST, fixer slot 09:13. Produced by a read-only subagent, landed unmeasured by the
parent run.**

## What this is, and what it is not

This is the most complete analysis of `18_displacement` anyone has produced - the class `classpick.py
--leverage` ranks first, 13 documents failing it alone and 39.7 clean documents behind it. It is **not a
fix**: nothing was built, converted or rendered, so it violates nothing to say so plainly. It is landed
because a proposal of this size dies with the subagent that wrote it, and the next run should start from
it rather than re-derive it.

## The three claims a run must check first, in this order

1. **`place()` at `DocxWriter.java:4149` is dead code - zero callers.** `FINDINGS/DOCS-ROOT-CAUSES-24NOV.md`
   quotes it as the mechanism. A patch written inside `place()` would change no output. Check with
   `grep -n "place(" app/src/main/java/com/kavopdf/app/engine/DocxWriter.java` before anything else.
2. **`spacing()`'s `pageFirst` argument is always false** - both flow call sites pass `ctx.newPage` *after*
   clearing it (`:4626->:4638`, `:3711->:3787`). If true, the first-line compensation at `:165` has never
   run and `-Dp2w.lineRule=autoflow` is not available as a fallback experiment.
3. **`w:beforeLines` is emitted nowhere** (0 grep hits), so that half of the brief's premise does not apply
   to this writer.

## The patches, smallest first

- **(b) partial spend, `:6117-6137`** - three integers and one guard condition on the table-gap spacer.
  `before + line` preserved to the twip, so LibreOffice should be byte-neutral. Predicted +3 clean,
  0 regressions. The subagent's own warning: the guard's `slackTw` reads the *source* page's white space
  (`:6119`), which is anti-correlated with the defect - worked numerically on `68_journal`, 688 tw of
  measured slack against a 144 pt gap whose absence already moved the render 114 pt up.
- **(a) `w:pgMar w:top` per-page section** - Google-proven shape (37 -> 40/42 on the probe), but it is a
  page-structure change and needs the `budgetTw` subtraction.

## The discriminating test

Positive controls from stored `gverify` verdicts: `68_journal_wide_table_spanning` (41/42),
`72_bank_statement_no_rules_right_amounts` (41/42, predicted clean), `bus-timetable-station-left-times-right`;
`412_page_labels_roman` for (a), because the A/B is inside one file (+2.3 pt page 0 vs -58.8 pages 1-4).
Six false-positive signatures, chief among them a fall in `runs_matched` - the exact shape of the refuted
1x1-table variant.

## Two things not in the brief

- The post-table carrier at `:7034-7038` is the same defect at 4 pt: a 3.14 pt shortfall after *every*
  table. It must not be swept in as a side effect of (b).
- `lineParagraph` at `:3811` puts exact line boxes inside the anchored boxes Google rasterises, so a blanket
  change to `spacing()` charges 04/25/59.

## Provenance and the line-number caveat

The subagent cloned at `96eb96d`; this run's clone is at `315d15c`. `96eb96d..315d15c` touches
`tools/p2w-bench/` only (a claim commit and a corpus-hash commit), so the `app/` line numbers should hold -
but they were not re-verified against this tree, and a run that acts on this must confirm each line number
before editing. Its own words: "the patches are proposals with a stated expected effect and a stated
falsifier, not measured fixes."

The full 593-line report is in this run's report chain; this file is its load-bearing part.
