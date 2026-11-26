# The page-count gate on the `aa496ebe` page-top clause is REFUTED — the clause is inert on every multi-page document, so a "1 page only" gate switches off 100 % of its measured effect

**Run:** research agent, 27 Nov 2026 · **Repo:** `kavopdf/app` at `a1efec6`, engine `9f0a8207` (tree clean, `git status` empty)
**Subject:** `tools/p2w-bench/PATCHES/aa496ebe-pagetop-not-identity.patch` (229 lines, one file)
**Proposal tested:** "gate it on page count — `pageTopTw = 0` when the document has exactly 1 page"
**Verdict:** **REFUTED.** The gate is a kill switch, not a discriminator. It removes the itr win and the
newsletter/601/401 losses together, because they are all the same documents.

---

## 0. What I measured, and what I only read

| | |
|:--|:--|
| **Measured here** (pandas over committed CSVs, plus `git`/`grep` over the source) | page counts of the deciding documents; the complete set of documents whose `share5` moved between the patched and reverted engine; the page-count distribution of the corpus; that `aa496ebe` is fully absent from `app/`; that the committed `RANKING.csv` is a *mixed* table |
| **Read, not measured** (quoted from committed FINDINGS/CSV) | the 785 pt / 842 pt ink extent of newsletter; the "change 1" measurement; every `share5` value, which is a LibreOffice-proxy render of a committed engine |
| **Not available on this pod** | the corpus PDFs (`/scratch/work/p2w/corpus` does not exist here; only 124 PDFs of 213 are in the repo, none of the deciding six). **No `doc.page_count` was read.** Page counts below come from `RANKING.csv`'s `pages` column — which is written from `pages_src`, the *source PDF* page count (`benchmarks/p2w.py:1762`) — cross-checked against `benchmarks/gverify/*.json`'s `want` field. Both are the same quantity PyMuPDF's `page_count` would give. |

---

## 1. Claim: the proposal is refuted, and it is refuted by page count itself

The gate would zero the clause on 1-page documents and keep it on multi-page ones. Measured, that is
exactly backwards from the effect:

**Every document the clause moves is a 1-page document. Every multi-page document is inert to the digit.**

From `tools/p2w-bench/FINDINGS/evidence-26NOV/RANKING-26NOV-patched-engine.csv` vs
`.../RANKING-26NOV-reverted-engine-212.csv`, joined on `document` (212 rows in both):

| document | `pages` | `share5` reverted | `share5` patched | delta | verdict |
|:--|--:|--:|--:|--:|:--|
| `newsletter-3col-header-footer` | **1** | 0.20 | 86.30 | **+86.10** | destroyed (clean → content-loss) |
| `601_fillable_admission_form` | **1** | 52.39 | 55.32 | +2.93 | worse |
| `401_trifold_brochure` | **1** | 0.03 | 0.79 | +0.76 | worse (doubling; guard fixes it, §5) |
| `39_small_caps_letter_spacing` | **1** | 0.70 | 0.80 | +0.10 | worse |
| `350_question_paper` | **1** | 0.11 | 0.12 | +0.01 | worse |
| `600_reviewed_invoice_with_annotations` | **1** | 62.46 | 60.70 | −1.76 | *better* — see §6, the prose says otherwise |
| `itr-computation-with-slab-table` | **1** | 42.33 | 9.10 | **−33.23** | **the win** |

* **7 documents moved; 7 of 7 are 1 page.**
* **20 documents are multi-page; the maximum `|delta|` among all 20 is 0.0000.** Not "small" — zero, on
  `bank-statement-5-pages` (5 pp), `324_loan_amortisation_schedule` (7 pp), `041122-Account_Opening_Form`
  (9 pp), `412_page_labels_roman` (5 pp), `602_bookmarked_annual_report` (3 pp) and the other 15.
* The corpus is **192 of 212 rows at 1 page (90.6 %)**, 20 multi-page.

So `pageTopTw = 0 when pages == 1`:

1. turns the clause off on `itr-computation-with-slab-table` (1 page) — **the win is forfeited**;
2. turns it off on `newsletter`, `601`, `401`, `39_small_caps`, `350` (1 page each) — the losses are avoided;
3. leaves it on for the 20 multi-page documents, where it is **measured to change nothing**.

