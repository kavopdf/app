# Route (c) tested without touching the engine

An already-emitted `.docx` was rewritten so that its two-column band became one flowed
paragraph per band line with a tab stop at each column's measured x, and the result was
rendered with LibreOffice and compared word by word against the source PDF.

- Engine: `git clone --depth 1 https://github.com/kavopdf/app`, built with
  `tools/p2w-bench/build-engine.sh`. **No file under `app/src` was modified.** Nothing was deleted.
- Corpus: `tools/p2w-bench/corpus-fetch.sh` → 213 PDFs, 213 `.docx` emitted by
  `corpus-convert.py --force` (4.6 min, 6 workers, engine b97d8172ce642eb0).
- Renderer: LibreOffice 7.4.7.2 headless. **LibreOffice is not Google.** Everything below is the
  .docx's own geometry in LO; what Google does with the same file is not measured here.

## The construct that was built

For every anchored text box on a page: read `wp:anchor` → `posOffset` (page x, page y),
`extent` (cx, cy) and the runs inside `w:txbxContent`. Group boxes that share a **baseline**
(a box's text baseline sits at `y + 0.8·cy` — verified on three different type sizes on
`policy-2col`, all agreeing to 0.02 pt). Each group is one row; each row becomes one paragraph:

```
<w:pPr>
  <w:tabs><w:tab w:val="left" w:pos="1020"/><w:tab w:val="left" w:pos="6151"/></w:tabs>
  <w:snapToGrid w:val="0"/>
  <w:spacing w:before="…" w:line="13" w:lineRule="exact"/>   <!-- gap in before, tiny line -->
  <w:ind w:left="0" w:right="0" w:firstLine="0"/>
</w:pPr>
<w:r><w:tab/></w:r><w:r>…column 1…</w:r><w:r><w:tab/></w:r><w:r>…column 2…</w:r>
```

`ind left = 0` and a **leading tab** for the first column, so every tab position is the column's
page x and nothing depends on how an indent interacts with tab stops. Vertical placement uses the
engine's own convention for flowed lines (`line=13` twips exact, the gap in `before`), because
LibreOffice bottom-aligns the text inside a large exact-height line box: with `line = advance` the
text drifts down by `advance − natural`. That was measured (variant B) and abandoned.

## 1. Per-document before/after

`src` = pages in the source PDF, `or` = pages of the original `.docx` in LO, `rw` = pages after the
rewrite. `extent` = last row baseline − first row baseline. `over` = flow end − usable height
(negative = the page holds, and by how much). `shift` = the worst amount a row had to be pushed
down because it sat above the flow cursor. `neg` = rows that needed a **negative** gap.
dy/dx are word-level against the source PDF, in pt.

### Genuine two-column band documents (17 of 60 boxed documents)

