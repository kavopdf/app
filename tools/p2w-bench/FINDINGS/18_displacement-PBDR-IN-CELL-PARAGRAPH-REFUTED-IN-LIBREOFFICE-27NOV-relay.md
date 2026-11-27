# The row rule as a `w:pBdr` in the cell paragraph: the pitch is right and the PLACEMENT is wrong, in LibreOffice, on the document the lead named

**Run:** 27 Nov 2026, relay/fixer slot 09:28 IST. **Class:** `18_displacement`.
**Verdict: refuted, by the proxy that gates every commit — before a single Google call was needed.**
**Outcome: measured lead, nothing kept. The engine is byte-identical to HEAD (`git checkout -- app/`).**

---

## 1. What this run was asked to build, and on what evidence

`FINDINGS/18-displacement-PBDR-CARRIES-THE-RULE-AND-ROW-PITCH-RECONCILES-27NOV-fixer.md` (27 Nov, 09:13)
measured a three-variant probe and concluded:

> | `w:pBdr/w:bottom` on the cell paragraph | **15.00** | **15.00** |

and called it *"the exception"* to the rule that a change correct in Google is guaranteed to look like a
regression in LibreOffice, because it reads 15.00 in both:

> **B is the exception:** it measures 15.00 in LibreOffice, so it cannot be refused by the proxy.

The spec was: emit `insideH` as `w:pBdr/w:bottom` on every cell paragraph but the last row, drop
`insideH` from `w:tblBorders`, leave `trHeight` and `insideV` untouched.

## 2. What was built

Three builds of `DocxWriter.java`, all behind `-Dp2w.pbdr=true` so the tree stays inert by default
(the patch is beside this file as `...REFUTED-IN-LIBREOFFICE-27NOV-relay.patch`, 87 lines):

| build | where the rule went |
|:--|:--|
| **B** | `w:pBdr/w:bottom` on the first paragraph of every cell, every row but the last; `insideH` → `nil`; table top and bottom kept |
| **T** | `w:pBdr/w:top` on the same paragraphs; table top → `nil` |
| **B+A** | B, plus `w:after` on the cell paragraph = `rowHeight − before − line`, so the paragraph box reaches the row's bottom edge |

Measured on `303_discharge_summary` — the document the 09:13 finding named as the first proof target
(it recorded it at +2.80 pt on its last row) — rendered with LibreOffice, rules read off the exported
PDF with PyMuPDF, compared against **the source PDF's own rule boxes**.

## 3. The source, and what the unmodified engine already does with it

`303_discharge_summary.pdf` draws its five ruled rows as five **stroked rectangles**, not lines:

    (273.38 → 288.38), (288.38 → 303.38), (303.38 → 318.38), (318.38 → 333.37), (333.37 → 348.37)
    x 28.0 → 538.0, stroke 0.4 pt, pitch 15.00

The **unmodified** engine reproduces that exactly in LibreOffice:

    273.2, 288.2, 303.2, 318.2, 333.2, 348.2   x 28.0 → 538.4   pitch 15.00

**There is nothing to fix here in LibreOffice.** This document's defect is Google-only — Google charges
each row 0.75 pt for its rule — so any change to it is pure risk to the proxy and can only be paid for
by a Google gain.

## 4. What all three builds do to it in LibreOffice

| build | rule y positions (LibreOffice) | pitch | verdict |
|:--|:--|:--|:--|
| **source** | 273.38, 288.38, 303.38, 318.38, 333.37, 348.37 | 15.00 | — |
| **HEAD** | 273.2, 288.2, 303.2, 318.2, 333.2, 348.2 | 15.00 | **exact** |
| **B** (bottom) | 273.2, **284.5**, 288.4, **299.2**, **314.2**, **329.2**, 348.2 | 11.3 / 3.9 / 10.8 / 15.0 / 19.0 | 5 rules where the page draws 4, the pBdr ones **3.9 pt high** |
| **T** (top) | 273.35, **283.7**, 288.4, **298.7**, **313.7**, **328.7**, 343.7, 348.2 | 10.35 / 4.7 / 10.3 / 15.0 / 4.5 | 8 rules, the pBdr ones **10.35 pt low** |
| **B+A** (`w:after`) | 273.2, 284.5, 288.4, 299.9, 315.2, 330.6, **350.0** | 11.3 / 3.9 / 11.5 / 15.3 / 15.4 / 19.4 | rules still 3.9 pt high **and** the table grew 1.8 pt |

