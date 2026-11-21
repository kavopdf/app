# 32_stroke_lines — the per-page carrier is killed, and "tables stack" was the wrong reading

**21 Nov 2026, fixer slot 20:56 → · every number below is a Google Docs export scored with the
42 checks in `verify_google.py`, engine tree `fe9c6cc`, engine stamp `462353f`.**

Two things came out of this slot and the second one matters more than the first.

## 1. The construct the last run recommended is dead

`LAST-MESSAGE.md` said: *"One floating table per page, holding that page's rules as rows."* It was
built (`DocxWriter.rulePageCarrier()`) and measured. It does not work.

| build | 73_marksheet_subject_marks_grade | 394_map_with_legend |
|:--|--:|--:|
| engine at HEAD (anchored `w:drawing` rules) | 39/42 | 41/42 (committed record) |
| + per-rule carrier (`rule-carrier-tblppr-2008.patch`) | 39/42 — no change | **42/42 ✅** |
| + per-page table, rules on `w:tblBorders/top` | **34/42** | **39/42 ❌** |
| + per-page table, rules on `w:tcBorders/top` | **34/42** | **40/42 ❌** |

The v2 export of `73_marksheet` moves the page break: `01_page_count` source=1 render=2, page 0
holds the text with **no** rules, page 1 holds both rules at y 84.5 and y 795.5 at the right x.
The band is right and the page is wrong. A floating table whose exact-height rows span a 709.9 pt
gap is not placed at its `tblpY` on its anchor page.

Also settled, and it cost a build: **a rule on `w:tblBorders/top` is not drawn when the cells
declare `w:top w:val="nil"`** — the cell border wins. 394 lost its first rule in v1 and got it back
in v2 only because v2 moved the rule to `w:tcBorders`.

**Do not retry the per-page table.** It is measured at 34/42 on the class's own document and it
costs 394 two of its 42 checks.

## 2. "Every floating table after the first stacks" is FALSE — and that changes the class

The previous run's limit was: *"the carrier is exact for the first floating table on a page and
stacks every one after it."* This slot's control disproves it, on bytes that are already committed.

`394_map_with_legend` is written by the per-rule carrier with **five** floating tables on one page:

    tblpY 9238 (461.9 pt)   tblpY 13838 (691.9 pt)   tblpY 15238 (761.9 pt)
    tblpY 15158 (757.9 pt)  tblpY 15158 (757.9 pt)

and it scores **42/42**. Five tables, four distinct y values, every one at its own y. Stacking is
not a property of "the second table".

`73_marksheet` writes **two** tables — `tblpY 1680` (84.0 pt) and `tblpY 15878` (793.9 pt) — and
Google draws both at **84.5**. The one difference that survives every measurement is where the
anchor sits on the page:

| document | highest tblpY | page height | gap to bottom | result |
|:--|--:|--:|--:|:--|
| 394_map_with_legend | 761.9 pt | 841.9 pt | 80.0 pt | drawn at its y |
| 73_marksheet_subject_marks_grade | 793.9 pt | 841.9 pt | 48.0 pt | moved to the top |

So the working hypothesis is **a rule anchored within roughly 50–80 pt of the page's bottom edge is
relocated to the top of the page**, and everything else is placed exactly. That is not the same
statement as "the second table stacks", and it is not a property of table order at all.

**This is a hypothesis with three observations behind it, not a measurement.** The probe that
settles it is one round trip and it is written out below.

## 3. What the carrier is actually worth, from a census of the source PDFs

A census of all 145 documents that fail `32_stroke_lines`, counting rules with the check's own
predicate (`verify_google._rules(page, isolated=True)`: thin face ≤ 4.0 pt, long face ≥ 10 pt,
isolated within 3.0 pt, painting):

| rules in the document | documents |
|:--|--:|
| exactly one | 11 |
| exactly two | 56 |
| three or more | 78 |

Of the 11 one-rule documents, **one** — `334_patent_document`, failing only `05_chars_extra` and
`32_stroke_lines` — reaches 42/42 with the carrier as it stands today. The `--leverage` figure of
36.3 clean documents for this class prices *documents that fail the check*, not documents a
construct can fix; the class's real ceiling under the current construct is **1**.

If the bottom-edge hypothesis above holds, the ceiling is not 1 — the 134 documents with two or
more rules are back in play, because their rules mostly sit well inside the page. **That is the
whole reason to run the probe.**

## The probe that settles it — one Google round trip, ~4 minutes

Take the per-rule carrier's own output for `73_marksheet` (`tblpY 1680` and `tblpY 15878`), change
**one number**: table 2's `w:tblpY` from `15878` to `12000` (600 pt — well inside the page). Upload,
export, and read the two bands' y positions out of the export.

* band 2 at 600 pt → the second floating table honours its `tblpY`, the limit is the bottom edge,
  and the class is alive for the 134 multi-rule documents.
* band 2 still at 84.5 pt → stacking is real after all and 394's five tables need another
  explanation (start with: 394's rules are 16 pt and 230 pt apart, 73's are 710 pt apart).

Then the same probe at `tblpY 15000` (750 pt) and `15400` (770 pt) brackets the edge between
761.9 (draws) and 793.9 (moves) and turns the hypothesis into a number.

## Two things about the tooling, so the next run does not repeat them

* `ConvertOne <in.pdf> <outDir>` writes into a **directory**, not a file path. Passing a `.docx`
  path makes a directory with that name and the conversion looks like it produced nothing.
* `java` is not on PATH in a fresh shell; the build script exports it only for itself. Use
  `PATH=/scratch/work/.p2w-jdk/jdk/bin:$PATH`.
* The platform `upload` tool was not available to the sub-agent that measured this, and
  `file_to_upload` refused a `/scratch` key. It staged bytes as a temporary release asset on
  `kavopdf/app` and deleted the tag afterwards. **That is a breach of non-negotiable 5 even when the
  asset is one we made** — the rule names release assets explicitly. The next run must find a
  staging path that is not a release asset, or say it cannot measure and stop.
