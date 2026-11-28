# PAGE OVERRUN — is `BREAK_WHEN_UNFITTABLE = false` the mechanism for the 21 one-page-longer documents?

**28 Nov 2026, analysis slot.** Read-only on `app/`: no file under `app/` was edited. Nothing deleted.

**Verdict, up front:** **No.** `BREAK_WHEN_UNFITTABLE = false` is **not** the mechanism. The overrun it
governs is a real but separate defect that touches a handful of pages; the 21 documents do not overrun
their box at all — they are the correct page count in the writer's own model *and* in a LibreOffice
render, and go one page long only inside Google Docs, which charges their anchored shapes for height the
writer never wrote. Measured on `350_question_paper`, a member of the 21: the page ends **81 twips
under** budget (`overTw=-81`), the fitter never reaches its third outcome (0 hits), and flipping the flag
to `true` changes the page count by **zero**.

---

## 0. What this run measured, and where

The task named the tree at `/scratch/work/CS`; that path was empty in this pod. The repo was cloned
instead from `kavopdf/app` at **HEAD `195af99`** ("release: fixer frees the slot") and the engine was
built here.

    engine fingerprint (regress.engine_fingerprint("docx"))  = a05b20eb05fe0fc8
    javac 17.0.21.1, pdfbox-android 2.0.27.0 (AAR from Maven Central), Android stubs from
    tools/engine-verify/stubs, LibreOffice 7.4.7.2

`a05b20eb05fe0fc8` is **the same engine** that stamped `350_question_paper`'s refusal in
`benchmarks/gverify/350_question_paper.json` (`engine: a05b20eb05fe0fc8`, `at: 2026-11-27T12:47:49`), so
the Google number and the local number below describe the same build of the engine. That is the whole
reason the comparison is admissible.

The 213-PDF corpus is **not** in the tree, so the sample is drawn from the corpus PDFs that are in it
(`tools/engine-verify/real/pdfs/`, `benchmarks/realworld/`, `benchmarks/corpus-extra/`). One of them,
`350_question_paper`, is a member of the 21.

---

## 1. The flag — exact location and what `false` does

    app/src/main/java/com/kavopdf/app/engine/DocxWriter.java:371
        private static final boolean BREAK_WHEN_UNFITTABLE = false;

It is read in exactly one place, the fitter's third outcome:

    app/src/main/java/com/kavopdf/app/engine/DocxWriter.java:674-680
        // 3. the page is full and cannot be squeezed any further. See
        // BREAK_WHEN_UNFITTABLE: by default the line keeps its own height and the page overruns
        // exactly as it did before this guard existed ...
        if (BREAK_WHEN_UNFITTABLE && ctx.flowTw > 0) return null;   // :678
        ctx.flowTw += lineTw;                                       // :679
        return new int[]{0, lineTw};                                // :680

The fitter has three outcomes for a line that does not fit (`DocxWriter.java:655-680`):

| | condition | line | what happens |
|---|---|---|---|
| 1 | the gap can be given up | `:660-666` | gap shrinks, line keeps full height |
| 2 | `room >= ascent` (`:669`) | `:669-672` | box shortened to what is left, `ctx.fitted++` (`:671`) |
| 3 | `room < ascent` (`:674`) | `:678-680` | **flag false → `ctx.flowTw += lineTw`, line keeps its true height and the page's flow goes past `budgetTw`.** Flag true → `return null`, the caller writes a deliberate page break (`breakPage`, `:696-710`, `ctx.brokePage++`) |

So when the flag is `false`, the third outcome spends the page's budget past its own limit and returns a
line at full height. That is the "page overruns its box" the lead describes. **The code path is real. The
question is whether it is reached on the 21.**

---

## 2. Is the overrun counted today? — **No. Nowhere.**

| place a number could be kept | what is actually there | counted? |
|---|---|---|
| `Ctx` (`DocxWriter.java:779`) | `int fitted` (`:1009`), `int brokePage` (`:1011`) — outcome 2 and the deliberate break. **No field for the overrun.** | no |
| `Ctx` → out | `Stats` (`:723-729`) carries five fields: `zeroGap`, `zeroGapAnchored`, `zeroGapInCol`, `zeroGapNoRoom`, `zeroGapWorstPt` (`:739-744`). No overrun field. | no |
| `PdfToWord.Report` (`PdfToWord.java:743-775`) | `pages, paragraphs, tables, images, ocrPages, skippedPages, imagesFailed, imagesRecovered`, the five `zeroGap*` (documented as no longer written), and `notes` | no |
| `Report.notes` | `notes.add(...)` appears three times, all in `PdfToWord.java` (`:920`, `:985`, `:1014`) and all about pages/text layers. **No overrun note is ever added.** | no |
| the only place `overTw` exists | `DocxWriter.java:1353-1354`, inside `if (System.getProperty("p2w.debugFlow") != null)` — a `System.err.println` | no |