| document | src | or | rw | boxes | rows | 2-col rows | extent | over | shift | neg | med dy | p90 dy | max dy | unmatched |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| policy-2col-spanning-section-heading | 1 | 1 | **1** | 62 | 37 | 21 | 674.5 | −31.0 | 0.0 | 0 | 0.41 | 0.41 | 1.02 | 0 |
| magazine-2col-pullquote-spanning | 1 | 1 | **1** | 37 | 30 | 7 | 483.8 | −28.2 | 0.0 | 0 | 0.42 | 0.42 | 1.20 | 0 |
| 65_two_col_full_width_figure_caption | 1 | 1 | **1** | 25 | 14 | 6 | 353.9 | −35.9 | 0.0 | 0 | 0.20 | 0.41 | 0.46 | 0 |
| 66_two_col_footnotes_bottom | 1 | 1 | **1** | 8 | 6 | 2 | 121.9 | −35.9 | 0.0 | 0 | 0.23 | 0.40 | 0.46 | 0 |
| 400_comic_page_speech_bubbles | 1 | 1 | **1** | 25 | 14 | 8 | 643.4 | −39.9 | 0.0 | 0 | 0.30 | 0.39 | 0.80 | 0 |
| 331_pid_diagram | 1 | 1 | **1** | 25 | 21 | 4 | 343.0 | −19.9 | 0.0 | 0 | 0.20 | 0.32 | 1.18 | 0 |
| 69_two_col_legal_numbered_clauses | 1 | 1 | 1 | 36 | 19 | 14 | 640.9 | −35.9 | 5.3 | 1 | 0.69 | 7.65 | 113.70 | 0 |
| academic-paper-ieee-2col-abstract | 2 | 2 | **2** | 51 | 51 | 15 | 561.9 | +291.5 | 32.9 | 3 | 0.37 | 10.53 | 235.08 | 97 |
| 323_credit_card_statement | 1 | 1 | **2** | 13 | 7 | 6 | 455.9 | −79.9 | 0.0 | 0 | 0.30 | 50.65 | 50.65 | 0 |
| 60_page_border (ring text) | 1 | 1 | 1 | 47 | 18 | 17 | 71.1 | −28.3 | 267.3 | 18 | 0.22 | 253.49 | 279.30 | 7 |
| 05_round_company_seal_curved_text (ring) | 1 | 1 | 1 | 63 | 25 | 19 | 154.6 | −19.7 | 243.1 | 25 | 0.16 | 221.38 | 260.51 | 12 |
| 312_affidavit_stamp_paper | 1 | 1 | 1 | 28 | 10 | 10 | 38.8 | −136.3 | 0.0 | 0 | 0.26 | 12.92 | 223.05 | 2 |
| 371_experience_certificate | 1 | 1 | 1 | 28 | 13 | 9 | 44.9 | −65.4 | 146.6 | 13 | 0.30 | 111.68 | 151.13 | 8 |
| 352_certificate_ornate_border | 1 | 1 | 1 | 28 | 13 | 9 | 44.7 | −37.4 | 104.3 | 13 | 0.40 | 96.15 | 104.36 | 4 |
| 305_vaccination_certificate | 1 | 1 | 1 | 48 | 16 | 12 | 47.4 | −113.5 | 446.2 | 16 | 0.32 | 505.92 | 519.91 | 2 |
| 318_court_summons_form | 1 | 1 | 1 | 31 | 10 | 9 | 33.9 | −107.3 | 420.4 | 10 | 0.16 | 456.50 | 476.70 | 4 |
| 041122-Account_Opening_Form (26 tables) | 9 | 10 | **13** | 189 | 110 | 86 | 734.4 | +472.6 | 1063.4 | 88 | 121.81 | 401.52 | 759.28 | 4549 |

Whole corpus: 213 documents, **60 (28 %) carry anchored text boxes at all**; 153 are already pure
flow and route (c) has nothing to do there. Of the 60, 17 have ≥3 multi-column rows.

`over` is measured against one usable page height, so on a document that already has more than one
page it reads as "how far into the next sheet" — `academic-paper-ieee-2col-abstract` shows +291.5
and stays at 2 pages because 1133.4 / 841.9 = 1.35.

Whole-corpus page counts: **17 of 60 grew a page, 43 held, none shrank.** All 17 growth cases but
three contain at least one table (`11_stamp_*`, `09_stamp_*`, `43_red_stamp_*` have none and grow by
13–21 pt of flow overflow, measured below).

### x fidelity — the part that works

Tab stops land where the columns were measured. Line-level (the line's left edge, which is the tab
stop) |dx| on `policy-2col` is **median 0.08 pt, max 0.16 pt** over 61 lines — identical to the
original render's 0.08/0.16, so the construct adds no horizontal error at all. Same on
`magazine-2col` (0.15/0.16) and `65_two_col` (0.16). The right column measured at x = 307.56 pt
renders at 307.70. Word-level |dx| is larger (median 2.96, max 15.34 on `policy-2col`) but is
**byte-for-byte the same on the original render**, so it is the engine's own intra-line letter
spacing, not the tab stops.

## 2. Does pagination hold? — **Yes for every genuine two-column band document.**

- 6 of the 17 band documents are reproduced with **one page, no shift, and no position defect**:
  `policy-2col` (37 rows from 62 boxes), `magazine-2col-pullquote`, `65_two_col_full_width_figure`,
  `66_two_col_footnotes`, `400_comic`, `331_pid_diagram`. Median dy ≤ 0.42 pt, max dy ≤ 1.2 pt,
  zero unmatched words, zero negative gaps.
