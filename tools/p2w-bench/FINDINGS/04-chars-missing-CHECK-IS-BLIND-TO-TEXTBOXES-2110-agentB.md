# `04_chars_missing` — is the check measuring the wrong thing?

**26 Nov 2026, agent B.** Verifying the lead in
`tools/p2w-bench/FINDINGS/DOCS-ROOT-CAUSES-24NOV.md:99-160`
("the check never opens the .docx, and 63 of 65 lose nothing").

Every number below is **MEASURED** from the committed store, the emitted `.docx` XML, the repo's
own source PDFs, or python-docx/pymupdf runs I made in the sandbox, unless the line says
**INFERRED**. No JDK and no Google Docs access exist here; no Google export PDF is committed, so
every statement about *what Google's exporter did* is INFERRED from the numbers the check itself
stored.

---

## 1. Verdict

**The claim's mechanism is CONFIRMED. Its numbers, its file:line citation and its single "proven,
not inferred" example are all wrong.** The check is measuring the wrong thing in a precise sense:
it charges the engine for characters that are provably inside the `.docx` file and that only
Google's importer loses. But the correct count of documents that shows this is **44**, not 54, and
the failing population is **59**, not 65 — and on the only three documents where the source PDF is
available to me the `.docx` really does lose characters (127, 131, 2), so "nothing was lost at
conversion" is true of the *group's* Google deficit and false as a statement about the engine.

| question | answer | basis |
|---|---|---|
| Does `04` ever open the emitted `.docx`? | **No.** Not for this check. | MEASURED, `verify_google.py:4817-4820` |
| Does Google's export lose exactly the shape text the `.docx` carries? | **Count-identical on 40 of 44 documents** (9,076 of 18,362 missing characters) | MEASURED |
| Is the `.docx` character-complete against the engine's own extraction? | **Yes, on 53 of 53** (deficit 0) | MEASURED |
| Is the `.docx` character-complete against the *source PDF*? | **No on 2 of 3 testable** (127 and 131 characters) | MEASURED |
| Is the "perfect one-sided separator" real? | **Yes at HEAD: 44 of 44 box-carrying documents fail; 0 of 142 box-free passing documents carry a box** | MEASURED |
| Do 65 documents fail? | **No — 59** | MEASURED |

---

## 2. What the check actually is

The predicate, verbatim (`tools/p2w-bench/verify_google.py:4817-4820`):

```python
4817    s_chars = collections.Counter(norm_text(s_text))
4818    g_char_count = collections.Counter(norm_text(g_text))
4819    chars_missing = s_chars - g_char_count
4820    checks["04_chars_missing"] = (0, sum(chars_missing.values()), not chars_missing)
```

- **What it compares:** the source PDF's text layer against **Google's PDF export of the `.docx`**.
  `s_runs` is built from `src` (`verify_google.py:4731-4734`, `runs(p, i, ...)`), `g_runs` from `gd`
  (`4733-4734`), where `gd = fitz.open(gd_path)` (`4717-4718`) — the Google render PDF, passed in by
  `gvbatch.py:71` as `<src.pdf> <render.pdf> --docx <docx>`. The `.docx` is never read by this check.
- **Tolerance:** **none.** `not chars_missing` is multiset containment of the whole document, zero
  slack. The comment above it (`4806-4816`) states this deliberately: the unit was moved from word
  to character precisely so that "not one thing may be missing" is a character statement.
- **Fields it reads:** only `s_text`/`g_text`, the text of `runs()` spans on both sides, through
  `norm_text()` (`345-361`: whitespace, U+00A0, C0 controls, U+200B, U+FEFF stripped; case folded).
  No geometry, no fonts, no `.docx`.
- **Fields it writes:** `(source, render, ok)` = `(0, missing_count, ok)`. The **`source` field is
  the literal `0`** — it is not a measurement, and the store therefore shows `source: 0, render: 35`
  on a failing document, which reads like "the render has 35 more". The deficit lives in `render`.
  Any reader who assumes `source` is a source count will misread all 59 rows.
