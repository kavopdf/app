# `855f443` rebuilt as a spec — justified lines were being emitted left-aligned

This is the fix the 04:56 run found, measured, kept and lost. Its commit exists nowhere: `git push`
returned 403 before a single byte uploaded. The report survives, and it is precise enough to
implement from. **This is a specification, not code** — the change spans three model classes and
four writer methods with three guards, and the agent that wrote this has no `java` and cannot
compile. Writing it blind would repeat the mistake the 00:58 run made with `|Trm|`: a plausible
formula that measured worse.

The fixer implements it, builds it, and screens it. Nothing here is measured on the current engine.

---

## The defect

A line the page **justified** is emitted **left-aligned**. The page stretches a line's inter-word
gaps so both ends sit on the measure; the writer puts the words down with the face's natural space
and stops, so the line ends short of the right edge and every word on it slides left by a share of
the missing width. The error grows with the number of spaces on the line — which is why it is worst
on two-column academic and policy layouts, where lines are narrow and carry few words.

Measured by the 04:56 run on the documents it kept:

| document | before | after |
|:--|--:|--:|
| `academic-paper-ieee-2col-abstract` | 8.09 | **0.83** |
| `policy-2col-spanning-section-heading` | 5.37 | **0.01** |
| `magazine-2col-pullquote-spanning` | 3.49 | **0.01** |
| `304_package_insert_small_print` | 3.41 | **0.03** |
| `61_two_col_abstract_spanning` | 2.01 | 1.34 — improved, still open |

Corpus, that run: **22 better, 190 same, 0 worse** on 212.

---

## 1. The model must carry the fact

The model throws away the one thing the writer needs: whether the page justified the line. Add a
flag to the three classes that carry a line of text:

    PdfToWord.Box.stretched             boolean   (class Box, PdfToWord.java:212)
    PdfToWord.Line.stretched            boolean   (class Line, PdfToWord.java:3122)
    PdfToWord.Table.CellPara.stretched  boolean   (class CellPara, nested inside Table at
                                                   PdfToWord.java:303 - note the path: CellPara
                                                   is not a top-level class)

`PdfToWord.convert()` sets it. **Nothing else reads it** — it is written by `convert()` and read
only by `DocxWriter`, so the `.txt` cannot move. That is the isolation claim and it must be checked,
not assumed: `TxtWriter` walks the same model.

## 2. How `convert()` decides

Compare each line's own inter-word gaps against **the 3rd percentile of that page's gaps**. The
narrow end of the distribution is where the face's own space lives, because justification only ever
**widens** a gap — a page cannot shrink a space below the font's natural width. A line whose gaps sit
above that floor has been stretched.

    floor = 3rd percentile of every inter-word gap on the page
    stretched(line) = the line's median inter-word gap > floor by more than the tolerance

Percentile, not mean: one wide word-space on a page of tight text must not move the floor, and a
page with no justification has a flat distribution where nothing crosses.

**The tolerance is the fixer's to measure.** Start from the report's own note that a justified line's
gaps differ by a visible fraction, and choose it by screening the class — not by picking a round
number. A tolerance that is too small stretches ordinary lines and costs more than the defect.

## 3. What the writer emits

`w:jc="distribute"` — Word's *Distributed*, the only OOXML alignment that stretches a **single-line**
paragraph. `w:jc="both"` does not: it leaves the last line of a paragraph alone, which is exactly the
line that needs the treatment, and the 00:58 run measured it at 8.09 → 8.09, no movement.

Plus a **right indent at the page's own ink edge, less 12 twips (0.6 pt)** of slack. The slack is for
the substitute face: the .docx is laid out in a face whose advance differs slightly from the page's,
and a right indent set exactly to the edge makes the last word wrap.

Emit it in all three paths, because a two-column layout puts paragraphs in all three:

    DocxWriter.flowFromBox()      body lines in the normal flow
    DocxWriter.lineParagraph()    a paragraph inside an anchored text box -
                                  102 of the IEEE paper's 190 paragraphs live here
    DocxWriter.cellParaXml()      a paragraph inside a table cell

## 4. The three guards — each one is a measurement, not a theory

**Guard 1 — never stretch a dot leader.** A leader is drawn to fill its measure; stretching it
re-lays the dots and the heading wraps. Measured: `table-of-contents-dot-leaders` **10.72 → 26.27**
without this guard.

**Guard 2 — never stretch a line carrying a complex-script character.** The Devanagari substitute
face is wider than the page's face, so the line is already at or past the measure. Measured:
`78_mixed_english_devanagari_line` **13.51 → 16.08** without this guard.

**Guard 3 — a 3 pt floor.** OOXML's `w:sz` is half-points, so an 8.9 pt line goes out at 8.5 and every
advance is 4.5 % short. Stretching a line that is 1–2 pt short of its own edge buys nothing and
disturbs the fit. Fire only when the shortfall is worth **at least 3 pt**.

## 5. Already refuted — do not spend a run on these

| idea | measured |
|:--|:--|
| `w:jc="both"` + right indent in `flowFromBox` | 8.09 → 8.09, no movement |
| `xyCut()` column-major ordering for the 2-column class | 8.09 → 8.09, no movement |
| doubled spaces | 8.09 → 45.33, worse |
| splitting every word into its own Box | 8.09 → 22.76, worse |

## 6. What the fixer must prove before keeping it

1. **Build it.**
2. `screen.py --class "content-partly-lost"` and the two-column documents by name.
3. **The three guards must each be shown to fire and to matter** — remove one, re-screen, see the
   document it protects get worse. A guard nobody tested is a guard nobody knows works.
4. **Full corpus pass, both ratchets.** `txt_gate.py --snapshot` before, `--verify` after. The claim
   is that the `.txt` does not move, because the flag is written by `convert()` and read only by
   `DocxWriter` — **that is a claim about the code, and the gate is how it becomes a measurement.**
5. The 04:56 run's own honest gap stands: **`w:jc="distribute"` was measured only through
   LibreOffice.** It is the OOXML standard's distributed alignment and LO honours it exactly, but
   nothing in this pipeline renders through Word or Google Docs. If Word treats a single-line
   distributed paragraph differently, the gain is unproven there. Say so in the report.

## 7. Two documents the lost run could not finish

`journal-2col-with-footnotes` (7.75 → 3.53) and `66_two_col_footnotes_bottom` (13.03 → 9.09) carry
the same cause and did not cross 1.0. Their residual was **not diagnosed** — it is not the measure.
Do not assume the same fix finishes them.

`61_two_col_abstract_spanning` sits at 1.34 for a different reason the lost run did name: its body is
in `w:tbl` cells built from **rows strings** rather than `paras`, so there is no `CellPara` to carry
the flag and the rule cannot fire there. That is a model change in `buildTables`, not a writer change,
and it is a separate piece of work.
