# What is pending, and what blocks each one

Written 18 Nov by the agent, not by a fixer run. Every item here was found by reading the
files, not by guessing, and each one names the command that closes it.

The short version: **nothing on this list can be closed without `java`.** The agent's sandbox
has no `java` and no `scipy`, so it cannot build the engine, cannot convert, and therefore
cannot measure. Every item below is a measurement or a build. They belong to a fixer run.

---

## 1. The cause census covers almost nothing

`tools/p2w-bench/CAUSES.md` opens with its own coverage line, and that line is the problem.
A cause table built from a sample sends a run at the wrong class.

**Close it with:**

    python3 tools/p2w-bench/cause.py --open --limit 25
    python3 tools/p2w-bench/cause.py --report

Run it against docx built by **this** engine. The census reads the rendered docx, so a docx
built by an older engine answers a question nobody asked.

---

## 2. The .docx ratchet cannot compare

    python3 tools/p2w-bench/ratchet.py --check
    DENOMINATOR DRIFT: rows claim x/59, the live instrument reports 47

The stored marks were stamped against 59 checks; `verify_google.py --list-checks` reports 47
today. The gate refuses to compare, which is correct behaviour and not a pass. A reset does
not help - the drift lives in the rows of `RESULTS.jsonl`, not in `RATCHET.json`, and a reset
was tried and changed nothing.

**Close it by re-measuring**, so every row is re-stamped against the live universe:

    python3 benchmarks/p2w.py --budget 250

Then `ratchet.py --check` has something it can compare.

---

## 3. RANKING.csv was published by a different path than the pipeline's own

The 19:12 report says this itself, in its own words:

> The corpus number is real but it was not produced by `benchmarks/p2w.py`. `p2w.py --budget 260`
> does not resume: it restarts `docx 0/213` on every call and spends the whole budget converting,
> so it measured **0 of 213 twice in a row**. The 212-document ratchet was run with
> `screen.py --docs` over the full `RANKING.csv` list instead... That is the same instrument
> `p2w.py` uses, but it is not the pipeline's own publisher, and the next run should confirm
> the two agree.

**What is already checked, and holds:** `RANKING.csv` has 212 rows, no duplicates, no document
in the baseline that is missing from the ranking and none the other way, and **0 documents
worse** than the 15 Nov baseline. So the table is complete and nothing regressed. What is not
checked is whether `p2w.py` would produce the same numbers.

**Close it with:**

    python3 benchmarks/p2w.py --budget 250      # repeat until it reports 213/213
    git diff benchmarks/RANKING.csv             # the two must agree, row for row

If they disagree, `p2w.py` is the publisher and its numbers win; find out why the other path
differed before trusting either.

---

## 4. `416_many_tiny_pages` has never been measured

300 pages in one command, no result written. It is the one document in `EXEMPT.json`, so it is
excluded from every count - but excluded is not measured, and a document nobody has looked at
is a document nobody knows the state of.

**Close it by measuring it alone**, so the per-command limit is not the thing that decides:

    python3 tools/p2w-bench/screen.py --docs 416_many_tiny_pages

If it still cannot finish, say so and leave it exempt. What is not acceptable is leaving it
exempt without ever having tried.

---

## 5. The documents themselves

    benchmarks/RANKING.csv           72 open of 212
    tools/p2w-bench/txt/RANKING-TXT.csv   64 failing of 213

The .txt has one lever worth more than the rest: **`t13_amount_columns` holds 30 documents, and
24 of those fail on nothing else.** One fix that clears that check takes the .txt from 64
failing to 40. The next-largest are `t02_position` (15) and `t12_word_invention` (15).

**No two checks in the .txt move together enough to be called one defect.** Measured on the
corpus: `t02_position` fails alone on 67% of its documents and `t08_line_order` on 50%, and the
two occur together on four. Naming them one cause would hide the second from whoever fixes the
first. `classify_txt.py` therefore names a cause for the set that actually failed.

---

## 6. The .txt setup is written and proved, and is not committed

The whole .txt measurement setup - baseline, marks, ratchet, class table, census, causes,
unmeasured record, `classify_txt.py`, `step_txt.py` - exists in the working tree and is proved
by seven hand-run cases:

    no marks                    -> exit 3, "an empty marks file proves nothing"
    marks present and held      -> exit 0
    a lowered mark              -> exit 1, and the document is named
    a fake universe sha         -> exit 3, both shas printed
    baseline after a scoring pass -> unchanged, byte for byte
    gate with marks missing     -> exit 3
    gate with the store empty   -> exit 3