- `--docx` *is* accepted and used by other checks (`1698`, `1881`, `2109`, `2222`, `3195`, `3417`,
  `6179`) — the instrument knows how to open the file; this check does not. `grep -c txbxContent
  verify_google.py` = **0**: it has no concept of shape text anywhere.

**The line reference in the lead (`verify_google.py:4695-4697`) is wrong.** That range is inside
`_engine_head()`, the engine-fingerprint fallback (`4680-4714`). The predicate is `4817-4820`.

---

## 3. The failing population (MEASURED from `benchmarks/gverify/*.json`)

213 verdict files, **all stamped `981ff1fa35e2cf67`**, and that is the fingerprint of the repo at
HEAD — I recomputed it with `gvbatch.py`'s own formula (sha256 over `name+bytes` of every
`app/src/main/java/com/kavopdf/app/engine/*.java`) and got `981ff1fa35e2cf67`. The store is current.

| quantity | value |
|---|---:|
| verdicts in store | 213 |
| documents failing `04_chars_missing` | **59** |
| documents failing **only** `04` | **0** |
| smallest failed-check count in the group | 2 |
| sum of the check's own reported loss over the 59 | **18,581** characters |
| failing documents with an emitted `.docx` in `out/` | **53** (6 have none: `newspaper-2col-fullwidth-headline`, `one-page-rotated-180-degrees`, `property-tax-receipt`, `table-across-page-break-repeated-header`, `table-with-rotated-header`, `very-long-single-column-table`) |
| of those 53, carrying `<w:txbxContent>` | **44** |
| of those 53, carrying none | **9** |
| sum of the check's reported loss over the 53 | 18,362 |

Failed-check-count distribution: 2→2 docs, 3→4, 4→14, 5→13, 6→6, 7→9, 8→4, 9→5, 23→1, 26→1.
**Fixing `04` alone cleans nothing** — no document has it as its only failure.

`RANKING.csv`'s `chars_missing` column is a different instrument (`p2w.py` text recall), not this
check: `041122-Account_Opening_Form` reads `127` there against `3,329` in `04`.

---

## 4. Independent test of the claim's numbers

I took all 53 failing documents that have an emitted `.docx` and measured four things per document:
`docx XML` (every `w:t` in `word/document.xml` via ElementTree — the engine emits **no**
`mc:AlternateContent` in any of the 195 files, so there is no Fallback copy to double-count);
`box` (the `w:t` inside `<w:txbxContent>`, the construct written by `DocxWriter.anchorShape()`:
`<wp:anchor>…<a:graphicData uri="…wordprocessingShape"><wps:wsp><wps:txbx><w:txbxContent>`, inspected
in `out/041122-Account_Opening_Form.docx`); `python-docx` (`Document(p).paragraphs` + tables, the
method the brief prescribes); and `txt` (the engine's own text output, standing in for the source
text layer).

### 4a. The check's own loss equals the shape text, to the character, on 40 of 44

| document | `04` missing (store) | box chars in `.docx` | equal? | LO `04` | failed checks |
|---|---:|---:|:--:|---:|---:|
| `Account_Opening_Form_Fillable_filled` | 3334 | 5502 | no | 131 | 26 |
| `041122-Account_Opening_Form` | 3329 | 5502 | no | 127 | 23 |
| `policy-2col-spanning-section-heading` | 2586 | 2586 | **yes** | 0 | 8 |
| `academic-paper-ieee-2col-abstract` | 2506 | 2505 | no (off by 1) | 0 | 8 |
| `magazine-2col-pullquote-spanning` | 1811 | 1811 | **yes** | 0 | 9 |
| `69_two_col_legal_numbered_clauses` | 1155 | 1155 | **yes** | 0 | 7 |
| `65_two_col_full_width_figure_caption` | 535 | 535 | **yes** | 0 | 7 |
| `66_two_col_footnotes_bottom` | 374 | 374 | **yes** | 0 | 5 |
| `322_mutual_fund_factsheet` | 311 | 311 | **yes** | 0 | 9 |
| `400_comic_page_speech_bubbles` | 246 | 246 | **yes** | 0 | 7 |
| `331_pid_diagram` | 215 | 215 | **yes** | 0 | 9 |
| `20_numbered_list_separate_column_txtpos` | 195 | 195 | **yes** | 0 | 4 |
| `323_credit_card_statement` | 194 | 194 | **yes** | 0 | 7 |
| `311_fir_police_form` | 176 | 176 | **yes** | 0 | 4 |
| `gst-invoice-horizontal-rules-only` | 128 | 128 | **yes** | 0 | 6 |
| `305_vaccination_certificate` | 113 | 113 | **yes** | 0 | 9 |

