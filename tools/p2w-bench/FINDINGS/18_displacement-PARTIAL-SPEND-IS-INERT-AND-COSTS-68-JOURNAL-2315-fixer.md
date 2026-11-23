# 18_displacement — the table-gap spacer spent PARTIALLY is inert in Google, and costs `68_journal` a check

**23 Nov 2026 · fixer slot 18:58 → · engine reverted to HEAD · every Google number below is a live
round trip made this slot (ConvertOne → Drive create-as-Google-Doc → export PDF → `verify_google.py`)**
· all 6 probe Docs deleted after scoring, created in `KavoPDF-Verify`, never in the Drive root

## The claim this tested

A census agent ranked the constructs behind `18_displacement` and put the **table-gap spacer** first:
53 of the 100 documents failing the check in Google carry one, and Google charges the `w:line` leg of
that spacer only **21.6 %** of what is declared on it (`2.5873 * max(L/240, 0.06)` pt). The engine's
guard on that spacer is **binary**: a page with room spends the whole gap, a page without room spends
none of it. The proposal was a **partial spend** — hand Google as much of the gap as the page's
remaining slack allows — with a computed prediction that three documents would go clean
(`72_bank_statement` +14.46 pt against 14.35 needed, `bus-timetable` +5.09 against 4.98,
`two-tables-stacked` +9.79 against 9.68) and four more would improve.

## What was built

`DocxWriter.table()`, the spacer emission at `:6092-6140`. Three changes, all inside the spend guard:

1. `partialTw = min(wantTw, slackTw - spacerSplitTw - rowExcessTw)` replaces the boolean test, so a
   page with *some* room spends *some* gap instead of none.
2. The emitted pair becomes `w:before=partialTw`, `w:line=max(hair, spacerTw - partialTw)` — the sum
   is still the gap to the twip, so LibreOffice and Word see the page they always saw.
3. A `fullSpend` latch keeps every spacer the old guard already spent whole **byte-identical**; this
   change may only add a spend the old guard threw away, never re-cut one it made.

The third point was not cosmetic. Without it the first build also moved
`22_invoice_four_columns_txtpos` — clean at **42/42** in Google today — from a whole spend to 205 of
214 twips. With the latch it drops out of the changed set entirely.

## What it changed, measured two independent ways

| method | result |
|:--|:--|
| `P2W_SPACER_TRACE` census, 249 spacers over 213 documents | 51 documents had a spacer cross the spend boundary |
| `word/document.xml` byte diff, old build vs new build, whole corpus | **49 documents changed** |

The two agree on the population to within the two documents the `fullSpend` latch removed between the
census run and the diff run. Of the 49 changed, **45 fail `18_displacement` today**, 4 are
`page_count_refused` (unscorable), and **none is currently passing** it — the latch removed the only
one that was.

## What it did in Google — the refutation

| document | before (this engine) | after (partial spend) | verdict |
|:--|--:|--:|:--|
| `72_bank_statement_no_rules_right_amounts` | 41/42 | **41/42** | predicted clean, **did not move** |
| `two-tables-stacked-with-no-gap` | 41/42 | **41/42** | predicted clean, **did not move** |
| `68_journal_wide_table_spanning` | 41/42 | **40/42** | **one check WORSE** — `59_shape_anchor` 49 → 0 |

`68_journal` was measured twice on the patched engine from two separately created Docs, and scored
**40/42 with `59_shape_anchor` both times**. It is a regression, not verifier noise.

So the mechanism the census ranked first does not deliver displacement in Google at all. On the two
documents where the arithmetic said it should land the table exactly, the check did not change — which
says the `18_displacement` reading is not the gap the table is sitting on, or that the slack the guard
computes is not the room the page has. The `68_journal` result says something else again: moving that
spacer down costs a shape anchor, so the two are coupled on that page.

**Engine reverted to HEAD. Recorded as `reverted`, 0 moved.**

## What this leaves for the next run

- The prediction "spend the spacer and the table lands" is **refuted on 2 of 2 documents** and harmful
  on a third. Do not re-propose a partial spend of this spacer without first explaining why the gap
  the guard spends is not the gap Google moves.
- **`18_displacement` prints a count, not a distance.** `verify_google.py` computes `med_dy` /
  `worst_dy` / `med_dx` (`:5653-5655`) and writes none of them; the stored `gverify/*.json` carries
  `name/status/passed/total/failed/engine` only. Every attempt at this class is therefore steering
  blind — the fixer cannot see whether a document is 0.5 pt or 50 pt out. **Publishing those three
  numbers is the highest-value change available to this class**, and it is an instrument change, not
  an engine change, so it is not blocked by the corpus measure.
- `tools/p2w-bench/dy.py` exists and calls itself "the measurement `18_displacement` never prints".
  The next run should start by making that the default output of the check.

## Second lead, not taken this slot

The page-count agent found that **21 of the 23 `page_count_refused` documents render the source's exact
page count in LibreOffice and only gain a sheet in Google**, and that 14 of them pass every LibreOffice
check they have — finished documents blocked from scoring by one extra page. It named `w:pgBorders`
(replacing the 62 page-frame shapes) as the one construct with a *measured* Google delta:
`60_page_border` 2 → 1 page with the same 689 characters. That is a measured, unbuilt fix and it
converts unscorable documents into scorable ones.
