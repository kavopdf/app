# 18_displacement — the row rule is the Google charge: move it off the row's box and the pitch is fixed. The text then does not travel with it.

**22 Nov 2026 · fixer slot 22:50 → · engine HEAD `a6a5fbdc` · 4 Google round trips (2 probe documents, 2 builds
of a corpus document), LibreOffice measured on every build · all 5 probe Docs and staged files deleted after
scoring, Drive root left empty**

## Why this class, and what is actually in it

`18_displacement` is priced at **38.7 clean documents** by `classpick.py --leverage`, nearly double
`32_stroke_lines` (23.3), and **16 documents fail it and nothing else**. The class was at attempt 23, all
`lead`. That is the arithmetic reason to be here, and it is also the reason not to trust the last 23
attempts' framing: they all assumed the term to fix was the *declaration* (`w:trHeight`, dither, ladder).

Census this run, source PDFs only: of those 16, only **5 are ruled tables with a sub-point row pitch** —
`mobile-bill`, `insurance-policy-schedule`, `table-with-no-header-row`,
`bus-timetable-station-left-times-right`, `two-tables-stacked-with-no-gap`. The other 11 have 0–4
horizontal rules on their one page. So this construct's whole population is 5 documents, which is exactly
a quarter of the class — the charter's own "kept" bar — and it is worth saying before anyone spends a slot
on it: **the other 11 documents are not a row-pitch fault at all.**

## The measurement: where the charge lives

Four synthetic 13-row tables, one source pitch of 18.40 pt, one document per round trip, read off the
exported PDF's own rules. LibreOffice measured on the same file.

| variant | declared | LO laid | **Google laid** | mean |
|:--|:--|:--|:--|--:|
| control: cell borders sz 4 (0.5 pt), trHeight 18/19 | 18/19 | 18/19 | 19,20,18,20,19,18,20,19,19,19,19,19,19 | **19.08** |
| same, control repeated in a second document | 18/19 | 18/19 | identical 13 values | **19.08** |
| declare net of the rule, (t − 0.5) | 17.5/18.5 | 17.5/18.5 | 18,20,18,19,18,18,20,18,19,18,18,20,18 | 18.62 |
| declare constant (18.4 − 0.5) | 17.9 | 17.9 | 18.7 | 18.7 |
| line-driven, no trHeight, line = t − 0.5 | 17.5/18.5 | 18/19 | 19,21,19,21,20,… | 19.9 |
| cell borders sz 2 (0.25 pt) | 18/19 | 18/19 | **no rules drawn at all** | — |
| **paragraph borders instead of cell borders** | 18/19 | 18/19 | 18,19,18,19,18,18,18,18,19,18,18,19 | **18.33** |
| **same, cell margins 0** | 18/19 | 18/19 | 18,18,18,19,18,18,19,18,19,18,18,18 | **18.25** |

Three things are settled and one is refuted:

1. **LibreOffice lays `w:trHeight` exactly; it never charges the rule.** Every variant above, in both
   renderers' declarations, LO reproduced the declaration to the 0.05 pt. This is why every
   "declare it a rule short" construct regresses LO: it is subtracting a charge LO does not make.
2. **Google charges the row's own rule on top of the declaration and rounds to a whole point.** That is the
   whole of `18_displacement` on a ruled table: +0.83 pt a row, +9.1 pt at the foot of 13 rows.
3. **A paragraph border is not charged.** The same 0.5 pt rule, the same trHeight, drawn as `w:pBdr` inside
   the cells: Google 18.25–18.33 against a source of 18.40. The rule's *ownership* is the term, not its
   width, and not the declaration.
4. Refuted: thin cell borders. `w:sz="2"` (0.25 pt) made Google drop the rules entirely — the document
   loses its table grid, which is a worse fault than the pitch.

## The engine, A/B, on a real document

`two-tables-stacked-with-no-gap`, two builds of the same tree, one live round trip each, LO on both.
The patch (`FINDINGS/18_displacement-RULES-AS-PBDR-BOTTOM-2330-fixer.patch`, 51 lines, guarded by
`-Dp2w.pbdr=true`, **inert by default** — `document.xml` byte-identical with the flag off, verified).

| | LO rule positions | Google mean pitch | first rule (source 86.52) | Google dy | n_out |
|:--|:--|--:|--:|:--|--:|
| A — cell borders (HEAD) | 18.4/18.3/18.5 | **19.23** | 77.5 (−9.0) | −2.34 + 0.01414 y, med −4.66 | 55/72 |
| B — paragraph borders | **identical to A, to 0.05 pt** | **18.50** | **87.5 (+1.0)** | −11.90 − 0.00663 y, med −10.70 | **69/72** |

Both builds score **41/42, `18_displacement` the only failure** (42-check denominator, no `--docx`).

**The pitch half works and the placement half breaks.** B removes 0.73 pt a row of drift (19.23 → 18.50
against 18.40) and puts the table's top rule within 1 pt of the page's where A was 9 pt high — and then the
cell text does not travel with the rules: median dy goes from −4.66 to −10.70 and `n_out` from 55 to 69. The
rule moved from the row's box edge to the paragraph's *bottom* edge, so the row grows below its text, and
the engine places cell text at `LINE_BASE` (0.8) of the row pitch — an offset that was tuned to a box whose
bottom edge was the rule.

**Not kept.** B is worse on the check it was built for, and the charter's rule is that no document gets
worse. The patch is in this directory, off by default, one flag away.

## The next run's first round trip, and it is bracketed

Emit the rule as **`w:pBdr` TOP**, not bottom, so the row grows above the text and the text keeps the offset
`LINE_BASE` gives it — and **nil the table's own `top` side at the same time**, or the table draws two
rules at its head. That second half is already measured in LibreOffice, cheaply: a top-border build (C, `FINDINGS/18_displacement-RULES-AS-PBDR-TOP-2330-fixer.patch`)
drew **18 rules where A drew 15**, at 58.05, 93.75, 105.45, 115.35, 132.75 — the extra rules are the table
top plus the first row's own top. With the table's top side nil'd, C becomes the B experiment with the
border on the other edge, and one round trip says whether the text travels with it.

## What would prove all of this wrong

A document whose rules are drawn at a *whole* point pitch should show no charge at all — Google's rounding
would land on the declaration either way. `68_journal_wide_table_spanning` is that control: source pitch
19.00, and it fails `18_displacement` too, so if the charge theory is right its failure is not the pitch and
must be a second term. That is the measurement to run before the top-border build.