40 of 44 have `missing == box chars` **exactly**, totalling 9,076 of the 18,362 characters the
check charges. A count coincidence of that kind on 40 documents is not plausible; the identity is
the mechanism. Three more have `missing < box` (`041122` and `Account_Opening_Form_Fillable_filled`
as above, plus `411_nested_xobject_transforms` 2 vs 23), i.e. consistent with the same cause
partially. One (`academic-paper-ieee-2col-abstract`) is one character over its box count.

**MEASURED:** the counts. **INFERRED:** that the missing multiset is the box multiset (the store
does not carry the missing characters — see §8).

### 4b. The nine documents with no shape text at all

| document | `04` missing | `.docx` chars (XML) | `.txt` chars | LO `04` | failed checks |
|---|---:|---:|---:|---:|---:|
| `25_signature_block_underscores_txtpos` | 84 | 1322 | 1322 | 0 | 4 |
| `38_faux_bold_italic_synthesised` | 19 | 936 | 871 | **19** | 2 |
| `58_header_rule_footer_rule` | 4 | 1306 | 1306 | 0 | 4 |
| `381_incident_report_timeline` | 2 | 1131 | 1131 | 0 | 3 |
| `601_fillable_admission_form` | 2 | 471 | 471 | **2** | 5 |
| `383_api_docs_page` | 1 | 999 | 999 | 0 | 6 |
| `417_rotate180_and_mirrored` | 1 | 338 | 338 | 0 | 4 |
| `602_bookmarked_annual_report` | 1 | 693 | 693 | 0 | 4 |
| `form16-part-b` | 1 | 2308 | 2308 | 0 | 4 |

115 characters in total — 0.6 % of the class. This is the claim's "9 undetermined" set, and I
confirm it is not the shape-text mechanism.

### 4c. The separator, over all 195 emitted `.docx`

| | fails `04` | passes `04` |
|---|---:|---:|
| carries `<w:txbxContent>` | **44** | **0** |
| carries none | 9 | 142 |

Perfectly one-sided at HEAD. The claim said "54 of the 65 fail, 0 of the 125 that pass" — the shape
is right, the numbers are not.

### 4d. The `.docx` loses nothing relative to the engine's own extraction

Over the 53: `.docx` (all `w:t`) = **140,035** characters, `.txt` = **135,024**, multiset deficit
`txt − docx` = **0 on all 53**. The shape text is a sub-multiset of the `.txt` on **44 of 44**, so the
engine's extraction carries the box text and the writer carries it into the file.

### 4e. python-docx alone overstates the loss by 12,327 characters

Run the brief's own method and the answer is wrong: on **44 of 53** documents the python-docx
deficit against the `.txt` is positive, totalling **12,327** characters, because python-docx returns
only body-level `w:p` and table text and **cannot see inside `<w:txbxContent>`**. Anyone verifying
this with python-docx as the only reader will "confirm" a loss the file does not have. The XML
reader is mandatory here.

### 4f. Where the `.docx` really does lose characters — the source PDFs in the repo

124 source PDFs are committed under `benchmarks/realworld/`, `benchmarks/corpus-extra/` etc. Three
of the 53 failing documents have one, plus `602`:

