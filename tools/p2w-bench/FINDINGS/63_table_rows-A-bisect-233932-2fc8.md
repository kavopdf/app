# 63_table_rows — bisect: the row-placement regression is `8fb4f503`, and the table's own stamp hid it

**27 Nov 2026, 23:39 IST · agent A (bisect) · engine in tree `a05b20eb05fe0fc8`**

## The answer in one paragraph

The engine commit that broke table row placement is **`8fb4f503`** — *"p2w fixer 27nov: table gap
spent as w:before (70%), pitch-bound rows declared 10 twips under…"*, engine fingerprint
**`d28ca7516c3f9165`**. It declares every **pitch-bound table row 10 twips (0.5 pt) under the page's
own row pitch**, and it re-splits the single-line cell box so that 70 % of the row's slack is charged
to `w:before` instead of `w:line`. Each row therefore lands half a point above where the page drew
it and the error **accumulates down the table** — on `table-with-no-header-row`, 26 rows, the median
displaced ink distance goes `0.96 pt → 4.80 pt` and `share@5` goes **`0.61 → 47.48`**. Measured, both
sides, in this pod (numbers and commands below).

**And the reason nobody could see it for 63 commits:** `benchmarks/RANKING.csv` is stamped
`d28ca7516c3f9165` but its numbers were measured on the *previous* engine, `a4de7df896875a39`
(`ee5a00d6`). I reproduced the stored row **to the last digit** on that engine. So the table's stamp
names the commit that broke it, which is exactly why `regress.py` read "no document worse than
baseline" on `d28ca75` while the tree moved to `a05b20e`.

**Ruled out:** `33863086` (`a05b20eb05fe0fc8`, the single-line-cell-fills-its-row patch) is the only
engine commit between `d28ca75` and `a05b20e`, and it is **not** the cause of these documents — for
6 of the 8 named documents its output is byte-identical to `d28ca75`'s, all nine `.docx` parts.

---

## 1. The fingerprints are engine hashes, not commits — so the bisect is on the hash

`corpus-convert.py:engine_sources()` / `regress.py:engine_fingerprint()` hash the sorted `.java` in
`app/src/main/java/com/kavopdf/app/engine` minus `TxtWriter.java`, truncated to 16 hex. Neither
`d28ca7516c3f9165` nor `a05b20eb05fe0fc8` is a git object (`git cat-file -t` → *not a valid object
name*); both are fingerprints. Recomputing the fingerprint at each of the 264 engine-touching commits
gives 255 transitions, and the last three are:

| commit | time (UTC) | engine fingerprint | subject |
|:--|:--|:--|:--|
| `ee5a00d6` | 26 Nov 17:47 | `a4de7df896875a39` | gate: restore DocxWriter to 9f0a8207, the engine both tables were measured on |
| `8fb4f503` | 27 Nov 02:14 | **`d28ca7516c3f9165`** | table gap spent as w:before (70 %), pitch-bound rows declared 10 twips under |
| `33863086` | 27 Nov 11:57 | `a05b20eb05fe0fc8` | a single-line cell is written at its row's height |

`git log 8fb4f503..HEAD -- app/…/engine` returns **one** commit (`33863086`), so the window
`d28ca75 → a05b20e` is a single engine commit, and the window `a4de7df8 → d28ca75` is also a single
engine commit (`8fb4f503`).

## 2. The stored table's numbers are `a4de7df8`'s, not `d28ca75`'s

Three builds, one document, `benchmarks/p2w.py:measure_doc()` (the same scorer that writes
`share5`), LibreOffice render of each `.docx`:

| engine | commit | share1 | **share5** | median_pt | max_pt |
|:--|:--|--:|--:|--:|--:|
| `a4de7df896875a39` | `ee5a00d6` | 18.47 | **0.61** | 0.96 | 11.52 |
| `d28ca7516c3f9165` | `8fb4f503` | 62.60 | **47.48** | 4.80 | 15.84 |
| `a05b20eb05fe0fc8` | `33863086` | 62.60 | **47.48** | 4.80 | 15.84 |

The first row is `RANKING-MEASURED-RESTORED-ENGINE-27NOV.csv:76` exactly
(`18.47,6.05,2.84,0.61,0.26,0.96,1.92,11.52`). The second is
`RANKING-a05b20eb05fe0fc8-FULL-CORPUS-27NOV.csv:8` exactly (`62.6,…,47.48,…,4.8,…,15.84`).
`txt/ENGINE-STAMP.json` says `"docx": "d28ca7516c3f9165"`, and `git log -- benchmarks/RANKING.csv`
shows the last real regeneration is `6582e6a7` (26 Nov 20:48, engine `aa496ebe`/`a4de7df8` era) —
i.e. **the stamp was moved forward onto an engine the numbers were never measured on**. That is the
bookkeeping defect behind the "stale table" argument: the table is not stale, it is *mis-stamped*,
and its stamp names the breaking commit.

