# `60_text_column_right_edge` — Google honours a right tab stop to 0.11 pt; the reader cannot see it

**27 Nov 2026 · fixer · engine d28ca7516c3f9165 (HEAD, unmodified) · proof document `321_auditors_report`**

## What was measured, and in what order

Three renders of the same source, all scored with `verify_google.py` in one session, all from the
same compiled engine except where stated. Every "after" number has a control taken in the same hour
on the same engine, because the stored row was on `74a152e7d3fb3d26` and an engine has moved twice.

| render | what it is | 42-check score | fails |
|---|---|---|---|
| **control** | engine as it stands, no change | **41/42** | `60_text_column_right_edge` |
| **A** | last inter-word space → space + `<w:tab/>` | 40/42 | `60`, `17_matched_runs` |
| **B** | last inter-word space → `<w:tab/>` alone | 40/42 | `60`, `17_matched_runs` |

A and B are geometrically identical, so the space before the tab is not what moves anything.

## The construct

`flowFromBox` writes no right edge for a left-aligned body line: `rightTw = 0`, no `w:jc`, and
`w:pgMar w:right="0"`, so the line ends wherever the renderer's substitute face advances to. On
`321` the source body column's right edge is **538.61 pt**; the unmodified Google render's is
**473.00 pt** — **65.61 pt of the line simply not there**.

The change: for `p.align == 0`, not in a column, not rotated, not a ring character, and **not** a
base-14 metric family (Arial / Helvetica / Times / Courier / Symbol — those already land where the
page drew them), write

    <w:tabs><w:tab w:val="right" w:pos="{round(b.right * 20)}"/></w:tabs>

before `w:snapToGrid`, and turn the box's last inter-word space into a `<w:tab/>`. `w:pgMar w:left`
is 0 on every page this writer emits, so the stop is `b.right` itself. `google_safe.py`'s IGNORED
list has no `w:tabs` entry, so the construct is permitted.

## What Google did with it — measured from the exported PDF's own operators

`rawdict`, span origins, not the line grouping:

| | text before the tab | trailing word |
|---|---|---|
| baseline y | 84.73 | **84.73** — the same line |
| font / size | ArialMT 9.5 | ArialMT 9.5 |
| right edge, line 1 | — | **309.00** where **309.00** was asked |
| right edge, line 5 | — | **538.50** where the source drew **538.61** |

**Google honours a right tab stop in a body paragraph to 0.11 pt.** That was open question #2 in
`60-EDGE-AUDIT-27NOV.md` ("whether Google honours `w:tab w:val="right"` — the left flavour is
measured, the right flavour is not anywhere in the repo"). It is answered: yes, exactly, and the
trailing word stays on its line.

## Why the run still read 40/42: the reader, not the renderer

`page_lines()` (`verify_google.py:2660`) takes one bbox per **PyMuPDF `line`**. PyMuPDF splits a line
at a horizontal jump, so the tabbed line comes back as two entries — `x0 57.00 x1 239.54` and
`x0 278.40 x1 309.00`, both `bottom 86.75`. Taken as two lines:

* the fragment at `x0 278.40` forms its own one-line left-edge cluster and is dropped by
  `COL_MIN_LINES = 3`, so its right edge is never seen;
* the real column's widest line stops at **239.54** instead of **309.00**, and `60` charges an
  underrun the page does not have;
* the line count doubles, **34 → 62**, and `17_matched_runs` loses the pairs.

**Tested.** A local copy of `verify_google.py` whose `page_lines()` merges lines with the same
`bottom` within 1.0 pt and a gap under 200 pt:

| render | merged reader | fails |
|---|---|---|
| control | 41/42 | `60` |
| **A (space + tab)** | **41/42** | `17_matched_runs` — **`60` PASSES** |
| **B (tab only)** | **41/42** | `17_matched_runs` — **`60` PASSES** |

Merged line sets, one per render: source 34 lines / max right **538.61**; control 34 / **473.00**;
tabbed 34 / **540.99**. The control is unchanged by the merge, so the merge is not a blind pass.

## The one failure left, and it is a different check

`17_matched_runs` needs `matched >= ceil(0.9 * len(s_runs))` (`verify_google.py:5799`). The tab
splits one source run into two pieces in Google's export, and only one piece is taken per source run
(`taken[i] = j`), so the ratio drops under 90 %. This is the run-matching rule, not the edge: it is
the same failure shape the Arial re-face produced on `RIGHT-TAB-POSITION-60-EDGE-27NOV-fixer.md`
(`17_matched_runs` 33 → 21), and it is why that re-face could not ship.

## What the next run should do, in this order

1. **Fix `page_lines()` first.** It is an instrument defect with a measurement: a render whose body
   edge is right to 0.11 pt is charged an underrun, and every check that counts lines sees double.
   It is one function, it changes nothing on a render without tabs (control 41/42 both ways), and it
   is worth 60 documents' verdicts being true. It needs a corpus pass before commit, not a document.
2. **Then re-measure the tab** on the merged reader. It is a **1-document move on `321` today**
   (41/42 either way, one failure swapped for another) — not a fix until `17_matched_runs` is
   satisfied.
3. **`17_matched_runs` is the thing to solve** for this family: either the piece matcher should let
   one source run be satisfied by the concatenation of consecutive render pieces on the same
   baseline, or the engine should place the trailing word without a tab. Do not ship the tab alone.

## What this refutes

* "A tab stop cannot place a body line's right edge in Google." **False** — 0.11 pt.
* "`w:val="right"` is normalised away like `w:jc="distribute"`." **False.**
* "The tab wraps the trailing word onto a new line." **False** — the baselines are identical; the
  wrap was a reading of PyMuPDF's line grouping, and it cost this run a wrong first conclusion.
* Nothing here says `60` is a Google-side limit. It is not: the edge is placeable and the engine
  does not place it.

## Artifacts (this run, in the Drive verify folder `1qAl4xzzU-FOl6E2nAv8PuZ6GaBpjsXCA`)

`321_auditors_report` (control), `321_auditors_report_ctl`, `321_auditors_report_nospace`.
The engine change is **not** in the tree: it made `321` 41/42 → 40/42 on the reader as it stands,
which is a Google regression, and the gate is right to refuse it.