Net effect on the whole 212-document corpus: **zero documents move.** The gate does not narrow the
clause, it deletes it.

The prior run's own acceptance criteria make the contradiction explicit — `LAST-MESSAGE.md:123-125` records
the proposal as *"`pageTopTw = 0` when pages == 1"* with six deciding documents: *"newsletter, 600, 601, 401
must not move; itr-computation and bank-statement-5-pages must keep their gain."* All six are 1 page
(`bank-statement-5-pages` is 5 and was never gaining — 0.56 → 0.56, delta 0.0000). Under the gate all six
are byte-identity, so both arms are satisfied **vacuously** and nothing is bought. The criteria cannot be met
by that gate in any non-vacuous way.

---

## 2. What the patch actually changes (measured by reading the diff)

One file, `app/src/main/java/com/kavopdf/app/engine/DocxWriter.java`, 10 hunks, all one semantic move: the
page's top gap is written in `w:sectPr/w:pgMar@w:top` instead of in the first paragraph's `w:before`.

| patch line | hunk (old line) | what it does |
|--:|--:|:--|
| 27 | `@@ -817` | adds `int pageTopTw;` to `Ctx` — the section's top margin in twips |
| 38 | `@@ -1092` | `ctx.pageTopTw = sectionTopTw(result);` set once, before any byte of `<w:body>` content is written |
| 47 | `@@ -1125` | the section-break emitter passes `ctx.pageTopTw` into `sectPrXml` |
| 62-63 | `@@ -1351` | the final `w:body` `w:sectPr` passes `sb.indexOf("<w:body><w:p") >= 0 ? ctx.pageTopTw : 0` — a byte-level guard so a body opening with a `w:tbl` gets the identity |
| 70-72, 79-81, 91 | `@@ -2424`, `@@ -2437` | `sectPrXml` gains a 5-arg overload carrying `topTw`; the two existing signatures forward `0` |
| 100 | `@@ -2437` | `w:pgMar w:top="0"` → `w:pgMar w:top="{max(0,topTw)}"` — **the only byte in the file that changes** |
| 108, 117 | `@@ -3740`, `@@ -3816` | `flowRow`'s emitter: captures `firstOnPage = ctx.newPage` and routes `w:before` through `pageFirstBeforeTw` |
| 150-192 | `@@ -4378` | new `sectionTopTw(Result)`: `min` over `result.pages` of `y - LINE_BASE*hairlinePt(size)` in twips, capped at `max(2000, pageHeight·TWIPS_PER_PT)`; **returns 0** unless `page.blocks[0]` is a non-`pinned` `PdfToWord.Para` with non-blank text, or a `Box` with non-blank text |
| 205-208 | `@@ -4378` | new `pageFirstBeforeTw(ctx, pageFirst, beforeTw)` = `pageFirst && pageTopTw > 0 ? max(0, beforeTw - pageTopTw) : beforeTw` |
| 217, 226 | `@@ -4655` | `flowParagraph`'s emitter: same `firstOnPage` capture and same routing |

Two properties of the diff matter for the gate question:

* the margin is **one number per document** (`min` over pages, patch:189), so nothing in the patch is
  per-page — the gate would also be per-document;
* `flowTw` / `budgetTw` are deliberately **not** adjusted (patch:24-25, 198-201). That is the defect the
  gate is being asked to paper over; see §4.

---

## 3. What the current code does (measured)

`aa496ebe` is **fully reverted** — `ee5a00d` ("gate: restore DocxWriter to 9f0a8207"), 141 lines removed.

```
$ grep -rn "pageTopTw|sectionTopTw|pageFirstBeforeTw" app/
(no matches — 0 hits)
```

* `DocxWriter.java:2448` — `w:pgMar` is a literal: `"<w:pgMar w:top=\"0\" w:right=\"0\" w:bottom=\"0\" w:left=\"0\""`.
* `DocxWriter.java:2426` and `:2439` — only the 2-arg and 4-arg `sectPrXml`. There is no `topTw` parameter.
* `DocxWriter.java:1128` and `:1354` — both `w:sectPr` emitters call the 4-arg form. The final body section is
  `sectPrXml(secW <= 0 ? 595f : secW, secH <= 0 ? 842f : secH, secCols, secGap)` — no margin argument at all.
