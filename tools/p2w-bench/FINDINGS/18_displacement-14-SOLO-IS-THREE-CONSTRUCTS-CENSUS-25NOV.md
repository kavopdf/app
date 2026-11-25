# `18_displacement` on the 14 solo documents is THREE constructs, not one — and the row-height declaration is the only lever that reaches more than one of them

**25 Nov 2026, fixer slot 09:59 IST.** No engine change landed. The measurement below is the
deliverable: it replaces "18_displacement is worth 40.9 clean documents, take the class" with a
per-document census, and it is the first time the 14 solo documents have been split.

The leverage table (`classpick.py --leverage`) says `18_displacement` is worth **40.9 clean
documents** and that **14 documents fail it and nothing else**. Those 14 are the cheapest clean
documents in the corpus, which is why four prior runs took this class and none of them landed.

## What the check is

`verify_google.py`, the `18:` block. Per page: take the upright source runs
(`|sin(angle)| <= 0.02`), match each to a render run, compute `dy = g.ry - r.ry` against a
per-run tolerance of `clamp(0.35*size, 1.5, 4.5)` pt. A page fails if
`n_out > max(2, ceil(0.05*n))`, or every run is out, or one run exceeds `2x` its own tolerance.

So it is a per-page count of displaced baselines. It is not a margin test, a page-height test or
an ink test — `47_margins` and `60_text_column_right_edge` are different questions that happen to
travel with it.

## The census: three constructs, measured by instrumenting the guard

Method: `p2w.dbgSpacer` instrumentation on the live spacer guard in `DocxWriter`, then
`ConvertOne` on all 14 solo documents. `slack` is the page's own remaining room in twips,
`rowExcessTw` is the charge the guard applies for row growth (`15 * pageRowCount`, i.e. 0.75 pt
per row), `spendable` is the guard's own verdict on whether the table spacer may be spent.

| construct | docs | evidence |
|---|---|---|
| **A. Refused table spacer** — guard says `spendable=false` | 7: `68_journal`, `72_bank_statement_no_rules_right_amounts`, `bus-timetable-station-left-times-right`, `insurance-policy-schedule`, `mobile-bill`, `table-with-no-header-row`, `two-tables-stacked-with-no-gap` | `68` tw=2880 slack=568 rowExcess=105 · `72` tw=366 slack=558 rowExcess=270 · `mobile-bill` tw=248/128/124 slack=380 rowExcess=360 · `bus-timetable` tw=127 slack=547 rowExcess=495 |
| **B. Spacer already spent, still failing** | 5: `16_right_aligned`, `303_discharge_summary`, `36_embedded_subset_font`, `74_balance_sheet`, `balance-sheet-two-columns` | guard print `spendable=true` on all five: `16` tw=93 slack=558 · `303` tw=227 slack=2018 · `36` tw=268 · `74` tw=65,66 · `balance-sheet` tw=252 |
| **C. No table at all** — flow arithmetic | 2: `31_times_body_arial_headings`, `71_invoice_space_aligned_no_rules` | no `sz=2` spacer paragraph exists in either .docx |

**The decisive number is `rowExcessTw = 15 * pageRowCount`.** On these single pages the page's own
slack is 380–660 tw (19–33 pt) and the row-growth charge is 195–495 tw, so on construct A
`spacerWant + rowExcess > slack` on every document. The guard refuses **because of a row-height
term**, not because the page has no room. That is the 0.75 pt quantum law already recorded in
`FINDINGS/18_displacement-ROW-GROWTH-075-QUANTUM-LAW-2354-fixer.md`: Google lays a declared
height `D` at `0.75*(round(D/0.75)+1)`, so 360 tw lays 18.75 pt and 380 tw lays 19.50 pt against
a page pitch of 18.40 pt. The error is one-signed and cumulative.

`68_journal` is the exception inside A: slack 568 against a 2880-tw spacer, so it is refused on the
gap alone, not on rows. That matches
`FINDINGS/18_displacement-GUARD-IS-THE-BLOCKER-68-JOURNAL-111PT-25NOV.md`, which measured the
spend moving it -114.3 -> -3.1 pt and costing a `59_shape_anchor`.

## LibreOffice against the same 14 — measured here for the first time on all of them

