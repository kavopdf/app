# What Google Docs hides or drops in our .docx — the construct, the counts, the emitter

Measured 2026-11-23 on a fresh clone of `kavopdf/app`, engine built in the sandbox
(`tools/p2w-bench/build-engine.sh`), corpus fetched (`tools/p2w-bench/corpus-fetch.sh`, 213 PDFs,
0 missing), 127 documents re-converted with `ConvertAll` and their `word/document.xml` read
directly. Google verdicts are the **recorded** ones in `benchmarks/gverify/*.json`; nothing here
drives Google.

---

## 1. The answer

**The construct is an anchored DrawingML shape — `<w:drawing><wp:anchor> … <a:graphicData
uri="…wordprocessingShape"><wps:wsp>` — emitted by `DocxWriter.anchorShape()`
(`app/src/main/java/com/kavopdf/app/engine/DocxWriter.java:5580-5685`). Google Docs rasterises
every one of these on import, and that single behaviour produces both classes, as its two faces:**

| face | what is inside the shape | check | failing docs that carry it | Google-clean docs that carry it |
|---|---|---|---:|---:|
| **DROP** | the **text itself**, in `<wps:txbx><w:txbxContent>` | `04_chars_missing` | **54 of 65** (and 54 of 54 documents that carry shape text) | **0 of 30** |
| **HIDE** | the **background** the white text sits on (a dark `wps:wsp` fill); the text is flow text | `25_invisible_text` | **48 of 48** (exactly the 48 that carry near-white text) | **0 of 30** |

Both counts are perfect separators: every document carrying either construct fails the
corresponding Google check, and **not one of the 30 Google-clean documents carries either.**

The repo already holds the measurement that this rests on, in its own words:

> "Google does not drop the shape. It **rasterises** it: 108 vector drawings in the source become
> 108 [images]" — `tools/p2w-bench/FINDINGS/00_page_count-EMPTY-PARAGRAPH-COSTS-THE-PAGE-0530-fixer.md:32`

> "`25_invisible_text` is the white masthead: `METROPOLIS PATHOLOGY LAB` (13 pt, `#FFFFFF`) and the
> accreditation line (7.5 pt, `#FFFFFF`) are white type over a dark band **that Google rasterises**,
> so the span has no ink behind it." — `…/00_page_count-SHAPE-RUNS-NOT-PARAGRAPHS-LANDED-0730-fixer.md:67`

---

## 2. How the two faces work, mechanically

### 2a. DROP — text inside `<w:txbxContent>` (04_chars_missing)

The text is real WordprocessingML, inside a text box that is a shape. A rasterising importer bakes
it into pixels: the characters are in the picture, not in the text layer, so the Google export has
no text to extract. LibreOffice renders the same box as a text frame and keeps the text.

Quantified on the 54 documents that carry shape text: **14,449 of 84,364 characters (17.1 %) live
inside `w:txbxContent`**. It is not a rounding error — on some documents it is nearly the whole
document:

| document | chars in `w:txbxContent` | share of the .docx's text |
|---|---:|---:|
| `policy-2col-spanning-section-heading` | 3,041 | 91.5 % |
| `magazine-2col-pullquote-spanning` | 2,182 | 91.4 % |
| `400_comic_page_speech_bubbles` | 275 | 89.3 % |
| `331_pid_diagram` | 248 | 81.8 % |
| `69_two_col_legal_numbered_clauses` | 1,358 | 67.2 % |
| `academic-paper-ieee-2col-abstract` | 2,942 | 46.3 % |
| `66_two_col_footnotes_bottom` | 448 | 24.9 % |