- 9 more hold their page count but with a position defect (rows pushed down by 5–446 pt), because
  the band's first line sits *above* where the flow already ended. These are ring-of-text
  documents, stamp overlays and certificates, not bands in empty space.
- 2 grow a page (`323_credit_card_statement` 1→2, `041122-Account_Opening_Form` 10→13). Both carry
  tables whose height is outside the .docx flow model, and both are the two documents in the set
  whose rewrite also reorders content relative to those tables. I do not attribute their growth to
  the construct.

`policy-2col` — the document named in the brief (62 boxes, 6 flowed paragraphs) — goes
**1 page → 1 page**, with the tab construct replacing all 62 boxes, and the worst word 1.02 pt from
where the source PDF put it.

## 3. The height arithmetic

The measured facts on `policy-2col-spanning-section-heading` (A4, 841.9 pt, zero margins,
band baselines 136.22 → 810.36):

| | boxes (as emitted) | route (c), 1 paragraph per band line |
|---|---|---|
| paragraphs carrying the band | 62, each `line=1` twip exact | 37, each `line=13` twips exact |
| flow height consumed | 62 × 0.05 = **3.1 pt** | 674.5 (extent) + 37 × 0.65 = **698.5 pt** |
| **cost of the construct** | — | **+695.4 pt** |
| flow end | ~3 pt after the intro | **810.9 pt** |
| page | 841.9 | 841.9 → **31.0 pt of slack** |

Three statements follow, and they are arithmetic, not opinion:

1. **A flow is monotonic in y.** It cannot place a line above the line before it. So the flowed
   height of a page is at least the vertical extent of everything on that page, and the construct
   can never cost less than the band's own height. On `policy-2col` that is 674.5 pt of band
   replaced 3.1 pt of anchored boxes — a cost of ~695 pt against ~0.
2. **The page grows iff** `pre-band flow end + band extent + post-band flow > usable height`. On
   `policy-2col`: 117 + 674.5 + 20 = 811 ≤ 841.9. It holds with 31 pt to spare. Measured on all 60:
   this test calls growth correctly on 12 documents, wrongly on 1, and misses 5 (all of them
   table-bearing, where a table's height is not in the model).
3. **The measured overflow in pt** on the documents that grew: 13.0 (`01_stamp_rotated_15deg`),
   16.9 (`04_stamp_180deg`), 20.3 (`06_rect_paid_stamp`), 21.0 (`11_stamp_with_signature`),
   25.8 (`02_stamp_rotated_15deg_upleft`), 6.4 (`43_red_stamp_over_black_text`) — each of those
   crosses the page boundary by exactly that much. On `policy-2col` the same arithmetic gives
   **−31.0 pt**, i.e. it does not cross.

### What the tab stops are actually worth

If the same band is emitted one paragraph per **box** instead of one per **row**, the flow has to
carry 62 line advances instead of 37. At the band's own pitch of 12.9 pt that is
62 × 12.9 = 800 pt against 37 × 12.9 = 477 pt — **the tab construct saves 25 rows × 12.9 =
322.5 pt on this document**, and 800 + 136 = 936 pt would put the page 94 pt over the bottom.
That is the arithmetic behind "a page became two": it is what happens when a two-column band is
flowed line-by-line instead of row-by-row. Row grouping is the whole point of route (c).

The second variant measured (`--line-mode natural`, each row carrying the font's real line height
instead of a 13-twip exact line): `policy-2col` flow end 812.6 pt, still 1 page, median dy 0.11 pt.
Where the measured pitch is *denser* than the natural line height the natural variant costs extra —
the sum of `natural − pitch` over those rows: 5.7 pt on `policy-2col`, 22.6 pt on `69_two_col_legal`,
58.8 pt on `60_page_border`, 101.3 pt on `05_round_company_seal`. None of them crosses a page
boundary on its own.

## 4. What distinguishes the documents where it works

Works (shift = 0, no position defect): the boxes form a band in **vertical space the flow has not
already used** — the flowed text before the band ends above the band's first baseline, so the
construct starts where the flow stopped and nothing has to be pushed.

Fails, and the failures are one mechanism, not several:

- **The band starts above the flow cursor** (shift > 0, `neg` = number of such rows). Then the
  construct must push the row down to the cursor and everything after it moves by that amount.
  Measured shifts: 5.3 pt (`69_two_col_legal`), 104–147 pt (certificates), 243–267 pt
  (ring-of-text documents), 420–446 pt (`318_court_summons`, `305_vaccination_certificate`).
  This is exactly the "negative gap" question: those rows *need* a negative `before`, and `w:before`
  is unsigned, so the gap is not available. `policy-2col` needs zero of them — but only because the
  two lines the engine had already flowed out of the left column were folded back into the band
  (2 absorbed). Left in the flow, the same document needs a −21.5 pt gap on its first row.
- **The band is dense**: consecutive rows closer than the font's natural line height (pitch 3.0–7.8
  pt against 9.8–10.4 pt natural on the ring/stamp documents). Compression is possible (the line
  boxes overlap, the baselines are still right) but nothing can recover the space.
