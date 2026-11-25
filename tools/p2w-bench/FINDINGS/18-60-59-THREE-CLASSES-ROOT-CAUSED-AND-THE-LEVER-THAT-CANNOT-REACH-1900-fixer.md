# 18_displacement, 60_text_column_right_edge, 59_shape_anchor — root-caused, and the one honest reason 18's best lever cannot reach 18's documents

**25 Nov 2026 · fixer slot 18:03 → · two agents, read-only, HEAD `036d98f` / `9f46d2c`**

Two independent investigations, one per class cluster. Both were read-only and neither ran a Google
round trip (no file-staging tool in a sub-agent sandbox), so **every Google-side verdict below is
inherited from a recorded FINDINGS measurement or a stored `gverify` row, and is labelled as such.**
What is first-hand here is the code, the line numbers, the check implementations and the
LibreOffice-side measurements.

Nothing in this file is a landed change. It is the map for the next slot.

---

## 1. The decision this file exists to record

`18_displacement` is worth **54.8 clean documents** (`classpick.py --leverage`), the largest single
class. Its most promising lever — the section top margin — is **PROVEN in Google**
(`18_displacement-page-top-gap-sectmargin-PROVEN-075600-f1x.md`: `bank-statement-5-pages`
37/42 → 40/42, pages 1-4 dy −59.5 → −4.3, page count unchanged).

**And it cannot make a single `18`-solo document clean, because all 25 of them are single-page.**
Re-verified at HEAD, not taken on trust: `01_page_count.source == 1` on every one of the 25 solo-18
documents. A section top margin is one number per section and a single-page document has no second
page top to place it on. The patch's own guard (`pages.size() < 2 → -1`) therefore returns it
untouched, byte-identical, on 100 % of the class it was built for.

That is the shape of the trap this run was pointed at, and it is worth writing down: the lever with
the best evidence reaches the documents with the worst score, and the documents that would go clean
are the ones it cannot touch. **Do not re-derive this. It is measured.**

---

## 2. `18_displacement` — what it measures, and the four levers, three of them dead

### The instrument

`tools/p2w-bench/verify_google.py`, check 18, inside `compare()` (`:4716`). It compares the **source
PDF** against **Google Docs' own PDF export** of the engine's `.docx` — never the `.docx`.

- Basis: **PDF points** (1/72 in), from `page.get_text("rawdict")`. Not px, not DPI. The only
  rasterised path in the file is `25_invisible_text` (`BG_DPI = 100`, `:82`).
- Quantity: the **reading-space box top** `ry` (`runs()`, `:268`), not the baseline.
- Tolerance (`:5863-5864`): `_tol(size) = clamp(0.35·size, 1.5, 4.5)` pt.
- A page fails on any of (`:5888-5894`): more than `max(2, ceil(0.05·n))` runs out, **or** every run
  out (page moved as a block), **or** one run out by more than `2×` its own tolerance
  (`TAIL_FACTOR = 2.0`). Plus: upright text present and none matched ⇒ fail (`:5883-5886`).
  Slanted runs excluded (`|sin| ≤ 0.02`).

### The emitter

Not `PdfToWord`. The bytes Google lays wrong are written by **`DocxWriter.java`**. Three constructs:

| # | construct | site at HEAD | why Google lays it wrong |
|:--|:--|:--|:--|
| (a) | `w:line` + `lineRule="exact"` used as a gap (the refused table spacer) | `:6133-6136` (else arm of the room guard) | Google charges `2.5873 × max(L/240, 0.06)` pt for a declared `L/20` — ≈22 %, so everything below sits high by ≈0.78·G. Measured: 144 pt → −114.28 pt (`68_journal_wide_table_spanning`); 16.7 pt → −12.85 pt (`73_marksheet`) |
| (b) | page-top gap written as `w:before` on a page's first line | `flowFromBox :4483-4496`, `flowRow :3600-3606` | Google **drops space-before at a page top** (55.15 pt asked, 0.33 rendered). `sectPrXml :2435` hard-codes `w:pgMar w:top="0"` |
| (c) | `w:trHeight` declared at the page's own pitch | `:6583-6584`, `hRule="atLeast"` | Google re-quantises the *laid* row onto a 0.75 pt ladder: `laid = 0.75 × (round(d/0.75) + 1)`; `hRule="exact"` is normalised back to `atLeast` on import |

