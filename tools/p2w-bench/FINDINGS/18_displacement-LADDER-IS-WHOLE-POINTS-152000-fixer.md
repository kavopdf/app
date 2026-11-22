# 18_displacement — the row-pitch ladder is WHOLE points, 18.5 does not exist, and the rounding has to be diffused

**22 Nov 2026 · fixer slot 13:56 → · engine HEAD `462353f9` + one measurement-only patch · two live
Google round trips on `two-tables-stacked-with-no-gap` · all probe Docs and staged files deleted after
scoring, Drive root left empty**

## Why this was measured

The 13:18 relay left one instruction: *"the next test is one round trip and it is bracketed... **18.5** is
0.1 pt a row from the source, reachable between the 17.40 and 18.00 declarations measured here, and lands
`18_displacement` on a document that is one check from clean. Build that first."* It rested on the claim
that *"laid pitches are always multiples of 0.5 and laid rule positions always sit on the half-point
grid"*, taken from a **synthetic 28-row probe** whose rows were built by hand.

Three points from three builds cannot tell a 0.5 pt ladder from a 1 pt one, and the relay's own numbers
could not either: 18.0, 19.0, 19.5 is consistent with both. So instead of building the 18.5 point and
guessing again, one build swept **thirteen declarations in one document** and read the laid pitch of each.

## The sweep

A measurement-only patch (`p2w.sweepBase`, `p2w.sweepTw`) makes row *r* declare `base + step*r`. Nothing
else changes: same source PDF, same engine, same `atLeast` construct, same borders (`w:sz="7"`). One
upload → create-as-Google-Doc → export PDF → rule positions off the export's own drawings.

| declared (tw) | 344 | 348 | 352 | 356 | 360 | 364 | 368 | 372 | 376 | 384 | 388 | 392 |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| declared (pt) | 17.2 | 17.4 | 17.6 | 17.8 | 18.0 | 18.2 | 18.4 | 18.6 | 18.8 | 19.2 | 19.4 | 19.6 |
| **laid (pt)** | **18** | **18** | **18** | **19** | **19** | **19** | **19** | **19** | **20** | **20** | **20** | **20** |

Laid rule positions: 77.5, 95.5, 113.5, 131.5, 150.5, 169.5, 188.5, 207.5, 227.5, 246.5, 266.5, 286.5,
306.5, 326.5 — pitches **18.0, 18.0, 18.0, 19.0, 19.0, 19.0, 19.0, 20.0, 19.0, 20.0, 20.0, 20.0, 20.0**.

**Every laid pitch is a whole number of points. Not one is a half.** (The one 19.0 at declared 380 is the
row where the cell's own content binds, not a rounding step.)

## What this settles, and what it refutes

1. **The 18.5 point does not exist on this construct.** The relay's ladder 18.0 / 18.5 / 19.0 / 19.5 is
   wrong for `atLeast`; the ladder is 18 / 19 / 20. **Do not build the 18.5 declaration.** The lead the
   class has been carrying since 13:18 is void, and it would have cost a slot to discover.
2. **The map is `laid = round(declared_pt + 0.875)`, and 0.875 is the row's own rule** (`w:sz="7"` =
   7/8 pt), charged on top of the declaration and rounded to the nearest whole point. 11 of the 12 rows
   above fit it exactly (17.2+0.875=18.075→18; 17.8+0.875=18.675→19; 18.6+0.875=19.475→19;
   18.8+0.875=19.675→20; 19.4+0.875=20.275→20). The 12:30 relay's `+0.75 pt` constant and the 11:30
   relay's `+0.875 pt` are the same number seen on a document with a different border.
3. **A source pitch of 18.40 pt cannot be declared to, and the error accumulates.** 18.4 rounds to 19 on
   every row: +0.6 a row, +9.1 pt at the foot of a 13-row table, and that is the whole of the check. The
   foot of the HEAD build sits at y=326.5 where the page draws 316.7.

## The construct that follows from it — error-diffused pitch

The quantisation cannot be removed, but it can be **spread**: declare one row a point short and the next
a point long, carrying the rounding error forward. `patches/18-row-pitch-error-diffused.patch` does this
in the row loop, before the cell's own line is derived from the row height (declaring a row short while
leaving its content at the pitch changes nothing — the content binds and the row lays at the pitch again).

**Measured, second live round trip:**

| | HEAD | error-diffused |
|:--|:--|:--|
| laid pitches | 19,19,19,19,20,18,19,20,19,21,19,19,19 | 18,18,19,18,19,18,18,19,18,21,18,18,18 |
| foot of the table (source 316.7) | 326.5 (**+9.8**) | 317.5 (**+0.8**) |
| `23_line_pitch` | passes | passes, render now reads the source's own **18.4** |
| `verify_google` | 46/47 | **46/47 — same single failure** |

So the construct removes 92 % of the drift and still does not clear `18_displacement`. **The remaining
failure is one run more than `TAIL_FACTOR` (2.0) of its own tolerance out**, on the one row the diffusion
hands a 20 pt target to (the row laid at 21.0). The next attempt should not re-derive the ladder — it
should find that row's binding term (its cell content, not its declaration) and cap it.

## What would prove this wrong

A sweep on a second document with a different border size (`w:sz="4"`, 0.5 pt) should move the whole
ladder one way by 0.375 pt and keep the whole-point quantisation. If any laid pitch on such a document
lands on a half point, the constant in item 2 is wrong and the construct needs the rule read per table
rather than assumed.

## Cost

One measurement patch, two builds, two round trips, three probe Docs and three staged `.docx` — all
deleted after scoring. The patch is not committed to the engine: it moves every ruled table in the corpus
and a corpus ratchet does not fit a slot.