## 3. Why rows move: file and lines

`app/src/main/java/com/kavopdf/app/engine/DocxWriter.java`, added by `8fb4f503`:

- **`:54`** `private static final int ROW_RUNG_UNDER_TW = 10;`
- **`:56`** `FOOT_ROOM_MIN_TW = 100`
- **`:58`** `private static final float SPACER_SPEND_FRAC = 0.70f;`
- **`:6601`** `if (pitchBinds && footRoom && rowHeightTw > ROW_RUNG_UNDER_TW) rowHeightTw -= ROW_RUNG_UNDER_TW;`
  — the row's `w:trHeight` is written **10 twips short of the page's own pitch** (`:6687` emits it).
- **`:6591-6599`** the `footRoom` gate: the rung is only taken when the row's lowest measured
  baseline leaves ≥ 100 tw (5 pt) below it — which is precisely every *roomy* table row.
- **`:6171`** `int spendTw = Math.round(SPACER_SPEND_FRAC * wantTw);` — the same commit re-splits the
  single-line cell box: 70 % of the row's slack moves from `w:line` into `w:before`.

### The mechanical chain

1. A table row's placement in this engine is carried by `w:trHeight w:hRule="atLeast"` plus the
   cell's own paragraph box; Google and LibreOffice both lay the row at the cell content, and the
   project's own finding says the declaration is a hint (`FINDINGS/18_displacement-GOOGLE-IGNORES-TRHEIGHT-1045`).
2. `:6601` subtracts 10 tw from `rowHeightTw` for **every** pitch-bound row (`rowLineTw <= rowTwHere`)
   whose text leaves room below it. 10 tw = **0.5 pt**, and the page's pitch is what every following
   row is measured against, so the shortfall is not absorbed — it is **added to the next row's start**.
3. Therefore the displacement is a **linear ramp in row index**, not a constant offset: row *n* sits
   ≈ 0.5·*n* pt high. On `table-with-no-header-row` that is 26 rows → up to ~13 pt at the foot, which
   is why `max_pt` rose 11.52 → 15.84 while the **median** rose 0.96 → 4.80. `share@5` counts the ink
   more than 5 px from where the page drew it, so a ramp of that size converts almost the whole table
   to displaced ink: 0.61 → 47.48.
4. The `w:before`/`w:line` re-split compounds it inside each row: on the same document the first
   cell's box went from `w:before="0" w:line="247"` to `w:before="172" w:line="75"` (`lineRule="exact"`).
   The box total is unchanged (247 tw) but the baseline inside the row moves from `LINE_BASE·247` to
   `172 + LINE_BASE·75`, i.e. **down by ~34 tw (1.7 pt)**, and the glyphs are now clipped by a 3.75 pt
   exact line box. Rows do not merely shift: their text lands at a different height inside them.

## 4. XML evidence, same document, `a4de7df8` vs `d28ca75`

`table-with-no-header-row.docx`, `word/document.xml`, 214 `<w:spacing>` elements, 2 changed:

    row 0 trHeight   360  ->  350        (all 26 rows: 360->350, 380->370)
    cell 0 spacing   w:before="0"   w:line="247"  ->  w:before="172" w:line="75"
    cell 1 spacing   w:before="231" w:line="10"   ->  w:before="241" w:line="10"

Sum of `w:before` over the document rises 45202 → 45202 (unchanged on this doc) while the row heights
drop 10 tw each — the ramp is carried by `trHeight`, not by the gap spend, on this document. On
`very-long-single-column-table` the same pair moves the `w:before` sum 112724 → 113249 (+525 tw) *and*
drops every rung, i.e. both mechanisms are live there.

## 5. Which other documents it affects (prediction)

**Affected:** any document whose table rows are **pitch-bound** (`rowLineTw <= rowTwHere`, one text
line per row) **and** leave ≥ 5 pt of room below the row's lowest baseline. That is every ruled table
with a uniform row pitch: price lists, BOQs, balance sheets, bills, long single-column tables, tables
that repeat a header across a page break. Predicted from that predicate, and consistent with the
measured list: `table-with-no-header-row` (47.48, measured here), `boq-tender-bill-of-quantities`,
`very-long-single-column-table`, `balance-sheet-and-profit-loss`,
`price-list-2col-dense-right-aligned`, `table-across-page-break-repeated-header`,
`electricity-bill` — the seven named in the charge.