* `DocxWriter.java:819` — `Ctx` has `boolean newPage = true;` and **no `pageTopTw` field**.
* `DocxWriter.java:149` — `spacing(int beforeTw, int lineTw, float size, boolean auto, boolean pageFirst)`
  takes `pageFirst` and spends it only on the auto first-line compensation (`:166`,
  `b += Math.round((1f - LINE_BASE) * (boxTw - lineTw))`). It never subtracts a section margin.
* `DocxWriter.java:3819` and `:4670` — the two body-paragraph emitters pass `ctx.newPage` straight into
  `spacing(...)`.

So the current engine puts the whole page-top gap in the first paragraph's `w:before` and writes
`w:pgMar w:top="0"` on every section, everywhere. The patch is the only copy of the clause
(`git cat-file -t aa496ebe` fails in a shallow clone; `REPORT.md:74`).

---

## 4. Why the gate was proposed at all, and why page count is the wrong axis

The newsletter loss is not a displacement — it is a **repagination**. Quoted from
`tools/p2w-bench/FINDINGS/18-DISPLACEMENT-PATCH-IS-NOT-IDENTITY-26NOV.md` (their measurement, not mine):

> The assumption fails in LibreOffice because **space-before at a page top is suppressed**. The old
> `w:before` was never being spent; the new `w:pgMar w:top` is net-new offset. On the newsletter, whose
> content already reached y = 785 pt of an 842 pt sheet, 60 pt of new margin overflows: the render goes to
> two pages, page 1 keeping only the top band … That is the 86.3.

The arithmetic that follows from those two quoted numbers: 842 − 785 = **57 pt of room below the last mark**;
the margin is 1200 tw = **60 pt**; 57 < 60, so the page overflows. The patch cannot see this because it leaves
`ctx.budgetTw` alone (`DocxWriter.java:1172`) while the reader's usable height drops by `pageTopTw`.

That is a **room** question, not a **size** question — which is why page count cannot separate the winner from
the loser: both are 1 page and both already render 2 pages against a 1-page source (`benchmarks/gverify/*.json`
`want=1, pages=2, status=page_count_refused` for `newsletter`, `itr`, `401`, `350`). The observable that
differs is how much vertical slack the page has, not how many pages the document has.

---

## 5. The best alternative discriminator I can derive — a ROOM gate, not a page-count gate

The engine already has exactly this construct, shipped and used: the table-gap spacer guard.

```
DocxWriter.java:1172   ctx.budgetTw = max(1, round(ph*TWIPS_PER_PT) - PAGE_ROUNDING_TW);
DocxWriter.java:1395   ctx.pageInkBottomPt = pageInkBottom(page);      // source's lowest ink, pt
DocxWriter.java:6152   int slackTw = ctx.budgetTw - round(ctx.pageInkBottomPt * TWIPS_PER_PT);
DocxWriter.java:6155   int roomTw = max(0, slackTw - ctx.spacerSplitTw - rowExcessTw);
```

`PAGE_ROUNDING_TW = 2` at `:377`. The comment at `:1393-1395` states the intent verbatim: *"HOW FULL THE PAGE
IS … the gap is only worth spending where the page has room for it."* A page-top margin is the same spend.

**Proposed guard, inside `sectionTopTw` (patch:150-192), replacing the `pages == 1` test:**

```java
// per page, not per document: one page that cannot absorb the margin means no margin anywhere
int roomTw = (int) Math.round((ph - pageInkBottomPtOf(page)) * TWIPS_PER_PT) - PAGE_ROUNDING_TW;
if (tw > roomTw) return 0;          // identity, byte for byte
```

`tw` is the value `sectionTopTw` already computes per page before taking the `min` (patch:187-189), so this is
a clamp on an existing quantity and needs no new model read — only `pageInkBottom(page)` exposed to
`sectionTopTw`, which `:1395` already computes per page.

**Predicted outcome (inference, not measurement).** `newsletter`: room 57 pt vs margin 60 pt → guard fires →
`pgMar 0` → 0.20 preserved, page count back to 1. `itr`: gated on iff its room ≥ its own margin. I cannot
compute `itr`'s ink bottom — the corpus PDFs are not on this pod — so **I do not claim itr keeps 9.10**. That
is the one number this proposal turns on and it is unmeasured.