| document | source PDF chars | `.docx` chars | deficit source−`.docx` | `04` (store) | LO `04` |
|---|---:|---:|---:|---:|---:|
| `041122-Account_Opening_Form` | 39,840 | 42,319 | **127** (`ĥ` 89, `ħ` 25, `ģ` 13) | **3,329** | 127 |
| `Account_Opening_Form_Fillable_filled` | 39,924 | 42,398 | **131** | **3,334** | 131 |
| `601_fillable_admission_form` | 473 | 471 | **2** | 2 | 2 |
| `602_bookmarked_annual_report` | 693 | 693 | **0** | 1 | 0 |

Three readings of the same file agree to the character: the source-vs-`.docx` deficit, the
LibreOffice verdict's `04` count, and `RANKING.csv`'s `chars_missing` (127 for `041122`). Against
them, Google's export loses 3,329 — **3,202 more characters than the file is missing**, on a
document whose box text is 5,502 characters.

The `601` row is the check being **right**: the `.docx` genuinely lacks 2 characters (ZapfDingbats
ticks) and both renderers say so.

### 4g. LibreOffice verdicts (`benchmarks/gverify-lo/`, 213 files)

49 of the 53 read `04 = 0`; four read `>0`: `041122` 127, `Account_Opening_Form_Fillable_filled`
131, `38_faux_bold_italic_synthesised` 19, `601_fillable_admission_form` 2.

**Caveat:** those 213 LibreOffice verdicts are stamped on **older engine builds** — `b7699196` 32,
`5beb8b9d` 13, `462353f` 6, `7112d76` 1, unset 1 — not the `981ff1fa35e2cf67` of the Google verdicts
and the emitted `.docx`. So 4g is a cross-build comparison, indicative only. It is still the
strongest renderer-side evidence available without Google: a renderer that keeps shape text as text
reproduces the `.docx`'s characters and reads 0 on 49 of 53.

---

## 5. Where the lead is wrong

