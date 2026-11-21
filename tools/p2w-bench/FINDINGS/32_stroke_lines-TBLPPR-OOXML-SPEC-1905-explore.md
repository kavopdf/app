# Making a table occupy zero flow space, so a `w:tcBorders` rule does not push the text below it

**21 Nov 2026 · read-only investigation · no engine file, no `tools/p2w-bench/` file, no corpus run, no Google measurement**

Question asked: what OOXML construct makes a table — or a bordered element — occupy **zero** flow
space, so that a rule can be carried by a cell border without pushing the following paragraph down.

The problem it answers is already measured and is not re-derived here: Google honours
`w:tcBorders`, a cell-border rule places exactly in x (`w:tblInd`) and in length
(`w:tblLayout="fixed"` + `w:tblGrid`), and the one thing still standing in the way is that a table
occupies flow space — `BELOW` at y=52.31 under a 1×1 table against y=14.07 with no table, ≈38 pt,
and `w:trHeight w:val="0" w:hRule="exact"` did not prevent it.

---

## 0. The answer in one paragraph

**`w:tblpPr` is the OOXML construct designed for exactly this**, and it is the only one that
gives *zero* rather than *small*. The spec says in as many words that a table carrying it is "not
part of the main text flow" and is "absolutely positioned". It is a child of `w:tblPr`, so it needs
no wrapper, no nesting and no frame, and the cell border stays a cell border — the construct that is
already measured to survive Google. What is **not** known is whether Google's `.docx` importer
honours it: it has never been measured through Google, `google_safe.py` does not list it (that list
is built from measurements, so absence is not evidence of support), and three independent
third-party importers either drop it outright or implement it only partially. That single unknown is
what the probe in §5 settles, in one export, in a way that cannot be misread.

---

## 1. `w:tblpPr` — the floating table

### (a) What the spec says

`w:tblpPr` (Floating Table Positioning) is a child of `w:tblPr`, ECMA-376 Part 1 §17.4.55–57
(numbering varies by edition). The normative description:

> "Floating tables are tables in a document which are not part of the main text flow in the
> document, and are instead absolutely positioned with a specific size and position relative to
> non-frame content in the current document.
>
> The first piece of information specified by the `tblpPr` element is that the current table is
> actually a floating table. This information is specified simply by the presence of the `tblpPr`
> element in table's properties. If the `tblpPr` element is omitted, the table shall not floating in
> the document."

— ISO/IEC 29500-1 §17.4.58, reproduced at
<https://learn.microsoft.com/en-us/previous-versions/office/developer/office-2010/cc845673(v=office.14)?redirectedfrom=MSDN>
and <https://webapp.docx4java.org/OnlineDemo/ecma376/WordML/tblpPr.html>.

A second sentence in the same description matters more than it looks:

> "Note that the table still has a logical position in the file (its location within the block-level
> elements in the document). This logical location shall be used to calculate the position of the
> table relative to a paragraph, using the next regular (non-table, non-frame) paragraph in the
> document."

That is the spec stating that the table's *logical* position is a marker, and that the paragraph
used as the geometric reference is **the next regular paragraph** — not a paragraph the table
displaces. It is the sentence that makes `vertAnchor="text"` meaningful.

The attributes, all of them, with the spec's own wording for the four that matter here:

| attribute | type | spec text |
|:--|:--|:--|
| `w:vertAnchor` | `ST_VAnchor` (`text`/`margin`/`page`) | base object for the vertical position; **default `page`** |
| `w:horzAnchor` | `ST_HAnchor` (`text`/`margin`/`page`) | base object for the horizontal position; **default `page`** |
| `w:tblpY` | `ST_SignedTwipsMeasure` | "an absolute vertical position … expressed in twentieths of a point … If this attribute is omitted, then its value shall be assumed to be 0." |
| `w:tblpYSpec` | `ST_YAlign` (`inline`/`top`/`center`/`bottom`/`inside`/`outside`) | "supersedes any value which is specified in the `tblpY` attribute … **unless the `vertAnchor` is set to `text`, in which case any relative positioning is not allowed, and is itself ignored**" |
| `w:tblpX`, `w:tblpXSpec` | as above, horizontal | same precedence rules |
| `w:leftFromText` `w:rightFromText` `w:topFromText` `w:bottomFromText` | integer twips | distance from surrounding text — this is the text-wrap clearance |