**The stronger alternative, and I think the correct one: fix the accounting instead of gating it.**
`FINDINGS/18-DISPLACEMENT-PATCH-IS-NOT-IDENTITY-26NOV.md` §"What would make it land" already names it —
take the margin out of the budget next to `ctx.flowTw = 0;` (`DocxWriter.java:1172`):
`ctx.budgetTw = max(1, round(ph*TWIPS_PER_PT) - PAGE_ROUNDING_TW - max(0, ctx.pageTopTw));`
and reports it **measured**: *"Change 1 alone was measured: newsletter 86.30 → 0.20, back to one page with the
band restored. 601 stays 55.32 and 401 stays 0.79 with change 1 only."* If the model's budget and the reader's
text area shrink together, the clause stops being net-new offset and becomes a true identity-plus-Google-fix —
no document property is consulted at all. **`itr` was not measured under change 1.** That omission is the
single highest-value unmeasured experiment in this whole thread.

---

## 6. Two measurement-integrity findings that bear directly on the decision

### 6a. The committed `benchmarks/RANKING.csv` is a MIXED table — neither engine's

Joined against both evidence tables (212 rows): **209 rows match the patched table, 208 match the reverted
table, 0 match neither** — and the 7 rows that disagree are precisely the 7 movers:

| document | `RANKING.csv` | patched CSV | reverted CSV |
|:--|--:|--:|--:|
| `newsletter-3col-header-footer` | 86.30 | 86.30 | 0.20 |
| `itr-computation-with-slab-table` | 9.10 | 9.10 | 42.33 |
| `39_small_caps_letter_spacing` | 0.80 | 0.80 | 0.70 |
| `350_question_paper` | 0.12 | 0.12 | 0.11 |
| `600_reviewed_invoice_with_annotations` | 62.46 | 60.70 | 62.46 |
| `601_fillable_admission_form` | 52.39 | 55.32 | 52.39 |
| `401_trifold_brochure` | 0.03 | 0.79 | 0.03 |

This is the mechanism behind `REPORT.md:47` — `regress.py --check` refusing on a tree with nothing modified in
`app/`. Any re-land is judged by `regress.py`'s ratchet against a baseline that is not one engine's
measurement, so the gate's answer for these 7 rows is not currently trustworthy. **The baseline has to be
re-measured on one engine before any of this is decidable.**

### 6b. `600_reviewed_invoice_with_annotations` is not reproducible and should not be a deciding document

The task states `600: 54.30 → 62.46`. Four different values exist for this one document:

| value | where |
|--:|:--|
| 54.30 → 62.46 | `ATTEMPTS.json:523`, `HANDOFF.md:54`, `LAST-MESSAGE.md:101`, `REPORT.md:104`, `FINDINGS/26NOV-engine-7e0de1ab-corpus-remeasure.md:28` — all prose, one lineage |
| 60.70 (patched) vs 62.46 (reverted) | `evidence-26NOV/RANKING-26NOV-patched-engine.csv`, i.e. an **improvement**, not a regression |
| 62.46 | `evidence-26NOV/RANKING-26NOV-reverted-engine-212.csv` and `RANKING-MEASURED-RESTORED-ENGINE-27NOV.csv` |
| 63.08 | `benchmarks/RANKING-BASELINE.csv` |

And `ATTEMPTS.json:2305` records that this document is byte-unstable: *"two conversions of 600 differ in
sha256 (8cdb2dd8 patched vs ca292def HEAD)"*. The `54.30` figure is also the reason a **different** patch
(`txt-meta-annotation`) was refused (`ATTEMPTS.json:2284`) — the same number has been carried across two
unrelated attempts. **I cannot resolve which value is right without a re-render, and I am not going to pick
one.** What follows is that `600` cannot serve as a discriminator target: any gate tuned to hold 600 at 62.46
is tuned to noise.

---

## 7. What would decide it — the measurement I would run

Ordered by cost. Nothing here needs a full 212-document pass.

