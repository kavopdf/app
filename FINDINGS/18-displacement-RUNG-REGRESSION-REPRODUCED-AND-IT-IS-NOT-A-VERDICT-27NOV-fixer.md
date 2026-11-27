# The rung regression is real, it is 18 rows not 5, and `worst_dy` is what overstated it

**Run:** 27 Nov 2026, fixer slot 05:56 IST. **Engine:** HEAD `a4d8fca469bba636` + the re-applied rung patch.
**Status:** the change is still NOT landable. What changes is the reason, and the size of the harm.

## 1. The control is real: `-Dp2w.rungTw=0` is byte-identical to HEAD

```
HEAD  word/document.xml  108412 bytes  sha256 e162166f81c9d2d5…
base  word/document.xml  108412 bytes  sha256 e162166f81c9d2d5…   (patched tree, rungTw=0)
IDENTICAL: True      mobile-bill.txt identical too (8455 bytes both)
```

Every part of the `.docx` zip is identical between HEAD and half A except `word/document.xml`.

## 2. The last run's "five rows, 2.5 pt" is wrong. It is eighteen rows, 9 pt.

The last run wrote: *"on mobile-bill the patch changed exactly five rows, 360 → 350 twips, i.e. 0.5 pt each,
2.5 pt in total, in the direction that moves content **up**, not down. A 0.5 pt row change produced a
56.7 pt page movement, so the movement is not coming from the row heights at all."*

Counting every `w:trHeight` in order, HEAD against half A:

```
head  : 360 360 380 360 380 | 360 360 380 360 380 | 360 360 380 360 380 | 360 360 380 360 380 | 360 360 380 360
halfA : 350 350 370 350 380 | 350 350 370 350 380 | 350 350 370 350 370 | 350 350 380 350 370 | 350 350 370 350
```

**18 of 24 rows drop 10 twips**, and two `w:before` values rise 10 twips (`267 → 277`, `234 → 244`).
Net: 18 × −0.5 pt = −9 pt, plus +1 pt of spacing ≈ **−8 pt of page height**.

The movement is not a puzzle at all. It is the row heights, at exactly the size they were changed, and it
only looked impossible because the count was five instead of eighteen. **A run reading "2.5 pt cannot do
that" would have spent a slot hunting a phantom. The row count is the whole of the previous run's mystery.**

Measured independently in the two Google renders with PyMuPDF (not the harness), the page's line pitches
go from `19.1 / 19.2 / 18.9` to a flat `18.4` on the affected rows, and the last text block on the page
moves from y 811.3 to 801.0 — **−10.3 pt**, cumulative down the page, exactly as 18 shortened rows predict.

## 3. `worst_dy 66.7` is not a 66.7 pt displacement — it is a mispaired run

Both renders are one page, 115 text runs, and **every one of the 115 runs in half A has a text twin in
HEAD**. Pairing them by exact text and reading the y of each:

```
moved runs: 101 of 115
max |dy| over text-matched pairs: 10.3 pt
```

So no run in the document moved more than 10.3 pt, and yet `18_displacement`'s `worst_dy` reports **66.7**
for the same two PDFs. A number that is 6× the largest real movement can only come from a **pair whose two
members are different text** — and mobile-bill is full of candidates: the cell value `0.00` appears five
times, `—` and `Unlimited` four times each. Once every line on the page shifts by 10 pt, a run can be
matched to the next occurrence of the same string 60 pt away.

`worst_dy` is a *reported, never-scored* diagnostic (`verify_google.py:5897`: "reported and never scored"),
so no verdict moved — mobile-bill is 46/47 failing `18_displacement` before the patch and 46/47 failing
`18_displacement` after it, and 303_discharge_summary goes 46/47 → 47/47. **On checks it is one clean
against zero worse.** The revert was taken on a diagnostic that is inflated 6× by its own aligner.

**But the revert is still right**, and this is the part that must not be lost: the real harm is −4.7 pt of
median displacement (−6.0 → −10.7) on top of a document already 6 pt out. That is a genuine step away from
the goal of 99 %, even though no check can see it. **The gate cannot protect this class; a fixer has to.**

## 4. Why the rows come out short — the lead for the next run

The patch rounds the *laid* height to the rung and then subtracts the rule to get the declaration:

```
rowHeightTw = max(typeFloorTw, RUNG * round(max(wantTw, mustTw) / RUNG) - ruleTwHere)
```

`mustTw = rowLineTw + ruleTwHere` is the engine's estimate of the content floor, and on mobile-bill it is
**short**: the declaration chosen is 350 twips + 15 rule = 365 twips laid, while the content actually
occupies 368 twips (18.4 pt measured). The row is declared 0.7 pt under its own content, 18 times, and
Google takes the difference out of the flow below.

