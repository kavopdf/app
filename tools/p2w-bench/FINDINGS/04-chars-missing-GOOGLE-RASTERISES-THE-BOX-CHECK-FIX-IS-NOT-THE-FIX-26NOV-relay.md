# `04_chars_missing` — REAL defect or FALSE failure?

**26 Nov 2026.** Read-only investigation of `kavopdf/app` at commit `678248eb99deafdb62a8d36b5cdb7e398a39d860`
(`678248e claim: fixer takes the slot`, 2026-11-25 22:54 UTC). Nothing was modified or committed.

Every count below was **re-derived by me** from committed files or from artifacts I produced in the
sandbox. Where I could not measure, the text says *not determinable from repo evidence*. Numbers in the
prior report (`FINDINGS/04-chars-missing-CHECK-IS-BLIND-TO-TEXTBOXES-2110-agentB.md`) were **not** reused;
§2.7 lists where mine disagree and why.

**What I ran, to make the .docx measurable at all** (the repo commits none, and the check never opens
one, so the claim cannot be tested without them):

```
bash tools/p2w-bench/corpus-fetch.sh          # 213 corpus PDFs -> /scratch/work/p2w/corpus
bash tools/p2w-bench/build-engine.sh          # JDK 17 + PDFBox-Android, engine compiled (36 s)
java ConvertAll corpus docx                   # 213 .docx + 213 .txt, 0 failed (74 s)
```
Engine fingerprint of that build, computed with `verify_google.py:4676-4703`'s own formula
(`sha256(name + bytes)` over `app/src/main/java/com/kavopdf/app/engine/*.java`, first 16 hex):
**`d85db0a9822ddb54`**. That is HEAD. It is **not** `981ff1fa35e2cf67`, the stamp on 153 of the 213
stored Google verdicts (§2.7).

---

## 1. VERDICT

**MIXED — and the split is clean.**

| | finding | basis |
|---|---|---|
| **The check as written** | **FALSE failure on 21 of the 22 documents that fail it at HEAD.** The characters are in the `.docx`, inside `<w:txbxContent>`, and Google does not drop the shape — it emits **exactly one image per `<w:drawing>`**. `04` reads only Google's PDF text layer, so it cannot tell "Google kept the text" from "Google drew it as a picture". | MEASURED, §2.2–2.4 |
| **The construct** | **REAL engine defect — of a different name.** Text the writer puts inside a `<wps:txbx>` arrives in Google Docs as a picture: not selectable, not searchable, not editable. That is exactly the property the writer's own docblock promises (`DocxWriter.java:29-33`). | MEASURED that it is absent from the text layer (§2.5); INFERRED that it is present as pixels (§2.6) |

So: **the check is blind, and must be fixed — but fixing the check alone converts a real user-visible
defect into a passing score.** Both changes are required, and they are different changes:

* the **check** must stop charging the engine for characters the file carries (§3);
* the **engine** must stop routing body text through `wps:txbx` (§4).

Headline counts (all mine, method in §2.1):

| quantity | value |
|---|---:|
| documents in the newest Google run (engine `d85db0a9822ddb54` = HEAD) | **60** (58 scored + 2 `page_count_refused`) |
| of those, failing `04_chars_missing` | **22** |
| … of which carry `<w:txbxContent>` in the HEAD `.docx` | **21** |
| … of which carry none | **1** (`25_signature_block_underscores_txtpos`) |
| documents that PASS `04` and carry `<w:txbxContent>` | **0 of 36** |
| documents where `04` is the only failure | **0** |
| documents whose reported loss **equals** their box character count exactly (older numeric store, §2.3) | **21 of 35 failures** (7,520 chars) |
| documents whose box text is a sub-multiset of the source PDF's text | **45 of 47** box-carrying documents |
| documents where Google's export image count **equals** the `.docx` `<w:drawing>` count | **152 of 153** |

---

## 2. EVIDENCE

### 2.1 How I counted

* **Google side.** All 213 `benchmarks/gverify/*.json`. They are **two different stores** and must not be
  pooled: 60 records stamped `d85db0a9822ddb54` (dated 2026-11-25T22:06→22:43, HEAD, *no per-check
  numbers* — the `checks` key is the string `"375669-1795643901"`, a size-mtime fingerprint written by
  `gverify.py:550-551` via `_checks_now()` at `gverify.py:70-81`); and 153 records stamped
  `981ff1fa35e2cf67` with a full numeric `checks` dict (an **older** engine — `gvbatch.py:47-53` skips a
  record only when its `engine` matches the current one, so these 153 are the ones that were never
  re-measured). 2 more are `status: page_count_refused` with no checks at all.
