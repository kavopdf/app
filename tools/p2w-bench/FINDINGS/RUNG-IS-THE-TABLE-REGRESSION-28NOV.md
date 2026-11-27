# The table regression cluster is one constant: `ROW_RUNG_UNDER_TW = 10` (8fb4f503)

**Run:** fixer, 28 Nov 2026, slot 03:07 IST. **Engine:** a05b20eb (HEAD 7415d7ea).
**Instrument:** `benchmarks/p2w.py::measure_doc` — the same scorer `gate.py` uses, called directly on
one document so an A/B costs 15 s instead of a corpus pass.

## What we believed

The last three reports said the gate's 84 LibreOffice regressions were "five constructs, not one
constant", and the run before that blamed `ROW_RUNG_UNDER_TW` at corpus scale (4 better / 63 worse)
and reverted it. Nobody had bisected the engine to ask *which commit* broke the tables.

## What we measured

### 1. Bisect — one document, engine built at each commit in a throwaway `git worktree`

`table-with-no-header-row`: 15 Nov baseline 0.61, tree 47.48.

| engine commit | DocxWriter state | share5 |
|:--|:--|--:|
| `ff060d4c` | before the table-gap work | **0.61** |
| `5beb8b9d` | | **0.61** |
| `9f0a8207` | gap spent as `w:before` | **0.61** |
| `ee5a00d6` | DocxWriter restored to `9f0a8207` | **0.61** |
| `8fb4f503` | **+ pitch-bound rows declared 10 tw under, + gap spent at 70 %** | **47.48** |
| `33863086` (HEAD) | + single-line cell written at row height | 47.48 |

`8fb4f503` is the commit. `33863086` changes nothing here.

### 2. Which half of `8fb4f503` — a reversible property switch on each

Two rules went in together: `SPACER_SPEND_FRAC = 0.70` (the table gap is spent as 70 % of what it
wants, replacing a room clamp) and `ROW_RUNG_UNDER_TW = 10` (a pitch-bound row is declared 10 twips
under its own pitch). Each was made switchable at HEAD and measured on two documents:

| configuration | table-with-no-header-row | very-long-single-column-table |
|:--|--:|--:|
| HEAD (both on) | 47.48 | 41.14 |
| `-Dp2w.spacerfrac=0` (gap rule off) | 47.48 | 41.14 |
| `-Dp2w.rung=0` (rung off) | **0.61** | **2.38** |
| both off | 0.61 | 2.38 |

**The rung is the whole of it. The 70 % gap rule is inert on both documents.**

### 3. Does it generalise — `-Dp2w.rung=0` at HEAD, six documents

| document | 15 Nov baseline | tree (rung=10) | rung=0 |
|:--|--:|--:|--:|
| `table-with-no-header-row` | 0.61 | 47.48 | **0.61** |
| `very-long-single-column-table` | 6.87 | 41.14 | **2.38** |
| `boq-tender-bill-of-quantities` | 7.10 | 41.95 | **0.62** |
| `balance-sheet-and-profit-loss` | 6.20 | 36.69 | **0.21** |
| `electricity-bill` | 16.24 | 36.78 | **1.33** |
| `mobile-bill` | 18.48 | 30.09 | **1.55** |
| `price-list-2col-dense-right-aligned` | 2.69 | 27.89 | 2.69 |

Every one is restored, and five of the six come out **better than the 15 Nov baseline**, not merely
level with it: the other engine work since 15 Nov is real, and the rung is the only thing hiding it.

## The mechanism

`w:trHeight` is a declaration both renderers read. Google re-quantises a declared row height onto a
0.75 pt ladder and charges the row's rule on top (`FINDINGS/ROW-RUNG-26NOV.md`); declaring 10 twips
under compensates for that on the two documents it was proved on. LibreOffice lays the declaration
**literally**, so every pitch-bound row comes out 0.75 pt short, the shortfall is one-signed, and it
accumulates down the table — which is why the damage scales with the number of rows and not with the
page: a one-page, forty-row table reads 47.48 while a three-page table with fewer rows reads 41.14.

`8fb4f503`'s own commit message says what it bought: `mobile-bill` 46/47 → 47/47 and
`electricity-bill` 46/47 → 47/47 **in Google**. It bought two documents and charged the proxy for
dozens.

## What is now true, and what is not

**True:** the rung is the cause of this cluster, it is separable from the gap rule, and turning it off
restores every document probed.

**NOT measured, and this is the whole decision:** which renderer is right. The rung was landed on
Google evidence and I have only LibreOffice evidence against it. Under the charter's first
non-negotiable — *Google is the truth, LibreOffice is a proxy* — a change that is right in Google and
wrong in soffice is **not** a regression, and 10 of the 84 "regressed" documents pass **every** Google
check (`electricity-bill`, `mobile-bill` among them). That is consistent with the gate refusing on a
proxy artifact, and it is a hypothesis, not a finding, until the Google side is measured.

**The experiment that decides it, and it is two documents:** convert `mobile-bill` and
`electricity-bill` at rung=10 and rung=0, send both through Drive, and read the 42 checks.
- If both stay 47/47 at rung=0, the rung is pure cost and should go: it is worth the six documents
  above plus whatever else in the 84 it holds.
- If either falls to 46/47 at rung=0, the rung is right in Google and the gate must stop charging a
  Google-proved construct to the soffice proxy — which is a gate change, with this file as its
  evidence.

## What would prove this wrong

A document where `-Dp2w.rung=0` makes share5 worse at HEAD, or a Google check that rung=0 breaks.
Neither was observed; six documents were probed and none got worse.

## The probe, so the next run does not rebuild it

Both switches were reverted before the report — the tree's engine is byte-identical to HEAD. To
recreate them: `ROW_RUNG_UNDER_TW = Integer.getInteger("p2w.rung", 10)` and
`SPACER_SPEND_FRAC = Float.parseFloat(System.getProperty("p2w.spacerfrac", "0.70"))`, with the spend
falling back to `Math.min(wantTw, roomTw)` when the fraction is 0. Build is 29 s
(`javac -d out` over `app/src/main/java` + `ConvertAll.java ConvertOne.java`), one document is 5 s to
convert and 10 s to score, and `git worktree add /tmp/wt_<sha> <sha>` gives a clean engine at any
commit without touching this tree.
