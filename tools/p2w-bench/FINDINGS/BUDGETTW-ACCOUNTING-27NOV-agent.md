# `budgetTw -= pageTopTw`: the page-room arithmetic, measured from the source PDFs

**27 Nov 2026, research slot.** Claim, method, numbers, verdict, and what would overturn it.
Everything under **Measured** was read out of the corpus PDFs in this run; everything under
**Inferred** is reasoning over those numbers and the repository's own records, and is labelled.

---

## 1. Claim under test

The withdrawn commit `aa496ebe` moves a page's top gap out of the first paragraph's `w:before`
and into the section's `w:pgMar w:top` (`tools/p2w-bench/PATCHES/aa496ebe-pagetop-not-identity.patch`),
while deliberately leaving the flow's accounting alone — `ctx.budgetTw` is still set from the paper
height alone, `DocxWriter.java:1172`:

```java
ctx.budgetTw = (int) Math.max(1L, Math.round(ph * TWIPS_PER_PT) - PAGE_ROUNDING_TW);
```

If the reader does not spend space-before at a page top, that margin is **net-new offset**: the page's
usable height falls by `G = pageTopTw`, while the budget the engine believes it has does not. The
proposed accounting fix, written in the repository at
`tools/p2w-bench/FINDINGS/18-DISPLACEMENT-PATCH-IS-NOT-IDENTITY-26NOV.md:59`, is

```java
ctx.budgetTw = max(1, round(ph*TWIPS_PER_PT) - PAGE_ROUNDING_TW - max(0, ctx.pageTopTw));
```

**The arithmetic this run was asked to supply:** for each deciding document, with `G` the page-top
margin the patch sets and `slack` the distance from the page's lowest ink to the paper's bottom edge,

| condition | prediction |
|:--|:--|
| `slack >= G` | the page still fits on one sheet |
| `slack < G`  | the last `G` of the page falls to a second sheet |

---

## 2. Method

**Measured.** Corpus unzipped flat from the `corpus-v1` release assets (211 PDFs, `/scratch/work/p2w/corpus`),
read with PyMuPDF. Per document, page 1:

* **page height** `H` = `page.rect.height` (media, crop and rect boxes agree on all eight; rotation 0
  on all eight).
* **lowest ink** = `max(text span bbox y1, page.get_drawings() rect y1, page.get_image_info() bbox y1)`.
  The text-only and drawing-only bottoms are reported separately, because on four of these documents
  the deepest object is a full-bleed fill that reaches the paper edge and on one it is a drawing
  outside the paper entirely (see §4).
* **slack** = `H − lowest ink`; **slack60** = `H − 60 − lowest ink`.

