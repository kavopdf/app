# The guarded carrier clears 13 of 16 {05,32} documents in Google, and the handoff named the wrong patch

**22 Nov 2026, fixer slot 01:53. Measured through Google, not LibreOffice.**

## What the handoff told the next run to do, and why that would have cost 59 documents

`LAST-MESSAGE.md` ended with:

> 1. `git apply tools/p2w-bench/patches/rule-carrier-followed-by-block-2008.patch` — this one only.

**That is the destructive patch.** The same slot wrote
`FINDINGS/32_stroke_lines-CARRIER-OVERSHOOTS-3608-VERTICALS-0023-relay.md` at 01:16, which says the
opposite: the predicate is symmetric, it admits a table cell's 0.4 pt vertical separator, 3608 of the
4595 carriers are those, and `rule-carrier-horizontal-only-2008.patch` **supersedes** it. The 19:42
entry in the same file only established that `followed-by-block` is a superset of `per-rule` — a
different pair — and the "Next run" section carried the wrong name forward from there.

Verified here, both patches apply clean to HEAD `20488472`:

| patch | lines | guard | corpus effect |
|:--|--:|:--|:--|
| `rule-carrier-followed-by-block-2008` | 185 | none | 4595 carriers, 3608 of them 8-twip verticals |
| `rule-carrier-horizontal-only-2008` | 193 | `if (s.wPt < s.hPt) return false;` | 987 horizontal carriers |

`diff` of the two patches is the guard and nothing else. **A handoff instruction is not evidence.**

## What was measured

Engine = HEAD `462353f` + `patches/rule-carrier-horizontal-only-2008.patch`, built with
`tools/p2w-bench/build-engine.sh` (33-34 s cold, JDK fetched). Corpus fetched (213 PDFs). The 16
documents that fail exactly `{05_chars_extra, 32_stroke_lines}` in the committed Google table were
converted (2.5-3.7 s each), uploaded to `KavoPDF-Test-Outputs`, exported by Google as PDF and scored
with `verify_google.py` — the same 42 checks, the same file.

| document | HEAD (committed Google) | HEAD + guarded carrier | |
|:--|:--|:--|:--|
| 17_three_column_widths_txtpos | 40/42 | **42/42** | CLEAN |
| 18_centred_heading_left_body_txtpos | 40/42 | **42/42** | CLEAN |
| 19_hanging_indent_txtpos | 40/42 | **42/42** | CLEAN |
| 24_address_block_indents_txtpos | 40/42 | **42/42** | CLEAN |
| 26_footnote_marker_bottom_note_txtpos | 40/42 | **42/42** | CLEAN |
| 32_serif_nondefault_body | 40/42 | **42/42** | CLEAN |
| 334_patent_document | 40/42 | **42/42** | CLEAN |
| 34_monospace_document | 40/42 | **42/42** | CLEAN |
| 37_font_not_embedded_substitution | 40/42 | **42/42** | CLEAN |
| 45_coloured_callout_box | 40/42 | **42/42** | CLEAN |
| 47_grey_body_black_headings | 40/42 | **42/42** | CLEAN |
| 53_single_space_body_15_headings | 40/42 | **42/42** | CLEAN |
| 74_balance_sheet_indented_subitems | 40/42 | **42/42** | CLEAN |
| 315_gazette_notification | 40/42 | 41/42 | `32_stroke_lines` |
| 49_coloured_background_block_paragraph | 40/42 | 41/42 | `32_stroke_lines` |
| product-catalogue-code-left-price-right | 40/42 | 41/42 | `32_stroke_lines` |

**13 documents 40/42 -> 42/42 in the renderer the user opens. `05_chars_extra` cleared on all 16.**
The results are in `benchmarks/gverify-carrier-2008/`, kept out of `benchmarks/gverify/` on purpose:
that table is HEAD's, and these were not measured on HEAD.

`05_chars_extra` and `32_stroke_lines` are one cause with two symptoms, confirmed: the anchored
`<w:drawing>` is dropped by Google (rule lost) and its anchor survives (extra character). Every
document that lost the drawing gained the rule and lost the character together.

## The three that did not clear, and what they say

Read out of the `.docx`, HEAD vs patched, `word/document.xml`:

| document | HEAD drawings | patched drawings | carriers | still failing |
|:--|--:|--:|--:|:--|
| 315_gazette_notification | 5 | 3 | 2 | `32_stroke_lines` |
| 45_coloured_callout_box | 5 | 3 | 2 | `32_stroke_lines` |
| 49_coloured_background_block_paragraph | 5 | 3 | 2 | `32_stroke_lines` |
| product-catalogue-code-left-price-right | 21 | **0** | 21 | `32_stroke_lines` |

For 315 / 45 / 49 the residual is a rule `isRuleShape` refuses — most likely a stroke-only box whose
`lineWidthPt > RULE_MAX_PT`, or a shape with `kind != 0`, or a band thinner than `hi > 2f` allows.
For `product-catalogue` all 21 drawings became carriers and the check still fails, so its rule is lost
for a different reason — a carrier that does not render, or a rule the page draws inside something
`isRuleShape` excludes. **Those two are different defects and must not be fixed as one.**

## The falsification, done before the claim

| test | predicted | measured |
|:--|:--|:--|
| `.txt` unchanged by the patch | byte-identical on all 16 | **0 of 16 differ** |
| the guard leaves the destroyed documents alone | 375: 1 table, 13 rows, 456 drawings | **1 table, 13 rows, 456 drawings, 0 carriers** |
| same, 341 / 324 | 1/25/301 and 6/246/1483 | **1/25/301 and 6/246/1483, 0 carriers** |
| every drawing removed is replaced by a carrier | equal counts | **2/2, 2/2, 3/3, 10->7+3, 21/21** |
| 13 documents reach 42/42 | 13 | **13** |

Because the `.txt` is byte-identical on all 16 and the guard restores HEAD exactly on the three
documents that hold 3608 verticals, **the txt table cannot regress and no document gets worse** — that
is the guard's whole purpose and it is now measured on a second engine build.

## What is still unproven, and it is the only thing left

**The 987 horizontal carriers in 160 documents are not measured in Google, and the engine change is not
in the table.** `regress.py --check` refuses it: *"ENGINE CHANGED (docx): table measured on
6c6cf642e13b7ed2, the tree is 78ab519d6e92a2ee"*. The 213-document pass that would stamp it is 35 min
convert + 15 min measure, and this slot had 45.

So this is a **lead with a proven fix**, not a landed fix. The next slot's whole job:

1. `git apply tools/p2w-bench/patches/rule-carrier-horizontal-only-2008.patch` — **this one, not
   `followed-by-block`**
2. `bash tools/p2w-bench/build-engine.sh`
3. the pass: `docx(deadline)` then `run(deadline)` in slices, then `rank()`
4. `regress.py --check`, `regress.py --stamp`, commit — and only then merge
   `benchmarks/gverify-carrier-2008/*.json` into `benchmarks/gverify/`
5. re-measure 315 / 45 / 49 / product-catalogue in Google against the *stamped* engine, and take
   `isRuleShape`'s three refusals one at a time

## What would prove this wrong

The 13 are 42/42 in Google on a *clean* upload of the same bytes; the export was scored against the
source PDF with `verify_google.py`, page counts matched, none refused. If a later run scores those same
`.docx` below 42/42 on a re-upload, the number here is wrong. It has not been re-uploaded twice.
