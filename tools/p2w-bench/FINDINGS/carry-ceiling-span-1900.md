# The carry's ceiling never bound on a merged cell - 3 of 213 change, 0 worse

Run: 17 Nov 2026, fixer slot, carry-over item 1 from the previous run's HANDOFF.

## What was asked, and what was found instead

The carry-over asked for the wrap charge to be re-planned as a PAGE-layout change: after a
table's rows are charged, re-flow the bands that follow onto the page's remaining height
instead of letting them overflow. The three earlier builds (flat, allowed, differential) had
already shown that RAISING a row's height loses corpus-wide, and this run did not build a
fourth.

What this run measured instead is that on the document the whole thread is about, the row does
not need to be charged taller - it needs the renderer to wrap it the way the page did, and the
mechanism for that (the ARIAL_W carry, `w:w`) is already in the engine and was silently not
applying its ceiling to merged cells.

## The defect, in numbers

041122-Account_Opening_Form, the instruction row carrying "Government Department establishing
identity and address of such person":

| | |
|---|---|
| cells in the row | 1 |
| gridSpan / tcW | 6 / 11000 tw (550 pt) |
| paragraph indent (w:ind left) | 393 tw (19.65 pt) |
| paragraphs in the cell | 9, each one line the page drew |
| w:w emitted | 97, 97, 97, 95, 97, 96, 96, 97 |
| renderer's usable width (measured on the render) | 530.35 pt (text x 43.0 -> 573.3) |
| longest paragraph at Arial metrics, 10 pt | 563.7 pt -> 546.8 pt at 97 % |
| page drew | 9 lines, 118 pt |
| we rendered | 13 lines, 154 pt |
| space the page had left on the sheet | 158 pt |

The engine's clamp is in `carryScalePct(CellPara, sz, availTw)`: the scale is the page's drawn
width over Arial's natural width, then lowered so it cannot exceed the cell
(`availTw * 0.98`). The caller passed `colTw[c] - pInset` - the FIRST grid column under the
cell. On this cell that is 360 - 393, a negative number, and `carryScalePct` skips the clamp
when the width is not positive. So the scale went out at the page's drawn ratio, 97 %, on a
cell that only allows 92, and four of the nine lines wrapped.

`spanTw` - the sum of the columns the cell covers - was already computed two blocks above,
for `w:tcW`. The fix is that one token.

## The diff, and why it is the whole ratchet

213 documents converted twice from the same corpus, same JDK, same classpath, every zip entry
compared:

| | |
|---|---|
| documents | 213 |
| changed | **3** |
| byte-identical in every entry | 210 |

The three: `041122-Account_Opening_Form`, `Account_Opening_Form_Fillable_filled`,
`373_leave_application_form` - all form documents whose tables hold merged cells. A document
whose .docx is byte-identical cannot render differently, so those 210 need no measurement; the
three that can move were all three measured.

| document | share@5 before -> after | pages (source) before -> after |
|---|---|---|
| 373_leave_application_form | 5.46 -> **4.64** | 1 -> 1 |
| 041122-Account_Opening_Form | 99.02 -> 99.02 | 9 (9) 11 -> **10** |
| Account_Opening_Form_Fillable_filled | 99.02 -> 99.02 | 9 (9) 11 -> **10** |

0 of 3 worse.

## Why the two form documents' score does not move

Because the LAST spurious page is not a table row that is too tall - it is a folio written as a
row of the table. The 24-row declaration table ends with a single-cell row whose whole text is
"7". It renders as the only content of our page 8 (y 25.3-35.3, one character), so every page
after it is compared one source page out: our page 8 reads share@5 99.02 with text_recall 0.04.

The flow-line folio rule already exists (`b.y > 0.88 * pageHeightPt && isFolio(p)` -> anchored,
not flowed) and its own comment measures this document. It cannot fire here, because the folio
is a row of the table and not a flow line.

So the class moves when that row becomes a position. See the UNTESTED entry in HYPOTHESES.md:
detect the folio row before the row loop, skip it, take the last-row bookkeeping from row-1,
and emit the text after `</w:tbl>` where the post-table carrier paragraph already goes -
`anchor(sb, ctx, x, yTop, w, h, inner)` needs only a hand-built paragraph string, no model
object. A `w:framePr` text frame was tried as the cheap route and does NOT place reliably:
anchored to the page at y 16104 tw it rendered at y 218 pt. Use `anchor()`, which is the path
378 boxes on this document already go through.

## What would prove this wrong

A document whose .docx changed and whose render did not - none of the three. Or a fourth
document changing on a re-run of the diff: the conversion is deterministic and 210 came out
byte-identical twice.