**`G`, recomputed from the PDF, not guessed.** The patch's own expression
(`sectionTopTw`, in `aa496ebe-pagetop-not-identity.patch`) is the smallest over all pages of

    round( (baseline of the page's first non-empty line  −  LINE_BASE * hairlinePt(size)) * 20 )

with `LINE_BASE = 0.8f` (`DocxWriter.java:214`), `hairlinePt = min(0.069*size, 0.6485)`
(`DocxWriter.java:4113`, `:107`), `TWIPS_PER_PT = 20` (`:52`) and the cap `max(2000, round(ph*20))`.
This run reproduces exactly that expression from the PDF's topmost non-empty span per page.

**Method validation — 6 of 6.** The expression was checked against every `w:pgMar w:top` this
repository has already read out of an emitted `word/document.xml`:

| document | `pgMar` measured in emitted XML | this run, from the PDF |
|:--|--:|--:|
| `newsletter-3col-header-footer` | 1200 | **1200** (60.00 pt) |
| `601_fillable_admission_form` | 1230 | **1230** (61.50 pt) |
| `401_trifold_brochure` | 1190 | **1190** (59.50 pt) |
| `412_page_labels_roman` | 1227 | **1227** (61.35 pt) |
| `416_many_tiny_pages` | 1790 | **1790** (89.50 pt) |
| `bank-statement-5-pages` | 55.15 pt (patch comment) | **1103** (55.15 pt) |

XML values from `tools/p2w-bench/FINDINGS/18-displacement-PGMAR-TOP-DOUBLING-FOUND-AND-FIXED-GATE-WANTS-REMEASURE-26NOV-relay.md:17-22`
and `:49`. Six exact hits on six documents, so the PDF-side `G` in the table below is the number the
patch would write, and no other value needs to be assumed.

---

## 3. Numbers

All lengths in points. `G` in twips and points. `deficit = G − slack`; a negative deficit means the
page has that much room to spare.

| document | pages | H | lowest ink | what the lowest ink is | slack | slack60 | `G` (tw / pt) | deficit | one page? |
|:--|--:|--:|--:|:--|--:|--:|--:|--:|:--|
| `itr-computation-with-slab-table` | 1 | 841.89 | 969.15 | stroke drawn **outside** the paper (text alone 842.21) | **−127.26** | −187.26 | 1057 / 52.85 | **+180.11** | **OVERFLOW** |
| `newsletter-3col-header-footer` | 1 | 841.89 | 841.89 | footer band fill, to the paper edge (text alone 823.62) | **0.00** | −60.00 | 1200 / 60.00 | **+60.00** | **OVERFLOW** |
| `600_reviewed_invoice_with_annotations` | 1 | 842.00 | 418.93 | red annotation rectangle | 423.07 | 363.07 | 1190 / 59.50 | −363.57 | **FITS** |
| `601_fillable_admission_form` | 1 | 842.00 | 528.00 | form rule | 314.00 | 254.00 | 1230 / 61.50 | −252.50 | **FITS** |
| `401_trifold_brochure` | 1 | 595.28 (landscape) | 595.28 | full-bleed side panel (text alone 543.63) | **0.00** (text 51.64) | −60.00 | 1190 / 59.50 | **+59.50** (+7.86 vs text) | **OVERFLOW** |
| `39_small_caps_letter_spacing` | 1 | 841.89 | 807.62 | last text line | 34.27 | −25.73 | 1319 / 65.95 (or 1310 / 65.50, see note) | **+31.68** | **OVERFLOW** |
| `350_question_paper` | 1 | 841.89 | 837.32 | last text line | 4.57 | −55.43 | 710 / 35.50 | **+30.93** | **OVERFLOW** |
| `bank-statement-5-pages` | 5 | 841.89 | 817.81 | last text line | 24.08 | −35.92 | 1103 / 55.15 | **+31.07** | **OVERFLOW** |

Per-page detail (measured): `bank-statement-5-pages` carries the identical `G` and the identical lowest
ink on all five pages — `G = 1103 tw`, ink bottom 817.81 on pages 1–5, so the deficit is 31.07 pt on
every sheet, not only the first. The other seven documents are one page each, so page 1 is the page.

Note on `39_small_caps_letter_spacing`: its first line carries two spans on the same baseline, one at
size 11.7 and one at size 1.0. `hairlinePt` clamps at 0.6485 for the first and gives 0.069 for the
second, so `G` is 1310 or 1319 tw depending on which span the engine's `Box` keeps. The conclusion is
the same either way: 65.5–66.0 pt against 34.27 pt of slack.

Note on `401_trifold_brochure`: its lowest ink is a page-height panel fill. `G` is 59.50 pt and the
text alone leaves 51.64 pt, so the page is over by 59.50 pt on the ink reading and 7.86 pt on the text
reading. Both readings say overflow.

Budget after the fix, for reference (`round(H*20) − PAGE_ROUNDING_TW − G`, `DocxWriter.java:377`):
itr 15779, newsletter 15636, 600 15648, 601 15608, 401 10714 (11904 if the guard zeroes it), 39 15517,
350 16126, bank-statement 15733 twips.

---

## 4. Per-document reading

**`newsletter-3col-header-footer` — the arithmetic is decisive, and it is worse than 3 pt.**
The lead's figure is *"content reaches y=785 of 842 with a 60 pt margin, 3 pt short"*. 785.20 is
measured, but it is the **top edge** of the footer band: the band is a filled rectangle from y=785.20
to y=841.89 — the paper edge (`type=f`, 6.7 % of the page). The lowest ink is therefore 841.89, not
785.20, and the page has **zero** slack, not 57 pt. Against `G = 60.00` the deficit is the full 60 pt,
not 3.3. The document is a full-bleed three-column newsletter whose bottom band cannot be pushed down
at all, which is consistent with the measured `0.20 → 86.30` and with "page 1 kept only the top band,
0 dark px in the masthead band against 105 094 in the source"
(`18-DISPLACEMENT-PATCH-IS-NOT-IDENTITY-26NOV.md:44`).

**`itr-computation-with-slab-table` — the question is not well posed on this document.**
Its source page 1 does not fit its own paper: the text runs to y=842.21 on an 841.89 pt sheet (0.32 pt
past the edge), and its table frame is stroked to y=969.15 — 127 pt below the paper, clipped by the
page box. Slack is −127.26 pt against `G = 52.85`, so the page was over capacity before the patch,
after the patch, and after the fix. Any correct engine must break this page somewhere. What the
arithmetic *does* say is that the fix removes 52.85 pt of budget from a page that is already over:
under the patch alone the break moves `G` (52.85 pt) earlier than baseline; under patch + fix it moves
`2G` (105.7 pt) earlier. There is no monotone reason for that second shift to preserve the 9.10.

**`600_reviewed_invoice_with_annotations` and `601_fillable_admission_form` — they fit, and they still
moved.** 423 pt and 314 pt of slack against 59.50 and 61.50 pt of margin. Overflow cannot be their
mechanism. Their `+8.16` and `+2.93` are the *displacement* half of the patch (the first block moves by
`G`, or by `2G` where the page opens with a `w:tbl` and the reduction never reaches the paragraph), and
the accounting fix does not touch displacement. The repository already measured exactly this: with
change 1 alone, "601 stays 55.32 and 401 stays 0.79"
(`18-DISPLACEMENT-PATCH-IS-NOT-IDENTITY-26NOV.md:64`).

**`401_trifold_brochure` — the fit test fires, the guard is what saves it.** Deficit 59.50 pt (or 7.86
pt on the text reading), so the page would overflow — and under `aa496ebe` as published it did worse
(0.03 → 0.79) by the doubling (pgMar 1190 **plus** first `w:before` 1790, a 2980 tw gap where the
source has 1790). The guarded patch makes 401 byte-identical by returning `G = 0`
(`18-displacement-PGMAR-TOP-DOUBLING-FOUND-AND-FIXED-GATE-WANTS-REMEASURE-26NOV-relay.md:26-35`), and
the accounting fix would then subtract nothing.

**`39_small_caps_letter_spacing`, `350_question_paper`, `bank-statement-5-pages` — the test fires, the
record says they did not move.** Deficits of 31.68, 30.93 and 31.07 pt. `39` moved only +0.10 and
`350`/`bank-statement` moved 0.0000. **Inferred:** those three are documents where `sectionTopTw`
returns 0 — `350` opens with an inline picture (see `FINDINGS/00_page_count-350-INLINE-PICTURE-CARRIES-THE-LINE-1120-agent.md`),
`bank-statement-5-pages` opens on a ruled table, and the guard returns 0 for a page whose first block
is a `w:tbl`, a shape or a pinned paragraph, writing the identity byte for byte. `401` is the
repository-measured example of exactly that guard. If that inference is right, `G` for these three is
never written and the deficits above are counterfactual; if it is wrong, three documents should have
overflowed by ~31 pt and did not, which would falsify the test.

---

## 5. Verdict

**Does the accounting fix predict `newsletter` staying at ~0.20? Yes — and the arithmetic is exact,
not approximate.** The band's lowest ink is at the paper edge, slack 0.00, and the margin the patch
adds is 60.00 pt. Subtracting exactly `G` from the budget removes exactly the room the margin took, so
the flow's break lands past the band instead of 60 pt before it. This is also measured rather than
inferred: "Change 1 alone was measured: newsletter **86.30 → 0.20**, back to one page with the band
restored" (`18-DISPLACEMENT-PATCH-IS-NOT-IDENTITY-26NOV.md:63`).

**Does it predict `itr` keeping its gain? No — the arithmetic does not reach that, and what it does say
is unfavourable.** `itr`'s source page already overruns its own paper by 127 pt of drawing (0.32 pt of
text), so "does it fit" has no answer on this document; the fix takes 1057 tw (52.85 pt) off a page
that is already over budget, moving the break to `2G` earlier than baseline rather than `G`. Whether
that leaves 9.10, improves it, or returns it toward 42.33 is **not derivable from page geometry** — the
gain came from a pagination change, and the second pagination change is a different point on the same
curve. It must be measured.

**So the honest form of the verdict is: the fix is supported for the document it was written for and
unproven, at some risk, for the document the patch was almost reverted for.** Three of the eight
deciding documents (`600`, `601`, `401`-guarded) are not overflow cases at all, so no budget arithmetic
can restore them; one (`newsletter`) is fully explained; four (`itr`, `39`, `350`, `bank-statement`)
have the fit test firing, of which one is a source that cannot fit any paper and three are probably
identity documents where `G` is never written.

---

## 6. Where the arithmetic is not available

1. **Which documents actually received a non-zero `w:pgMar w:top`.** `G` is a property of the PDF; the
   *written* margin also depends on `sectionTopTw`'s guard (first block must be a non-pinned `Para` or
   a `Box` with text) and on `sb.indexOf("<w:body><w:p")`. This run can compute `G` for all eight but
   cannot see which of the eight the guard zeroed without emitting `document.xml`. That is the one
   missing input, and it decides whether `39`, `350` and `bank-statement` are counterfactual rows.
