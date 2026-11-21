# The carrier places ONE of a page's rules: 7 documents are one construct from clean

**21 Nov 2026 · relay slot 23:19 → · every number is a Google Docs export scored with the 42 checks**

## What was measured

`patches/rule-carrier-per-rule-2008.patch` was applied to HEAD `44abc5d`, the engine built, and 11
documents uploaded to Google Docs one at a time and exported. Baseline is the committed
`benchmarks/gverify/*.json`.

| document | committed | with carrier | with carrier + `05` correction |
|:--|--:|--:|--:|
| `394_map_with_legend` | 41/42 | **42/42** | 42/42 |
| `45_coloured_callout_box` | 40/42 | 41/42 | **42/42** |
| `51_two_cm_margins` (clean control) | 42/42 | **42/42** | 42/42 |
| `17_three_column_widths_txtpos` | 40/42 | 40/42 | 41/42 |
| `18_centred_heading_left_body_txtpos` | 40/42 | 40/42 | 41/42 |
| `19_hanging_indent_txtpos` | 40/42 | 40/42 | 41/42 |
| `24_address_block_indents_txtpos` | 40/42 | 40/42 | 41/42 |
| `26_footnote_marker_bottom_note_txtpos` | 40/42 | 40/42 | 41/42 |
| `53_single_space_body_15_headings` | 40/42 | 40/42 | 41/42 |
| `74_balance_sheet_indented_subitems` | 40/42 | 40/42 | 41/42 |
| `73_marksheet_subject_marks_grade` | 39/42 | 39/42 | 40/42 |

**Nothing got worse.** The clean control stayed 42/42, and the carrier is worth two clean documents
(`394` on its own, `45` once `05` stopped counting tabs).

## Why the other seven still fail, and it is one number

`32_stroke_lines` on those documents reads `{"source": 2, "render": 1}`: the page draws two rules, the
carrier emitted two floating tables, and **Google placed one of them**. On `45` it reads
`{"source": 2, "render": 0}` and passes.

So the construct is not wrong — it is placed once per page and then not again, on these documents.
`394` places five on one page and scores 42/42, so it is not a count limit either. The difference is
that `394`'s five are all at the top of an otherwise empty map page, while `17`/`53`/`74` put one rule
inside or beside a real table.

**The next probe is not another construct.** It is: where does the second carrier's anchor paragraph
sit in these documents, and does Google drop a floating table whose anchor is inside a `w:tbl`? One
document, two anchors, one at the top level and one inside the table, is a single Google round trip
and it settles whether the fix is "anchor carriers in the body, never in a table".

## Why the patch is not landed

It changes the construct on 146 documents that carry a rule and only 9 of those were measured through
Google. "No document gets worse" cannot be asserted for the other 137 in one slot, so it stays a
measured lead with its table — not a revert, and not a claim.

The `05` correction it was measured alongside **is** landed: it is a verifier change, provably
symmetric, and worth 11 of 11 documents with no count going down.
`FINDINGS/05_chars_extra-TABS-ARE-ZERO-WIDTH-SPACES-2350-relay.md`.
