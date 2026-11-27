# A ruled row's horizontal rule costs 0.75 pt of row height in Google — until the rule is written as a PARAGRAPH border

**Run:** 27 Nov 2026, fixer slot 08:34 IST. **Class:** `18_displacement` (worth 54.4 clean documents).
**Verdict:** the first construct found in this class that reconciles **both** renderers. Row pitch
15.00 pt in Google *and* 15.00 pt in LibreOffice, from one `.docx`, with the rule still drawn.
**Outcome: measured lead.** No engine change was committed this run; the engine patch is specified
below and is the next run's first attempt.

---

## 1. What was already known, and the one cell of the table that was empty

`FINDINGS/18-displacement-RULED-ROW-PITCH-IS-GOOGLE-ONLY-27NOV-fixer.md` (27 Nov, 03:01 IST) established:

> Google lays a ruled row at `trHeight + 0.75 pt`; LibreOffice lays it at `trHeight`.

and proved it over seven variants: `hRule` irrelevant (exact = atLeast), outer box irrelevant,
and — the important one — **V9: moving the rule from `w:tblBorders/insideH` onto the cells'
`w:tcBorders/bottom` does not help.** The cost follows the rule, not the element it is written in.

That finding concluded the reconciliation was impossible:

> There is no value of `trHeight` for which both renderers produce 15.00.

and named the only escape:

> the horizontal rules have to leave the table (drawn as shapes or as paragraph rules that are not charged)

**`w:pBdr` on the cell paragraph was never tested.** It is the one construct that is a paragraph
rule *inside* the table rather than a table rule. This run tested it.

## 2. The measurement

One probe `.docx`, three variants, five rows each, every row `w:trHeight w:val="300" w:hRule="atLeast"`
(= 15.00 pt), every cell paragraph `w:spacing before=209 after=0 line=11 lineRule="exact"` (the corpus
construct), 7 pt text. Variants:

| | horizontal rule between rows carried by |
|:--|:--|
| **A** | `w:tblBorders` with `insideH` + `insideV` + outer box — the control, reproduces the known law |
| **B** | **no `w:tblBorders` at all; each cell paragraph carries `w:pBdr/w:bottom` (single, sz=3)** |
| **C** | no `w:tblBorders`; each cell carries `w:tcBorders/w:bottom` — the V9 repeat, as a control on the control |