**It IS committed as of 19 Nov.** It was held back for four days by a 403 that turned out to be the
Sarvam GitHub App missing from the `kavopdf` organization rather than a repository permission; the
app was installed and the work landed as commits 57a0507 and 199d611. The patch file is kept only as
a record of what changed. If you are reading this because a push failed again, check
`gh api /user/installations` first - an empty list means the app is gone, and no retry will help.

    git apply /scratch/saved/TXT-FULL-PARITY.patch

Nothing in it touches `app/`.

---

## What is not on this list, and why

* **`ReadingOrder.apply()` is not called by the app or by `ConvertOne`.** That is real, and it
  is not a defect: the stamp is written as an anchored box whose `positionH`/`positionV` are both
  `relativeFrom="page"`, so its place in the block list decides which page it attaches to and not
  where on that page it lands. Every stamp document scores the same with and without the pass.
  Do not wire it up to "fix" a side effect that is not happening - `SECTOR19.md` section 0.1.
* **The `.txt` scores are quotable.** `TXT-FALSIFIABILITY.md` carried a standing rule saying they
  were advisory because `t09_page_furniture` was blind. `t09` was fixed twenty minutes after that
  rule was written, re-tested, and now fails when a head is duplicated. The result is 12 of 12.
  The rule is withdrawn in that file, with its history, rather than deleted.

---

## The stamp method is proved in principle, NOT solved in practice. Read SETTLED.md first.

**This section is superseded.** The seven entries under "Stamps:" in `SETTLED.md` are the current state.
What changed since this section was written:

- **The six rules below are still correct** and still worth reading, but rule 1 ("the most common non-black
  colour among the drawings near the anchor") is **not enough** - a stamp's ink is a **set** of colours, and
  rule 1 breaks on any two-tone stamp.
- **"Solved and proved" is not true.** Colour cannot locate a stamp at all; three discriminators were measured
  and all three failed. The locator is geometric now: rotated text (14 of 16), an image (1), a closed tall
  path (1).
- **Five colour masks were built and all five failed.** They are listed in `SETTLED.md` so none is rebuilt.
- **The rect is the ink box, not the stroke's centre path** - that single line was every geometry error.
- **12_stamp_across_page_break is one stamp drawn across a page boundary**, at y -16.4 on page 1. Locating it
  works; rendering it needs stitching and is not built.
- **The count is 16, not 52.** The locator returns 52 candidates and includes rotated tables, page borders,
  photographs and callout boxes.

**Read `SETTLED.md` for the numbers. Read
`FINDINGS/STAMP-GENERAL-METHOD-OBJECT-IDENTITY-NOT-COLOUR-27NOV-agent.md` for the measurements.**

### The original section, kept for the rules that still hold

Written 27 Nov by the agent, after proving it end to end on one real document.

**Read `FINDINGS/STAMP-AS-ONE-IMAGE-FOUR-RULES-TWO-GATES-PROVEN-27NOV-agent.md` before touching
anything stamp-shaped.** It holds six rules, two gates, the corrections, and three approaches that
already failed. Re-deriving any of it costs a run.

**What is proved, on four structurally different stamps** (red 15 degree rectangular, green 15 degree
the other way, blue vertical, and a circular navy notary seal with curved text):

    position      dx +0.0, dy +0.0 pt on the seal, +0.4 / +0.6 pt on the 15 degree stamp
    size          within 0.4 pt
    ink           within 6 to 10 percent of the vector original
    shape         only the stamp is opaque; the corners of the box are transparent
    isolation     nothing but the stamp - measured foreign ink removed 553 / 748 / 1456 / 100 px
    Google        keeps it as one image with the alpha intact (smask present)

**The six rules, in one line each:**

1. stamp ink = the most common non-black colour among the drawings near the anchor
2. crop rect = the **union** of the drawings carrying that colour - **not** `wp:extent`; on one
   document the extent is 10.0 x 8.6 pt against a 76 x 76 pt stamp
3. pad the crop by `(max stroke width / 2) + 1 pt` - the union is the stroke's centre line
4. mask = colour distance under 160 **and** saturation at least `max(25, target x 0.45)`; without the
   saturation term dark body text comes through
5. emit **RGBA**, alpha = the mask; the interior stays transparent because all eleven stamp documents
   are unfilled
6. **every anchor whose rect lies inside the stamp's rect belongs to the stamp - textbox, shape or
   picture, every kind. Remove all of them, then place one image.**

Rule 6 is the one that bites. On `312_affidavit_stamp_paper` the stamp is **30 anchors**: 28 textboxes,
one per letter of the curved text, plus 2 shapes for the two circles. Removing only the textboxes leaves
an empty circle on the page. On `01_stamp_rotated_15deg_upright` it is one anchor. The kind does not
matter; the position inside the stamp's rect is the whole test.

**Do not retry, all measured and all failed:** rebuilding the stamp from XML (loses borders, rotation
and font), redacting non-stamp objects and rendering (a zero-height rule survives a degenerate
redaction rect, and `get_drawings()` misses content inside Form XObjects), 300 DPI, 600 DPI, binary
alpha, continuous alpha, and redact-then-render.

**What is not done, and is yours:**

1. **The count.** How many documents carry a stamp whose text Google rasterises is **not measured**.
   Four local classification attempts were all wrong - by counting `wps:txbx`, by stamp-like words, by
   whether words sit inside a textbox, and by comparing an export to the wrong docx. **The only
   reliable measure is one Google export per document and a check of whether the stamp words are
   extractable.** `stamp03.docx` against its matched export loses VERIFIED, AUDIT, INTERNAL and
   31-03-2026 while keeping every body-text probe, and carries 22 images against 0 in the source.
2. **A black stamp.** All eleven stamp documents are coloured. A pure black stamp has saturation 0 and
   rule 4 would keep nothing. There is none in the corpus to test a fallback on - do not write one.
3. **A filled stamp.** All eleven are unfilled, so the interior is transparent. If one ever carries a
   fill, rule 5 inverts for it. Also unproven, also not to be written blind.

**Close it by** applying the six rules to one stamp document, exporting to Google, and checking
position, size, ink and isolation against the source PDF - the same four numbers above. Then widen.

---

## The stamp method is now stated generally. Read this before any stamp work.

`FINDINGS/STAMP-GENERAL-METHOD-OBJECT-IDENTITY-NOT-COLOUR-27NOV-agent.md`

The short version, because it changes what a run should do:

**Do not build another colour mask.** Five were measured and every one failed, each differently, and the
reason is not tuning. Where two objects paint the same pixel the result is a blend, and a blend does not
record how much of each contributed. No threshold recovers information that was never in the image.

**Separate by object identity instead.** The PDF knows which object each pixel came from. Find the stamp
as a cluster of vector objects that is not part of the body text grid, then render **only those objects**
onto a blank page. The body text is not on that page, so nothing can blend. It is colour-blind, so it
holds for black stamps, multi-colour, semi-transparent, any shape, and stamps that are already raster or
are glyphs with no border.

**Step 2 is engine work** - PyMuPDF renders pages, not objects. PDFBox's `DrawObject` filter, MuPDF's
display list, or copying the operator subset into a fresh page. The standing rule keeps the engine out of
this work's hands, so this is a fixer task.

**The acceptance test is a proof, not a threshold:** render the page with the stamp's objects and again
without them; the difference must equal the image. No colour variant could ever pass it because they all
inferred the difference instead of measuring it.

Still proved and unchanged: the crop is the union of the stamp's drawings and its own text spans, padded
in **points** not pixels; every anchor overlapping the stamp rect belongs to it, of any kind; never
redact; RGBA, one floating anchor, `wrapNone`; position through a real Google export at 0.0 to 0.7 pt on
ten documents.

---

## Stamp work: the method is proved, two corrections are named and not yet run

`FINDINGS/STAMP-GENERAL-METHOD-OBJECT-IDENTITY-NOT-COLOUR-27NOV-agent.md` - read the last section first.

Object reconstruction was built as a proof of concept and measured through Google on four documents.
**The two that every colour mask failed on - 06 ghosted, 07 holed - are clean under it.** No ghost, no
hole, because the body text is not on the page the stamp is drawn on. That was the open question.

Two things are still wrong and both have a named fix, neither of which has been run end to end:

1. **Position and size drift a few points** because the reconstruction draws approximately. **Do not tune
   it.** Crop the rendered image to its own ink bbox and place that box at the stamp rect with the stamp
   rect's exact size - then the ink lands on the rect by construction.
2. **06's PAID comes out fully opaque against a source opacity of about 0.67.** `get_texttrace()` returns
   `alpha=None` for every span, so the opacity must be measured from the render: the coverage along the
   paper-to-ink line. **Use the median of covered pixels, not a high percentile** - a first attempt used
   the 90th percentile and the border's opaque pixels outvoted the text, returning 1.0 for everything.

**The engine should copy the stamp's operators into a fresh page rather than reconstructing from
`get_drawings()` and `get_text()`.** Reconstruction has now lost two things the API does not expose: the
text's alpha, and the exact stroke cap and join. Operator copying loses nothing.