Before this patch nobody could see the shortfall, because the declarations (360, 380) sat *above* the
content and `atLeast` hid it. The rung change lowers the declaration to the rung and thereby exposes an
under-estimate in `rowLineTw` that has been in the engine all along.

**Next test, and it needs no corpus and no Google round trip per document:** for the 18 changed rows, print
`wantTw`, `mustTw` and the measured `rowEdge` delta side by side. If `mustTw` is under `wantTw` on all 18,
the guard is one line — take the content floor from the measured row pitch (`wantTw`) rather than from
`rowLineTw`, which is what the code already computes and then overrides. Then re-measure mobile-bill and
303 through the same probe path this run used.

## 5. Instrument defect found on the way: the Drive corpus folder holds duplicates

`GOOGLEDRIVE_FIND_FILE` over the corpus folder `1qAl4xzzU-FOl6E2nAv8PuZ6GaBpjsXCA` returns **471 files**,
not 213, and **31 names appear twice**. Example:

```
mobile-bill.docx  1QKksFbffl6XB7W5TAmaAfVwhx84ZgtoV  2026-11-25T04:50:14Z  11446 bytes
mobile-bill.docx  1vq3637yW82ghdJstJMSpiQ9FJ5ss9x_w  2026-11-26T07:24:20Z  11447 bytes
```

`refresh-google.py:74` takes `fs[0]` from that list, so **a document's verdict can be computed from the
wrong `.docx`**. The two copies differ on 31 names — 1 byte on mobile-bill, 6 on `property-tax-receipt.docx`,
69 on `Account_Opening_Form_Fillable_filled`. Nothing was deleted: which of two same-named files is the
real one is not this run's decision. The fix that is available to a run is to **refuse to score a name the
folder returns more than once**, and print it.

## 6. What this run measured, in one table

| | HEAD | half A (`rungTw=15 rungCharge=0`) |
|---|---|---|
| mobile-bill, Google | 41/42, `worst_dy` **9.2**, `med_dy` −6.0 | 41/42, `worst_dy` **66.7**, `med_dy` −10.7 |
| mobile-bill, max real run movement (PyMuPDF, 115/115 matched) | — | **10.3 pt** |
| `w:trHeight` changed | — | **18 rows, −10 twips each** |
| `w:before` changed | — | **2, +10 twips each** |

Both renders came from my own probe path — upload → Drive converts to a Google Doc → export PDF →
`verify_google.py` against `corpus/mobile-bill.pdf`. The two probe files and their two Google Doc copies
were trashed after measuring; nothing else in the folder was touched. 42 checks, not 47, because this path
passes no `.docx` — `50_annotation_text`, `53_embedded_faces` and `59_shape_anchor` are unjudged, the same
three the harness names.

## 7. Attempt two: a pitch floor. It changed nothing, and the debug dump says why

Hypothesis: `mustTw` is the content floor and it is short, so make it the measured row pitch:
`int mustTw = Math.max(rowLineTw + ruleTwHere, pitchTwHere);`

**Measured, not assumed: it produces the identical file.** `w:trHeight` came out `350 350 370 350 380`
for the first five rows, exactly as before the guard. Reverted.

The reason is in the per-row dump the patch already had the data for (`-Dp2w.rungDebug=1`, first table):

```
RUNG r=0 want=360 must=360 edge=360 decl=350 laid=360 rule=10 line=350 pitch=360
RUNG r=1 want=360 must=360 edge=720 decl=350 laid=360 rule=10 line=350 pitch=360
RUNG r=2 want=380 must=380 edge=1100 decl=370 laid=375 rule=10 line=370 pitch=380
RUNG r=3 want=365 must=360 edge=1460 decl=350 laid=360 rule=10 line=350 pitch=360
RUNG r=4 want=385 must=380 edge=1840 decl=380 laid=390 rule=10 line=370 pitch=380
```

`must` already equals `pitch`, so raising the floor to the pitch is a no-op by construction. And on these
rows the patch is **self-consistent and correct by the law**: declared 350 + rule 10 = 360, which is on the
15 rung, and 360 is exactly the source pitch (`edge` delta 360). HEAD declared 360, so HEAD lays 370 — half
a point too tall per row, 18 times.

**So the engine's own model says the patched file is the better one, and Google disagrees.** That gap
between "declared + rule, on the rung" and what Google lays is the whole of the remaining question, and it
is a question about Google's row layout, not about this patch. It is the right next test and it is cheap:
two hand-made docx, one row each, declared 350 and 360 with the same content, exported through Drive. Until
that is measured, no guard derived from `rowLineTw`/`pitchTwHere` can help, because on this document both
of them already agree with each other and disagree with the renderer.
