# `18_displacement` / agent A2's row change: LibreOffice lays the declaration, so it is not invariant

24 Nov 2026, fixer slot 07:00, attempt 3. Measured in this pod on this tree; the engine is back at HEAD.

## The proposal (agent A2)

Google lays a table row at `0.75 * round((max(w:trHeight, content) + rule) / 0.75)` — the declaration is
a quantised **floor** and the rule is charged outside it, so a row declared at the page pitch and drawn
with a 0.5 pt rule lands one whole pixel (0.75 pt) too tall. A2 proposed declaring the row one rule short:

    DocxWriter.java:6468   int rowHeightTw = Math.max(rowLineTw, rowTwHere - ruleTwHere);

The argument for invariance: LibreOffice lays `max(trHeight, content + rule)` and the cell's content is
already `rowTwHere - ruleTwHere`, so `max(P-r, P-r+r) = max(P-r, P) = P` — the row should lay at the
pitch with the declaration or without it.

## The measurement

`mobile-bill` and `electricity-bill`, built before and after, `soffice --headless --convert-to pdf`,
line tops compared:

| document | pages | lines | LibreOffice layout | worst move |
|:--|:--|:--|:--|--:|
| `mobile-bill` | 1 → 1 | 112 → 112 | **CHANGED** | **-10.5 pt** |
| `electricity-bill` | 1 → 1 | 125 → 125 | **CHANGED** | **-10.0 pt** |

104 of 112 lines and 117 of 125 lines moved. The declarations themselves went `360/380 → 350/370`, a
delta of **10 twips = 0.5 pt**, not the 15 twips the proposal assumed — the `insideH` rule here is
0.5 pt, so `ruleTwHere = 10`, and the "one whole pixel" is delivered by the *quantiser*, not by the
declaration.

## Why the invariance argument fails

`content + rule` is not what LibreOffice lays. It lays the **declaration** where the declaration is the
larger of the two, and it lays the cell's measured content where that is larger. Dropping the
declaration by 0.5 pt per row shortened the table by roughly that much per row, and the whole block
below the table followed it up by up to 10.5 pt.

So the row half of `18_displacement` is **content-quantised in LibreOffice too**, and any change to the
declaration alone moves LibreOffice. That is the same conclusion `…WHOLE-PIXELS-0052-fixer` reached from
the other direction (17 documents worse, 5 better, `regress.py` refused), now with the arithmetic of the
proposal itself as the falsifier rather than a corpus sweep.

## What this costs, and what it leaves

One build (37 s), two conversions, two `soffice` renders — about six minutes to refute a well-argued
proposal. The engine is reverted and `regress.py --check` passes.

**The row half still has no LO-invariant lever, and that is now measured twice.** The next slot should
not spend itself on the declaration. What remains untried is the cell's **content** side (`:6403`,
`:6786-6803`): the row's height is what the cell asks for, and that is where a change can move both
renderers together.