`66_two_col_footnotes_bottom` is the clean worked example: its footnote text ("1  IS 1479 (Part 1):
2016, Methods of test for dairy products, Bureau of Indian Standards." …) exists **only** inside
`w:txbxContent` — I checked every string against the source PDF (all present in the PDF) and against
the rest of the document.xml (no second copy in the flow). Google fails `04_chars_missing` on it;
LibreOffice renders it and passes.

### 2b. HIDE — the rasterised band behind white flow text (25_invisible_text)

Here the text is *not* in the shape. The writer faithfully emits the source's `#FFFFFF` runs as flow
text, and the band behind them as an anchored `wps:wsp`. Two things follow in a rasterising importer:
the band stops being a dark **vector fill**, and the white runs end up contained by a fill that *is*
white — the page-sized white fill Google's export carries ("a render legitimately stacks a white
page-sized fill under every band it draws", `tools/p2w-bench/verify_google.py:5358`). Check 25 counts
a run whose colour matches the fill under it, so the run is counted invisible.

The mechanism is confirmed from both ends:

* **The writer is faithful, not inventing white.** For 47 of the 48 documents the count of
  near-white characters in the `.docx` equals the count in the source PDF exactly
  (`300_prescription_rx` 116/116, `324_loan_amortisation_schedule` 557/557, `bank-statement-5-pages`
  145/145 …). The one exception is `text-held-twice-shadow-text`, which holds its text twice by
  design (1,328 vs 807).
* **LibreOffice's render passes the same check on the same file, for a reason I could measure.**
  Rendering `300_prescription_rx.docx` with soffice and running the verifier's own helpers: each
  white run is contained by **exactly one** fill, and that fill is the band —
  `(0.071, 0.208, 0.357)` = `#12355B` — which is not colour-close to white, so `invisible = 0`.
  Google fails the check, which by the check's own code means the white run is contained by a fill
  that *is* white within 0.08: the band is not a dark vector fill there.

White text is a **perfect predictor** of the class: the set of documents with any near-white
character in the source PDF is *identical* to the set of 48 documents that fail `25_invisible_text`
in Google, and no clean document has one.

---

## 3. The exact XML

### 3a. DROP — `66_two_col_footnotes_bottom.docx`, `word/document.xml` (verbatim, namespaces stripped)

```xml
<w:p>
  <w:pPr>
    <w:snapToGrid w:val="0"/>
    <w:spacing w:beforeAutospacing="0" w:afterAutospacing="0" w:before="0" w:after="0"
               w:line="1" w:lineRule="exact"/>
    <w:rPr><w:sz w:val="2"/><w:szCs w:val="2"/></w:rPr>
  </w:pPr>
  <w:r>
    <w:drawing>
      <wp:anchor distT="0" distB="0" distL="0" distR="0" simplePos="0" relativeHeight="251658241"
                 behindDoc="1" locked="0" layoutInCell="1" allowOverlap="1">
        <wp:simplePos x="0" y="0"/>
        <wp:positionH relativeFrom="page"><wp:posOffset>711200</wp:posOffset></wp:positionH>
        <wp:positionV relativeFrom="page"><wp:posOffset>8602675</wp:posOffset></wp:positionV>
        <wp:extent cx="3801595" cy="105156"/>
        <wp:effectExtent l="0" t="0" r="0" b="0"/>
        <wp:wrapNone/>
        <wp:docPr id="1" name="KavoPDF text 1"/>
        <wp:cNvGraphicFramePr/>
        <a:graphic>
          <a:graphicData uri="http://schemas.microsoft.com/office/word/2010/wordprocessingShape">
            <wps:wsp>
              <wps:cNvSpPr txBox="1"/>
              <wps:spPr>
                <a:xfrm><a:off x="0" y="0"/><a:ext cx="3801595" cy="105156"/></a:xfrm>
                <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
                <a:noFill/>
                <a:ln><a:noFill/></a:ln>
              </wps:spPr>
              <wps:txbx>
                <w:txbxContent>
                  <w:p>
                    <w:pPr>
                      <w:snapToGrid w:val="0"/>
                      <w:spacing w:beforeAutospacing="0" w:afterAutospacing="0" w:before="0"
                                 w:after="0" w:line="166" w:lineRule="exact"/>
                      <w:ind w:left="0" w:right="0" w:firstLine="0"/>
                      <w:rPr><w:sz w:val="14"/></w:rPr>
                    </w:pPr>
                    <w:r>
                      <w:rPr>
                        <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"
                                  w:cs="Times New Roman"/>
                        <w:color w:val="595959"/>
                        <w:sz w:val="14"/><w:szCs w:val="14"/>
                      </w:rPr>
                      <w:t xml:space="preserve">1  IS 1479 (Part 1): 2016, Methods of test for dairy
products, Bureau of Indian Standards.</w:t>
                    </w:r>
                  </w:p>
                </w:txbxContent>
              </wps:txbx>
              <wps:bodyPr wrap="none" lIns="0" tIns="0" rIns="0" bIns="0" anchor="t"
                          anchorCtr="0"><a:noAutofit/></wps:bodyPr>
            </wps:wsp>
          </a:graphicData>
        </a:graphic>
      </wp:anchor>
    </w:drawing>
  </w:r>
</w:p>
```

The construct that decides it is `<wps:txbx><w:txbxContent>` — text that only exists inside a
shape. (`wps:cNvSpPr txBox="1"`, `wp:wrapNone`, `behindDoc="1"` and `wps:bodyPr wrap="none"` are all
secondary; none of them appears in a clean document with text in the flow.)

### 3b. HIDE — `300_prescription_rx.docx`, the white masthead and the band it sits on

The text (flow paragraph, no shape, colour `FFFFFF`):

```xml
<w:p>
  <w:pPr>
    <w:pStyle w:val="Heading1"/>
    <w:snapToGrid w:val="0"/>
    <w:spacing w:beforeAutospacing="0" w:afterAutospacing="0" w:before="550" w:after="0"
               w:line="13" w:lineRule="exact"/>
    <w:ind w:left="560" w:right="0" w:firstLine="0"/>
  </w:pPr>
  <w:r>
    <w:rPr>
      <w:rFonts w:ascii="DejaVuSans" w:hAnsi="DejaVuSans" w:cs="DejaVuSans"/>
      <w:b/>
      <w:color w:val="FFFFFF"/>
      <w:sz w:val="26"/><w:szCs w:val="26"/>
    </w:rPr>
    <w:t xml:space="preserve">SHRIRAM MULTISPECIALITY HOSPITAL</w:t>
  </w:r>
</w:p>
```

The band (a separate anchored shape; 7,560,000 × 584,200 EMU = 595.3 × 46 pt, fill `#12355B` — the
page's own band colour):

```xml
<w:r>
  <w:drawing>
    <wp:anchor … behindDoc="1" …>
      <wp:positionH relativeFrom="page"><wp:posOffset>0</wp:posOffset></wp:positionH>
      <wp:positionV relativeFrom="page"><wp:posOffset>0</wp:posOffset></wp:positionV>
      <wp:extent cx="7560000" cy="584200"/>
      <wp:wrapNone/>
      <a:graphic><a:graphicData uri="…/wordprocessingShape">
        <wps:wsp>
          <wps:spPr>
            <a:xfrm><a:off x="0" y="0"/><a:ext cx="7560000" cy="584200"/></a:xfrm>
            <a:custGeom>…</a:custGeom>
            <a:solidFill><a:srgbClr val="12355B"></a:srgbClr></a:solidFill>
```

The source PDF has the same thing: `SHRIRAM MULTISPECIALITY HOSPITAL`, `color=FFFFFF`, over a fill
`(0.0706, 0.2078, 0.3569)` at `y 0…46`. The conversion is faithful; the renderer's handling of the
shape is not.

---

## 4. The census: every candidate family, counted

127 documents re-converted at HEAD (the union of the two failing sets plus the 30 Google-clean
documents; all 127 had a source PDF). Presence counted per document in `word/document.xml`.
`inv` = the 48 documents failing `25_invisible_text` in Google, `miss` = the 65 failing
`04_chars_missing`, `clean` = the 30 that pass all 42 checks in Google.

| candidate construct | 25_invisible (48) | 04_chars_missing (65) | Google-clean (30) | verdict |
|---|---:|---:|---:|---|
| **`w:txbxContent` / `wps:txbx` (text in a shape)** | 14/48 | **54/65** | **0/30** | **CONFIRMED — the DROP construct** |
| **`w:color` near-white (`FFFFFF`)** | **48/48** | 16/65 | **0/30** | **CONFIRMED — the HIDE construct** |
| `w:vanish` | 0/48 | 0/65 | 0/30 | absent — not it |
| `w:specVanish` | 0/48 | 0/65 | 0/30 | absent — not it |
| `w:webHidden` | 0/48 | 0/65 | 0/30 | absent — not it |
| `w:position` (raised/lowered, non-zero) | 0/48 | 0/65 | 0/30 | absent — not it |
| `w:framePr` | 0/48 | 0/65 | 0/30 | absent (the writer removed it — see `para()` docblock) |
| `w:fitText` | 0/48 | 0/65 | 0/30 | absent — not it |
| `w:shd` foreground/fill white | 0/48 | 0/65 | 0/30 | absent — no `w:shd` at all in the corpus |
| `w:highlight` (`none` or any) | 0/48 | 0/65 | 0/30 | absent — not it |
| character `w:spacing` on `rPr` | 3/48 | 7/65 | 1/30 | present in clean too — not it |
| table row `w:hidden` | 0/48 | 0/65 | 0/30 | absent — not it |
| run inside `w:ins` / `w:del` | 0/48 | 0/65 | 0/30 | absent — not it |
| `w:tblpPr` (floating table) | 0/48 | 0/65 | 0/30 | absent — not it |
| `w:vertAlign` | 0/48 | 0/65 | 0/30 | absent — not it |
| `mc:AlternateContent` / `w:pict` (VML) | 0/48 | 0/65 | 0/30 | absent — not it |
| `w:altChunk`, `w:tblOverlap`, `w:noWrap`, `w:mirrorMargins`, `w:textDirection` | 0 | 0 | 0 | absent — not it |
| `w:sz` of 0 or 2 | 46/48 | 64/65 | **11/30** | **refuted — see below** |
| any `w:color` at all | 48/48 | 61/65 | 25/30 | present in clean too — not it |
| `w:drawing` present | 48/48 | 63/65 | 26/30 | present in clean too — not it |
| `wps:wsp` (any shape) | 48/48 | 63/65 | 25/30 | present in clean too — not it |

**`w:sz` of 0/2 is a confound, and worth recording so nobody re-finds it.** It looks like a
near-perfect discriminator (46/48, 64/65) but 11 clean documents have it too, and the element is not
text: it is the **paragraph mark's** run properties — `<w:pPr><w:rPr><w:sz w:val="2"/></w:rPr>` — the
1 pt paragraph mark that `anchorShape()` writes on a zero-height carrier paragraph
(`DocxWriter.java:5627`, and the same trick at 2602 and 2911). No character carries `w:sz` ≤ 2 in any of these documents; I checked every
`w:t`-bearing run. It correlates only because the documents that carry shapes carry carrier
paragraphs.

---

## 5. Where it is emitted

`app/src/main/java/com/kavopdf/app/engine/DocxWriter.java`

| line | what |
|---|---|
| **5580–5685** | `anchorShape(...)` — the one place that writes `<w:drawing><wp:anchor>…<wps:wsp>`. Line **5664** is the construct itself: `"<wps:txbx><w:txbxContent>" + inner + "</w:txbxContent></wps:txbx>"`. Every `w:txbxContent` in the corpus comes from here. |
| 5394 | `stampBox()` → `anchorShape` — a whole stamp (frame + every line of its text) as one rotated box. |
| 5516–5562 | `anchorAt()` → `anchorShape` — the generic anchored box. |
| 3325 / 3345 / 3351 | `anchorBox()` → `anchorAt` — the per-line path: ring characters, quarter-turn lines, and every other rotated line. |
| 4793 | `anchor()` → `anchorAt` — the same box used to hold a block (the "a table stays a table, inside a text box" path). |
| 3101–3330 | `para()` — the **flow** alternative: `flowFromBox()` (4381) / `flowRow()` (3535) / `flowParagraph()` (4627) write ordinary `w:p` paragraphs when the line is horizontal; `anchorBox()` (2793) is the branch that does not. |

The branches in `para()` that still route text into a box are exactly the documents in the 04
population:

* `if (p.pinned && !anyRotated && !ctx.positioned) { pinnedBoxes(...); return; }` — a short line
  the page drew inside a table's vertical band (`pinShortParas`);
* `if (ctx.positioned && !anyRotated) { … anchorBox(…); }` — a page whose flow has run out of room;
* `if (ctx.positioned || containerOf(ctx.curShapes, b) != null) { anchorBox(…); }` — a label the page
  drew inside a closed outline (a sidebar, a boxed footnote, a comic speech bubble);
* the `anyRotated` branch — genuinely rotated lines (stamps, watermarks, ring text), where a shape is
  the only construct OOXML has.

Note the irony recorded in the code itself: `w:framePr` was abandoned *because* "Google Docs ignores
`w:framePr` positioning outright", and the replacement construct — the `wps:wsp` text box — is the one
Google rasterises. For a stamp that is still the right trade (it renders in place in Google, and a
stamp's characters are few); for body text, footnotes, sidebar text and column text it is not.

---

## 6. What the writer should emit instead

1. **Never put text that belongs to the document's content inside `wps:txbx`.**
   * `pinnedBoxes()` / `pinShortParas()`: emit the pinned line as a flow paragraph and carry the
     table's own top with the table (`tblpPr`/row height), instead of anchoring the line.
   * `containerOf(...)` labels (sidebar, boxed footnote, speech bubble): emit the container as a
     **1×1 table** with `w:tblBorders` for the outline and the text as cell content — the construct
     the writer already uses for tables, and flow content in every renderer.
   * `ctx.positioned` (flow ran out of room): this is a layout failure, not a construct decision —
     it should fall back to flow and let the page break, not to a shape.
   * Keep `wps:txbx` **only** for rotated lines, where a shape is the only construct that can carry
     an angle (`a:xfrm rot`).
2. **Do not let an anchored shape be the background of flow text.** For a band that carries text
   (the white-masthead case), paint the fill as a flow object: a 1×1 table with `w:shd` fill =
   the band colour and the white runs as cell text, or `w:shd` on the paragraph. A shape whose only
   job is a fill behind text is the construct that disappears under a rasterising importer.
3. Both changes are one rule with one test: **text and the fill behind it must be in the flow; only
   geometry that genuinely floats (a rotated line) may be a shape.**

---

## 7. Cross-check performed (LibreOffice only — Google was not driven)

| document | construct | soffice render | 42-check run on the LO render |
|---|---|---|---|
| `300_prescription_rx` | 116 white chars over a `#12355B` band | text present (`SHRIRAM MULTISPECIALITY HOSPITAL`, 116 near-white chars in the render) | **47/47 PASS** — `25_invisible_text` source 0 / render 0 |
| `66_two_col_footnotes_bottom` | 448 chars inside `w:txbxContent` | text present ("Bureau of Indian Standards", "milking register") | **42/42 PASS** — `04_chars_missing` source 0 / render 0 |
| `322_mutual_fund_factsheet` | both | text present, 126 near-white chars in the render | (not run) |

So the text is in the `.docx`, LibreOffice shows it, and the recorded Google JSON says Google does
not. That is the whole premise, and it reproduces.

---

## 8. What is not proven, and the residuals

* **The mechanism inside Google is inferred, not observed.** I cannot drive Google
  (`gverify.py`/`grender.py` need credentials, and `benchmarks/gverify/*.json` carries only
  pass/fail — no `checks`, no render file). Two sub-mechanisms fit the counts equally:
  (i) the shape is **rasterised**, so its text is pixels and its fill is an image; (ii) the text is
  **clipped** by the box (`wp:extent` + `wps:bodyPr wrap="none"` with `a:noAutofit`), so it falls
  outside the box and is not drawn. Both are the same construct and the same fix. A single Google
  render of `66_two_col_footnotes_bottom` with its text layer dumped would separate them.
* **The verdicts are stale relative to HEAD.** `benchmarks/DEFECT-CLASSES-GOOGLE.md` says HEAD is
  `5beb8b9d` and only 2 of the 190 Google results were measured on it; the rest came from
  `98be7c3c`/`462353f`. The `.docx` I censused were converted at HEAD. The separation is so clean
  (48/48, 54/54, 0/30 on both axes) that a wholesale change of behaviour is unlikely, but the
  census and the verdicts are not the same build — re-measure before landing.
* **11 of the 65 `04_chars_missing` documents carry no shape text** and are a different mechanism:
  `25_signature_block_underscores_txtpos`, `381_incident_report_timeline`, `383_api_docs_page`,
  `38_faux_bold_italic_synthesised`, `417_rotate180_and_mirrored`, `58_header_rule_footer_rule`,
  `601_fillable_admission_form`, `602_bookmarked_annual_report`, `form16-part-b`,
  `table-across-page-break-repeated-header`, `very-long-single-column-table`. None of the candidate
  families in §4 fires on them either, so whatever they are, it is not in that list.
* **`25_invisible_text` may have no writer-side fix that keeps both the text and its colour.** If
  Google's export really does paint a page-sized white fill on every page (the comment at
  `verify_google.py:5358` says it does), then *any* near-white text is counted invisible in Google,
  whatever construct carries it. Recommendation 2 above (band as flow shading) is the best
  construct-level answer and it needs one Google measurement to confirm; the alternative — baking
  band and text into one picture — trades `25_invisible_text` for `04_chars_missing`, which is
  worse. That trade-off is worth stating to whoever owns the class.
* 16 documents fail both classes and carry both constructs, as expected:
  `01_stamp_rotated_15deg_upright`, `02_stamp_rotated_15deg_upleft`, `04_stamp_180deg_upside_down`,
  `07_stamp_over_table`, `08_two_overlapping_stamps`, `14_stamp_chars_positioned_td`,
  `322_mutual_fund_factsheet`, `323_credit_card_statement`, `344_customs_declaration`,
  `364_event_ticket`, `381_incident_report_timeline`, `383_api_docs_page`,
  `54_two_column_body_full_width_header_footer`, `62_two_col_newsletter_pull_quote`,
  `delivery-challan`, `newsletter-3col-header-footer`.

---

## 9. Reproduce

```bash
git clone --depth 1 https://github.com/kavopdf/app /scratch/work/CS && cd /scratch/work/CS
bash tools/p2w-bench/build-engine.sh          # fetches a JDK + PDFBox-Android, compiles ConvertAll
bash tools/p2w-bench/corpus-fetch.sh          # 213 PDFs -> /scratch/work/p2w/corpus
# the 127 = union(gverify failing sets) ∪ (30 Google-clean); convert them
cd tools/engine-verify && java -cp "out:libs/aar/classes.jar:libs/aar/assets:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar" \
    ConvertAll <dir-of-those-pdfs> /scratch/work/docx
# then: unzip word/document.xml and count <w:txbxContent> and <w:color w:val="FFFFFF"/>
# LO cross-check of one document:
soffice --headless --convert-to pdf --outdir /tmp docx/66_two_col_footnotes_bottom.docx
python3 tools/p2w-bench/verify_google.py /scratch/work/p2w/corpus/66_two_col_footnotes_bottom.pdf \
        /tmp/66_two_col_footnotes_bottom.pdf --docx docx/66_two_col_footnotes_bottom.docx
```

Scratch files kept in `/scratch/work`: `census.py`, `census.json`, `white.py`, `white.json`,
`sets.json` (the failing/clean sets), `docx/` (the 127 converted documents), `lo/` (the three
LibreOffice renders).