* **`.docx` side.** My own 213 files, parsed with `ElementTree` over `word/document.xml`: every `<w:t>`,
  and separately every `<w:t>` whose ancestor chain contains `<w:txbxContent>`. Both sides normalised with
  the check's own `norm_text()` (`verify_google.py:345-361`), so counts are in the check's own unit
  (whitespace, C0, U+200B, U+FEFF stripped; lower-cased).
* **Source side.** `fitz`/PyMuPDF over the 213 corpus PDFs, same normalisation.
* **Failure sets** are taken from each record's `failed` list, not from prose.

### 2.2 Q1 — where the "google" text comes from: **Google's export, never the `.docx`**

`tools/p2w-bench/verify_google.py`:

```python
4716  def compare(src_path, gd_path, docx_path=None):
4717      src = fitz.open(src_path)
4718      gd = fitz.open(gd_path)
```
```python
4731      s_runs, g_runs = [], []
4732      for i, p in enumerate(src):
4733          s_runs += runs(p, i, mirrored=(i in s_mir), page_angle=page_reading_frame(p))
4734      for i, p in enumerate(gd):
4735          g_runs += runs(p, i, mirrored=(i in g_mir), page_angle=page_reading_frame(p))
```
```python
4752      s_text = " ".join(r["text"] for r in s_runs)
4753      g_text = " ".join(r["text"] for r in g_runs)
```
```python
4817      s_chars = collections.Counter(norm_text(s_text))
4818      g_char_count = collections.Counter(norm_text(g_text))
4819      chars_missing = s_chars - g_char_count
4820      checks["04_chars_missing"] = (0, sum(chars_missing.values()), not chars_missing)
```

`gd_path` is the PDF Google exported from the uploaded document: `gvbatch.py:65-66` invokes
`verify_google.py <src.pdf> <render.pdf> --docx <docx>` and the render is `a.renders/<name>.pdf`
(`gvbatch.py:62`). The `.docx` is passed to `compare()` and **is** used by other checks (`docx_path` at
1698, 2109, 2222, 6179…), but `grep -c txbxContent tools/p2w-bench/verify_google.py` = **0**: the
verifier has no concept of shape text anywhere.

Two consequences worth stating because they mislead readers of the store:

* `source` in this check is the **literal `0`**, not a source count (line 4820). A failing row reads
  `{"source": 0, "render": 374}` — that `render` is the *loss*, not the render's size.
* The predicate is **zero-tolerance multiset containment of the whole document**. One character
  anywhere fails it.

### 2.3 Q2 — do the affected `.docx` really carry that text only inside text boxes?

Yes, for the box-carrying majority; and the separator is perfect in both stores.

Census of my HEAD build (213 `.docx`): **47 carry `<w:txbxContent>`**, **22,820** characters live inside
them, and **0 of 213 contain `mc:AlternateContent`** (so there is no `mc:Fallback` second copy of the same
text to double-count — this matters for §3).

Separator, HEAD store (58 scored documents):

| | fails `04` | passes `04` |
|---|---:|---:|
| carries `<w:txbxContent>` | **21** | **0** |
| carries none | **1** | **36** |

Separator, older numeric store (153 scored documents), box presence read from the same HEAD `.docx`:

| | fails `04` | passes `04` |
|---|---:|---:|
| carries `<w:txbxContent>` | **24** | **0** |
| carries none | **11** | **118** |

Not one document that passes `04` carries a text box, in either population. The construct decides the
check; nothing else in the corpus separates as cleanly.

The text is genuinely the document's own text, not an artefact of the writer: for **45 of 47**
box-carrying documents the box's character multiset is a **sub-multiset of the source PDF's text**
(measured against the corpus PDFs). The two exceptions are `041122-Account_Opening_Form` and
`Account_Opening_Form_Fillable_filled`, each with a 15-character residue out of 5,502 box characters
(`ĥ`/`ħ`/`ģ`, the same glyph-substitution residue the repo records elsewhere).

Exact identity of the reported loss against the box count (older numeric store, 35 failures):