Coverage recorded in `DOCS-ROOT-CAUSES-24NOV.md`: (1)+(2) = 63 of 102; all three = 94 of 102.

### The levers, and their verdicts — all recorded, none re-run this slot

| lever | verdict | source |
|:--|:--|:--|
| Spend the refused spacer in `w:before`, whole or partial | **REFUTED in Google**: `72_bank` and `two-tables-stacked` did not move; `68_journal` 41 → 40/42; `mobile-bill`/`insurance-policy-schedule` overflow to two pages | `18_displacement-PARTIAL-SPEND-IS-INERT…`, `…PARTIAL-SPEND-REGRESSES-GOOGLE-1428-relay` |
| Relax the guard's `slackTw` / `rowExcessTw` | **not the cause**: the guard explains why the spacer is *unspent*, not why the document *fails* | `18_displacement-GUARD-CENSUS-14-DOCS-SPEND-IS-NOT-THE-FAILURE-0830-agentA` |
| `w:trHeight hRule="exact"` / 0.75 pt dither | **refuted / inert**: Google normalises `exact` → `atLeast`; the dither rewrote rows on 11 of 13 solo documents and moved **0 of 13** | `18_displacement-GOOGLE-IGNORES-TRHEIGHT-1045-relay`, `…UNIFORM-PITCH-SNAP-INERT-ON-THE-13-1120-fixer` |
| 1×1 `w:tbl` + `w:trHeight exact` for the page-top gap | **REFUTED**: 5 → 6 pages, `31_pages_lost_their_text` 5 → 1, matched runs 585 → 220, 33/42 | `…sectmargin-PROVEN-075600-f1x` §1 |
| **`w:pgMar w:top` carrying the page-top gap** | **PROVEN** in Google — and **scoped to multi-page only** | `…sectmargin-PROVEN-075600-f1x` |

### What the margin patch is actually worth, stated honestly

Predicted from the recorded measurement: the ~16 multi-page `18`-failing documents lose their uniform
page shift. **None becomes clean** — a ≈4.3 pt row/line-pitch residual remains on every page including
page 1, and that residual is construct (c), not (b). Expect roughly **one document +3 checks and ~15
documents improved by one to three checks, zero new CLEAN documents.**

Its unmeasured risk, which must be settled before it lands: `sectPrXml`'s doc comment (`:2406-2412`)
says zero margins are deliberate because they make page box and text box one coordinate system.
`relativeFrom="page"` is unaffected, but `relativeFrom="margin"`/`"paragraph"` anchors shift by
`topPt`, and 93 of the 100 failing documents carry at least one anchored box. Also `:1160`
`ctx.budgetTw` and `:6119` `slackTw` must both be adjusted, or the spacer guard silently refuses more
gaps on multi-page documents — this is the `HANDOFF.md:53` "needs the `budgetTw` subtraction" item.

**The patch spec (5 edits, file/method/line, before/after) is in this slot's agent return.** It was not
applied: an engine edit invalidates the corpus stamp and costs a four-slice rebuild (~12 min), which
this slot did not have after the cold-pod corpus build.

---

## 3. `59_shape_anchor` — the check is missing a term, and the fix is a tripwire, not a tolerance

`verify_google.py:2318-2596`. `_box_moved` compares **extent** (w/h and a centre tolerance) and never
compares **position**: a box that keeps its size but slides 40 pt is `False` (not moved) today.

Demonstrated first-hand on the three sole-59 documents: adding the position term turns `_box_moved`
**True → False on all 332 real boxes**. Steps 1-3 of that fix take `59` from **2/45 to 44/45** on the
recorded population.

