**22 Nov 2026 · relay slot 17:12 → running IST**

> **The waiver three slots asked for already exists, and it is in `regress.py` — tested, with a control.
> The patch it was meant to ship is refuted: on `mobile-bill` the dither takes LibreOffice from 1.55 to
> 39.21 and leaves Google at 46/47, still failing `18_displacement`.** So the largest class in the corpus
> is not "one build from 16 clean documents". The patch fixes the document it was measured on and does
> not generalise, and the gate refuses it for the right reason. Nothing was committed to the engine.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **23**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `18_displacement` |

## The class, and why this one

`18_displacement`, and the reason is that two runs had left a decision open rather than a patch: the 15:55
report's own next move was *"either the ratchet gains a documented path for a change that is clean in
Google and regressed in the proxy, or this class is parked"*. That is a question I could answer this slot
with a test instead of another build.

## What this slot measured

### 1. The waiver exists, and it works

`regress.py::docx_regressions()` has allowed a LibreOffice regression since 20 Nov **when Google improved
on the same document** — `g_after < g_before`, read from `benchmarks/gverify/<doc>.json`. The 15:55 run
read `ratchet.py`, which is the legacy 59-check tool and knows nothing about Google; `regress.py` is the
gate, and `install-gate.sh` installs it as the pre-commit hook.

Falsified in a throwaway copy with a control, `RANKING.csv` edited so `mobile-bill` reads 39.21:

| case | working-tree gverify | `regress.py --check --only docx` |
|:--|:--|:--|
| A control | unchanged, 1 failing | `docx: 1 REGRESSION(S)` → **REFUSED** |
| B | 0 failing | `docx: ALLOWED mobile-bill 18.48 -> 39.21 in LibreOffice, Google 1 -> 0 failing` → **PASS** |

The control is the test: a proxy regression with no Google gain is still refused.

### 2. The dither patch does not generalise, and that kills the 16-document claim

Patch applied clean, engine built in 42 s, and the worst of the 14 proxy regressions measured in both
renderers — `mobile-bill`:

| `mobile-bill` | LibreOffice share@5 | Google |
|:--|--:|:--|
| committed baseline | 1.55 | 46/47, fails `18_displacement` |
| dither patch | **39.21** | **46/47, fails `18_displacement`** |

The LibreOffice figure reproduces 15:55's to the hundredth, which proves the patch was live. Google does
not move. One live round trip: ConvertOne → create as a Google Doc → export PDF → `verify_google.py`
(`18_displacement source=0 render=1`). Probe Doc deleted; Drive root empty; engine reverted to HEAD.

### 3. The next test is one hunk, not one corpus pass

`mobile-bill` is one page whose rows are already on Google's 0.75 pt grid, so the dither has nothing to
diffuse there — the remaining mechanism in the same patch is the spacer moved to `w:before`, which has
never been measured alone on this document. Apply the patch without that hunk and round-trip
`mobile-bill` again: 47/47 means the dither ships alone, and the waiver above is how it lands.

### 4. An obstacle cleared, because it read exactly like a blocker

The gate REFUSED every commit for the first ten minutes — `ENGINE CHANGED (docx): table measured on
6c6cf642e13b7ed2, the tree is 226f7f2df3013ad7`. It was the clone: `--depth 1` leaves `462353f9^`
absent, `scope.py`'s fallback diff fails, the scope comes back empty, the gate goes strict. After
`git fetch --unshallow` the same tree says PASS. Recorded in `LESSONS.md`.

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
| Slot window | 17:12 → running · 12 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 10 |
| Longest silence | **6.9 min** — from 17:17:46, after `relay: engine built with dither patch, converting 2 worst-regressed do` |
| Silences over 2 min | 2 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| setup - claim, housekeeping, reading the gate | **2 min** | `#####` |
| fix - diagnose and change the engine | **6 min** | `#############` |
| record - attempt, handoff, class rows | **0 min** | `#` |
| other - not attributed to a tool | **1 min** | `###` |