| reported loss == box chars | documents |
|---|---:|
| exactly equal | **21** (sum 7,520 chars) |
| box present, not equal | **3** — `Account_Opening_Form_Fillable_filled` 3,334 vs 5,502; `academic-paper-ieee-2col-abstract` 2,506 vs 2,505; `411_nested_xobject_transforms` 2 vs 23 |
| no box at all | **11** (sum of losses 38 chars) |

The 21 exact matches: `policy-2col-spanning-section-heading` (2,586), `magazine-2col-pullquote-spanning`
(1,811), `69_two_col_legal_numbered_clauses` (1,155), `65_two_col_full_width_figure_caption` (535),
`66_two_col_footnotes_bottom` (374), `400_comic_page_speech_bubbles` (246), `gst-invoice-horizontal-rules-only`
(128), `newspaper-2col-fullwidth-headline` (106), `401_trifold_brochure` (104), `table-with-rotated-header`
(90), `80_gstin_pan_cin_ifsc_table` (63), `60_page_border` (53), `admit-card` (47), `364_event_ticket` (44),
`352_certificate_ornate_border` (35), `371_experience_certificate` (35), `delivery-challan` (33),
`43_red_stamp_over_black_text` (28), `353_admit_card` (24), `property-tax-receipt` (16),
`344_customs_declaration` (7).

That is **21 of 24** box-carrying failures, not the "40 of 44" the lead claims. The *proportion* the lead
reports (≈0.9) reproduces; its absolute population does not (§2.7).

### 2.4 Q3, part 1 — does Google **drop** the shape? No. It emits one image per shape.

`08_image_count` in the older numeric store records the render's image count. Against the `<w:drawing>`
count of my HEAD `.docx`:

```
rows compared                          153
render images == .docx w:drawing       152     (exact equality)
median(render − drawings)                0
only exception   401_trifold_brochure   render 21 vs drawings 26
```

`Account_Opening_Form_Fillable_filled`: source 1 image, render **2,653** images, `.docx` **2,653**
`<w:drawing>`. The repo states the mechanism in `verify_google.py:957-960`:

> "Google Docs exports every anchored shape in the .docx as one raster image: on 207 of the 211 corpus
> documents the render's 08_image_count equals the .docx `<w:drawing>` count exactly, and the median
> difference is zero."

and, for the fills inside those shapes, `verify_google.py:55-62` (measured on **34 real Google exports**):

> "every page carries exactly ONE filled rect and it is page-sized… The bands ARE there; Google
> rasterises them, so a navy table header that arrives as an image is invisible to `get_drawings()`."

So the export contains a picture **at the shape's position and size**. Nothing is discarded.

### 2.5 Q3, part 2 — is the box text in Google's **text layer**? No, and that is measured in Google.

The one case in the repo where Google was actually driven twice through the real path
(Drive upload → convert to a Google Doc → export PDF → `verify_google.py --docx`) is recorded in
`FINDINGS/RUNNING-FOOT-IS-A-ROW-GOOGLE-DROPS-THE-BOX-1855-fixer.md:11-24, 77-87`:

> "At HEAD, Google's own export of that document is missing **two lines and nothing else** … Those two
> lines are the document's **only two DrawingML text boxes** (`w:txbxContent` count = 4 in the .docx,
> i.e. 2 shapes …). So: `04_chars_missing` fires because 43 characters of the page are not in the
> render's text layer …"
>
> | | HEAD `b7699196` | with `footBand` |
> |---|---|---|
> | `27_two_column_left_short_txtpos` | 40/42 FAIL (`04` render 43) | **42/42 PASS** |
> | `w:txbxContent` in that .docx | 4 | **0** |
> | footer lines in Google's text layer | absent | **present** |

`FINDINGS/DOCS-ROOT-CAUSES-24NOV.md:118-122` adds the observation on the same document:

> "the same document with the boxes removed exports at 1601 with **zero** missing, and the box's ink
> reappears in the export's image list as a **270x12 px bitmap where the footer line was**."

**Caveat on that example:** it is history, not HEAD. At HEAD that document has **0** text boxes in my
build and passes all 42 checks (`failed: []`). The mechanism it demonstrates is not contradicted; the
document it was demonstrated on has been fixed.

### 2.6 Q3, part 3 — what Google-side artifacts are actually stored, and what they can and cannot settle