Row baseline pitch, rows 1→4 (the pitch of the table's own rows, not the title-to-first-row gap):

| variant | LibreOffice pitch | **Google pitch** | Google row height |
|:--|--:|--:|:--|
| A — `tblBorders/insideH` | 15.00 | **15.75** | trHeight + 0.75 |
| **B — `w:pBdr` bottom on the cell paragraph** | **15.00** | **15.00** | **trHeight, exactly** |
| C — `tcBorders/bottom` | 15.00 | **15.75** | trHeight + 0.75 |

- LibreOffice measured locally: `libreoffice --headless --convert-to pdf`, baselines read with PyMuPDF.
- Google measured end to end: `upload` → `GOOGLEDRIVE_CREATE_FILE` (mimeType
  `application/vnd.google-apps.document`) → `GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE` (pdf) → read the
  export with PyMuPDF. Google baselines for B: 236.84, 251.84, 266.84, 281.84, 296.84 — four pitches of
  **exactly 15.00**.

A and C both land on 15.75, which is what makes B trustworthy: the probe reproduces the published law
on the two constructs already known to fail, and reads 15.00 on the one construct that was untested.
The difference is not a measurement artefact of this probe.

## 3. The rule is still drawn — the fix is not "delete the rules"

The obvious failure mode of a row-height fix is that the rule disappears, which trades
`18_displacement` for `32_stroke_lines` / `29_blank_where_ink_was`. It does not. Vector rules in the
two exports of variant B:

| renderer | rules in variant B | y positions | stroke width |
|:--|:--|:--|--:|
| Google | 5 (each split into two segments, `90→294` and `306→510`) | 237.50, 252.50, 267.50, 282.50, 297.50 | 1.00 pt |
| LibreOffice | 5 (same two-segment split) | 240.30 … 300.30 | 0.35 pt |

Google's 1.00 pt against LibreOffice's 0.35 pt is **not a new discrepancy**: the control variant A shows
the identical 1.00 / 0.35 pair for `w:tblBorders` rules. The stroke-width relationship is unchanged by
moving the rule to `w:pBdr`; only the row-height charge goes away.

## 4. The two differences this measurement does not clear

Stated plainly, because a lead that hides its own gaps is a trap for the next run.

1. **The rule is inset and split at the column boundary.** Google draws B's rules at x 90→294 and
   306→510, where A's table rules run 84→516 continuous. The inset is 6 pt, which is the default
   `w:tblCellMar` left/right — the probe did not zero it. The corpus's ruled tables *do* zero
   `w:tblCellMar` (the 27 Nov finding records `tblCellMar` all zero on `303_discharge_summary`), so the
   inset should vanish there. **Untested.** The split at the column boundary is a paragraph border
   cannot cross a cell, so a two-column table will draw two segments; whether Google joins them at zero
   cell margin, and whether the original PDF's rule is one continuous line, has to be measured on a
   real corpus document before the patch is trusted.
2. **Vertical rules.** `w:pBdr` gives no `insideV`. A table that draws column rules as well as row rules
   loses them unless they are carried by a different construct. `303_discharge_summary` and the other
   three documents this finding reaches all carry `insideV` as well as `insideH`. **Untested.**

## 5. Why this matters more than its four documents

The 27 Nov finding attributed **4 of the 9** documents that fail `18_displacement` and nothing else to
this construct, and said of the class: 98 recorded attempts have not closed it because they were
looking for a `trHeight` number, and for a ruled row the number does not exist. It does not exist — but
the construct does. If `w:pBdr` carries the row rule and `insideV` is solved, every ruled table row in
the corpus is laid at its true pitch in Google, and the LibreOffice proxy stops being an obstacle by
construction rather than by tuning.

`regress.py --check` gates on LibreOffice, and the 27 Nov finding's central point was that a change
correct in Google is *guaranteed* to look like a regression in the proxy. **B is the exception:** it
measures 15.00 in LibreOffice, so it cannot be refused by the proxy. That is what makes it worth the
next run.

## 6. The engine change, specified but not written

In the table-emission path (`DocxWriter.java`, the `w:tblBorders` block): when a table's horizontal
rule is `insideH`, emit it as `w:pBdr/w:bottom` on **every cell paragraph of every row but the last**,
and drop `insideH` from `w:tblBorders`. Keep `w:trHeight` exactly as it is — that is the whole point;
no number moves. Leave `insideV` on `w:tblBorders` for the first attempt, so the change is one rule and
its effect is measurable in isolation.

Prove it, in this order, before committing:

1. `303_discharge_summary` — the document the 27 Nov finding measured at +2.80 pt on its last row
   (4 rows × 0.70). Expect the row pitch to go 15.75 → 15.00 in Google and `18_displacement` 46/47 → 47/47.
2. `320_balance_sheet_statutory` — a different table shape, to test the cause rather than the document.
3. `regress.py --check` on the full corpus: it must pass, and B is expected to pass it because
   LibreOffice's page is unchanged.

**What would overturn this:** if the inset rule of §4.1 measures as visibly short of the table edge on a
corpus document with zero cell margins, the construct trades a 0.75 pt pitch error for a rule that does
not reach the edge, and the trade has to be weighed against `32_stroke_lines` before it is committed.

## 7. The instrument this run re-confirmed

The Google after-side is reachable from a fixer slot in about 90 seconds a document, with the platform
`upload` tool staging the file **from `/scratch/output`** first (`upload(path=..., tool_slug=
"GOOGLEDRIVE_CREATE_FILE", toolkit="googledrive")` → `s3key` → `GOOGLEDRIVE_CREATE_FILE` with
`mimeType="application/vnd.google-apps.document"` and `parents=["1OoSHtsv-qEUwk8CnNa9d5hsCKu8PFeij"]` →
`GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE` → `artifacts[0].workspace_path`, which lands under
`/scratch/downloads/composio/` and must be copied before it is read). Measured working on this pod,
27 Nov 08:5x IST.