1. **No render: instrument `sectionTopTw` to print `(document, page, pageInkBottomPt, budgetTw, tw)` for the
   7 movers and the 20 multi-page controls.** One conversion pass of 27 documents, no scoring. This is the
   cheapest possible test of §5: if `roomTw` separates `newsletter` (fires) from `itr` (does not), the room
   gate is alive; if `itr` also fires, the room gate is refuted too and only the budget fix (§5) is left.
   It also settles, for the first time, *why* the 20 multi-page documents are inert to 0.0000 — whether their
   `sectionTopTw` returned 0 or their render was unaffected. **That is currently unexplained and it is the
   fact the whole proposal rests on.**
2. **Convert + score 10 documents, LibreOffice proxy** (`benchmarks/p2w.py`, per-document): `itr` (must be
   9.10), `newsletter` (must be 0.20, 1 page), `601` (must be 52.39), `401` (must be 0.03), `39_small_caps`
   (0.70), `350_question_paper` (0.11), `bank-statement-5-pages` (0.56), plus `324_loan_amortisation_schedule`
   (0.00, 7 pp), `412_page_labels_roman` (0.00, 5 pp) and `602_bookmarked_annual_report` (0.00, 3 pp) as
   controls. Any variant that moves a control off 0.00 is wrong by construction.
3. **Google `gverify` on `newsletter` and `itr` only** — the two documents the clause exists for. `share5` is a
   LibreOffice proxy; the project's target is Google, and `newsletter`'s failure mode (repagination) is exactly
   the class Google and LO could disagree about.
4. **Re-measure `benchmarks/RANKING.csv` on one engine** (§6a) before `regress.py`'s ratchet is used as the
   arbiter of any of this.

**What would overturn my refutation.** If a page count of 1 could be shown to co-vary with the loss and not the
win — e.g. if a re-render put `itr` at 2+ source pages, or `newsletter` at 2+ — the gate would be back in play.
The committed data says the opposite four ways: `RANKING.csv` `pages=1` for all seven movers
(`p2w.py:1762` writes `pages_src`), and `benchmarks/gverify/{newsletter,itr,401,350}.json` independently carry
`want=1`. I could not read the PDFs to triple-check with PyMuPDF, which is the one gap in this finding.

---

## 8. Verdict, in one paragraph

`pageTopTw = 0 when the document has exactly 1 page` is refuted by the corpus's own table: the clause's entire
measured effect — the 33.23-point `itr` win **and** the 86.10-point `newsletter` loss, plus `601`, `401`,
`39_small_caps` and `350` — lives inside the 192 one-page documents, while all 20 multi-page documents are
inert to the digit (max `|delta|` = 0.0000). The gate therefore switches the clause off on 100 % of what it
does and leaves it on where it does nothing: a no-op on the corpus, not a narrowing. The axis that actually
separates `newsletter` from `itr` is not document size but vertical **room** — the margin is net-new offset
because the patch leaves `budgetTw` untouched (`DocxWriter.java:1172`), and the newsletter has 57 pt of slack
against a 60 pt margin. The engine already ships the right construct for that question
(`pageInkBottomPt`/`slackTw`, `DocxWriter.java:1395`, `:6152-6155`), so a room gate is cheap; but the better
move is the accounting fix already named in `FINDINGS/18-DISPLACEMENT-PATCH-IS-NOT-IDENTITY-26NOV.md`
(measured: newsletter 86.30 → 0.20), whose one missing number is `itr` under that fix. Two further caveats
before anything is re-landed: the committed `RANKING.csv` is a mixed table (7 rows from two different engines,
§6a), and `600_reviewed_invoice_with_annotations` — one of the six "deciding documents" — reads four different
values in four committed records and is byte-unstable (§6b).

---

### Appendix: exact commands behind the numbers above

```
git clone --depth 200 https://github.com/kavopdf/app.git CS          # a1efec6, tree clean
grep -rn "pageTopTw\|sectionTopTw\|pageFirstBeforeTw" app/           # 0 hits -> aa496ebe fully reverted
grep -n "sectPrXml" app/src/main/java/com/kavopdf/app/engine/DocxWriter.java   # :1128 :1354 :2426 :2439
# page counts and movers:
pandas merge of evidence-26NOV/RANKING-26NOV-patched-engine.csv
             and evidence-26NOV/RANKING-26NOV-reverted-engine-212.csv on `document`
#   -> 212 rows, 7 movers, all pages==1; 20 multi-page rows, max |delta| = 0.0000
#   -> RANKING.csv vs both: 209 match patched, 208 match reverted, 0 match neither
```