1. **The population is 59, not 65, and "63 of 65 lose nothing" is not reproducible.** The store has
   59 failing documents, 53 of which have an emitted `.docx`. My measured result is stronger than
   the claim in one direction (53 of 53 lose nothing against the engine's own extraction) and
   weaker in another (2 of the 3 source-checkable documents do lose 127 and 131 characters).
2. **`verify_google.py:4695-4697` is the wrong line range.** The predicate is `4817-4820`.
3. **The decisive example is stale.** The lead's only "proven, not inferred" case is
   `27_two_column_left_short_txtpos` ("the missing 43-character multiset is identical to the 43
   characters inside that document's text boxes"). At HEAD it **passes 42/42** with `04 = {source:
   0, render: 0}`, and its emitted `.docx` carries **zero** `<w:txbxContent>`. Same for
   `61_two_col_abstract_spanning`. `ATTEMPTS.json` records the 43-character experiment on build
   `b7699196`, which no longer appears in the store. The mechanism survives; the proof has to be
   rebuilt on today's documents — §4a is that rebuild.
4. **`38_faux_bold_italic_synthesised` is not a "pure check artefact".** The lead says its 19
   characters are one duplicate copy of a fake-bold heading "the .docx correctly carries once".
   Measured: it has no shape text, its `.docx` carries **936** characters against the `.txt`'s
   **871** (65 *more*, not fewer), and **LibreOffice reads `04 = 19` too** — the same number as
   Google. A renderer that keeps everything as text also cannot find the second copy, so the
   missing copy is missing from the *file*, not from Google's export. Whether emitting one copy is
   correct is a judgement; calling it a check artefact is not supported by the data.
5. **"the engine is wrong on 54 in the way a user feels it" is INFERRED.** The rasterisation of a
   `<wps:txbx>` by Google's importer is nowhere observable in this sandbox. What is measured is
   that Google's export lacks exactly as many characters as the boxes hold. The user-visible
   consequence (a picture of a footer instead of a footer) is the lead's inference, and it is a
   reasonable one.

---

## 6. The minimal instrument fix

**Attribution, not loosening** — the same shape of rule the `60` investigation proposed: charge the
loss where the file is at fault. Subtract, from `04`'s deficit, exactly those characters the `.docx`
carries inside a shape, and report the subtracted count so the signal does not vanish.

New helper, to be inserted immediately before `def compare(` at **`verify_google.py:4716`**:

```python
def docx_box_text(path):
    """The characters the .docx carries inside a shape (<w:txbxContent>), or "" without one.

    Google's DOCX importer rasterises a <wps:txbx>, so every character inside it is present in
    the file and absent from Google's PDF export: measured 26 Nov, the export's character deficit
    equals the box character count exactly on 40 of the 44 failing documents that carry one
    (9,076 of 18,362 characters). 04 must not charge the engine for a loss the file does not
    have. The rasterisation is a real defect and belongs to 59_shape_anchor, not here.
    The engine emits no <mc:AlternateContent> (0 of 195 emitted .docx), so there is no Fallback
    copy to double-count.
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

(`ET` and `zipfile` are already imported — `verify_google.py:44-45`.)

Replacement for **`verify_google.py:4819-4820`**:

```diff
@@ -4817,8 +4817,16 @@ def compare(src_path, gd_path, docx_path=None):
     s_chars = collections.Counter(norm_text(s_text))
     g_char_count = collections.Counter(norm_text(g_text))
     chars_missing = s_chars - g_char_count
-    checks["04_chars_missing"] = (0, sum(chars_missing.values()), not chars_missing)
+    # Google's importer rasterises shape text, so characters the .docx carries inside
+    # <w:txbxContent> are absent from its export. Charging them here says the ENGINE lost
+    # them; it did not (measured 26 Nov: deficit == box count exactly on 40 of 44, and the
+    # .docx is character-complete against the engine's own .txt on 53 of 53). Attribute the
+    # loss to the construct that causes it, keep it visible in detail, and leave 04 to say
+    # what its name says: a character the source draws that the document does not carry.
+    boxed = collections.Counter(norm_text(docx_box_text(docx_path))) if docx_path else \
+        collections.Counter()
+    rasterised = chars_missing & boxed
+    unexplained = chars_missing - rasterised
+    checks["04_chars_missing"] = (0, sum(unexplained.values()), not unexplained,
+                                  {"rasterised": sum(rasterised.values())})
```

`checks` values elsewhere are 3-tuples or 4-tuples with a `detail` dict (`18_displacement` at
`verify_google.py:5904-5907` is a 4-tuple with a detail dict), so a 4-tuple is the established shape.

**What this deliberately does not do:** compare the source against the `.docx` instead of the
export. That variant would hide `041122`'s 3,202 characters of Google-side loss and
`25_signature_block`'s 84, and would stop `04` describing what a Docs user sees. The attribution
above leaves `04` describing the file, and the Google-side loss charged once, by a check about the
construct.

**The signal must not disappear.** After this change no check charges "Google rasterised this text"
unless one is added or `59_shape_anchor` is extended to count box characters present in the `.docx`
and absent from the export. Landing only the `04` half would improve the score by 40 documents while
a Docs user still receives a picture of a footer. That is the failure mode this project's rules
exist to prevent, and it must be an explicit decision, not a side effect.

---

## 7. What the fix would do to the stored verdicts

- **Documents that go FAIL → PASS: at most 41, and 40 of those are count-identical today.** The 40
  in §4a flip if their deficit multiset is contained in their box multiset, which is what the count
  identity says. `411_nested_xobject_transforms` (2 missing, 23 box characters) is the 41st
  possibility. `academic-paper-ieee-2col-abstract` cannot flip on count alone — 2,506 > 2,505, so at
  least one character stays unexplained.
- **Documents that stay failing: at least 12** — the 9 with no shape text, plus the two
  `Account_Opening_Form` documents (3,329 and 3,334 missing against 5,502 box characters, so a
  residue survives unless the deficit is exactly the box text), plus `academic-paper`.
- **Documents that newly fail: 0, by construction.** The change only ever removes characters from
  `chars_missing` (`chars_missing & boxed` is a multiset intersection with `chars_missing`), so a
  document that passes today — empty deficit — has nothing to remove. This is the one part of the
  before/after that is provable without re-measuring.
- **The exact flip set is not measurable in this sandbox** (see §8). Stating a single number here
  would be inventing one.

---

## 8. The measurement that proves it, and the measurement that refutes it

**Proves it** (pure instrument re-score, no Google round trip, no JDK): re-run `verify_google.py`
with the patch over the **cached Google export PDFs** used to produce the 213 verdicts, and diff the
`04` verdicts against `benchmarks/gverify/`. Expected: 40 documents `FAIL → PASS`,
`detail.rasterised` equal to the document's box character count on all 44, **0 documents
`PASS → FAIL`**, the 9 shape-free documents unchanged. Any document that flips with
`detail.rasterised != box chars` was not the box text, and §4a's mechanism is not what it says.

**Refutes it**, any one of:
- a document that currently passes `04` while carrying `<w:txbxContent>` (measured: 0 of 142 today —
  if one appears, the separator is broken and the attribution is unsound);
- a document whose `detail.rasterised` exceeds its own box character count (impossible under the
  patch — the intersection is bounded by `boxed` — so this can only show up as a *mismatch* between
  `missing` and `box chars`, which is what the four non-identical rows in §4a already are);
- a document that flips to PASS while its `.docx` is measurably short of its **source PDF** by more
  than the residual — i.e. the `601_fillable_admission_form` control: its deficit (2) is not box
  text, it must keep failing after the patch, and LibreOffice agrees at 2;
- a fresh Google round trip on `27_two_column_left_short_txtpos` rebuilt at HEAD that shows any
  `04` loss at all — that document has no box today, so under this mechanism it must read 0.

**What the store should carry and does not:** `benchmarks/gverify/*.json` records `04` as
`{source, render, ok}` only — not the missing characters. The multiset identity §4a supports by
count therefore cannot be tested from the store, and no future run can falsify the mechanism from
committed data. `detail` with `rasterised` (as in the patch) plus a sample of the missing characters
would close that in one field.

---

## 9. What I could not test (INFERRED, not MEASURED)

**Rasterisation.** That Google's importer rasterises `<wps:txbx>` and the box's ink reappears as an
image is INFERRED: no Google export PDF exists here and there is no Google Docs access. What is
measured is the character-count identity; the rasterisation is the explanation, not an observation.
**The multiset.** That the missing multiset equals the box multiset on the 40 is INFERRED from
counts — the store does not carry the characters. **Provenance of `out/`.** That the emitted `.docx`
came from the build that stamped the store is INFERRED from three things: all 213 verdicts carry
`981ff1fa35e2cf67`, the repo HEAD fingerprints to `981ff1fa35e2cf67`, and
`27_two_column_left_short_txtpos`'s stored verdict (`04 = 0`) matches its emitted file (no box text).
**The leverage figure.** "11.9 clean documents" for `04` is **not stated** in any file I read;
`grep -rn "11\.9"` over `tools/p2w-bench/` returns unrelated numbers.

---

## 10. What the next run should do

1. Re-score `04` with the §6 patch against the cached Google exports; confirm 40 `FAIL → PASS`, 0
   regressions (§8), and land the rasterisation signal in the same change.
2. Retire or rename `04`'s `source` field — it is the literal `0` (`verify_google.py:4820`) and the
   59 rows read as if it were a source count.
3. The 9 shape-free documents (115 characters) are a separate, small class:
   `25_signature_block_underscores_txtpos` is 84 of them and reads `04 = 0` in LibreOffice, so its
   loss is Google-side and unexplained.

### Files and numbers used

Predicate `verify_google.py:4817-4820`; `norm_text` `345-361`; run extraction `231-249`, `4731-4734`;
the lead under test `FINDINGS/DOCS-ROOT-CAUSES-24NOV.md:99-160`. Verdict store `benchmarks/gverify/`
(213, engine `981ff1fa35e2cf67`); LibreOffice store `benchmarks/gverify-lo/` (213, older builds);
emitted files `out/*.docx` + `out/*.txt` (195 pairs); source PDFs `benchmarks/realworld/`,
`benchmarks/corpus-extra/` (124). `04`'s fields: `source` is the literal `0`, `render` is the
missing-character count, `ok` is the verdict.