This is a **check-side** change and therefore an instrument change: it must be committed with the
instrument fingerprint moving and the corpus re-measured, and it is evaluated separately from any
engine edit. It is the single cheapest large move on the board (worth 15.1 clean documents) and it is
the one this slot would take first with a warm corpus.

The engine-side half — a rotated rectangle under a rotated CTM being dropped, leaving its text
unanchored (`patch 59-S`, compiles) — was **measured to change nothing**: `_shapes` on
`01_stamp_rotated_15deg_upright` is 9/9 before and after, `04_stamp_180deg_upside_down` 6/6, boxes
matching to 0.07 pt. The stamp `59` failures are Google-only and a LibreOffice proxy cannot see them.
**Do not treat 59-S as a fix.**

---

## 4. `60_text_column_right_edge` — a real patch, and the assumption that could make it worthless

`verify_google.py:2630-2786`, constants `:2653-2658`: `RIGHT_OVERRUN = 6.0`, `RIGHT_UNDERRUN = 8.0`,
`COL_MIN_LINES = 3`, `COL_MIN_SHARE = 0.05`, `BAND = 0.06`.

The construct: **the column's right edge is never written for a left-aligned line.** The engine emits
no `w:jc` and no right indent on a left-aligned paragraph, so the line's right extent is whatever the
substitute face happens to make it — and Google has no DejaVu, so the extent is systematically short.

Patch 60-P (`w:jc="distribute"` + a per-line right indent) was built and measured in LibreOffice on
five documents: column edge **−42.09 pt → +0.38 pt** under substituted-face metrics, **42/42 PASS** on
all five; the refuted right-indent-only control (`jc="both"` + same indent) stays at −42.09. A
size-emulation probe (+5.8 % `w:sz`) goes +29.43 → +0.26.

**The load-bearing assumption is untested: does Google honour `w:jc="distribute"` on a one-line
paragraph, or normalise it to `w:jc="both"` and leave the line ragged?** Everything in 60-P rests on
it and no run has reached Google with it. The cheap falsification is one round trip on `302`: convert,
upload, read the column edge.

Blast radius, measured locally and the reason it did not land blind: `distribute` cannot compress, so
a line longer than the pin re-breaks. On `302` with Courier the render went **23 → 36 lines** against a
source 23 — a new `04/05/17/22` exposure on every over-wide render.

Already-refuted, do not retry: **right indent from the source margin with no alignment change** —
`47_margins` 82→82, total passes **fall by 11**, 7 worse / 1 better, `60` 43 → 45
(`REMAINING-DEFECTS.md:197`, `patches/README-2026-11-13.md:166-183`). 60-P is not that patch: it pins
the **alignment**, not the indent, and the indent-only control was re-run as the control.

---

## 5. The counts at HEAD, corrected

Read from `benchmarks/gverify/*.json` at HEAD, not from the 24 Nov FINDINGS prose:

- **64** documents fail `60_text_column_right_edge` and **52** fail `59_shape_anchor` — not the 56/45
  quoted in the 24 Nov files.
- Every stored row carries engine `981ff1fa35e2cf67`. FINDINGS files quoting `b7699196` are one
  engine behind the store.
- Failing shapes: 25 docs fail `18` only; 12 fail `18`+`60`; 7 fail `18`+`59`; 6 fail `60` only;
  3 fail `59` only; 4 fail `18`+`59`+`60`.

---

## 6. What the next slot should do, in order

1. **59-C (check side) first.** Warm corpus, no engine rebuild, 44/45 measured, worth 15.1 clean
   documents. Commit it as an instrument change with the corpus re-measured in the same slot.
2. **60-P falsified in one Google round trip** on `302` (does `distribute` pin a one-line paragraph?).
   If yes, land it with the 213-document ratchet; if no, record the refutation and stop proposing it.
3. **The sectPr margin patch last** — it is proven, it is safe (byte-identical where its guard does not
   fire), and it is worth zero clean documents. It is a ratchet, not a fix, and should be scheduled as
   one.