| artifact | present? | what it establishes |
|---|---|---|
| Google export **PDFs** | **none committed** (124 PDFs in the repo are all *source* corpus files; the stored `render_file`/`source` paths point at `/scratch/work/...` that no longer exists) | — |
| Google export **text dumps** | **none** | — |
| **screenshots** of Docs | **none** (`benchmarks/SCREENSHOT-DOC.json` is a *scanned PDF* named "Screenshot…", not a Docs screenshot) | — |
| `gverify` per-check results | **yes**, 213 JSON | text-layer absence, and the pass/fail separation. No pixels. |
| **SSIM / pixel data** | **6 documents only** (`benchmarks/PIXEL-SCORES-GOOGLE.csv`, `…-VS-LO.csv`) | see below |

The one SSIM row that matters is a box-heavy document. `academic-paper-ieee-2col-abstract` carries 2,505
box characters (≈46 % of its text by the older census) and fails `04` at 2,506:

```
academic-paper-ieee-2col-abstract  google ink_iou 37.78  google ssim 77.30
                                   libreoffice ink_iou 62.42  libreoffice ssim 83.63
```

Google's render is **worse than LibreOffice's but nowhere near blank**. If 46 % of the page's text had
simply vanished, ink IoU would collapse; it drops by 25 points, which is the signature of ink that is
present but re-rasterised and re-placed. That is consistent with rasterisation and inconsistent with
deletion — on one document, at one moment.

**What is therefore established and what is not:**

* **Established (measured):** the characters are absent from the export's **text layer**; the export
  carries **one image per shape**, at the shape's place; the fill ink inside those images is really there
  (34 exports, `verify_google.py:55-62`); the writer's own text is inside `w:txbxContent`.
* **NOT determinable from repo evidence:** whether the **glyph ink** inside the 270×12-style bitmap is
  legible in Google's export. No committed artifact shows the pixels of a box region, and no OCR of a
  Google export exists anywhere in the tree. The two sub-mechanisms (i) rasterise the box with its text,
  (ii) clip the text out of the box (`wp:extent` + `wps:bodyPr wrap="none"` + `a:noAutofill`) both
  produce "text absent from the text layer, one image present" and the repo does not separate them.
* **Which way that cuts:** under (i) the user sees the footer and only loses selectability — the check is
  blind and `04` is a false failure. Under (ii) the footer is **invisible**, and the defect is worse than
  `04` says. **Either way the engine must change** (§4); only the severity and the check's wording differ.
  One Google export of `66_two_col_footnotes_bottom` with its text layer and a crop of the footnote band
  would settle it in a single measurement.

### 2.7 Where my numbers disagree with the 2110 report — and why

