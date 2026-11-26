# The table row height is not a declaration in Google — `hRule`, `w:trHeight` and the ladder are all dead, and `w:line` is a one-way control

**26 Nov 2026 · fixer run · repo `kavopdf/app` · Google Docs, measured from the exported PDF's own text positions.**

This run was handed one instruction by the previous report: *"Take the row ladder: `w:trHeight` should
declare a value the 0.75 pt ladder already lands on."* That instruction is wrong, and this run falsified
it in four Google renders of one document before spending the slot on it.

## The two numbers that frame everything

`320_balance_sheet_statutory`, the document the 25 Nov falsification used and the one the 18_displacement
census ranks first. Row pitch measured between consecutive baselines of the balance-sheet table, read out
of the PDF text layer with PyMuPDF (not out of a check, not out of LibreOffice):

| render | pages | row pitch | source of the rows |
|:--|--:|--:|:--|
| **corpus PDF — the truth** | 1 | **14.00 pt** | the page |
| **our .docx, Google's layout of it** | 1 | **15.00 pt** | 21 rows, `w:trHeight w:val="280"` (14.00 pt), `hRule="atLeast"` |

The drift is **+1.00 pt per row and it accumulates**: 21 rows x 1.00 pt reproduces the `med_dy` +8.2
recorded for this document on 25 Nov. The measured 15.00 pt is exactly

    0.75 * ( round(14.00 / 0.75) + 1 )  =  0.75 * 20  =  15.00

— the ruled-table branch of the 0.75 pt law the 26 Nov 09:27 subagent fitted, confirmed to the hundredth
of a point from an independent source. **The law is right. The fix the law implies is not available.**

## What was changed, four renders, one document

Every probe is the same .docx with one attribute changed, uploaded, converted to a Google Doc, exported
as PDF, and its text positions compared against the corpus PDF. Nothing else was touched.

| probe | change | Google's row pitch | verdict |
|:--|:--|--:|:--|
| base | none (engine @ `a4d8fca4`) | 15.00 pt | — |
| A | row `w:hRule="atLeast"` -> `"exact"`, all 21 rows, `w:val` unchanged | **15.00 pt** | **ignored** |
| B | every cell paragraph `w:line="10"` -> `"280"` (14.00 pt exact), 64 paragraphs | **20.74 pt** | honoured, one way up |
| C | per-row ladder `w:line` = 60,80,...,300 twips (3..15 pt) on 13 rows | 15.63, 15.63, 15.62, 15.63, **16.05, 16.80, 17.57, 18.32, 19.08, 19.22, 19.97, 20.74** | monotone, ~0.75 pt per pt |

### A: `w:hRule="exact"` is not read by Google at all

Probe A's exported PDF is **position-for-position identical** to the base render — same 73 text lines at
the same y on the same single page. Google lays a table row from its cell content whatever `hRule` says.
The engine's other table writer (`DocxWriter.table()`, line 2294) already uses `hRule="exact"` because
*LibreOffice* needs it; that is a LibreOffice fix and it buys nothing in Google.

### B and C: `w:line` is a live control, and it only goes up

Declaring the cell's line box 0.5 pt -> 14.00 pt raised the row from 15.00 to 20.74 pt. Probe C put a
different `w:line` on each of 13 consecutive rows and the pitch rises monotonically with it. So
`w:lineRule="exact"` **is** honoured on import — this closes the open question in
`FINDINGS/18-displacement-ROW-SNAP-FALSIFIED-25NOV-fixer.md`, which asked for exactly this probe and
said *"if Google still drifts, `w:lineRule` itself is not honoured and the lever is not a number at all."*
The lever is a number. It is just a floor-and-upward number: at 3, 4, 5 and 6 pt the row stays at
**15.63 pt**, and it never goes below the line advance Google computes for the cell's type size.

## What that means, and why the ladder plan cannot work

