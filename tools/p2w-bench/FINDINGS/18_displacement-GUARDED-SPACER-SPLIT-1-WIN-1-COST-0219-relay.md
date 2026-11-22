# 18_displacement — the guarded spacer split: one document won, one check lost, and the "4 wins" do not reproduce

**23 Nov 2026, 02:19 IST, relay slot 01:14.** Engine `1779a130` + the guarded patch, reverted after
measurement. Google Docs, one round trip per document, `verify_google.py` with `--docx`.

## What was built

The 23:10 run measured the spacer split (spend the table gap as `w:before` instead of a
`w:line="exact"` paragraph) plus a row-pitch dither, reported **4 of 16 documents at 42/42 and 2
documents broken**, and reverted it. Its own next-run note asked for the split to be re-applied with
a scope guard, because the two broken documents were the ones whose pages were exactly full.

This run built that guard. The discriminator was not the spacer's size but the **carrier**: the four
wins are tables whose cell borders are all `nil` and whose rules are floating shapes; the two losses
are ruled tables. So:

    gapAtTrue = no side drawn (t.ruled false and all six t.sideDrawn false) AND spacerTw <= 400

and the dither was gated on `!ruledTable`. Outside the gate the paragraph is written byte for byte
as before, so no document outside the gate changes at all. Verified in the emitted XML: `mobile-bill`,
`insurance-policy-schedule`, `table-with-no-header-row` and `two-tables-stacked-with-no-gap` still
carry `w:before="0" w:line="<n>"`, and `68_journal_wide_table_spanning`'s 144 pt spacer is untouched.

## What Google said

Before = the committed Google table at engine `462353f9`, which is **byte-identical** to `1779a130`
in `engine/` (`git diff --stat 462353f9 HEAD -- app/src/main/java/com/kavopdf/app/engine/` is empty),
so it is a legitimate before for this engine.

| document | before | after | verdict |
|:--|:--|:--|:--|
| `29_dot_leaders_txtpos` | 41/42 | **42/42** | won |
| `41_coloured_headings_white_bg` | 41/42 | 41/42 | unchanged — the 23:10 run read 42/42 here |
| `73_marksheet_subject_marks_grade` | 41/42 | 41/42 | unchanged — the 23:10 run read 42/42 here |
| `72_bank_statement_no_rules_right_amounts` | 41/42 | 41/42 | unchanged — the 23:10 run read 42/42 here |
| `22_invoice_four_columns_txtpos` | 41/42 | 41/42 | unchanged |
| `16_right_aligned_amounts_txtpos` | 41/42 | **40/42** | **worse** — new `23_line_pitch` |
| `mobile-bill` | 46/47 | 46/47 | guard held, no regression |
| `insurance-policy-schedule` | 46/47 | 46/47 | guard held, no regression |

The guard does what it was built to do: both documents that cost the 23:10 run a page are held at
46/47 and one page. That part of the finding stands and can be relied on.

**The 4 wins do not reproduce.** Three of the four documents the 23:10 run read at 42/42 read 41/42
on this build, same engine, same patch, same conversion path (`ConvertOne`, one document per JVM).
Two readings of the same document at the same engine cannot both be right, and the honest conclusion
is that the earlier reading is not reproducible here — either it was taken on a build carrying more
than this patch, or Google's export is not deterministic across uploads at the margin. What this run
can state is its own: **the guarded split is worth +1 clean document and costs one check on another**,
which is not a trade the rules allow.

`16_right_aligned_amounts_txtpos` lost `23_line_pitch`, not `18_displacement` — the dither changed
its row declarations (its 13 rows now read 360/375/360...) and the row pitch moved out from under a
check that had been passing. That is the dither, not the spacer, and it is the second time the
dither has cost a document it was not aimed at.

## What would re-open this

* A build that reproduces the 42/42 readings on `41_coloured_headings_white_bg`,
  `73_marksheet_subject_marks_grade` and `72_bank_statement_no_rules_right_amounts`. The record
  should carry the exact engine hash and the .docx hash for each, or the reading cannot be re-derived.
* The spacer split **without** the dither, measured on the same eight documents. The one win here
  (`29_dot_leaders_txtpos`, 15.85 pt gap, 5 rows) and the one loss (`16_right`, 4.65 pt gap, 13 rows)
  differ in gap size and row count, not in carrier — if the split alone is the win, the dither is
  what loses `16_right` and it should not travel with it.