Full attribute table: <https://ooxml.org/wordml/w-tblppr/>, schema at
<https://www.datypic.com/sc/ooxml/e-w_tblpPr-1.html>.

Companion element `w:tblOverlap` (`never`/`overlap`, default `overlap`) governs only whether two
*floating tables* may overlap each other; it is ignored on an inline table
(<https://ooxml.org/wordml/w-tbloverlap/>).

### Is this the feature built for this problem?

**Yes, and it is the only one that is.** Three independent renderer/layout projects describe it in
exactly the terms the pipeline needs:

* "Floating tables (`w:tblpPr`, §17.4.57) are painted at their position … **take no room in the
  flow** and do not split" — <https://recursiveai.org/onedocument/docs/layout-tables/>
* "A top-level floating table now **stands at its position without taking room in the flow**, and
  the text after it wraps around it" — a merged fix in a Word-compatible editor, 71 of 382 corpus
  documents affected, <https://github.com/storytold/wordcraft/pull/137>
* "floating table — only wraps text for the paragraph that was active when the table was
  encountered. **Subsequent paragraphs clear below the table.**" —
  <https://docs.rs/dxpdf/latest/dxpdf/render/layout/float/enum.FloatSource.html>

That last one is the sharpest statement of the semantics and the one to design against: a floating
table reserves nothing *in* the flow, but the paragraph that follows it clears *below its bottom
edge*. So the flow cost of a floating table is not zero in the absolute sense — it is **the table's
own height**, which for a hairline carrier is one row of one border. That is a different quantity
from the ≈38 pt measured today, and it is the quantity the probe measures.

### Word-specific behaviour that constrains the encoding

Microsoft's implementation notes are normative in practice, because they say when Word discards the
element:

> "The standard does not specify any conditions under which `tblpPr` is ignored. Word ignores the
> `tblpPr` element if all attributes are omitted. It also ignores this element if the table is
> contained in a textbox, footnote, endnote, or comment, or if all of the following conditions are
> met: the `tblpX` attribute value is 0; the `tblpY` attribute value is 0; the `horzAnchor` attribute
> value is `text`; the `vertAnchor` attribute value is not `text`."

— [MS-OE376] Part 4 §2.4.54,
<https://learn.microsoft.com/en-us/openspecs/office_standards/ms-oe376/cb9c4d92-d57f-4b2c-ab2e-6200db92fd83>

Practical consequences, all of which the probe obeys:

1. **Never write `tblpX="0"` with `tblpY="0"` and `horzAnchor="text"`.** That is the documented
   discard pattern.
2. Word's *runtime* defaults differ from the spec's: the spec says `vertAnchor`/`horzAnchor` default
   to `page`, Word defaults to `margin` and `text`. **Write both attributes explicitly.**
3. `tblpYSpec` must not be used with `vertAnchor="text"` — it is ignored there (spec, quoted above).
4. Word clamps `tblpX`/`tblpY`/`*FromText` to 0…32767 where the spec allows any integer.
5. A floating table inside a text box, footnote, endnote or comment is ignored — so the
   "nested container" idea in §2 is doubly dead.

### (b) What I infer, not what the spec says

* **A full-width carrier table cannot wrap text sideways.** Text wrap is driven by the
  `*FromText` distances and the table's width. A carrier spanning the whole text column leaves no
  room beside it, so the wrap failure mode collapses to "the following line clears below it" — i.e.
  at most the carrier's own height. This is my reading of the wrap rules, not a quoted rule.
* **The failure that made the engine reject `tblpPr` does not apply to a hairline carrier.** The
  engine's own comment (`DocxWriter.java:5895`) records that floating *content* tables in Word and
  LibreOffice "wrap the flowing text AROUND it": on file 01 the `BILL TO` heading at x=64 was shoved
  to x=528, and on file 16 a sentence was squeezed into a five-line column. That is a **horizontal**
  wrap collision between a narrow table and adjacent text. A 1-row, 1-border carrier has a band one
  border wide and is not a content table; it cannot reproduce that geometry. **This is inference.**
  The residual risk it leaves — a text line that happens to fall inside the carrier's one-border-tall
  band being pushed — is real and is the second thing to measure (§6, NEEDS MEASUREMENT N2).
* **Google's importer is likely to be the weak link.** Google Docs has no table-wrapping feature in
  its UI, and the reporting on that is flatly contradictory: one 2023 guide states "Google Docs
  wraps text around an image or a drawing, **but not around a table**. A table always sits on its own
  lines" (<https://theguidex.com/resources/wrap-text-in-google-sheets-and-docs>), while a
  StackExchange answer claims "You can set a table to 'Wrap Text' now in Google Docs"
  (<https://webapps.stackexchange.com/questions/74870/>). A renderer with no native floating table
  has nothing to map `tblpPr` onto and will most likely drop it and lay the table out inline — which
  would reproduce today's ≈38 pt displacement exactly. **That is the kill condition, and it is what
  the probe detects.** It is also the same family as `wp:anchor`, which Google is *measured* to drop.

### (c) What is unknown

Whether Google honours `w:tblpPr` at all. **NEEDS MEASUREMENT** — see §5. There is no measurement of
it anywhere in this tree: `grep -rn tblpPr` over `app/` and `tools/p2w-bench/` returns the one engine
comment above, one `w:tblpPr: 0` count in a findings file, and nothing in `ATTEMPTS.json`. The
corpus documents that carry it (per the wordcraft measurement, roughly 19% of a general corpus) have
never been scored for it here.

---

## 2. The two container ideas

### 2a. A table inside a paragraph with `w:spacing w:line` exact

**Impossible by schema, so the question does not arise.** `w:tbl` is a block-level element. Its
permitted parents are `w:body`, `w:tc`, `w:sdtContent`, `w:ins`, `w:del`, `w:hdr`, `w:ftr` — and,
per the schema summary, "`w:tbl` cannot be a direct child of `w:p`"
(<https://ooxml.org/wordml/w-tbl/>). A table placed inside a paragraph is not merely ignored: Word
reports "Word experienced an error trying to open the file" and refuses the document
(<https://stackoverflow.com/questions/78644438/>). LibreOffice and Google are more permissive and
will open it — Google opened exactly that malformed file fine — so this is a construct that would
appear to work in the two lenient renderers and **fail to open in Word**, which is the worst possible
trade for a converter whose output people also open in Word.

The only way to get a table "inside" a paragraph-shaped container is a text box
(`w:txbxContent` inside `w:drawing`/`wp:anchor`). Google **drops the whole drawing** — measured, not
inferred: `FINDINGS/32_stroke_lines-google-drop-113048-9597.md` §2, two exports byte-identical in
their spans, 0 segments drawn with the drawing present. And `tblpPr` inside a text box is ignored by
Word by name. Dead twice.

### 2b. A nested table inside a cell of an outer zero-height row

**The outer container's height still counts, and nesting makes it worse, not better.** Reasoning:

* **(a) spec:** a row's height is `w:trHeight` under the rule `w:hRule`. With `auto` or `atLeast`
  the row "should be at least the value … regardless of its contents" and grows to fit content;
  a nested table is content, so it adds its own height. With `exact`, "the height of the parent
  object shall be exactly the value specified, regardless of the size of the contents … **If the
  contents are too large for the specified height, then they shall be clipped**"
  (<https://webapp.docx4java.org/OnlineDemo/ecma376/WordML/ST_HeightRule.html>). Clipping is the
  opposite of what a rule carrier wants.
* **(a) spec:** a zero-height exact row is not expressible in Word at all. See §3.
* **(b) inference:** if the outer row is clipped to a height below the nested table, the nested
  table's bottom border is the part most likely to fall outside the clip — so the border you are
  trying to draw is the first casualty. **Whether Word clips the nested table's *borders* along with
  its content is not stated in the spec.**
* **(b) inference:** even in the best case the outer row's minimum is not zero — it is bounded by
  cell padding and border widths (see §3), so nesting replaces one floor with two.

Verdict: nesting is not a route to zero. It is a route to "one more container, same floor, plus a
clipping hazard".

---

## 3. Can `w:tcBorders` render on a genuinely zero-height row?

This is the crux of why `w:trHeight w:val="0"` failed, and the answer is uncomfortable: **a
genuinely zero-height row is not a legal construct in Word, so no conformant `.docx` can ask for
one.**

### (a) What the spec and the implementation notes say

The standard permits it; Word does not:

> "The standard allows the `hRule` attribute to be set to `exact` while the `val` attribute is set
> to 0.
>
> — In Word, **if the `hRule` attribute is set to `exact`, then the `val` attribute must not be 0.**"

and, immediately after, the second half that explains the rest of the ≈38 pt:

> "The standard states that if the `hRule` is `exact`, the row height must be exactly as specified.
>
> — In Word, if the `hRule` attribute is `exact`, **Word sets the row height to the exact height
> plus the largest bottom cell padding of any cell in the row.**"

— [MS-OI29500] Part 1 §17.4.80,
<https://learn.microsoft.com/en-us/openspecs/office_standards/ms-oi29500/5919e0bd-e6ce-477e-8d66-0e5282f5c506>

Two consequences, both spec-backed:

1. `val="0"` + `hRule="exact"` is a value the standard allows and the dominant implementation
   rejects. A renderer that rejects it falls back to sizing the row to its content — which is
   exactly the measured ≈38 pt.
2. Even a *legal* exact row is **exact height + largest bottom cell padding**. So an exact row is
   never as short as its `trHeight` unless cell padding is zeroed too.

### (b) What I infer

* **The measured ≈38 pt is most likely the illegal `val="0"` being discarded, not a table minimum.**
  A discarded `trHeight` leaves a row sized to its content: one empty paragraph in the cell at the
  document default size, plus cell margins. ≈38 pt is the right order for that and is *not* the right
  order for "a table always costs 38 pt". This is a hypothesis that the probe prices directly
  (§5, ARM A), and it is the reason the probe includes an inline arm at all: if it is right, the
  whole problem may be solved without `tblpPr`.
* **A zero-height row would still draw its borders.** Nothing in the spec conditions border painting
  on row height; borders are properties of the cell edges and the row's grid edges are still
  coincident. In Word a row of exact height `h` draws its bottom border at `y+h`, and at `h≈0` the
  top and bottom edges coincide. **This is inference, and it is untestable as specified**, because
  §3(a) says you cannot express `h=0` in the first place. It is also moot for Google: the measured
  behaviour is that `val="0"` is ignored, so the row is never zero-height there either.

### The legal minimum

`w:trHeight w:val="1" w:hRule="exact"` — one twip, 0.05 pt — is legal (val ≠ 0), and this project
has already **measured that a positive exact `trHeight` is honoured by Google**: 55.83 pt rendered of
55.15 pt asked (`ATTEMPTS.json`, `18_displacement`, third probe). Combined with zeroed `w:tcMar` and
`w:tblCellMar`, that is a carrier whose flow cost should be ≈0.05 pt plus the border's own width,
against ≈38 pt today. It is not *zero*, but it is 0.05 pt, which is indistinguishable from zero at
any tolerance this bench uses. See §5 ARM A.

---

## 4. Any other OOXML mechanism that takes a bordered box out of flow

Checked, with a verdict on each:

| construct | takes a bordered box out of flow? | verdict |
|:--|:--|:--|
| `w:tblpPr` on `w:tblPr` | **yes, by design** — "not part of the main text flow" | **the answer**; Google support unmeasured |
| `w:framePr` on a paragraph, with `w:pBdr` | yes in Word — a text frame is out of flow | **dead**: `google_safe.py` lists `w:framePr` as ignored ("Google renders the paragraph as body text at the left margin"), shipped as 3.53.5 and broke every stamp |
| `w:txbxContent` in `w:drawing`/`wp:anchor` | yes in Word | **dead**: Google drops the drawing entirely — measured, 0 segments drawn, anchor left behind |
| VML `w:pict` / `v:shape` / `v:line` | yes in Word | **dead on the same evidence**; Google treats it as a drawing. The engine emits none (`grep` for `v:line`/`v:rect` returns nothing) |
| a table in the page **header** (`w:hdr`) | out of *body* flow, certainly | renders, but repeats on every page and cannot carry a per-rule y. Not a per-rule mechanism; noted and discarded |
| `w:tblOverlap` | no — it is a collision rule between floating tables | not a flow construct; only meaningful *with* `tblpPr` |
| `w:trHeight` exact, positive | no — but it can be made ≈0.05 pt | the **fallback** (§3) |
| `w:pBdr` on an empty 1 pt paragraph | no — costs the paragraph's line box | already known: construct honoured, **placement** is the blocker, not flow |

Nothing else in ECMA-376 positions a table or a bordered box outside the flow. The set is closed:
`tblpPr` for tables, `framePr` for paragraphs, `txbxContent`/VML for boxes — and two of the three are
on the measured-ignored list.

---

## 5. THE PROBE

One `.docx`, three pages, one Google export, one measurement of `BELOW`'s y on each page. It is
built and verified locally; the file is delivered alongside this report as
**`probe-flow-zero.docx`**.

### Layout

Each page carries exactly `ABOVE`, optionally the carrier, then `BELOW`, with `w:pgMar` top/left as
in the §2 control so the y numbers are comparable to 14.07.

| page | carrier | what it establishes |
|:--|:--|:--|
| 1 | **none** — the control | `BELOW` y with no table. This is the reference; the existing control read 14.07 |
| 2 | **ARM A** — inline 1×1 table, all six `w:tblBorders` `nil`, one `w:tcBorders/w:bottom single sz=8`, `tblInd=1000`, `tblLayout=fixed`, `gridCol=2000`, **`trHeight w:val="1" w:hRule="exact"`**, all `tcMar`/`tblCellMar` zero, cell paragraph at `sz=2` with `line=1 exact` | whether the ≈38 pt was the **illegal `val="0"`**. If page 2 ≈ page 1, the problem is solved with no floating table at all |
| 3 | **ARM B** — byte-identical carrier plus `w:tblpPr` with `vertAnchor="margin" horzAnchor="margin" tblpX="1000" tblpY="8000"` (400 pt down the page) and all four `*FromText` = 0, plus `w:tblOverlap w:val="overlap"` | whether Google honours `w:tblpPr` **and** takes the table out of flow |

ARM B parks the rule **400 pt below** where ARM A's rule sits. That is the trick that makes the probe
unambiguous: the rule's y and the flow's y are decoupled, so the two readings cannot be confused.

### Decision rule — read it before running, not after

| page 3 shows | verdict |
|:--|:--|
| a rule at y≈400 (x0 = 50 pt from the margin) **and** `BELOW` at the page-1 y | **PROVEN.** Google honours `w:tblpPr` and it takes zero flow space. Build the carrier on `tblpPr` |
| a rule at y≈400 **and** `BELOW` pushed to ≈400+ | honoured but *not* out of flow (following paragraph clears below the table). Then the cost is the carrier's own height — go to ARM A's numbers and pick the cheaper |
| a rule at ARM A's y (≈14) and `BELOW` pushed like ARM A | **KILLED.** Google dropped `tblpPr` and laid the table out inline. Fall back to ARM A |
| no rule at all on page 3 | **KILLED harder** — Google dropped the table with the float. Fall back to ARM A |

### Four traps, three of them hit while building this

1. **`vertAnchor="page"` / `horzAnchor="page"` is dropped.** Measured here through LibreOffice on a
   5-variant matrix: `page`/`page` fell back to inline (rule at the inline y, `BELOW` pushed +1 pt),
   while `margin`/`margin` and `text`/`text` floated correctly. The spec's own defaults are `page`,
   so **the naive encoding is the one that fails.** Write `margin` explicitly. (This is a
   LibreOffice-importer observation, i.e. a proxy; whether Google agrees is part of what the probe
   measures.)
2. **Child-element order inside `w:tblPr` is strict and a violation is silently fatal.** The first
   build of this probe put `w:tblBorders` after `w:tblLayout` and `w:tcMar` before `w:tcBorders`;
   LibreOffice then dropped the float without a word. Correct order is
   `tblStyle, tblpPr, tblOverlap, bidiVisual, tblW, jc, tblCellSpacing, tblInd, tblBorders, shd,
   tblLayout, tblCellMar, tblLook` in `tblPr`; `tcW, tcBorders, tcMar` in `tcPr`; `cantSplit,
   trHeight` in `trPr`. **A dropped float and a refused float look identical in the export — check
   the order before you conclude anything.**
3. **Do not write `tblpX="0"` with `tblpY="0"` and `horzAnchor="text"`** — Word discards the element
   on that exact combination (§1a).
4. **A `.docx` with a table inside a paragraph will not open in Word** (§2a) — do not "fix" a failure
   by moving the table into a paragraph.

### Proxy result already obtained (LibreOffice, **not** Google)

Built and rendered here, for the record, so the next run knows the file is structurally sound and
knows what the two arms *should* look like if the renderer cooperates:

| page | `ABOVE` y | `BELOW` y | rule |
|:--|--:|--:|:--|
| 1 control | 2.70 | **16.40** | none |
| 2 ARM A inline `trHeight=1` | 2.70 | **17.40** (+1.00) | `x0=122.00 y=14.20 w=100.00` |
| 3 ARM B floating | 2.70 | **16.40** (+0.00) | `x0=122.00 y=400.60 w=100.00` |

Read it for what it is: **a proxy, and a proxy that honours everything.** It confirms (i) the file
parses in a real renderer, (ii) `tblInd`+`fixed`+`gridCol` still give x0=122.00 (50 pt from the
margin) and w=100.00 exactly, (iii) `tblpY=8000` twips lands at 400.60 pt against 400.00 requested
(the 0.60 is the rule's own offset within the row, not a placement error), and (iv) with
`margin` anchors the floating carrier costs **0.00 pt** of flow while the legal minimal inline row
costs **1.00 pt**. It says nothing about Google, and must not be quoted as if it did — LibreOffice
honouring a construct is the exact situation that produced this whole class of defect.

---

## 6. Spec vs inference vs still unmeasured

### (a) Spec-backed, quoted
* `w:tblpPr` makes a table "not part of the main text flow", absolutely positioned, by presence
  alone; `vertAnchor`/`horzAnchor` select the base object; `tblpY` is a signed twips offset from it;
  `tblpYSpec` supersedes `tblpY` except under `vertAnchor="text"`.
* The table keeps a *logical* position, and the geometric reference is "the next regular
  (non-table, non-frame) paragraph".
* `hRule="exact"` + `val="0"` is legal per the standard and **forbidden by Word**; Word's exact row
  is "exact height plus the largest bottom cell padding".
* `hRule="exact"` clips content taller than the row.
* `w:tbl` cannot be a child of `w:p`; permitted parents are body/tc/sdtContent/ins/del/hdr/ftr.
* Word discards `tblpPr` on the `tblpX=0 + tblpY=0 + horzAnchor=text + vertAnchor≠text` combination,
  and inside a text box, footnote, endnote or comment.

### (b) Inference, mine, labelled
* A full-width carrier cannot wrap text sideways, so its only flow cost is its own height.
* The ≈38 pt is the illegal `val="0"` being discarded, not an inherent table minimum.
* A zero-height row would still draw its borders (untestable, since `h=0` is not expressible).
* Clipping an outer exact row removes the nested table's border before its content.
* Google's importer, having no table-wrapping model, most likely drops `tblpPr` and inlines the table.
* The engine's `tblpPr` rejection (text shoved sideways) does not transfer to a hairline carrier.

### (c) NEEDS MEASUREMENT
* **N1 — the probe in §5.** Does Google honour `w:tblpPr`, and is the floating table out of flow?
  This is the one that decides the question. One `.docx`, one export, one `BELOW`-y reading per page.
* **N2 — wrap collision in the real use case.** With the carrier at the y the PDF drew the rule —
  i.e. inside the text column rather than parked at 400 pt — does the line that falls in the
  carrier's one-border-tall band get pushed sideways or down? The §5 probe deliberately avoids this
  by parking the table below the text; it is the follow-up probe, and it is the failure mode that
  killed `tblpPr` for content tables in this engine.
* **N3 — vertical rules.** The measured vertical rule is carried by a `trHeight=1440` (72 pt) row and
  therefore costs 72 pt of flow. Under `tblpPr` the same 72 pt row placed absolutely should cost 0.
  Same probe, transposed; worth doing in the same export if the vertical rule matters as much as the
  horizontal one.
* **N4 — page-anchor support.** `vertAnchor="page"` is dropped by the LibreOffice importer. Whether
  Google drops it too is unknown, and it matters because `page` is the spec default and is the
  natural anchor for "the rule the PDF drew at y=312".

---

## Sources

* ISO/IEC 29500-1 §17.4.58 `tblpPr` — <https://learn.microsoft.com/en-us/previous-versions/office/developer/office-2010/cc845673(v=office.14)?redirectedfrom=MSDN>
* ECMA-376 `tblpPr` full text — <https://webapp.docx4java.org/OnlineDemo/ecma376/WordML/tblpPr.html>
* `w:tblpPr` attribute summary — <https://ooxml.org/wordml/w-tblppr/>
* `w:tblpPr` schema — <https://www.datypic.com/sc/ooxml/e-w_tblpPr-1.html>
* [MS-OE376] §2.4.54 `tblpPr` (when Word ignores it) — <https://learn.microsoft.com/en-us/openspecs/office_standards/ms-oe376/cb9c4d92-d57f-4b2c-ab2e-6200db92fd83>
* [MS-OI29500] §17.4.80 `trHeight` (val≠0 under exact; exact + bottom padding) — <https://learn.microsoft.com/en-us/openspecs/office_standards/ms-oi29500/5919e0bd-e6ce-477e-8d66-0e5282f5c506>
* `ST_HeightRule` (exact clips content) — <https://webapp.docx4java.org/OnlineDemo/ecma376/WordML/ST_HeightRule.html>
* `w:tblOverlap` — <https://ooxml.org/wordml/w-tbloverlap/>
* `w:tbl` parent elements / block-level rule — <https://ooxml.org/wordml/w-tbl/>
* Table inside a paragraph is invalid and Word refuses the file — <https://stackoverflow.com/questions/78644438/>
* Floating tables take no room in the flow — <https://recursiveai.org/onedocument/docs/layout-tables/>
* "stands at its position without taking room in the flow" — <https://github.com/storytold/wordcraft/pull/137>
* "subsequent paragraphs clear below the table" — <https://docs.rs/dxpdf/latest/dxpdf/render/layout/float/enum.FloatSource.html>
* Floating tables always wrap surrounding text — <https://www.nutrient.io/guides/document-authoring/page-layout/floating-tables-and-positioned-content/>
* Partial floating-table fidelity, next-paragraph anchoring — <https://www.docx-editor.dev/docs/2.x/docx-fidelity>
* Two importers that drop `tblpPr` outright — <https://tiptap.dev/docs/conversion/import/docx/convertkit>, <https://tiptap.dev/docs/pages/guides/pages-tablekit>
* Google Docs has no table wrapping — <https://theguidex.com/resources/wrap-text-in-google-sheets-and-docs>
* Contradicting claim, for completeness — <https://webapps.stackexchange.com/questions/74870/>
* ECMA-376 Part 1 (1st edition, PDF) — <https://web.mit.edu/~stevenj/www/ECMA-376.pdf>