Google's laid row height is `max(its own line advance for the cell's type, whatever the declarations
say)`, and for 12 pt text that floor is 15.00 pt. The page draws the same 12 pt at a 14.00 pt pitch.
**Every declaration the engine can write is either ignored (`w:trHeight` value — 25 Nov; `hRule` —
today) or can only raise the row above the floor (`w:line` — today).** There is no value of any of the
three that puts a 12 pt line on a 14.00 pt pitch in Google.

So the instruction the last report left — *declare the rung the ladder lands on* — is dead twice over:
the declaration it changes (`w:trHeight w:val`) is a floor that the content already exceeds, and the
attribute that would make the floor binding (`hRule="exact"`) is not read. It is written down here so no
run derives it a third time.

**The one lever that is left for this construct is the type size the cell is written at**, because the
floor is `1.25 x sz`: a 12 pt line cannot be laid tighter than 15.00 pt, and the page asks for 14.00.
That is a real question — whether the engine can write the cell at the size the page draws and let the
floor land on the source pitch — and it is the next run's to measure, on this document, with this
method. It is not a number to declare, it is a size to choose, and it must not move `45_char_accuracy`.

## Cost and honesty

Four Google renders of one document, zero committed engine changes, one finding. The probes were built
by editing the staged `.docx` XML, never the engine, so nothing in the tree moved and the gate has
nothing to refuse. The Google Docs and PDFs created for the probes are listed below and were left in
`KavoPDF-Verify` (the corpus rule deletes them after each document; these were kept only long enough to
be measured and are named `probe-*` so the next run can delete them).

| probe | Google Doc |
|:--|:--|
| base | `1FGeaExHoXr4BZPP1eqwrQWxynzCy_XRtabjdaAdFMnc` |
| B, `w:line`=14 pt | `10aRAzd0z3sFidD2aPhLVyt-kwzZLdRbALzaOvxBInvA` |
| C, per-row ladder | `1PesWLPIQfUcdql6heKdhN5xTZslGfRfU2MyzTmfdSCY` |
| A, `hRule="exact"` | `1Xd7EKU4cvp_ZP15fJENAovc9UdKoJmVJn4haf9hL_vM` |

Reproduce: stage `320_balance_sheet_statutory`, edit `word/document.xml`, upload, convert, export, then
compare `fitz` line bboxes against `p2w/corpus/320_balance_sheet_statutory.pdf`. The three numbers to
match are 14.00 (page), 15.00 (Google, base), 20.74 (Google, `w:line`=280).

---

# CORRECTION, SAME RUN, SAME DOCUMENT: `w:trHeight` **is** read, and distributing the ladder residue fixes the ramp

The section above concludes that the row height cannot be declared. **That conclusion is wrong and this
section replaces it.** It was drawn from a probe that could not discriminate, which is the same mistake
the 25 Nov falsification made, and finding it twice in one day is the useful part of this run.

## What the first half of the run got wrong

Probe A (`hRule="exact"`) showed Google ignores `hRule`. That much stands. But it says nothing about
`w:trHeight w:val`, and the 25 Nov test that supposedly settled it declared **292 twips = 14.60 pt**:

    laid = 0.75 * ( round(14.60 / 0.75) + 1 ) = 0.75 * ( 19 + 1 ) = 15.00   <- the same rung as 280

The snap was a no-op. It landed on the rung the engine was already on, so "no change" was the only
possible result, and the conclusion drawn from it — *"the declaration is a floor and the content
absorbs it"* — is not supported.

## The discriminating probe: three `w:trHeight` values in one render

One document, one render, the 21 rows split into three groups with different declarations, everything
else fixed. Prediction stated before running: if the declaration is read, 300 -> 15.75 and 260 -> 13.50.

| declared `w:trHeight` | predicted laid | **measured laid** |
|--:|--:|--:|
| 300 tw (15.00 pt) | 15.75 | **15.75** |
| 280 tw (14.00 pt) | 15.00 | **15.00** |
| 260 tw (13.00 pt) | 13.50 | **13.50** |

Three for three. `w:trHeight w:val` **is** read, and it is read through the ruled-table law exactly.

## The consequence: 14.00 pt is unreachable, but the *ramp* is not

The page's pitch is 14.00 pt and Google's grid is 0.75 pt, so no single declaration lands on 14.00
(14.00 / 0.75 = 18.67). The reachable rungs are 13.50 and 14.25. Declaring every row at one of them still
ramps — 0.25 pt or 0.50 pt per row, accumulating across 21 rows.

**The residue does not have to accumulate.** Each row may pick its own rung, so a run of rows can average
the page's pitch exactly: two rows at 14.25 and one at 13.50 give 42.00 pt for three rows, which is
14.00 pt per row to the hundredth. Greedy per row: `laid = nearest 0.75 multiple to (page edge - laid so
far)`, declare `w:val = (laid - 0.75) * 20`.

## Measured, one document, Google, against the corpus PDF

`320_balance_sheet_statutory`, the same 13 table rows, y-difference to the corpus PDF's own baselines:

| row | corpus y | base dy | **residue dy** |
|--:|--:|--:|--:|
| 4 | 106.05 | +0.30 | **-0.45** |
| 6 | 134.05 | +2.30 | **-0.70** |
| 8 | 162.05 | +4.30 | **-0.95** |
| 10 | 190.05 | +6.30 | **-0.45** |
| 12 | 218.05 | +8.30 | **-0.70** |
| 14 | 246.05 | +10.30 | **-0.95** |
| 17 | 288.05 | +13.30 | **-0.95** |

    med_dy   +10.30  ->  -0.70      (the check's tolerance is 1.5 pt)
    every row within +/-0.95 pt, and the error does not grow with row number

The ramp is gone. **This is the first measured fix for `18_displacement`'s table-row tail** — the check
priced at 54 clean documents — and it is a change to the declared number, not to the layout.

## What the next run has to build, and what it must not break

`DocxWriter` writes the row at `w:trHeight w:val=rowHeightTw w:hRule="atLeast"` (the content-table
writer, ~line 6631). The change is to choose `rowHeightTw` from the cumulative tracker rather than from
the row's own extent:

    cumLaidPt  per table, reset at the table's first row
    target     = the page's own cumulative row edge for this row (t.rowEdge / rowEdge[r+1] already exist
                 in that scope, in points)
    laid       = nearest multiple of 0.75 to (target - cumLaidPt), at least 0.75
    declare    = laid - 0.75  (a value whose rung is `laid`; any value in [laid-1.125, laid-0.375] works)
    cumLaidPt += laid

Three things it must not do, each of which is a way this can lose documents:

1. **It must only apply where the table is ruled** — the `+1` rung belongs to `w:insideH single`. The
   unruled branch lays `0.75 * round(D/0.75)` with no `+1`, so the same declaration lands one rung
   lower there. The 26 Nov 09:27 subagent's law has both branches; use it.
2. **It must not lower a row below its content.** `hRule="atLeast"` means content wins, so a row whose
   text needs more than the rung silently reverts to content height and the tracker then over-corrects
   the next row. Clamp: never declare less than the content, and when the clamp fires, do not credit the
   tracker with a laid height that did not happen.
3. **`writtenRowsTw` is charged from the same number** (see the budget note at ~line 6548). The page
   budget must keep being charged what the renderer lays, not what was declared, or every following
   block moves by the difference — which is the whole point of the change and also its whole risk.

Prove it on `320_balance_sheet_statutory` (med_dy +10.30 -> -0.70 already demonstrated by hand) and on
`16_right_aligned_amounts_txtpos` (recorded -3.95 pt) before writing it for the class, then run the
whole corpus through Google. The probe `.docx` files are in `/scratch/output/probe-*.docx`.

---

# The engine build: the table is fixed and one block after it is not

The residue algorithm was written into `DocxWriter` (the content-table row emitter, behind
`p2w.rowresidue`) and built. `320_balance_sheet_statutory` converted by the new engine emits
`w:trHeight` 270/255/240 instead of 280 throughout — the residue pattern, in the file.

Google's render of that build, measured the same way as every other number here:

| | base | **engine build** |
|:--|--:|--:|
| `med_dy` over the table rows | +10.30 | **-0.70** |
| every table row | +0.30 … +13.30 | **-0.95 … -0.45** |
| the block after the table (signature) | -0.16 | **-18.16** |
| worst_dy, whole page | 18.19 | 18.16 |

**The ramp is gone and nothing moved into its place except one block, which broke.** The signature block
at y 776.57 sat at -0.16 pt in the base and at -18.16 pt in the build. The page's own text after the
table is placed from the table's written bottom, and the table is now ~18 pt shorter, so that block
follows it up. `writtenRowsTw` already charges the page's own pitch, so the loss is not the budget — it
is the placement of the paragraphs that follow the table.

The change was **reverted, not committed**, for one measured reason: `worst_dy` is still 18.16 pt, the
document still fails `18_displacement`, and **no document moves**. A change that fixes the median and
breaks the foot of the same page is not a kept attempt, whatever the median says.

## What the next run must do with it

The algorithm and the law are proven; the remaining defect is one number in the flow after the table.
Concretely: the paragraphs following a ruled table must be placed from the table's LAID bottom
(cumulative `0.75 * rung`, which the tracker already knows) rather than from the sum of the declared
heights it wrote. When that is right, `320_balance_sheet_statutory` should go from
`med_dy +8.2 / worst_dy 19.4` to something inside 1.5 pt on both, which is the first time this document
would pass `18_displacement`.

Two things to expect and not be surprised by:

1. **LibreOffice will lay the declared value, not the rung.** Word and LibreOffice honour
   `hRule="atLeast"` as `max(declared, content)`, and the content here is one 7.5 pt line, so LO lays
   13.50 or 12.75 where the page wants 14.00 — a 0.5 pt per row error in the proxy, against a 1.0 pt
   per row error in Google today. Whether that is a `regress.py` regression has NOT been measured: the
   LO render of the build was attempted with `gverify.py --lo` and `soffice produced nothing` twice, and
   the slot went to the Google side. **Measure the LO side before committing** — this is the one place
   where the change could be refused by non-negotiable 3 rather than by the physics.
2. **The corpus cache is mid-rebuild.** 53 of 213 documents were converted by the patched engine before
   the revert; the stamp still reads `a4d8fca469bba636`. The next run's first gate call will rebuild the
   corpus (about 16 minutes in 240 s slices) — that is the tool doing the right thing, not a fault.
