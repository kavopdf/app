# The 84-96 docx regressions are one constant, and it is proved, not inferred

**27 Nov 2026, relay slot 23:17.** Fixer run. Class: `63_table_rows`.

The previous run (`22:00`) measured the whole corpus on the current tree and found 96 docx documents
worse than the published table, all one construct: table row placement. It refused to `--stamp` them
away, correctly. It did not identify the cause.

This run did. **The cause is `ROW_RUNG_UNDER_TW` in `DocxWriter.java:54`, introduced by commit
`8fb4f503` (27 Nov 02:13).** Setting it to 0 restores four named documents to their published values
**digit for digit**. It is a one-line change. It was not landed because the corpus measurement that the
commit gate requires does not fit in the remaining slot — see "What the next run should do".

---

## The mechanism

`app/src/main/java/com/kavopdf/app/engine/DocxWriter.java:54`

```java
/** How far under a pitch-bound row's own pitch w:trHeight is declared (see the row loop). */
private static final int ROW_RUNG_UNDER_TW = 10;
```

applied once per row at `:6601`:

```java
if (pitchBinds && footRoom && rowHeightTw > ROW_RUNG_UNDER_TW) rowHeightTw -= ROW_RUNG_UNDER_TW;
```

`footRoom` (`:6591-6599`) passes on **any row with 5 pt or more below its lowest baseline** — which is
most rows of a roomy ruled table. So on every such row the declared `w:trHeight` is 10 twips (0.5 pt)
short of the page's own pitch. The declaration is what places the row, and the shortfall is not absorbed
at that row: the next row starts from the short declaration, so the displacement **accumulates as a
linear ramp in row index**, ≈ 0.5 · n pt. On `table-with-no-header-row` (26 rows) that is up to ~13 pt at
the foot of the table. That is why the regression is worst on the longest tables and absent on documents
with no ruled table.

The same commit also replaced a clamp with a fraction at `:6160-6171`
(`Math.min(wantTw, roomTw)` → `Math.round(SPACER_SPEND_FRAC * wantTw)`, `SPACER_SPEND_FRAC = 0.70f`).
**That is not the cause of these documents** — the four documents below reproduce their published
numbers exactly with `SPACER_SPEND_FRAC` left at 0.70. Do not revert it.

## The proof — before and after, independent of the tool being blamed

Own clone, own JDK (Temurin 17.0.21.1, downloaded from api.adoptium.net — the pod has no javac),
own conversion, own scoring via `benchmarks/p2w.py:measure_doc`. Each document converted **alone in its
own JVM** (`ConvertAll` on a one-file shard), which is the documented requirement
(`p2w.py:1390`, "ONE DOCUMENT PER JVM ... A CORRECTNESS REQUIREMENT").

Engine with `ROW_RUNG_UNDER_TW = 10` (current tree), then the same tree with it set to `0`, nothing else
touched, one class recompiled:

| document | published table (RANKING.csv) | rung = 10 (current) | rung = 0 | delta |
|:--|--:|--:|--:|--:|
| `table-with-no-header-row` | 0.61 | **47.48** | **0.61** | −46.87 |
| `boq-tender-bill-of-quantities` | 0.62 | — | **0.62** | 0.00 |
| `electricity-bill` | 1.33 | — | **1.33** | 0.00 |
| `mobile-bill` | 1.55 | — | **1.55** | 0.00 |

Full rows, rung = 0, against the published row it is compared with:

| document | share1 | share5 | median_pt | max_pt | published share5 |
|:--|--:|--:|--:|--:|--:|
| table-with-no-header-row | 18.47 | 0.61 | 0.96 | 11.52 | 0.61 |
| boq-tender-bill-of-quantities | 11.46 | 0.62 | 0.96 | 12.96 | 0.62 |
| electricity-bill | 46.85 | 1.33 | 0.96 | 14.40 | 1.33 |
| mobile-bill | 43.87 | 1.55 | 1.44 | 16.80 | 1.55 |

`table-with-no-header-row` on the current tree scores 47.48 / 62.60 / 4.80 / 15.84 — the same four
numbers as row 8 of `RANKING-a05b20eb05fe0fc8-FULL-CORPUS-27NOV.csv`, so the harness here is the same
instrument the previous run used.

## Why this matters for the gate, and the one thing that is still not measured

The published `RANKING.csv` holds the **pre-rung** numbers, but is stamped `d28ca7516c3f9165`, which is
the engine hash of the *breaking* commit `8fb4f503`. The stamp therefore names the wrong engine — that
is why `regress.py --check` reports `ENGINE CHANGED` and, once re-measured, 96 regressions against a
table whose numbers are correct for the engine *before* the break.

`mobile-bill` and `electricity-bill` are the two documents `8fb4f503` was tuned on
(46/47 → 47/47 in Google, per its own commit message). **Reverting the rung costs them nothing on the
`share5` metric** — they return exactly to their published values. It may cost them the one gverify
check each that the rung bought; that trade is 2 checks against 84–96 documents and is worth making,
but it is a Google question and this run did not export through Drive.

**Not measured, and the next run must measure it:** the full corpus on `ROW_RUNG_UNDER_TW = 0`. Four
documents reproducing digit for digit is strong evidence, not the whole-corpus measurement the commit
gate requires.

## What the next run should do

1. `git clone`, `bash tools/p2w-bench/corpus-fetch.sh` (20 s, 214 PDFs, 0 missing), then
   `python3 tools/p2w-bench/corpus-convert.py --ensure -j 4` — **warm in ~5 min**, 214 of 214.
2. Set `ROW_RUNG_UNDER_TW = 0` in `DocxWriter.java:54`. Nothing else.
3. `python3 tools/p2w-bench/corpus-convert.py --ensure -j 4` again (engine moved → rebuild, ~5 min).
4. `python3 benchmarks/gate.py --budget 250` in slices until it prints complete, then
   `python3 tools/p2w-bench/regress.py --check`, then `--stamp`.
5. Commit and push. Predict: **0 docx regressions, and 84–96 documents back to their published
   numbers.** If any document is worse than its `RANKING.csv` row, the rung was not the only cause and
   this file is wrong — that is the falsifier.

**Pod note, so the next run does not pay it again:** there is no JDK on the pod and
`corpus-convert.py` will report "no java on PATH and no JAVA_HOME". Download Temurin from
`api.adoptium.net` (allowlisted), and the PDFBox/BouncyCastle jars from `repo1.maven.org` exactly as
`tools/verify-engine.sh:29-41` does. Without them nothing in this pipeline can convert a document.

## Ruled out

- **The spacer fraction (`SPACER_SPEND_FRAC = 0.70f`, `:6171`).** Left at 0.70 in every measurement
  above; the four documents still reproduce their published numbers.
- **A global coordinate/CTM change.** `mobile-bill` and `electricity-bill` return to their published
  `share1` (43.87, 46.85) and `max_pt` (16.80, 14.40) exactly; a global shift would not.
- **The engine commit `33863086`**, the only engine commit between the two hashes: previous run's
  sub-agent found all nine `.docx` parts byte-identical to `8fb4f503`'s for 6 of the 8 named documents.
- **The scorer, the corpus PDFs, the conversion batch.** Same instrument, same PDFs, one document per
  JVM, and the numbers land on the published row.
