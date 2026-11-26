# `18_displacement` on the 213-document PDF→DOCX corpus — read-only diagnosis

**Repo:** `kavopdf/app`, clone at HEAD `6f3c0ba` (shallow). **Nothing in the repo was modified, committed or pushed.**
**Stores read:** `benchmarks/gverify/*.json` (213 files, engine `981ff1fa35e2cf67`), `benchmarks/DISP-TABLE.csv`, `tools/p2w-bench/RESULTS.jsonl`, `tools/p2w-bench/FINDINGS/` (391 files).
**First-hand work done this session:** engine built with `tools/p2w-bench/build-engine.sh`, corpus fetched with `tools/p2w-bench/corpus-fetch.sh` (213 PDFs), **all 213 documents converted** with `ConvertAll`, the emitted `word/document.xml` parsed, and one LibreOffice probe built and rendered.

---

## 1. What check 18 actually measures

`tools/p2w-bench/verify_google.py`, check 18, inside `compare()`: the block runs **lines 5801–5906**, and the verdict is written at **5904**.

**Population.** Source-PDF runs against Google Docs' own PDF export of the engine's `.docx` — never the `.docx`. `s_runs` / `g_runs` come from `runs()` (`:231`). The measured quantity is `ry`, the **reading-space box top**: the span origin projected through the line's own direction, minus the ascent measured in device space (`verify_google.py:288`, `"ry": round(ryb, 2)`). Units are **PDF points (1/72 in)** throughout; the only rasterised path in the file is check 25. Runs whose text is slanted (`|sin(angle)| > 0.02`) are excluded (`:5860-5861`); 180°-rotated lines are kept because their `dy` is still a displacement.

**The measured difference**, per matched pair: `ds = [(g["ry"] - r["ry"], r["size"]) for r, g in pairs]` — i.e. **render box-top minus source box-top, in points, positive = the render sits lower**.

**Tolerance** (`:5863-5864`):

```python
def _tol(size):
    return min(max(0.35 * size, 1.5), 4.5)
```

**The failure predicate** (`:5888-5895`):

```python
n_out = sum(1 for d, sz in ds if abs(d) > _tol(sz))
worst_here = max(abs(d) / _tol(sz) for d, sz in ds)
if (n_out > max(2, -(-len(ds) * 5 // 100)) or n_out == len(ds)
        or worst_here > TAIL_FACTOR):
    bad_pages.append(pg)
```

with `TAIL_FACTOR = 2.0` (`:5869`). A page fails when, on **that page**:

1. more than `max(2, ceil(0.05·n))` matched runs are out of tolerance, **or**
2. *every* run on the page is out (the page moved as a block, however few runs it carries), **or**
3. one run is out by more than **2× its own tolerance** (the tail clause, absorbed from the retired `19_worst_dy`), **or**
4. upright text is present on the page and **none of it matched** (`:5883-5886`).

A page with no upright run at all is skipped (`if not flat_src: continue`). The check passes only when `bad_pages` is empty. Its stored tuple is `(0, len(bad_pages), not bad_pages, detail)` — so the value written for a failing document is **a count of bad pages, not a distance**; the distances live in the fourth element (`med_dy`, `worst_dy`, `med_dx`, `bad_pages`, `runs_matched`).

**Where the engine decides the number.** `app/src/main/java/com/kavopdf/app/engine/DocxWriter.java`:

* the line box is a **hairline**: `w:line = 1.38·size` twips, clamped at `0.6485` pt — `hairlinePt()`, `:4081`;
* the rest of the pitch rides in **`w:before`** — `spacing()`, `:148-175`;
* a page's top gap is written as **`w:before` on the page's first paragraph** — `flowFromBox` `:4483-4495` and `flowRow` `:3600-3606`, capped by `firstGapCapTw()` `:3998`;
* the section carries **zero margins** — `sectPrXml()`, `:2426-2441`, `w:pgMar w:top="0"` at `:2435`;
* a table's top gap is written as an **empty spacer paragraph**, whole gap in `w:line` on an `sz=2` mark when the page has no room, split into `w:before` when it has — `:6117-6145`, `spacerHairTw = 1` at `:6117`, the room guard at `:6118-6124`;
* a row's height is **`w:trHeight w:hRule="atLeast"` at the page's own pitch** — `rowHeightTw` `:6493`, emitted at `:6583`.

---

## 2. The measured evidence

### 2.1 How many documents fail it

From `benchmarks/gverify/*.json` (213 files, one per corpus document, all stamped engine `981ff1fa35e2cf67`, written 2026-11-26 00:05–00:36):

| | |
|:--|--:|
| documents in the store | 213 |
| **failing `18_displacement`** | **119** |
| passing it | 94 |
| fully CLEAN (empty `failed`) | 47 |
| failing `18_displacement` **and nothing else** | **25** |
| `page_count_refused` (unscorable) | 5 |
| total failing check-instances across the store | **567** |