Cell text is byte-identical in all four builds (first twenty baselines all
22.0, 33.0, 70.0, 70.0, 70.0, 81.0, 81.0, 81.0, 92.0, 102.0, 120.1, 132.1, 151.6, 163.6, 175.1, 194.6,
206.6, 226.1, 238.1, 261.6). **Nothing here is a text problem. It is entirely a rule-placement problem.**

## 5. Why the 09:13 probe could not see this, and the method correction it needs

**A paragraph border is placed by the PARAGRAPH'S BOX, not by the row.** The cell paragraph is written
`w:spacing w:before=209 w:line=11 exact` — 10.45 pt of before, then an 11 pt line box — inside a
`trHeight` of 15.00. The paragraph's top edge is therefore ~10.45 pt below the row's top edge and its
bottom edge is ~3.9 pt above the row's bottom edge, and `w:pBdr` draws its rule on one of those two
edges. Both builds put the rule exactly there, which is exactly where the page does not draw it.

**And the probe read pitch, not position.** Three rules at 15.00, 15.00, 15.00 measure *pitch 15.00*
whether they sit on the row boundaries or 3.9 pt above all of them. A uniform offset has **zero pitch
error**. The probe's own table even shows the tell and passes over it: variant B's Google rule ys are
`237.50, 252.50, 267.50, 282.50, 297.50` — four pitches of exactly 15.00 — and it never asks where the
first one is relative to the row it belongs to.

> **The method correction, and it is the thing worth carrying forward: when a construct moves a RULE,
> measure the rule's ABSOLUTE y against the page's rule, not the pitch between rules.** Pitch is a
> difference and is blind to a constant. Two of this class's constructs now have a right pitch and a
> wrong origin, and the first one (the 22 Nov `w:pBdr` build) was diagnosed as a *text* problem when it
> was the same placement problem seen from the other end.

`w:after` cannot fix it either, and build **B+A** is the measurement that says so: extending the
paragraph box to the row's bottom edge makes the row grow (table bottom 348.2 → 350.0) before the
border arrives at the right y, because `trHeight` is `atLeast` and the renderer takes
`max(trHeight, content + after)`.

## 6. The blast radius, which is why this had to be measured before it was committed

The change would have touched **every ruled table's row separators in the corpus**: on the 213 built
`.docx` at HEAD, **284 tables**, and **177 `insideH` rules in 77 documents** (census by reading
`<w:insideH w:val="single"` in `word/document.xml`). A construct that is wrong on the first document it
is tried on, at that reach, is a corpus-wide regression — and `regress.py --check` refuses it on
LibreOffice alone, which is why this run did not need a Google round trip to stop.

## 7. What would prove this wrong

A table whose cell paragraph's box **is** the row's box — `w:before=0`, `w:line = trHeight` exact, no
`w:after` — would place a `w:pBdr` on the row's own edges. If such a document exists in the corpus and
its `18_displacement` failure is the rule charge, the construct is still available for **it**, and the
patch beside this file is the starting point. What is now measured is that it is **not** available for
the corpus's common cell paragraph, which is the one with `before=209 line=11 exact`.

## 7b. Where the construct could still be placed at all, counted

A `w:pBdr` on the cell paragraph can only land on the row's edges where the paragraph's box **is** the
row's box. Counted over the 213 built `.docx`: of the 77 documents that carry an `insideH` rule, **2**
have any ruled row whose cell paragraph satisfies that (`w:before` <= 2 twips and `before + line` >=
98 % of `trHeight`) - `041122-Account_Opening_Form` and its fillable twin, 8 rows each of 88. So the
construct cannot carry the corpus's common cell paragraph, which is `w:before=209 w:line=11 exact`
inside a 15 pt row, on either edge. That census is why this is parked for the ruled-row branch rather
than retried with a different edge.

## 8. What this run did not do

No Google call. None was needed: the proxy refuses all three builds on the document the lead named, and
the charter's rule 3 (no document gets worse) is decided by `regress.py --check`, which is LibreOffice.
The 09:13 finding's Google numbers are not contradicted — a Google pitch of 15.00 for variant B is
consistent with a rule 3.9 pt above the row boundary, because pitch does not measure origin.
