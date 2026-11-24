# The four-site foot-band rule makes `61_two_col_abstract_spanning` CLEAN in Google

**Recorded:** 2026-11-24 ~21:20 IST, fixer slot 20:25. Measured in Google Docs.

## What was run

`tools/p2w-bench/patches/foot-band-spend-the-gap.patch` (four `gapCapTw` escapes guarded by
`inFootBand(ctx, y) = y > 0.90 * pageHeightPt`) applied to `DocxWriter.java`, engine rebuilt with
`build-engine.sh` (46 s), five documents converted with the patched engine.

The previous finding (`RUNNING-FOOT-IS-A-ROW-GOOGLE-DROPS-THE-BOX-1855-fixer.md`) measured the
**one-site** variant (the `flowRow` pitch branch only) on `27_two_column_left_short_txtpos`:
40/42 → 42/42 in Google, and named `flowFromBox` as the second site it did not touch. This run
measures the four-site version.

## Measured, before and after, on the patched engine

| document | `w:txbxContent` | `wp:anchor` | characters | page count |
|:--|:--|:--|:--|:--|
| `27_two_column_left_short_txtpos` | 2 → **0** | 5 → 3 | 1913 → 1914 | 1 → 1 |
| `46_chart_coloured_labels_body_text` | 2 → **0** | 26 → 24 | 870 → 871 | 1 → 1 |
| `55_sidebar_box_beside_body` | 2 → **0** | 6 → 4 | 1622 → 1623 | 1 → 1 |
| `61_two_col_abstract_spanning` | 2 → **0** | 6 → 4 | 2493 → 2494 | 1 → 1 |
| `67_two_col_with_sidebar` | 2 → **0** | 6 → 4 | 1553 → 1554 | 1 → 1 |

**Every character of the source is still in the document.** The character multiset of the `w:t` runs
is identical except for **one added space** on each (the anchored box's text became a flowed
paragraph and the join carries a space). Nothing is lost, nothing is duplicated. This is the
falsification the previous attempt at this construct needed and did not have.

`2` `w:txbxContent` is **one** shape, written twice for `mc:Choice`/`mc:Fallback`. The earlier
finding recorded `4` for the same documents at engine `b7699196`; the current engine writes one box
where it used to write two, so the counts are not comparable across engines. The after-count is.

## Google, through the real path

`61_two_col_abstract_spanning`, patched .docx → Drive upload → convert to
`application/vnd.google-apps.document` → export as PDF → `gverify.py --collect`:

| | stored record (engine `b7699196`) | this run, four-site patch |
|:--|:--|:--|
| score | **40/42 FAIL** | **42/42 PASS** |
| failed | `04_chars_missing`, `44_header_footer` | none |
| `w:txbxContent` | 2 | 0 |

With `27` (42/42 at the one-site patch) this is **two documents whose only failures were the
anchored footer row, both now clean in the renderer the user opens.**

`46`, `55` and `67` also lose their box, but they fail `45_char_accuracy` as well, so this construct
alone does not clean them. That is the answer to "if this works, which documents become CLEAN":
**two, and both are now measured.**

## What did not happen, and the arithmetic that stopped it

The patch is **not landed**. It cannot be: `regress.py --check` refuses an engine change whose
`RANKING.csv` was measured on another engine, and the restamp is a full 213-document pass:

* p2w's own recorded throughput is **26 documents per 250 s budget** (`benchmarks/p2w.py:421`);
* plus `docx()`, which is **one JVM per document** by design (see below): 213 × ~10.8 s / 2 cores ≈
  19 min;
* so a restamp is **≈ 54 min**, and the slot had 50 when the measurement above finished.

The patch file stays in `patches/` with two Google renders behind it. **The next run that starts
with a warm corpus and 90 minutes can land it in one pass**: `p2w.py --budget 280` repeatedly (it
resumes — `dist2/<name>.json` per document, and a partial pass writes only
`/scratch/output/RANKING.partial.csv`), then `regress.py --stamp`.

## The cold pod is the reason the last three runs landed nothing, and it is now 8 minutes

The gate refuses **every** commit, including the claim, when the converted corpus is absent — and on
a fresh pod it always was, for two mechanical reasons:

1. **No JVM.** `build-engine.sh` fetches one from Adoptium itself; nothing had run it.
2. **No corpus.** `corpus-fetch.sh` puts the 213 PDFs on the pod (4 release zips + 5 in-repo). It
   was never called, so `corpus-convert.py` returned 3 and `regress.py` set `fail = 1`.

Then, with both present, the build still could not finish: it started from zero every time, and
213 × 10.8 s is 19 min against a 290 s call limit. `corpus-convert.py` now resumes (a document
already converted by this engine is skipped, validated as an openable zip holding
`word/document.xml`, so a JVM killed mid-write is not counted as finished) and converts a shard of
10 documents per JVM. Measured this run: **213 documents, warm, stamp `b97d8172ce642eb0`, in ~8 min
across two calls**, and `regress.py --check` then printed PASS for both formats and google-safe.

**A run that starts on a fresh pod must do these three things before it can claim anything:**
`corpus-fetch.sh`, `build-engine.sh`, `corpus-convert.py --ensure` (repeat until the stamp exists).

## One caution about the shard size, and the evidence for it

`benchmarks/p2w.py:1050-1075` records that **`ConvertAll` carries state between the documents it is
given**: `392_statistical_console_output` scored `share5` 1.61 converted alone, 1.61 with 1 other,
**1.61 with 11 others**, and **28.39 inside the full corpus of 213 in one JVM**. A sharded corpus
build is therefore only safe up to about twelve documents per JVM; `corpus-convert.py` uses 10, and
a build of 213 in one JVM would be wrong. This is why the corpus build is sharded and the ranking is
not: the ranking needs one JVM per document because its numbers must be reproducible per document,
the gate only needs the construct census.

## What would prove this wrong

* **Displacement.** The census refutes spend-always on displacement, not page count. If `27` or `61`
  shows a median or max displacement above its HEAD value in `p2w`, the foot band bought a text
  layer by moving the page and this is not a fix. Neither has been re-measured in `p2w` yet — that
  is the first number the next run should take, before the restamp.
* **A second document of a different shape.** `61` (two columns, spanning abstract) is a different
  shape from `27` (two columns, short text position), and both pass — that part is satisfied.
* **A page count change** on any of the five: none moved.