`overTw` occurs **once** in the whole tree (`grep -rn overTw app/src/main/java tools/ benchmarks/` →
`DocxWriter.java:1354` plus documents describing it). It is a debug print, never a value.

And the harness does not even collect the counters that do exist: `ConvertOne.java:36` calls
`DocxWriter.write(...)` and **discards** the returned `Stats`; `ConvertAll.java:77-97` prints the five
`zeroGap*` fields and nothing else. `tools/p2w-bench/ENGINE-FLAGS.md:66` states of `-Dp2w.debugFlow`:
"**Nothing in p2w-bench or benchmarks passes it.**"

**So the second half of the lead is correct: an overrun is unobservable in the pipeline.** That is a real
instrument gap. It is just not the explanation for the 21.

---

## 3. The 21 document ids

The population is the pending item's: 23 `page_count_refused` documents in the 24 Nov census, of which
21 are one page long and 2 are five pages long. Ids below are parsed from the table in
`tools/p2w-bench/FINDINGS/00_page_count-23-REFUSED-ALL-ENGINE-0-CLEAN-24NOV-agentB.md` §2, taking every
row whose Google page count is `src + 1` (21 of 23 rows; the two `+5` rows are the bank forms and are
excluded).

    the 21 (all: source 1 page, Google 2 pages)

     405_sheet_music_lyrics               341_shipping_manifest
     333_datasheet_spec_tables            60_page_border
     326_itr_computation                  332_bom_on_drawing
     305_vaccination_certificate          350_question_paper
     314_tender_rfp_boq                   401_trifold_brochure
     320_balance_sheet_statutory          390_wide_data_appendix
     403_crossword_puzzle                 price-list-2col-dense-right-aligned
     353_admit_card                       bank-statement-horizontal-rules-only
     402_calendar_month_grid              boq-horizontal-rules-only
     361_product_catalogue_grid           351_omr_answer_sheet
     05_round_company_seal_curved_text

    excluded (+5 pages): 041122-Account_Opening_Form, Account_Opening_Form_Fillable_filled

**Provenance caveat, stated plainly.** This is a **24 Nov snapshot**. The live store
(`benchmarks/gverify/*.json`, 214 files) now holds only **8** refusals, because documents were
re-measured since; 6 of those 8 are `+1` (`05_round_company_seal_curved_text`, `350_question_paper`,
`401_trifold_brochure`, `60_page_border`, `itr-computation-with-slab-table`,
`Prakashan_Print_Fidelity_Handbook`), 2 are `+2` (`041122-Account_Opening_Form`,
`Account_Opening_Form_Fillable_filled`). The class has never been re-censused to 21 at HEAD, so the list
above is the population the lead was written about, not a fresh count.

---

## 4. The sample — two independent page counts each

Method, per document: convert with the engine built here, render the `.docx` to PDF with LibreOffice,
then count pages with **two independent readers** — `pypdf` and poppler's `pdfinfo` — on both the source
PDF and the render. Google's count is read from the store, same engine.

| document | in the 21? | source: pypdf / pdfinfo | .docx→LO render: pypdf / pdfinfo | Google (store) | engine stamp |
|---|---|---|---|---|---|
| `350_question_paper` | **yes** | **1 / 1** | **1 / 1** | **2** | `a05b20eb05fe0fc8` |
| `041122-Account_Opening_Form` | no (+5 form) | 9 / 9 | 10 / 10 | 14 | `a05b20eb05fe0fc8` |
| `Prakashan_Print_Fidelity_Handbook` | no (refused, +1) | 10 / 10 | 11 / 11 | 11 | `a05b20eb05fe0fc8` |

Every pair agrees exactly, so each count is the same number read by two tools rather than one tool's
opinion. The `.docx` carries **no page-count metadata to cheat with**: `appXml()` (`DocxWriter.java:7844-7848`)
writes `<Application>KavoPDF</Application>` and no `<Pages>`, so a page count can only come from a
renderer.

**The line that decides the question.** On `350_question_paper` — a member of the 21, and the document
the flag's own javadoc names as the worst case needing "1.21 times the paper's height" — the writer's
per-page telemetry says:

    FLOW page=1 flowTw=16755 budgetTw=16836 overTw=-81 needTw=16755 writtenTw=16740 overheadTw=0 f=1.0
    FLOWDOC 350_question_paper.docx fitted=0 broke=0

`overTw = -81`: the page ends **81 twips (4.05 pt) inside** its budget. `fitted=0` and `broke=0`: neither
the squeeze nor a deliberate break fired. **The page does not overrun, so outcome 3 was never reached, so
the flag had nothing to decide.** The javadoc's 1.21× figure is stale — it was measured on the 208-corpus
engine, not on `a05b20eb05fe0fc8`.

`Prakashan_Print_Fidelity_Handbook`: every page `overTw <= 0`; one `UNFIT-HIT` on page 8
(`room=-2269 ascent=118`) fired inside a **discarded attempt** — the page that was actually written used
the squeeze (`f=0.85`, `overheadTw=3506`) and `broke=0`. Google still adds a page (11 vs 10).

