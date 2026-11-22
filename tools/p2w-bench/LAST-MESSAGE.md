**22 Nov 2026 · fixer slot 13:56 → running IST**

> **The carry-over patch is refuted.** I applied it, bisected it into its four mechanisms, and measured
> it in both renderers on engine `462353f9`. `two-tables-stacked-with-no-gap` reads **46/47 in Google
> with the same single failing check it had at baseline** — the handoff's "41/42 → 42/42 PASS" does not
> reproduce. Nothing committed to the engine; the tree is at baseline. What the slot did produce is a
> measured law that relocates the lead: **`w:before` is charged by Google at exactly `V/20` pt, with no
> floor, no threshold and no cap.**

## Progress

| | |
|:--|:--|
| Document-moves this run | **1** — 3 attempt(s), 1 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **23**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `18_displacement` |
| Committed | **16** files in 4 commit(s) from `f3157f6` |

The ledger's one moved document is the **14:45 kept attempt from the 13:56 slot**, which report.py still
counts inside this window. **My own attempt — 15:34 — is `reverted` and moved 0 of 16.** No engine file
is changed by this run.

## The class, and why this one

`18_displacement`, and not because the tool printed it. The arithmetic:

- `classpick.py --leverage` prices it at **38.7 clean documents**, the largest step in the table.
- **16 documents fail `18_displacement` and nothing else** — read straight from
  `benchmarks/gverify/*.json`, not from the class table. A fix that works makes 16 documents CLEAN at
  once: **23 → 39**.
- It held the carry-over: a measured lead with a patch written, which the 13:56 run could not ship
  because the gate refused it unratcheted.

That last point is why the build was the slot. It was the right class; the patch was wrong.

## What this slot measured

### 1. The patch has four mechanisms, so I bisected it instead of accepting or rejecting it whole

Every row is a fresh build (40–47 s) and a fresh screen. LibreOffice proxy, share@5, lower is better:

| document | baseline | spacer only (h1-2) | spacer+rowpitch (h1-3) | full patch (h1-7) |
|:--|--:|--:|--:|--:|
| `insurance-policy-schedule` | 0.53 | 0.53 | 0.53 | **33.55** (+33.02) |
| `mobile-bill` | 1.55 | 1.55 | **12.66** (+11.11) | **36.90** (+35.35) |
| `table-with-no-header-row` | 0.61 | 0.61 | 0.61 | **36.40** (+35.79) |
| `two-tables-stacked-with-no-gap` | 0.77 | 0.77 | **3.29** (+2.52) | **30.02** (+29.25) |
| `product-catalogue-code-left-price-right` | 0.47 | 0.47 | 0.47 | 0.47 |
| `74_balance_sheet_indented_subitems` | 0.03 | 0.03 | 0.03 | 0.03 |

The baseline row reproduces `benchmarks/RANKING.csv` exactly (`6 measured, 6 same`), so the instrument is
sound and the regression is the patch's, not a stale table.

**The spacer half is invisible to LibreOffice** — 6 same, 0 better, 0 worse. That is the signature of a
construct Google undercharges and LibreOffice honours, and it is why `screen.py` can never judge this
half. **The row/cell half is what regresses**, and hunk 3 alone (row pitch from the table average instead
of the row's own snapped `rowEdge`) takes `mobile-bill` 1.55 → 12.66.

### 2. In Google, the patch moves nothing on the document it was written for

Fresh round trips, `GOOGLEDRIVE_CREATE_FILE` → `GOOGLEDRIVE_DOWNLOAD_FILE` → `verify_google.py --docx`:

| document | build | Google | vs baseline |
|:--|:--|:--|:--|
| `two-tables-stacked-with-no-gap` | baseline | 46/47, fail `18_displacement` | — |
| `two-tables-stacked-with-no-gap` | spacer only | **46/47**, same check | **no change** |
| `two-tables-stacked-with-no-gap` | **full patch** | **46/47**, `18_displacement {source: 0, render: 1}` | **no change** |
| `mobile-bill` | baseline | 46/47 | — |
| `mobile-bill` | spacer only | **43/47, `01_page_count` 1 → 2** | **REGRESSION** |

### 3. The law that survives, and it is worth more than the patch

An agent measured the charge curve directly — 25 values from 1 to 4320 twips, synthetic documents
through Google only:

    spacer paragraph height = V/20 + 0.1552 pt        (V = w:before in twips)
    max |residual| = 0.000000 pt over all 25 points   no floor, no threshold, no cap, run or no run
    w:line is read as the written value divided by 240, times the mark's own line height: 0.2156x

That confirms the 13:56 run's `~0.22x` in size and corrects its cause. And it **refutes the
over-charge theory**: `w:before` is arithmetically right. I then checked the obvious follow-on and it is
wrong too — `DocxWriter.java:5875` is `ctx.flowTw += spacerTw`, so the engine already charges its
pagination model the declared value and `w:before` now renders exactly that. **Model and render agree
after the patch.** `mobile-bill`'s extra page is not a model mismatch; it is a **real surplus** that only
fitted before because Google was under-charging that gap by ~4.9 pt. That surplus is the lead.

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 15:34 | **reverted** | 0/16 | applied the carry-over patch and bisected it. Full patch leaves `two-tables-stacked-with-no-gap` at 46/47 in Google with the same check as baseline (the 42/42 does not reproduce); spacer-only leaves it at 46/47 and pushes `mobile-bill` 46/47 → 43/47 with an extra page; row/cell hunks are +29..+36 in the proxy on four documents |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **197** (92.5%) |
| Failing at least one check | **16** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Timing

| | |
|:--|:--|
| Slot window | 13:56 → running · 1h 40m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 39 |
| Longest silence | **48.0 min** — from 14:46:48, after `pending.py: reading the pending gate` |
| Silences over 2 min | 5 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |

### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **1h 10m** | `###############` |
| measure or build - a conversion, screen or compile writes no beacon | **20 min** | `####` |
| record - attempt, handoff, class rows | **3 min** | `#` |
| report - the report and the chain | **4 min** | `#` |
| other - not attributed to a tool | **2 min** | `#` |

## Why the silence

One 48-minute stretch, and it is mine to own: a sub-agent that was meant to run in the background ran
**inline** (a scheduled run has no one to answer later), and its Google probe sweep took 11 minutes of
wall clock inside my turn. It earned its keep — the `w:before` law is the best thing this slot produced —
but a single blocking delegation is not what the brief asks for, and the next run should budget for it
rather than discover it.

## Next run

**Do not re-apply `patches/18-spacer-before-rowpitch-rowrule.patch`.** `patches/README.md` now carries
the refutation at the bottom, and the four hunks are measured separately there.

Two things are live:

1. **Keep the spacer half (hunks 1–2) on its own.** It is a correctness fix, LibreOffice-neutral, and the
   law above says it is right. It cannot be kept as it stands only because `mobile-bill` spills a page.
2. **Find `mobile-bill`'s real surplus.** With the gap charged honestly the page no longer fits, so
   something else on it is over-tall by at least 4.9 pt. That is the lead, it is one document, and it is
   measurable page by page. Do not reach for `flowTw` — it is already correct.