2. **`itr`'s pagination.** The source overruns its paper; the arithmetic cannot say where a correct
   engine breaks it, and the metric's treatment of ink that has no source counterpart is not something
   page geometry can answer.
3. **A live conflict in the records.** The brief states all 20 multi-page documents moved 0.0000,
   while the patch's own comment reports `bank-statement-5-pages` measured through Google on 22 Nov as
   "pages 1-4 −59.5 pt → −4.3 pt, page count unchanged at 5, 37/42 → 40/42". Both cannot describe the
   same engine. One is stale; this run cannot tell which, and the difference matters because a
   multi-page document that really did move 55 pt per continuation page is the largest overflow
   surface the patch has.
4. **The 60 pt bottom margin** in the brief is not a property of these PDFs — all eight carry
   `w:pgMar w:bottom="0"` (`DocxWriter.java:2448`) and the source pages draw to the edge. `slack60` is
   reported because it was asked for, but the operative comparison is `slack` against `G`.

---

## 7. What would overturn this

* **`itr` scored with change 1 alone.** If it still reads ~9.10, §5's risk is dead and the fix is
  clean for all seven moved documents. If it reads near 42.33, the fix trades the newsletter for the
  itr gain and the patch must not land with change 1 only.
* **`pgMar` read out of the emitted `document.xml` for all eight** (the four-document table at
  `18-displacement-PGMAR-TOP-DOUBLING-FOUND-AND-FIXED-GATE-WANTS-REMEASURE-26NOV-relay.md:17-22` is the
  template). If `39`, `350` or `bank-statement` turn out to carry a non-zero margin, §4's "guard zeroed
  them" inference is wrong and the fit test is falsified by three documents that should have overflowed
  by ~31 pt and did not.
* **The rendered page count of the eight under patch-only and patch+fix.** The fit test predicts
  newsletter 2 → 1 sheet, itr unchanged in count, 600/601/401 unchanged in count. Any page count that
  disagrees kills the test in its current form.
* **`newsletter`'s band being page-anchored rather than flow-anchored.** This run's numbers assume the
  band is placed by the flow (it is the deepest *ink*, not necessarily the deepest *block*). If the
  engine writes that band as a `wp:positionV relativeFrom="page"` shape, the band would not move with
  the break at all and the 86.30 would need a different explanation — the fix's 0.20 would still be
  measured, but the mechanism in §5 would be wrong.
* **A correction of `785.20` as the ink bottom.** The lead's "3 pt short" is 3.3 pt if and only if the
  band's top edge is what must clear the margin. The band is drawn to the paper edge, so the measured
  deficit is 60.00 pt. If a later reading establishes that the band is clipped or that its fill is
  transparent in the render, the deficit falls back to 18.27 pt (text-only) — still an overflow, but a
  smaller one, and `0.20` would then need less than the full 60 pt of margin to be explained.