The HEAD .docx of all 14 was rendered through LibreOffice and scored with the project's own
`verify_google.py` (LO mode): **11 of the 14 pass 42/42 in LibreOffice**. Only `68_journal` (40/42),
`71_invoice_space_aligned_no_rules` (41/42) and `balance-sheet-two-columns` (41/42) fail in *both*
renderers. The class is therefore ~79 % Google-only, which is consistent with
`DOCS-ROOT-CAUSES-24NOV.md`'s 83-of-102 and is why every prior LibreOffice-measured attempt on this
class read as a win and was not one.

## Construct C, which no spacer or row change can reach

The engine's own declared flow position (sum of `before + line`) was compared against the source
baselines. On `31_times_body_arial_headings` the declared baseline is **-2.87 pt on all 20 lines**
— a pure constant, identical in the LO render (median -2.87, span 1.55). Its tolerance is
3.01–4.2 pt, so it scrapes through in LibreOffice and fails in Google. `71_invoice` is worse and
not constant (LO span 32 pt, n_out 29/72). Neither document contains a table spacer, so no
spacer/row patch can fix either.

**This -2.87 pt flow constant is a new lead and is not root-caused in any finding on disk.**

## `place()` is dead code

`DocxWriter.java:4149` `place()` is quoted by `DOCS-ROOT-CAUSES-24NOV.md` as the positioner. It is
not live: `grep -n "place("` returns the definition and two comments, no call site. The live
positioner is the inlined block in `flowFromBox`/`flowRow` (`:3560–3715`, `:4453–4631`). Anyone
patching inside `place()` changes nothing — which may be why a prior attempt on this class measured
no movement.

## The candidate patch, and why it was NOT landed

The smallest lever that reaches construct A:

```java
// DocxWriter.java, emitTable's row loop, immediately after
//     int rowHeightTw = Math.max(rowTwHere, rowLineTw);      // ~:6493
if (rowHeightTw > rowLineTw)
    rowHeightTw = Math.max(rowLineTw, 15 * Math.round(rowHeightTw / 15f) - 15);
```

It declares one quantum net of the nearest rung, so 360 -> 348 tw (lays 18.00), 380 -> 360
(lays 18.75), 328 -> 315 (17.25), 232 -> 225 (16.50). Per-row error becomes <= 0.375 pt signed
both ways instead of +0.1..+0.85 pt always downward. `rowLineTw` (the type floor) is preserved and
`hRule` stays `atLeast`, so nothing can clip. It compiles; all 14 still convert to one page each.

**It was not committed, for two reasons, and both are measurements rather than opinions.**

1. **It must not ship alone.** The same finding that measures the quantum law
   (`...ROW-GRID-AND-SPACER-1518-relay.md` §3) records that the row change *alone* made
   `mobile-bill` **worse**, -6.73 -> -12.73, because it cancels a -10.18 pt spacer step. The row
   change and the spacer spend have to land in the same commit, and the spend is what construct B
   shows is already being spent without clearing the document.
2. **No Google measurement exists on this pod.** There is no Drive credential in the sandbox
   (`gverify.py` cannot authenticate), so the pass/fail effect of the patch is *predicted, not
   measured*, in the only renderer the charter counts. The 105-document re-measure (pending item 13,
   `gverify.py --plan 105`) is the :20 cron's job and it has not run.

Predicted effect, stated so the next run can falsify it: it removes the row-drift term on the whole
corpus and unblocks the spacer spend on **6 of the 14** (`72_bank_statement`, `bus-timetable`,
`table-with-no-header-row`, `two-tables-stacked-with-no-gap`, `mobile-bill`,
`insurance-policy-schedule`). It cannot reach `31_times`, `71_invoice`, `68_journal`, or construct B.

Regressions to fear, and they are the reason to measure rather than reason: 124 of 213 documents
carry a table spacer whose spend decision this changes, including 13 that are clean today
(`041122-Account_Opening_Form` carries 22 spacers up to 166 pt).
`...PARTIAL-SPEND-REGRESSES-GOOGLE-1428-relay.md` and `...SPACER-SPLIT-LANDS-4-COSTS-2-REVERTED`
record two prior attempts that bought clean documents and cost others.

## What the next run does with this

- The class is **not** one construct and must not be taken as one. Take A, B or C separately.
- A needs the row change **and** the spend in one commit, measured in Google.
- C needs the -2.87 pt flow constant root-caused first — it is 2 documents and it is untouched.
- B is five documents with the spacer already spent, on which the residual is ~0.1 pt overshoot in
  LibreOffice (`16` +0.82 constant, `74` +0.96, `303` +0.01). A Google-only constant is the
  hypothesis; nothing on this pod can confirm it.