1. **"All 213 verdicts carry `981ff1fa35e2cf67`, and HEAD fingerprints to `981ff1fa35e2cf67`."** False at
   this commit. HEAD fingerprints to **`d85db0a9822ddb54`** (computed with the verifier's own formula),
   and only **60** verdicts carry that stamp. The other **153** are stamped `981ff1fa35e2cf67` and are
   stale. So that report's population (59 failures) is a mixed-build population, and its `out/` `.docx`
   were built on a different engine from the verdicts it compared them to.
2. **"44 documents carry a box, 40 of them count-identical."** Mine: **24** box-carrying failures in the
   numeric store, **21** count-identical; **21** box-carrying failures at HEAD. The ratio survives; the
   counts do not.
3. **`041122-Account_Opening_Form` = 3,329 missing.** At HEAD that document has **no `04` verdict at
   all**: its record is `status: page_count_refused` (11 pages exported against 9 wanted). The 3,329 is
   from a build that no longer exists in the store.
4. **"The predicate is at `4817-4820`"** — correct at this commit. The *writer* citation is not:
   `<wps:txbx><w:txbxContent>` is emitted at **`DocxWriter.java:5804`**, not 5664; `anchorShape()` starts
   at 5705.
5. **"The store records `04` as `{source, render, ok}`"** — true only of the 153 old records. The 60
   newest records carry **no numbers at all**, so the count identity **cannot be tested at HEAD from the
   store**. That is a data-loss defect in the store worth its own fix: `gverify.py:550-551` writes the
   size-mtime fingerprint into the same `checks` key that `verify_google.py:6423` uses for the per-check
   dict.

---

## 3. PATCH SPEC — attribution of box text (the check fix)

Minimal, additive, and monotone (it can only ever *remove* characters from the deficit).

**File: `tools/p2w-bench/verify_google.py`.** `zipfile` (line 44) and `ET` (line 45) are already imported.

**(a) Insert immediately before `def compare(` at line 4716:**

```python
def docx_box_text(path):
    """The characters the .docx carries inside a shape (<w:txbxContent>), or "" without one.

    Google's DOCX importer rasterises a <wps:txbx>: the shape's content arrives in its PDF export
    as one image (measured: the export's 08_image_count equals the .docx <w:drawing> count exactly
    on 152 of 153 documents) and none of its characters reach the export's text layer. 04 reads the
    text layer, so it charges the engine for characters the file demonstrably carries - 21 of the
    22 documents that fail it at HEAD are exactly the documents carrying one of these boxes, and 0
    of the 36 that pass carry one. Attribute the loss where it belongs and let 04 answer its own
    question. The engine emits no <mc:AlternateContent> (0 of 213 emitted .docx), so there is no
    Fallback copy of this text to double-count.
    """
    try:
        x = zipfile.ZipFile(path).read("word/document.xml")
        root = ET.fromstring(x)
    except Exception:
        return ""
    out = []

    def walk(el, inside):
        if el.tag == "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}txbxContent":
            inside = True
        if inside and el.tag == "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t":
            out.append(el.text or "")
        for c in el:
            walk(c, inside)

    walk(root, False)
    return "".join(out)
```

**(b) Replace lines 4819-4820:**

```diff
     s_chars = collections.Counter(norm_text(s_text))
     g_char_count = collections.Counter(norm_text(g_text))
     chars_missing = s_chars - g_char_count
-    checks["04_chars_missing"] = (0, sum(chars_missing.values()), not chars_missing)
+    # Google's importer rasterises shape text, so the characters the .docx carries inside
+    # <w:txbxContent> never reach its export's text layer. Charging them here says the ENGINE lost
+    # them; it did not (21 of the 22 HEAD failures are box-carrying documents, 0 of the 36 that
+    # pass carry a box). Attribute the loss to the construct that causes it, keep it visible in
+    # detail, and leave 04 saying what its name says. The rasterisation is a real defect and must
+    # be charged elsewhere - 59_shape_anchor, or a check that counts box characters present in the
+    # .docx and absent from the export.
+    boxed = collections.Counter(norm_text(docx_box_text(docx_path))) if docx_path else \
+        collections.Counter()
+    rasterised = chars_missing & boxed
+    unexplained = chars_missing - rasterised
+    checks["04_chars_missing"] = (0, sum(unexplained.values()), not unexplained,
+                                  {"rasterised": sum(rasterised.values())})
```

A 4-tuple with a `detail` dict is the established shape: `verify_google.py:6423-6425` serialises
`{"detail": v[3]}` when `len(v) > 3`, and `18_displacement` already uses it.

**Smoke-tested here** against all 213 emitted `.docx`: the helper finds box text in **47** documents,
**22,820** characters; on `66_two_col_footnotes_bottom` a synthetic deficit of 379 with a 374-character
box yields `rasterised 374, unexplained 5, ok False` — i.e. the residue still fails, as it must.

### Predicted effect

**Documents that newly FAIL: 0. Provable, not measured.** `rasterised = chars_missing & boxed` is a
multiset intersection with `chars_missing`, so `unexplained ⊆ chars_missing`. Therefore
`sum(unexplained) ≤ sum(chars_missing)` and `not unexplained ⇒ not chars_missing`: a document with an
empty deficit today keeps an empty deficit. This is the one part of the before/after that needs no
re-measurement.

**Documents that flip FAIL → PASS (`04` row only):**

| population | predicted flips | why |
|---|---:|---|
| older numeric store (153 docs, `981ff1fa`) | **21 certain**, + `411_nested_xobject_transforms` (2 missing vs 23 box chars, flips iff contained) = **up to 22** | their reported loss equals their box count exactly (§2.3) |
| newest store (58 docs, HEAD) | **≤ 21 — not determinable** | the 60 newest records carry no per-check numbers (§2.7.5), so the deficit is unknown; the bound is the 21 box-carrying failures |
| cannot flip, either population | `25_signature_block_underscores_txtpos` (no box); the 11 box-free failures; `Account_Opening_Form_Fillable_filled` (3,334 vs 5,502 → ≥2,168 chars stay unexplained); `academic-paper-ieee-2col-abstract` (2,506 > 2,505 → ≥1 char stays) | residue survives the subtraction |

**Documents that become fully CLEAN: 0.** `04` is never a document's only failure — 0 of 22 at HEAD;
among the 21 count-identical documents the median failed count is 5 and the minimum is 3, with
`45_char_accuracy` also failing on 16 of them and `59_shape_anchor` on 11. The patch fixes a row, not a
document. Anyone expecting a score jump should be told this before it lands.

---

## 4. RISK

**Can any document newly fail? No** — the monotonicity proof above is the whole argument, and it does not
depend on any measurement.

**Is the construct one Google ignores? No — it is worse than ignored.** Google does not discard the
shape: it reproduces it as an image (export image count == `.docx` `<w:drawing>` count on 152 of 153).
The text therefore survives *visually* and dies *as text*. Three consequences:

1. **The patch removes the only check that names this class.** After it lands, no check in the 42 says
   "this document's footer is a picture". `45_char_accuracy` will still fail 16 of the 21 and
   `59_shape_anchor` 11 of the 21, so the documents stay red — but for reasons that do not point at the
   construct. If the signal is to survive, the same change must land a `detail.rasterised` count *and*
   either extend `59_shape_anchor` or add a check that measures box characters present in the `.docx` and
   absent from the export. Landing the `04` half alone is the failure mode the project's own rules exist
   to prevent.
2. **The engine fix is the one that matters.** `DocxWriter.java:29-33` promises "real characters in real
   runs … selectable, searchable and editable, not a picture of a page". For the 47 documents that carry
   box text, Google delivers the opposite. The remedy is construct-level, not threshold-level: emit body
   text, footnotes, sidebar and column text as **flow** (`flowParagraph`/`flowRow`/`flowFromBox`) or as a
   1×1 table with cell borders, and keep `wps:txbx` only for genuinely rotated lines, where a shape is the
   only construct OOXML has for an angle. Two engine flags already exist that move this class and were
   measured and **not** kept (`p2w.pagepos=0`: 8 of 213 documents changed, boxed chars 27,501 → 22,476,
   but 21 overlaps and median |dy| 105.7 pt — `ATTEMPTS.json`, 2026-11-25 08:54); the landed `footBand`
   change (`flowRow`'s pitch branch, `DocxWriter.java`) is the one site that has been proved in Google
   (40/42 → 42/42 on `27_two_column_left_short_txtpos`). The remaining sites are the `containerOf`
   branch, `pinnedBoxes`, and `ctx.positioned`.
3. **Masking risk, bounded.** The subtraction is `chars_missing & boxed`, so it can absorb at most
   `min(deficit, box)`. Where a document's deficit *exceeds* its box count (the two
   `Account_Opening_Form` documents, `academic-paper`) the residue keeps it failing. Where the box text
   is also present elsewhere in the flow — **19 of the 21** count-identical documents, e.g. the stamp text
   `AUTHORISED SIGNATORY` whose letters recur in the letterhead — a genuine flow loss of the same
   characters could in principle be absorbed. This is not a defect of the patch: the deficit counts
   *copies*, so a second copy in the flow does not hide the loss of the box's copy, which is exactly what
   the count identity demonstrates. It does mean the patch should not be read as a proof that nothing
   else was lost.

**Residual risk that the mechanism itself is wrong.** The single measurement that would falsify it is a
document that passes `04` while carrying `<w:txbxContent>`: **0 of 154 passers across both stores today**.
The measurement that would confirm the fix is a re-score of the cached Google exports with the patch:
expect the flips in §3, `detail.rasterised` equal to the document's box character count on the
count-identical rows, `601_fillable_admission_form` still failing at 2, and **0** PASS → FAIL.

---

## 5. Not determinable from repo evidence

* Whether the glyph ink inside the rasterised box bitmap is legible in Google's export (§2.6). No export
  PDF, no export text dump, no Docs screenshot, and no OCR of a Google render is committed.
* The exact flip set at HEAD: the 60 newest verdicts carry no per-check numbers.
* Whether the 3 box-carrying non-identical rows (`Account_Opening_Form_Fillable_filled`,
  `academic-paper-ieee-2col-abstract`, `411_nested_xobject_transforms`) are build drift between
  `981ff1fa` and HEAD or a second mechanism — their box counts at `981ff1fa` are not recoverable from the
  repo.
* The 11 box-free failures (38 characters in total, largest 19 on `38_faux_bold_italic_synthesised`) are a
  separate, small class that this patch neither fixes nor explains.