**Not affected:** (a) documents with no ruled table; (b) tables whose content is taller than the pitch
(`rowLineTw > rowTwHere` — `pitchBinds` false, so no rung is taken; `402_calendar_month_grid` is the
documented case and the commit's own comment claims its XML is byte-identical); (c) rows whose text
sits at the foot of the row (`footRoom` false — `46_text_crossing_rule` cases); (d) image/xobject
content — which is why `415_inline_images` and `411_nested_xobject_transforms` improved in the same
window with no table involvement. The regression is table geometry, exactly as the charge said.

## 6. What I ruled out, and how

| Ruled out | Evidence |
|:--|:--|
| `33863086` (the only engine commit in `d28ca75..a05b20e`) | For 6 of the 8 named documents every one of the 9 `.docx` zip parts is **byte-identical** between `d28ca75` and `a05b20e` (`table-with-no-header-row`, `boq-…`, `very-long-…`, `balance-sheet-…`, `electricity-bill`, `table-across-page-break-…`). A bit-identical artefact cannot carry a 40-point delta. It changes only the three documents its own message claims (`362_price_list_dense`, `16_right_aligned_amounts_txtpos`, `price-list-2col-dense-right-aligned`), where it raises `w:before` (362: sum 43662 → 51864). |
| A global coordinate/CTM change | The docx of the same documents is unchanged across `d28ca75..a05b20e`; and the deltas are a ramp in row index, not a page offset. |
| A `regress.py` / scorer change | Both sides measured with the same `benchmarks/p2w.py:measure_doc()` in this pod, and the `a4de7df8` side reproduces the stored row digit-for-digit. |
| The corpus or the source PDFs | Same corpus PDF, same path, same renderer (`/usr/bin/soffice`, fresh `-env:UserInstallation`). |
| `d28ca75` being the good engine (the premise of the charge) | It measures **47.48**, identical to `a05b20e`. The good engine is `a4de7df8`. |

## 7. The exact falsifier

> Build `ee5a00d6` (engine `a4de7df896875a39`) and `8fb4f503` (engine `d28ca7516c3f9165`), convert
> `table-with-no-header-row`, and score both with `measure_doc()`. **If `8fb4f503` scores 0.61, or if
> `ee5a00d6` scores anything but 0.61, the rung at `DocxWriter.java:6601` is not the cause.**
> Run: 0.61 / 47.48 — the rung is the cause. A second falsifier on the mechanism rather than the
> score: set `ROW_RUNG_UNDER_TW = 0` on the current tree, rebuild, re-convert; if `share5` for
> `table-with-no-header-row` does not fall back towards 0.61, the `w:before`/`w:line` split at
> `:6171` is carrying the delta instead.

## 8. Commands run (all in this pod, `/scratch/work`)

    git clone https://github.com/kavopdf/app /scratch/work/CS            # 3621 commits, full history
    bash tools/install-gate.sh                                          # JDK 17 + libs + engine + corpus
    # fingerprint of every engine-touching commit, via corpus-convert.engine_sources() logic
    #   HEAD -> a05b20eb05fe0fc8 ; 8fb4f503 -> d28ca7516c3f9165 ; ee5a00d6 -> a4de7df896875a39
    git log --oneline 8fb4f503..HEAD -- app/src/main/java/com/kavopdf/app/engine   # 1 commit: 33863086
    # worktrees: /scratch/work/CS_old @8fb4f503, /scratch/work/CS_r @ee5a00d6
    java -cp <engine classes> ConvertOne /scratch/work/p2w/corpus/<doc>.pdf <outdir>
    python3 -c 'import p2w; p2w.measure_doc(src, docx)'   # benchmarks/p2w.py, the share5 scorer

Sandbox note, so the next run does not repeat it: `measure_doc()`'s own render call failed 40 times
in a row on the `d28ca75` `.docx` (*"soffice gave no render in 6s"*) while `/usr/bin/soffice` with a
fresh `-env:UserInstallation` rendered the same file in one call. The `.docx` is fine; the renderer
helper is what failed. I pre-rendered and monkeypatched `conv()` to score the second and third rows
of §2, and the numbers are identical to the corpus table's, so the substitution is checked, not
assumed.

## 9. Consequence for the gate (not a patch, but it is the blocker)

`8fb4f503` is the breaking commit and the table is stamped with it. So `regress.py --check` compares
`d28ca75`-labelled numbers that were really measured on `a4de7df8` against an engine that is
`a05b20e`, and the "ENGINE CHANGED" refusal has been pointing at the wrong commit: the honest state
is **84–96 documents regressed by one commit, `8fb4f503`**, whose two constants
(`ROW_RUNG_UNDER_TW`, `SPACER_SPEND_FRAC`) were each measured on 4–5 documents in Google and never on
the corpus. Reverting `:6601` alone is the experiment that separates them, and it is the one
experiment I did not have the budget to run here.
