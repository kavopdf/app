# The uniform-pitch guard works: 42/42 in Google, and the two cost documents are byte-identical

**Measured 24 Nov 2026, fixer slot 03:27.** The `18_displacement-UNIFORM-PITCH-SNAP-0559-fixer.patch` in
this directory was applied to `DocxWriter.java`, built, and measured in both renderers. **Not landed** -
the engine is reverted because the corpus ratchet does not fit the slot (see "why it is not committed").

## What was believed, and what is now true

`18_displacement-GOOGLE-LAYS-A-ROW-ON-WHOLE-PIXELS-0052-fixer.md` measured the mechanism (Google
truncates a table row to whole CSS pixels) and measured the snap on `362_price_list_dense` at 42/42 - but
it cost 17 documents in LibreOffice, because it was applied to every table. That finding's own next step
was a pre-pass that applies the snap **only to a table whose row heights are a uniform pitch**.

The 0559 patch does exactly that, without a pre-pass: it writes the rows, then rewrites the
`w:trHeight` **value** in place once every height is known. A table is a pitch when it has ONE fractional
row height that repeats at least three times, with already-whole-pixel rows ignored.

**Now measured, in the renderer the user opens:**

| document | before | after | why it is the right probe |
|:--|--:|--:|:--|
| `362_price_list_dense` | 41/42, fails `18_displacement` | **42/42** | 29 rows, uniform 168 tw pitch, the whole defect |
| `electricity-bill` | baseline share5 1.33 | **1.33, unchanged** | 360/375/390 alternation - the guard must skip it |
| `330_cad_drawing_sheet` | baseline share5 4.91 | **4.91, unchanged** | the doc that went 4.91 -> 5.22 last time |

`362_price_list_dense` was uploaded to the `KavoPDF-Verify` folder, converted to a Google Doc, exported
as PDF and scored with `gverify.py --collect`:

```
362_price_list_dense                         GOOGLE 42/42
                                             LIBRE  already have it
```

The result is committed at `benchmarks/gverify/362_price_list_dense.json` (`passed 42, total 42,
failed []`). The Google Doc was deleted after scoring; the folder is empty.

**The two documents that carried the cost are now byte-identical.** `electricity-bill` has two different
fractional heights (360/375/390) so `uniform = false` and the table is skipped. `330_cad_drawing_sheet`
is skipped the same way. That is the guard doing the job the 0052 finding said it had to do, and it is
the difference between this attempt and the one that was reverted.

## Why it is not committed

`regress.py --check` on the built tree:

```
ENGINE CHANGED (docx): table measured on 3e7f7c4475343a35, the tree is 0045c87ab848d942
             An unmeasured change is not a pass. Re-measure, then --stamp.
docx: no document worse than baseline
```

No document is worse - the gate says so - but an engine change needs a **full 212-document pass and a
re-stamp**, which is about forty minutes. This slot had twenty. Landing it unmeasured is exactly what
the gate exists to refuse, so the engine is reverted and the patch stays here.

**What the next run does, in this order:**

1. `git apply tools/p2w-bench/FINDINGS/18_displacement-UNIFORM-PITCH-SNAP-0559-fixer.patch`
2. `bash tools/p2w-bench/build-engine.sh`
3. `python3 benchmarks/p2w.py --force --budget 250` - repeated until the corpus is complete. **Start the
   slot with this, not with anything else**; it is the whole cost of the change.
4. `python3 tools/p2w-bench/regress.py --check`, then `--stamp`, then commit `app/` + `RANKING.csv`
5. `python3 tools/p2w-bench/attempt.py --class 18_displacement --moved N --total M --engine <hash>`

## The nine documents the 0052 finding named

`362` is one of ten. The other nine - `16_right_aligned_amounts_txtpos`, `31_times_body_arial_headings`,
`36_embedded_subset_font`, `68_journal_wide_table_spanning`, `71_invoice_space_aligned_no_rules`,
`72_bank_statement_no_rules_right_amounts`, `74_balance_sheet_indented_subitems`,
`balance-sheet-two-columns-of-figures` - become CLEAN only if their tables are a uniform pitch. **That is
the first thing to check after the corpus pass, and it is cheap**: the guard's decision is visible in the
`.docx` as a row-height sequence that is no longer uniform. A table whose heights are individually
measured is skipped, and those documents will not move.

## What would prove this wrong

- The corpus pass showing any document worse than baseline - the guard should make that impossible for
  the two cost documents, but 17 documents were worse without it and only three have been re-measured
  with it.
- `362_price_list_dense` failing `18_displacement` on a re-run of the Google round trip. It scored 42/42
  once, on this engine, and the check is deterministic given the same export - but one round trip is one
  sample.

## Two things the audit of this patch found, worth knowing before it is relied on

A static audit of the patch (subagent, this run) raised two risks that the measurement does not cover:

1. **The uniform test counts occurrences, not stride.** `168, 240, 168, 240, 168` passes it (240 is a
   whole pixel and is skipped), and so does three equal fractional rows followed by two hundred
   whole-pixel rows. The 200 are untouched - a whole-pixel height snaps to itself - but the test is
   looser than the comment claims.
2. **The last row absorbs the remainder** (`totalInTw - doneTw`). On a table whose last row is not part
   of the pitch - a total row, a footer band - the distortion lands on a row that had nothing wrong with
   it. Under one pixel, but it is the one row the snap is allowed to move.

Neither is a reason not to land it. Both are reasons to look at the two worst movers in the corpus pass
before stamping.
