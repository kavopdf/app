# 350_question_paper — why 1 page renders as 2

**Status in the record:** `status=page_count_refused, pages=2, want=1`. Source PDF: 1 page. Not available: the PDF and the .docx — everything below is read off `DocxWriter.java` and is stated as a code fact plus one labelled inference.

**Shape of the document (from the brief):** one drawing-only paragraph and nothing else. That single fact narrows the field hard, because it rules out every *paragraph-count* mechanism and every *table* mechanism.

---

## The construct I charge

`picture()`, **lines 2542–2564** — the branch that is taken when `p.placed` is false:

```java
2545:        if (p.placed) {
2546:            anchoredPicture(sb, p, id, ctx);
2547:            return;
2548:        }
2549:        sb.append("<w:p><w:r><w:drawing><wp:inline distT=\"0\" distB=\"0\" distL=\"0\" distR=\"0\">")
...
2563:                .append("</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>");
```

Two properties of line 2549 are the whole finding:

1. **`<wp:inline>` — the image is a box in the text flow**, not on the paper. Its `wp:extent cy` (line 2550–2551, `p.heightEmu`) is height the *flow* must pay, and the page is one paragraph tall as far as layout is concerned.
2. **That paragraph carries no `<w:pPr>` at all.** Line 2549 is the only `<w:p>` in the file emitted without a `w:pPr` — I checked every emitter (667, 1075, 1095, 1410, 2210, 2580, 2894, 3714, 3746, 4589, 5340, 5583, 6058, 6066, 6848, 6968, 7138). So it inherits `stylesXml()`'s docDefaults:

```java
7555:  "<w:sz w:val=\"22\"/><w:szCs w:val=\"22\"/></w:rPr></w:rPrDefault>"
7556:  "<w:pPrDefault><w:pPr><w:spacing w:after=\"120\"/></w:pPr></w:pPrDefault>"
```

i.e. an **11 pt paragraph mark and 6 pt of after-spacing**, neither of which is declared on the paragraph.

## Why the engine's own guard cannot see it

`spacingTw()` (449–495) is the only measure of page height the budget guard has, and it sums exactly three token kinds — `w:before` (481), `w:line` (481), `w:trHeight` (488):

```java
481:            } else if (startsWith(xml, BEFORE, i) || startsWith(xml, LINE, i)) {
```

The inline-picture paragraph emits **none of them**, and no reader-side line box is visible to it either. So on this page `writtenTw ≈ 0`, `needTw ≈ 0`, and every guard downstream is blind:

- `ctx.budgetTw` (1121) is the paper height and never gets near being exceeded;
- the measuring pass / re-write at 1186–1200 (`if (writtenTw > pageBudgetTw)`) never fires;
- `fitReserveTw` + `shaveToFit` at 1278–1290 have nothing to shave.

The guard is doing its job; the page it is measuring is not the page Google renders. That is the same class of blindness the code comments already flag at 1168–1171 ("the carriers that hold an anchored picture … are not charged to the flow"), but here it is the *drawing itself* that is uncharged, not a carrier.

## Why Google bills it and LibreOffice does not

**Code fact:** the paragraph in the flow = image height + (whatever line box the reader gives the paragraph mark) + 6 pt of `w:after`.