The 567 reproduces the brief exactly. `classpick.py --leverage` run in this session prints **`18_displacement 54.4`**, and recomputing `Σ 1/len(failed)` over the store gives **54.4** to one decimal — so the leverage figure and the store agree. (The brief's "42 CLEAN" and "208 documents" are a slightly older snapshot: the store now has 47 CLEAN and 213 documents, 5 of them refused.)

`benchmarks/DISP-TABLE.csv` carries a **second, 16-document-stale** verdict set: 103 True / 110 False. Its fail set is a strict subset of the store's (16 documents differ, all store-only failures, e.g. `403_crossword_puzzle`, `362_price_list_dense`, `320_balance_sheet_statutory`), and where both stores carry a `med_dy` they agree within 0.15 pt on **62 of 63** documents. Treat the store as authoritative and DISP-TABLE as a magnitude table.

DISP-TABLE's own attribution column (213 rows):

| attribution | documents failing 18 |
|:--|--:|
| `table-row` | 75 |
| `multipage/pagebreak` | 16 |
| `other` | 6 |
| `table-short` | 6 |
| *(no attribution)* | 0 of the failing |

### 2.2 The magnitudes and directions actually recorded

Only **61 of the 119** failing documents carry a `displacement` block; the other 58 are older records in the same directory with a different shape (`offered`/`checks`/`detail`) and **no magnitude at all**. Over the 61:

| statistic | `med_dy` (pt) | `worst_dy` (pt) | `med_dx` (pt) |
|:--|--:|--:|--:|
| min | **−110.1** | 3.0 | −2.1 |
| p25 | −8.0 | — | — |
| median | **+0.5** | **17.9** | −0.1 |
| p75 | +3.0 | — | — |
| max | **+104.2** | **357.8** | +4.9 |

Direction: **27 negative, 34 positive, 0 exactly zero.** `worst_dy` buckets: `<4.5` 11 · `4.5–10` 15 · `10–30` 11 · `30–100` 15 · `≥100` 9.

The shape is therefore **bimodal, not one constant**: 29 of the 61 have `|med_dy| ≤ 3 pt` (a residual a few points wide that fails on the 5 %-of-runs budget or the tail clause), and 9 documents have a `worst_dy ≥ 100 pt` (one block or one page moved a long way).

Quoted records (verbatim from `benchmarks/gverify/<doc>.json`):

| document | `med_dy` | `worst_dy` | `bad_pages` | `runs_matched` | fails |
|:--|--:|--:|:--|--:|:--|
| `416_many_tiny_pages` | −87.2 | 87.3 | 1…299 (299 of 300 pages) | 900 | 18, 27 |
| `602_bookmarked_annual_report` | −67.6 | 142.6 | 1, 2 | — | 18, 04, 27, 52 |
| `412_page_labels_roman` | −59.0 | 59.1 | 1, 2, 3, 4 | 15 | 18, 27 |
| `403_crossword_puzzle` | −43.6 | 45.7 | 0 | 27 | 18 **only** |
| `330_cad_drawing_sheet` | −110.1 | 161.6 | 0 | — | 18, 04, 45, 47 |
| `600_reviewed_invoice_with_annotations` | **+104.2** | 125.9 | 0 | 56 | 18, 05, 28, 32, 45, 47, 62 |
| `16_right_aligned_amounts_txtpos` | −1.6 | 3.4 | 0 | 64 | 18 **only** |
| `362_price_list_dense` | −2.8 | 5.4 | 0 | — | 18 **only** |

Note the `bad_pages` lists: in `412` and `416` **page 0 is not in the list** — the first page is right and every continuation page is wrong by the page's own top gap. That is the page-top mechanism in the instrument's own output.

### 2.3 First-hand: the emitted XML, and arithmetic that matches the measured `dy`

I converted all 213 documents on this HEAD and parsed every `word/document.xml`. Two constructs dominate.

**(a) The refused table-gap spacer.** 62 of 213 documents emit at least one spacer paragraph with `w:before="0"` and the whole gap in `w:line` on an `sz=2` mark. **59 of those 62 fail `18_displacement`, and 11 of the 25 solo-18 documents are in that set.** Google's measured law for that paragraph is `2.5873 · max(L/240, 0.06)` pt, so a refused gap of `G` pt is laid as `0.2156·G` and everything below it sits **`0.784·G` pt high**:

| document | refused spacer (`w:line`) | declared | Google lays | predicted shortfall | **measured** |
|:--|--:|--:|--:|--:|:--|
| `403_crossword_puzzle` | 1163 tw | 58.15 pt | 12.54 pt | **−45.6** | `med_dy` **−43.6**, `worst_dy` 45.7 |
| `68_journal_wide_table_spanning` | 2880 tw | 144.0 pt | 31.05 pt | **−113.0** | recorded −114.28 pt (`FINDINGS/18-60-59-…-1900-fixer.md` §2) |
| `360_restaurant_menu` | — | — | — | **−113.0** | `worst_dy` **109.9** |
| `374_org_chart` | — | — | — | **−58.7** | `worst_dy` **54.9** |
| `mobile-bill` | 248/128/124 tw | 12.4/6.4/6.2 pt | 2.7/1.4/1.3 pt | −19.6 total | — (no block stored) |
| `72_bank_statement_no_rules_right_amounts` | 366 tw | 18.3 pt | 3.95 pt | −14.3 | DISP-TABLE `med_dy` −15.0 |

Grouped over the 75 failing documents that have both a prediction and a stored `med_dy`:

* predicted shortfall **≥ 5 pt** (n = 32): median `med_dy` **−7.9 pt** (text sits **high**);
* predicted shortfall **< 5 pt** (n = 43): median `med_dy` **+1.7 pt**.

Pearson r between the predicted shortfall and `−med_dy` is only **0.22** — because `med_dy` is a document-wide median while the spacer moves only the block beneath it. On the documents where the spacer is the only large construct, the shortfall shows up in `worst_dy` instead, and there it matches to 1–4 pt (360, 374, 403, 68_journal).

**(b) The page-top gap after a hard break.** 6 of the 61 documents with a `displacement` block have **page 0 clean and later pages bad**. The emitted `w:before` on the first paragraph after each `<w:br w:type="page"/>` is the page's top gap:

| document | post-break gap | predicted shift | measured `med_dy` | agrees? |
|:--|--:|--:|--:|:--|
| `412_page_labels_roman` | 61.4 pt (×4) | −61.4 | **−59.0** | yes, to 2.4 pt |
| `416_many_tiny_pages` | 89.5 pt (×299) | −89.5 | **−87.2** | yes, to 2.3 pt |
| `602_bookmarked_annual_report` | 69.5 pt (×2) | −69.5 | **−67.6** | yes, to 1.9 pt |
| `57_centred_title_page_left_body_pages` | 69.5 pt | −69.5 | −34.1 | **no** |
| `58_header_rule_footer_rule` | 47.5 pt | −47.5 | +0.1 | **no** |
| `417_rotate180_and_mirrored` | 61.4 pt | −61.4 | +2.3 | **no** (180° page) |

Three of six reproduce to ~2 pt; the three that do not are the ones whose first block after the break is not a plain paragraph (title page, rule/footer band) or whose page is turned 180°. The law is real but not uniform — which is the same conclusion the repo reached from the other side (`18-displacement-PGMAR-TOP-REMEASURED-26NOV.md` §3, where `412` was the one document of five that did not move).

**(c) The row-height ladder, re-tested against the repo's own measurement.** Applying `laid = 0.75·(round(d/0.75)+1)` to the actual `w:trHeight` list of each document and comparing with `google_per_row_growth_pt` in DISP-TABLE (87 documents with both): predicted − measured has **median +0.15 pt/row**, but only **36 of 87 agree within 0.5 pt/row**. The law is right in sign and first order, and it is **not** a tight per-document predictor.

**(d) One LibreOffice probe, built here, because two FINDINGS files contradict each other.** A 6-line page, `w:pgMar` zero, 60 pt of gap either as `w:before` on the first paragraph (variant A, what the engine emits today) or as `w:pgMar w:top="1200"` (variant B, what the patch proposes), plus a no-gap control C, rendered with LibreOffice 7.4.7.2:

| variant | first line box top |
|:--|--:|
| A — `w:before="1200"` at a page top | **52.80 pt** |
| B — `w:pgMar w:top="1200"` | **52.80 pt** |
| C — no gap | −7.20 pt |

LibreOffice **does** honour space-before at the top of a page, and the two constructs are byte-for-byte equivalent in position here. This contradicts the mechanism claimed in `FINDINGS/18-DISPLACEMENT-PATCH-IS-NOT-IDENTITY-26NOV.md` ("space-before at a page top is suppressed" in LibreOffice) and supports `FINDINGS/18-displacement-PGMAR-TOP-REMEASURED-26NOV.md` §2 ("0 worse, 0 better, 212 unchanged"). Caveat: one hand-built probe, no styles, no table, no anchored shape — it refutes the general claim, not every instance of it.

---

## 3. Already-refuted hypotheses — do not re-derive

Every row below is a measurement in the repo, not an argument. All paths relative to `tools/p2w-bench/FINDINGS/`.

| hypothesis | verdict and the measurement that killed it |
|:--|:--|
| **Spend the refused spacer, whole or partially, and the table lands** | **Refuted in Google on 2 of 2 and harmful on a third.** `72_bank_statement_no_rules_right_amounts` 41/42 → 41/42; `two-tables-stacked-with-no-gap` 41/42 → 41/42; `68_journal_wide_table_spanning` 41/42 → **40/42** (`59_shape_anchor` 49 → 0, reproduced twice). `18_displacement-PARTIAL-SPEND-IS-INERT-AND-COSTS-68-JOURNAL-2315-fixer.md` |
| …but spending the spacer **where the page has room** did work | **Landed and kept: +3 documents to 42/42** — `73_marksheet_subject_marks_grade`, `41_coloured_headings_white_bg`, `29_dot_leaders_txtpos`, with `mobile-bill` byte-identical. `18_displacement-SPACER-SCOPE-GUARD-LANDS-3-GOOGLE-0051-fixer.md`. **This is the guard at `DocxWriter.java:6118-6124` — it is in HEAD and must not be removed.** |
| **The guard's `slackTw` / `rowExcessTw` thresholds are the cause of the failure** | **Not the cause.** The guard explains why a spacer is *unspent*, not why the document *fails*. `18_displacement-GUARD-CENSUS-14-DOCS-SPEND-IS-NOT-THE-FAILURE-0830-agentA.md` |
| **Dither the `w:trHeight` declarations onto the 0.75 pt ladder** | **Inert in Google and a regression in LibreOffice.** Applied and built, it rewrote the rows on **11 of 13** solo-failure documents and moved **0 of 13**; measured through Google on the two most favourable (`72_bank` 17 of 18 rows rewritten, `bus-timetable` 33 of 33) — both unchanged at 41/42. `18_displacement-UNIFORM-PITCH-SNAP-INERT-ON-THE-13-1120-fixer.md`. Separately `mobile-bill` LibreOffice 1.55 → 39.21 under the dither (`18_displacement-WAIVER-EXISTS-DITHER-DOES-NOT-GENERALISE-174500-relay.md`). |
| **`w:trHeight hRule="exact"` will pin the row** | **Refuted.** Google normalises `exact` back to `atLeast` on import; `atLeast` and `exact` laid the same pitch. `18_displacement-GOOGLE-IGNORES-TRHEIGHT-1045-relay.md`, `18_displacement-ROW-GROWTH-075-QUANTUM-LAW-2354-fixer.md` §2 |
| **The row is declaration-bound, so the cell content sets the height** | **Refuted arithmetically.** Content is `w:before + 0.483` = 9.78–10.98 pt inside an 18.00 pt declaration — 7 pt of slack; `max(declared, content) = declared` on every row. `18_displacement-ROW-GROWTH-075-QUANTUM-LAW-2354-fixer.md` §1 |
| **Table `w:tblpPr`/`tblpY`, cell top/bottom margins, or a whole-point rounding ladder** | **Refuted from the emitted XML.** No vertical table property is written at all, `w:tblCellMar` is already 0, and the ladder is 0.75 pt not 1 pt (18.20 declared lays 18.75). `18_displacement-RESIDUAL-2.5PT-ARITHMETIC-0355-fixer.md` §3, `18_displacement-ROW-GROWTH-075-QUANTUM-LAW-2354-fixer.md` §3 |
| **A 1×1 `w:tbl` + `w:trHeight exact` carrying the page-top gap** | **Refuted when applied.** `bank-statement-5-pages` 5 → 6 pages, `31_pages_lost_their_text` 5 → 1, matched runs 585 → 220, 33/42. The construct itself is real (Google laid 55.83 of 55.15 pt on a probe) but it is not safe at scale. `18_displacement-page-top-before-DROPPED-105000-f1x.md`, `…sectmargin-PROVEN-075600-f1x.md` §1 |
| **`w:before` at a page top is honoured by Google on page 1** | **Confirmed, and it is why the page-top fix cannot reach single-page documents.** `412` page 0 reads +2.3 pt with a 61.35 pt gap; pages 1–4 read −58.8. `18_displacement-page-top-before-DROPPED-105000-f1x.md` |
| **"108 of 122 failures are exactly +1.0 pt and none is negative"** | **An instrument misreading — do not build on it.** The stored value for a failing document is `len(bad_pages)`, not a distance. `416_many_tiny_pages`'s "299.0" is **299 bad pages** (its real `med_dy` is −87.2), and today 57 failing documents have exactly one bad page. The store's actual `med_dy` spans **−110.1 to +104.2 with 27 negative values**. `18-DISPLACEMENT-IS-ONE-UNIT-AND-ALWAYS-POSITIVE-25NOV.md` — refuted here from the store, not from a render. |
| **A right indent from the source margin, with no alignment change** (the `60`-adjacent sibling refutation) | **Refuted**: `47_margins` 82→82, total passes fall by 11. `REMAINING-DEFECTS.md:197`, `patches/README-2026-11-13.md:166-183` |
| **The LibreOffice proxy can referee any of this** | **No.** Every construct above is invisible to LibreOffice by construction: the spacer split and the pgMar move are identities in a renderer that honours both `w:before` and `w:line` exactly. `18_displacement-CENSUS-AND-TWO-INSTRUMENT-FAULTS-0015-relay.md` §2. Google is the only instrument for this class. |

Two further instrument faults worth knowing before you spend a slot: `tools/p2w-bench/dy.py:13` hard-codes `HERE = "/scratch/work/CS/tools/p2w-bench"`, a path that does not exist in a fresh pod; and 58 of the 119 failing records in `benchmarks/gverify/` predate the `displacement` block, so **half the failing population has no stored magnitude at all**.

---

## 4. Ranked root causes

Ranked by (documents the construct is measurably present on) × (how cleanly the arithmetic reproduces the recorded `dy`), restricted to what the repo has *not* already refuted.

### RC1 — the refused table-gap spacer is laid by Google at 21.6 % of its declared height
**Rank 1. Present on 62 of 213 documents; 59 of them fail 18; 11 of the 25 solo-18 documents carry one (10 of them with a shortfall of 5 pt or more).**

**Mechanism.** `DocxWriter.table()`, `:6117-6145`. The gap between the flow and a table's top rule is an empty paragraph with `w:rPr/w:sz=2`. When the room guard (`:6118-6124`) refuses, the whole gap goes into **`w:line`** on that 1 pt mark:

```java
// DocxWriter.java:6131-6135  (the `else` arm, spacerHairTw == 1, wantTw == 0)
sb.append("<w:p><w:pPr><w:snapToGrid w:val=\"0\"/>")
        .append("<w:spacing ... w:before=\"0\" w:after=\"0\" w:line=\"")
        .append(spacerTw)
        .append("\" w:lineRule=\"exact\"/><w:rPr><w:sz w:val=\"2\"/></w:rPr></w:pPr></w:p>");
```

Google does not read `w:line` as a length: it lays `2.5873 · max(L/240, 0.06)` pt. `L/20` is what LibreOffice lays. So `G` pt of gap is drawn as `0.2156·G` and **everything below it sits `0.784·G` pt too high** — a step, not a drift, which is why the check sees a document-wide `med_dy` near zero and a `worst_dy` equal to the step.

**Evidence.**
* `DocxWriter.java:6117` (`spacerHairTw = 1`), `:6118-6124` (guard), `:6131-6135` (refused emission). The law and its provenance are in the code comment at `:6084-6116`.
* First-hand: 62/213 documents emit ≥1 such spacer; 59 fail 18. `403_crossword_puzzle` — one refused spacer of 1163 tw (58.15 pt) → predicted −45.6 pt, stored `med_dy` **−43.6**, `worst_dy` **45.7**. `68_journal` — 2880 tw (144 pt) → predicted −113.0, recorded −114.28. `360_restaurant_menu` predicted −113.0, `worst_dy` **109.9**. `374_org_chart` predicted −58.7, `worst_dy` **54.9**.
* Population: docs with a predicted shortfall ≥ 5 pt have median `med_dy` **−7.9**; those below 5 pt, **+1.7**.
* `benchmarks/DISP-TABLE.csv`: 118 documents carry a spacer, 55 an unspent one; attribution `table-row` on 75 of 103 failing.

**What change would fix it.** *Not* "spend it" — that is refuted twice (§3). The un-refuted move is to make the **refusal no longer all-or-nothing in the renderer that matters**: on refusal, keep the sum `before + line` exactly (so LibreOffice is byte-identical) but choose the pair so Google's two laws agree with the intent, i.e.

```
laidTw  = round(240 * (G/20) / 2.5873)          // the w:line Google would have to be given
beforeTw = spacerTw - laidTw                     // the remainder, which Google draws 1:1
lineTw   = laidTw
```

`LibreOffice` sees `before + line/20 = G` (unchanged); `Google` sees `before/20 + 2.5873·(line/240) = G` (new). This is **the same algebra as the landed spend branch**, generalised to the case the guard refuses — and it is the one variant of this lever that has not been measured. Note the real reason the guard refuses on these documents: the page has no room *because the rows on it are laid ~0.75 pt taller than declared* — RC1 and RC3 are the same defect seen from two ends.

**Documents it would plausibly flip (to CLEAN).** The 10 solo-18 documents that carry a refused spacer with a shortfall of 5 pt or more: `403_crossword_puzzle` (45.6), `68_journal_wide_table_spanning` (113.0), `marksheet-subject-left-marks-right` (28.5), `insurance-policy-schedule` (21.0), `electricity-bill` (20.6), `mobile-bill` (19.6), `72_bank_statement_no_rules_right_amounts` (14.3), `table-with-no-header-row` (9.7), `two-tables-stacked-with-no-gap` (9.7), `bus-timetable-station-left-times-right` (5.0) — plus `table-inside-two-column-page` (3.1) at the margin. Beyond CLEAN, it touches 59 failing documents.

**The one-document test (under 10 minutes, no repo change).** `403_crossword_puzzle` — one page, one refused spacer, one failing check, `runs_matched` 27, `med_dy` −43.6.

```
# 1. convert and take the emitted docx (no code change)
java -cp "out:libs/aar/classes.jar:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar" \
     ConvertOne /scratch/work/p2w/corpus/403_crossword_puzzle.pdf /scratch/work/p2w/out

# 2. rewrite ONLY that one spacer paragraph in the .docx (unzip, replace
#    w:before="0" ... w:line="1163" with w:before="1053" ... w:line="110"), rezip as
#    403_crossword_puzzle_SPENT.docx  — a two-line script, the repo is untouched

# 3. score both through Google, same hour, same folder
python3 tools/p2w-bench/gverify.py --stage 403_crossword_puzzle      # then upload/convert/export
python3 tools/p2w-bench/gverify.py --collect 403_crossword_puzzle <export>
#    and the same pair for the _SPENT variant, then read the two displacement blocks
```

**Confirm:** `med_dy` −43.6 → **within ±2.5 pt** and `bad_pages` → `[]` (42/42).
**Refute:** `med_dy` unchanged (the spacer is not what 403 is measuring — then the −43.6 has another source and RC1's arithmetic match on 403 is a coincidence).

---

### RC2 — a page's top gap is written as `w:before`, which Google drops at the top of every page after a hard break
**Rank 2. Present on 17 of the 119 failing documents (all of them multi-page); measured to ~2 pt on three of them; already PROVEN end-to-end.**

**Mechanism.** `sectPrXml()` writes `w:pgMar w:top="0"` (`DocxWriter.java:2435`), so the text area and the paper are one coordinate system and the page's top gap has to be carried by the first paragraph: `flowFromBox` `:4483-4495` and `flowRow` `:3600-3606` set `beforeTw = min(firstGapCapTw(ctx), topGap·20)`. Google **drops space-before at a page top** — measured on a controlled probe, 55.15 pt asked → **0.33 pt** rendered — so every continuation page's whole block sits high by that page's own gap.

**Evidence.**
* `DocxWriter.java:2435` (margin hard-coded 0), `:4483-4495` / `:3600-3606` (the emitter), `:3998` (`firstGapCapTw`).
* First-hand from the store: in `412_page_labels_roman` and `416_many_tiny_pages`, `bad_pages` **excludes page 0** and includes every continuation page. Gap vs `med_dy`: 412 **61.4 → −59.0**; 416 **89.5 → −87.2**; 602 **69.5 → −67.6**.
* Already measured through Google with the patch: `416` 40/42 → **42/42 CLEAN**; `602` 38/42 → 41/42; `bank-statement-5-pages` 42/47 → 46/47; `324_loan_amortisation_schedule` 44/47 → 46/47; `412` unmoved. Nine check-instances, one CLEAN document, nothing worse. `18-displacement-PGMAR-TOP-REMEASURED-26NOV.md` §3.
* Not refuted, and the reason it cannot help the 25 solo documents: **Google honours space-before on page 1** (412 page 0 = +2.3 pt with a 61.35 pt gap), and all 25 solo-18 documents are single-page (verified: `pages == 1` on every one, both in the store and in my own conversion).

**What change would fix it.** Apply the existing, unlanded patch `tools/p2w-bench/patches/18-displacement-PGMAR-TOP-CARRIES-THE-PAGE-GAP.patch` — it moves the page-first gap into `w:pgMar w:top` and reduces the first paragraph's `w:before` by the same number of twips, so `pgMar + before` is unchanged in every renderer that honours both (my LibreOffice probe: identical to 0.00 pt). Two caveats that are measurements, not opinions: (i) the gate refuses the commit on three documents whose `share5` moves, and the two 26 Nov findings disagree about whether the patch causes that — my probe says the *mechanism* they blame (LibreOffice suppressing space-before at a page top) does not exist, so the regression is more likely the case `401_trifold_brochure` documents, where `pgMar` went `0→1190` while the first `w:before` stayed at `1790` and the gap was therefore **doubled**; (ii) `ctx.budgetTw` at `:1160` and `slackTw` at `:6119` must be reduced by `pageTopTw`, or the spacer guard silently refuses more gaps on multi-page documents.

**Documents it would plausibly flip.** 1 measured CLEAN (`416_many_tiny_pages`), `602` one check away, and ~15 multi-page documents improved by 1–3 checks. **Zero of the 25 solo documents.**

**The one-document test (under 10 minutes).** `412_page_labels_roman` — the one document of the five that did **not** move, so it is the honest discriminator rather than a re-run of a win.

```
git apply tools/p2w-bench/patches/18-displacement-PGMAR-TOP-CARRIES-THE-PAGE-GAP.patch
bash tools/p2w-bench/build-engine.sh
java -cp "out:libs/aar/classes.jar:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar" \
     ConvertOne /scratch/work/p2w/corpus/412_page_labels_roman.pdf /scratch/work/p2w/out
python3 tools/p2w-bench/gverify.py --stage 412_page_labels_roman   # → Drive → export → --collect
```

**Confirm:** `med_dy` −59.0 → ≈ −2 pt and `bad_pages` `[1,2,3,4]` → `[]`.
**Refute:** still −59.0 — then the page-1-only honouring law does not generalise to this document's construct (its post-break first block is not a plain paragraph) and RC2's scope is 416/602 only. Note: judge this on Google only; LibreOffice is an identity here by construction.

---

### RC3 — Google lays every `w:trHeight` one 0.75 pt rung taller than declared
**Rank 3. The residual class: 51 of the 119 failing documents carry neither a refused spacer nor a page break, and 14 of the 25 solo-18 documents are in it.**

**Mechanism.** `rowHeightTw = Math.max(rowTwHere, rowLineTw)` (`DocxWriter.java:6493`) declares the page's own pitch, emitted as `<w:trHeight w:val="…" w:hRule="atLeast"/>` at `:6583`. Google does not lay the declaration: it snaps it to a 0.75 pt grid and adds one whole quantum, `laid = 0.75·(round(d/0.75)+1)`. An 18.40 pt pitch is not on the ladder, so every row is laid 0.5–0.75 pt taller and everything below drifts down with the row count.

**Evidence.**
* The law rests on 11 published points from three independent instruments (`ROW-GRID-AND-SPACER-1518-relay`, `ROW-PITCH-LAW-135800-relay`, `ROW-RULE-IS-OUTSIDE-TRHEIGHT-1220-f1x`), reproducing whole-table sums exactly: `mobile-bill` Σ26 gaps = 513.00 pt = 24×19.50 + 45.
* `mobile-bill` emits 15×360 tw and 9×380 tw (`:6583`), which the law lays at 18.75/19.50 → mean **19.03** against the source's 18.40 — the reported 19.10 is that mean.
* Re-tested here on 87 documents against DISP-TABLE's measured `google_per_row_growth_pt`: predicted − measured **median +0.15 pt/row**, but only **36 of 87 within 0.5 pt/row**. Directionally right, quantitatively loose.
* The lever that follows from the law — dithering the declarations onto the ladder — is **refuted in Google: 0 of 13 solo documents moved**, including `bus-timetable` with all 33 rows rewritten (§3). That is the honest state of this cause: **the law is measured, the fix built from it is not a fix.**

**What change would fix it.** Nothing that only rewrites the declaration. Two things are untested and both are consistent with the refutation: (i) the ladder's quantum must be taken **net** of the row's rule width (`ruleTwHere` is already subtracted from `rowLineTw` at `:6492`, but not from the laid target); (ii) the row's **cell paragraph** must absorb the residue, because the engine's own comment at `:6706-6731` proves no `(w:line, w:before)` pair can be exact for a cell in both renderers and settles for a 0.12 pt bound. If the cell box is where the refuted dither was wrong, the fix is a `w:before` correction **per cell** of `0.75·(round(d/0.75)+1) − d`, not per row.

**Documents it would plausibly flip.** The 14 solo-18 documents with no refused spacer and no page break — `16_right_aligned_amounts_txtpos`, `303_discharge_summary`, `31_times_body_arial_headings`, `320_balance_sheet_statutory`, `325_demat_holdings_statement`, `362_price_list_dense`, `36_embedded_subset_font`, `402_calendar_month_grid`, `70_magazine_drop_cap_photo_caption`, `71_invoice_space_aligned_no_rules`, `74_balance_sheet_indented_subitems`, `balance-sheet-two-columns-of-figures`, `price-list-2col-dense-right-aligned`, `report-2col-table-spanning-both-columns` — plus 51 failing documents in total. Their measured residuals are small (`16_right` −1.6 / 3.4; `362` −2.8 / 5.4), i.e. they fail on the check's 5 %-of-runs budget with a couple of points of error, which is exactly a row-ladder residual.

**The one-document test (under 10 minutes).** `16_right_aligned_amounts_txtpos` — one page, 13 rows all declared `w:trHeight 380` (19.00 pt), no refused spacer, no page break, `runs_matched` 64, `med_dy` −1.6, `worst_dy` 3.4. The law says every row is laid 19.50, so the error must **grow linearly with row index**.

```
java -cp "out:libs/aar/classes.jar:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar" \
     ConvertOne /scratch/work/p2w/corpus/16_right_aligned_amounts_txtpos.pdf /scratch/work/p2w/out
python3 tools/p2w-bench/gverify.py --stage 16_right_aligned_amounts_txtpos   # → Drive → export
# then, on the exported PDF, the per-run dy (fix dy.py's HERE first, see §3):
python3 tools/p2w-bench/dy.py /scratch/work/p2w/corpus/16_right_aligned_amounts_txtpos.pdf <export>.pdf
```

**Confirm:** the per-run `dy` is a **ramp** — ≈0 pt on row 1 and ≈ +0.5·k pt on row k, reaching +6.5 pt at row 13 (the law's prediction: 13 × 0.5 = 6.5).
**Refute:** the `dy` is a **constant** (all rows the same few tenths of a point) — then the residual is the cell box, not the row pitch, and RC3 collapses into the cell-paragraph bound at `DocxWriter.java:6706-6731` and the 51-document residual class has no known cause.

---

### Why these three and not others

The three are disjoint on the population and together cover it: RC1's construct is on 59 failing documents, RC2's on 17, RC3's residual class on 51, with overlap only where a document has both a refused spacer and rows. What is **not** in the list is anything the repo has already measured and killed (§3) — and in particular the two most attractive-looking wrong turns: *"spend the spacer"* (refuted 2-of-2 plus one regression) and *"dither the row heights"* (0 of 13).

---

## 5. What I could not determine

1. **The magnitude of 58 of the 119 failing documents.** Those records in `benchmarks/gverify/` predate the `displacement` block (they carry `offered`/`checks`/`detail` and no `med_dy`), so **half the failing population has no stored distance at all**. Any statement about the class's shape is a statement about the 61 that do.
2. **Where `benchmarks/DISP-TABLE.csv` came from.** No script in the repository writes or reads it (`grep -rn "DISP-TABLE"` returns nothing), it is 16 documents behind the store on the verdict, and its `google_per_row_growth_pt` / `lo_per_row_growth_pt` columns have no stated measurement method. Its `med_dy` agrees with the store to 0.15 pt on 62 of 63 shared documents, so it is probably a snapshot of the same instrument — but the provenance of the growth columns is **not stated**.
3. **Whether the `w:pgMar w:top` patch causes the three-document regression the gate refuses on.** The two 26 Nov findings contradict each other on the mechanism, and my LibreOffice probe supports the "identity" side; I did not re-render the three documents (`newsletter-3col-header-footer`, `601_fillable_admission_form`, `401_trifold_brochure`), so I cannot say which finding is right. The patch's own diff does show the `401` case where `pgMar` went `0→1190` while the first `w:before` stayed at `1790` — a **doubled** gap, which is a sufficient explanation of a regression without any renderer-behaviour claim. **Not resolved here.**
4. **Google's exact law for the `sz=2` spacer paragraph.** I used `2.5873·max(L/240, 0.06)` from `FINDINGS/18_displacement-RESIDUAL-2.5PT-ARITHMETIC-0355-fixer.md` §2 and it reproduces three measured points (TOPB 1103 tw → 11.89 predicted vs 12.22 measured; 68_journal 144 pt → 31.05 laid vs −114.28 measured shortfall; 403 → −45.6 vs −43.6). I did **not** make a Google round trip myself — this session had no Drive write path — so every Google-side number in this report is either quoted from a FINDINGS measurement or derived from one.
5. **Whether RC1's generalised fix (the `laidTw` algebra above) is safe at scale.** It is algebraically an identity for LibreOffice and exact for Google, but the page-height cost is real: Google will now draw the gap it was not drawing, so any document whose source ink already reaches the bottom of the sheet can gain a page. `mobile-bill` and `insurance-policy-schedule` are the two documents that measured exactly that under an unguarded spend. The one-document test above is designed to expose it on `403` first (one page, 58 pt of gap, a crossword grid below it).
6. **The 9 documents with `worst_dy ≥ 100 pt`** (`600_reviewed_invoice_with_annotations` +104.2, `330_cad_drawing_sheet` −110.1, `table-across-page-break-repeated-header` 403.9, `very-long-single-column-table` 656.7 …). Their magnitudes are far outside every construct above and are probably a fourth mechanism (`600`'s `med_dy` is **positive**, which no construct in §4 produces). I did not diagnose them.

---

## Open questions

* Which store is authoritative for the gate — `benchmarks/gverify/` (119 failing) or `benchmarks/DISP-TABLE.csv` (103)? They differ on 16 documents and nothing in the repo says which one `gate.py` / `regress.py` reads.
* Was the `w:pgMar w:top` patch's three-document regression ever re-measured against the pre-regression engine `b7699196`, as `18-displacement-PGMAR-TOP-REMEASURED-26NOV.md` §4 asks? No measurement of that appears anywhere in `FINDINGS/`, and the later file blames the patch instead.
* Is there a Drive write path available to this session? `refresh-google.py` requires `GOOGLEDRIVE_UPLOAD_FILE` with an `s3key` from a staged upload, and `AUTOMATION-THE-GOOGLE-LOOP.md` records `UPLOAD_FROM_URL` as the only automatic route — which needs a public host. Without it, no candidate above can be confirmed from inside a sandbox, and every one of the three tests ends in a manual Drive step.
