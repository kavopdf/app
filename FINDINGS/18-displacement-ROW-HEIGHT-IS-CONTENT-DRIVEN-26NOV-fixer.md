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