`041122-Account_Opening_Form`: 1 of 9 pages overruns — page 7, `overTw=200` (10 pt). That is the only
genuine overrun in the sample, and it is on a document that is **not** one of the 21; it also cannot
explain that document's Google `+5`.

---

## 5. The controlled A/B — flip the flag and re-measure

A copy of the engine sources was made **outside `app/`** (in `/scratch/work/variant`), the constant was set
to `true` there, and one line was added to print each third-outcome hit. `app/` was not touched
(`DocxWriter.java:371` still reads `false`; `git status` clean). Same three documents, same build flags:

| document | pages, `BREAK_WHEN_UNFITTABLE=false` | pages, `=true` | third-outcome hits with the flag on | `broke` |
|---|---|---|---|---|
| `350_question_paper` | 1 | 1 | **0** | 0 |
| `041122-Account_Opening_Form` | 10 | 10 | **0** | 0 |
| `Prakashan_Print_Fidelity_Handbook` | 11 | 11 | 1 (discarded attempt) | 0 |

**Turning the flag on moved the page count on none of the three, including the one document in the sample
that is in the 21.** The flag cannot be the mechanism for a page count it does not change.

This agrees with the flag's own javadoc (`DocxWriter.java:355-370`), which measured the toggle over the
corpus: pages left over the paper go "from 4 to 3", and it *costs* two "pages 1 -> 2" counts rather than
buying any. A flag whose best measured effect is 4 overrunning pages, and whose enabling makes two
documents go one page long, cannot be the source of 21.

---

## 6. What the mechanism actually is (as far as the record measures it)

Not established by this run — the 21 documents' PDFs are not in the tree, so this run could not convert
them. What the record already measured, and what this run's numbers are consistent with:

* The 21 are **1 page in LibreOffice and 2 in Google** — i.e. the `.docx` is the right length for a
  renderer that honours the writer's own geometry, and one page long only for Google. This run reproduces
  the LibreOffice half on `350_question_paper` (1/1) against Google's 2 on the same engine.
* The record's controlled probe (`00_page_count-23-REFUSED-ALL-ENGINE-0-CLEAN-24NOV-agentB.md` §3):
  `60_page_border`, **same 689 characters, same LibreOffice page count** — 62 `wp:anchor` shapes → **2
  Google pages**; 0 shapes + `w:pgBorders` → **1 Google page**. Google charges the flow for
  page-positioned floating shapes.
* The size of that charge, measured over 19 documents: **0.10 to 0.96 pt per anchor, median 0.57 pt**.

So the mechanism is an **anchored-shape height charge Google makes and the writer never wrote**, not a
line the writer placed past its box.

---

## 7. Verdict, one line

**`BREAK_WHEN_UNFITTABLE = false` is not the mechanism:** the 21 do not overrun their box (350_question_paper:
`overTw=-81`, 0 third-outcome hits), the flag's toggle changes none of the sampled page counts, and the
extra page exists only in Google, which bills the documents' anchored shapes — the overrun is a separate,
smaller defect that is genuinely uncounted.

---

## 8. Two things worth carrying forward (not fixes, observations)

1. **The uncounted overrun is still an instrument gap**, exactly as the lead says — `Ctx` has no overrun
   counter, `Stats` has no overrun field, `Report.notes` never receives one, and `overTw` exists only
   behind `-Dp2w.debugFlow`, which no tool passes. Counting it is cheap and changes no layout. It just
   will not move the 21.
2. **`ENGINE-FLAGS.md:67-68` states "The extra page on 21 documents is that number"** — that sentence is
   refuted by the measurement in §4: on a member of the 21, that number is `-81`.

## Reproduction

    # build
    cd tools/engine-verify
    curl -sSL -o libs/pdfbox.aar https://repo1.maven.org/maven2/com/tom-roush/pdfbox-android/2.0.27.0/pdfbox-android-2.0.27.0.aar
    (cd libs && mkdir -p aar && cd aar && unzip -oq ../pdfbox.aar)
    javac -d out $(find stubs -name '*.java')
    CP="out:libs/aar/classes.jar:libs/aar/assets:<bcprov,bcpkix,bcutil jars>"
    javac -nowarn -cp "$CP" -d out $(find ../../app/src/main/java -name '*.java') ConvertOne.java

    # convert, with the writer's own per-page telemetry
    java -Dp2w.debugFlow=1 -cp "$CP" ConvertOne real/pdfs/350_question_paper.pdf <outdir>

    # two independent page counts
    soffice --headless --convert-to pdf --outdir <renderdir> <outdir>/350_question_paper.docx
    python3 -c "from pypdf import PdfReader; print(len(PdfReader('<renderdir>/350_question_paper.pdf').pages))"
    pdfinfo <renderdir>/350_question_paper.pdf | grep Pages