**Inference (labelled as such — I cannot run Google's layout):** LibreOffice lays a picture-only paragraph's line at the image's own height and does not add a separate line for the empty mark, so the page costs `cy + 6 pt` and fits. Google Docs keeps a line box for the paragraph mark at the inherited `sz=22` (~12.7 pt) on top of the image line, so the same page costs `cy + 12.7 + 6 ≈ cy + 18.7 pt`. A scan whose `cy` reaches within ~19 pt of the paper's height therefore fits LibreOffice's sheet and overruns Google's by a hairline — the second sheet holds nothing but that mark.

This is the *same* reader behaviour the file already documents for the shape carriers ("Google Docs bills every such paragraph the line box of its `sz=2` run (~0.83 pt) even though `w:line="1" exact` asks for nothing", pageBody 1356–1362 / shapeRun 2901–2912) — only here the mark's line is 11 pt, not 1 pt, and the image's own height is behind it.

## Ranked candidates, and what I would test first

| # | Construct | Lines | Verdict |
|---|---|---|---|
| **1** | `<wp:inline>` picture in a pPr-less paragraph | 2542–2564 | **Test first.** The only construct in the file that puts a page-tall box in the flow with metrics no guard can see. Explains "one drawing-only paragraph" exactly. |
| 2 | `flowParagraph()` writes `<w:p><w:pPr>` with `pStyle`/`snapToGrid`/`jc`/`ind` and **no `w:spacing`** | 4585–4604 (call site 3318) | Real hole of the same kind (inherits `after=120`, `sz=22`, invisible to `spacingTw`), but its text path is reached only for a `Para` with no boxes — it cannot be the *only* content of a drawing-only page. Keep as candidate if the docx turns out to hold text. |
| 3 | Shape carrier paragraph with `SHAPE_PARA_PPR` (`w:line="1" exact`, `sz=2`) | 2887–2891, 1409–1411, 2580–2582 | Excluded by the brief and arithmetically too small: 0.83 pt on a page with no other flow cannot make a sheet. |
| 4 | Page break / section break at the end | 1073–1081, 1093–1098, body `sectPr` 1303 | Excluded: the `!first` branches are only reachable from page 2 onwards, and 1303 is a property, not a break. |
| 5 | Empty table row / table overflow | `table()` 5906+, `POST_TABLE_TW` 7179 | Excluded: a table would make the document more than one paragraph. |

### Measurements that discriminate

Run these on the existing generated `350_question_paper.docx` (no rebuild needed):

```bash
unzip -p 350_question_paper.docx word/document.xml > d.xml
grep -o '<wp:inline' d.xml | wc -l      # candidate 1 confirmed if 1
grep -o '<wp:anchor' d.xml | wc -l      # candidate 1 refuted if 1
grep -o '<w:p>' d.xml | wc -l           # expect 1
grep -c '<w:p><w:r><w:drawing>' d.xml   # expect 1 for the pPr-less inline carrier
grep -o 'wp:extent cx="[0-9]*" cy="[0-9]*"' d.xml   # cy vs pgSz h (twips*635 EMU/pt)
```

Then, to size the overrun rather than guess it: `cy` (EMU) ÷ 12700 = image height in pt; compare with the `w:pgSz w:h` from `sectPrXml()` (2382–2400). If `h − cy` is roughly 6–19 pt, the extra line box + `after=120` is exactly the shortfall.

Note that `-Dp2w.debugFlow=1` (1298–1305) will **not** discriminate: in both candidate 1 and candidate 3 the printed `flowTw` is ~0–1 twip, because neither an inline extent nor an inherited default is a `w:before`/`w:line` token. The XML grep is the discriminator.

---

## The general rule

> **No drawing is ever placed in the text flow.** Every picture the PDF drew is written as a page-positioned anchor (`wp:anchor`, `relativeFrom="page"`, `wp:wrapNone`) inside the same zero-metric carrier paragraph a floating shape already uses, so the flow carries text only — and everything the flow does carry is a `w:before`/`w:line`/`w:trHeight` token that `spacingTw()` can measure.

The engine already believes this rule everywhere else: `Picture.placed` (2507–2515) says "an image the PDF drew is not part of the text flow — it is pinned to a place on the paper"; `anchoredPicture()` (2567–2573) says "a scan is the page's background"; `pageBody()` (1355–1370) removes the same overhead for shapes. `picture()`'s `else` branch is the one place that still contradicts it — and, being the only paragraph with no `w:pPr`, it is also the one place where the writer's flow model and the reader's disagree by more than a twip.

Nothing in the rule names a document: it removes an entire class (any page whose content is a full-bleed drawing), and it costs a normal text page nothing, because a picture that is already `placed` takes the `anchoredPicture()` path today.

**Patch:** `probe-350.java.patch` — deletes the inline emission, routes unplaced pictures through `anchoredPicture()` pinned at the flow's current y (`ctx.flowY`, 0 at the top of a sheet), and restores the picture's alt text (`descr=`) on the anchored path so the gate's word comparison still sees the scan's words.

**Verification caveat:** the patch was checked for brace/paren balance and applies cleanly with `git apply`, but it was **not compiled** — the rest of the tree (`PdfToWord`, `ReadingOrder`) is not in this sandbox and there is no `javac` here. Before merge, run the corpus and watch three checks: `01_page_count`, `59_shape_anchor` (the anchor now carries `behindDoc="1"`, so a picture under live text must still be visible), and `17_matched_runs` / word comparison (the `descr` hunk).