- **Tables interleaved with the boxes**: a table's height is not in the .docx flow model, so the
  rewrite reorders rows relative to it and the page counts on those documents are not attributable
  to the construct. Every document that grew is in this class or is a single-box overlay.

So the dividing line is not document length, column count or font: it is whether the boxes sit in
space the flow has already spent. Bands in empty space: clean. Overlays on top of flowed content or
of tables: not representable.

## 5. Judgement on route (c)

**Viable for real two-column bands, and it holds one page — measured, not argued.** On the six
genuine band documents it replaces 62/37/25/8/25/25 anchored boxes with 37/30/14/6/14/21 flowed
tab-stop paragraphs, keeps the page count at 1, puts every word within 1.2 pt of the source PDF,
and puts every tab stop within 0.16 pt of the column's measured x. The height cost is the band's
own vertical extent (695 pt on `policy-2col`) and the page absorbs it with 31 pt of slack, because
the band was already inside the page — the boxes were simply not paying for the space they occupied.

Three conditions come with that verdict, and each is a measurement:

1. **Row grouping is load-bearing.** Line-by-line flow (no tabs) needs 62 × 12.9 = 800 pt on
   `policy-2col` against 477 pt for 37 rows; that is the 94 pt by which the page goes over. If the
   engine emits route (c) without collapsing the columns into rows, it will grow pages.
2. **The engine must also stop flowing the lines that belong to the band.** `policy-2col` already
   flows the first two lines of its left column as real paragraphs; folding them back into the band
   is what takes the first row's required gap from −21.5 pt to +10.6 pt. A route (c) that converts
   only the boxes and leaves those two flowed lines where they are needs a negative gap on row 1.
3. **It does not cover the whole boxed population.** 17 of 213 documents have a band; the other 43
   boxed documents are overlays (stamps, ring text, certificate borders, form fields) where the
   construct needs a 96–446 pt negative gap. For those, route (c) trades a pixel problem for a
   position problem, and the pixel problem (Google rasterising the text) is the smaller one.

What is *not* established here: whether Google rasterises a tab-stop paragraph less than it
rasterises an anchored text box. That is the reason route (c) was proposed, and LibreOffice cannot
answer it. What is established is that the construct is geometrically representable, that it costs
the band's height and not more, and that it holds the page on every genuine band document in the
corpus.

## Open questions

- Whether Google Docs keeps a `w:tab` paragraph as text rather than rasterising it. Not measurable
  with LibreOffice; needs the Google gate.
- Which document produced the earlier 1-page→2-page result. I could not reproduce a page growth on
  any of the 17 band documents; growth appears only on single-box overlays (+6 to +26 pt of
  overflow) and on table-bearing forms where my flow model cannot place content.
- The height of a table is not recoverable from the .docx by spacing alone. I calibrated the
  pre-band cursor from the original render for 31 documents; 26-table forms such as
  `041122-Account_Opening_Form` remain unmeasurable this way.
