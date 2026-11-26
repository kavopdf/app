# The .txt half of the running-foot lead: t09 fails on two documents, both the same form — and the 125 is not yet attributable

**Recorded:** 2026-11-26 ~18:15 IST, relay slot 17:12. Engine HEAD as cloned (`d8026f0`).
**Class:** `44_header_footer`. **Outcome: lead, measured, nothing changed.**

## What the lead said, and what is now true of it

`classpick.py` suggested `44_header_footer` on this record: *"running foot is a row: flowRow anchors it
past gapCapTw, Google drops the box text entirely. footBand change measured in | next run: the .txt
half"*. Two separate claims were tested. Both halves came back negative, which is the useful result:

1. **The `.docx` half is already guarded, and the remaining anchor site is inert.** See
   `44_header_footer-FLOWFROMBOX-ALREADY-GUARDED-AND-INERT-1815-relay.md`. `flowFromBox` has carried
   `!inFootBand(ctx, b.y)` since `85b8735f` (25 Nov), the finding that named it predates that commit,
   and removing both `flowFromBox` guards changes no byte of `document.xml` on 17 documents. The boxes
   on `27_two_column_left_short_txtpos` and `46_chart_coloured_labels_body_text` come from `flowRow`
   and are already gone at HEAD: `w:txbxContent` = 0 on both.
2. **The `.txt` half is nearly clean already.** The live store `tools/p2w-bench/txt/RANKING-TXT.csv`
   (213 documents, engine stamp `a4d8fca469bba636`) has 8 documents failing any check, and
   `27_two_column_left_short_txtpos` and `46_chart_coloured_labels_body_text` both read **9/9, 0 failed**.
   So the two documents the footBand change fixed in Google are already clean in the `.txt`. There is
   nothing to carry over for them.

## What the `.txt` half actually fails on: `t09_page_furniture`, two documents

`t09_page_furniture` is the only check in the `.txt` set that speaks to page furniture, and it fails on
exactly two of 213 documents — and they are the same form twice:

| document | source (owed) | txt (present) | other failures |
|:--|--:|--:|:--|
| `041122-Account_Opening_Form` | 29 | 125 | `t06_encoding`, `t12_word_invention` |
| `Account_Opening_Form_Fillable_filled` | 29 | 125 | `t06_encoding`, `t12_word_invention` |

**Re-measured live this run, not read from the table.** Both PDFs were converted with `ConvertOne`
(engine compiled from HEAD, 9 pages each, 480 and 489 paragraphs) and scored with `verify_txt.py`.
Both returned `10/12 applicable, 7 passed, 2 abstained FAIL` with `t09_page_furniture source=29
txt=125` — identical to the stored row. So the row is current and the construct is one form, not two.

## The keys, and why 125 against 29

The owed keys are four, and three of them are single letters:

| key | owed (drawn occurrences) | present in the `.txt` |
|:--|--:|--:|
| `Y` | 12 | 41 |
| `D` | 8 | 33 |
| `M` | 6 | 45 |
| `Date` | 3 | 6 |
| **total** | **29** | **125** |

The source draws the date box of this form as eight separate one-glyph lines on one baseline —
`D D M M Y Y Y Y` at y=805.87, x=51.37 / 64.33 / 77.29 / 90.71 / 104.13 / 116.37 / 128.61 / 140.85
on page 1, and the same band on page 0 at y=90.81. `_src_pages` groups them as single-character lines,
so each is a furniture key of its own, and `t09` counts them **per drawn occurrence inside the band**.

The `.txt` side counts every matching line in the whole file. The `.txt` for this document carries
**247** single-character lines, of which the date box is only the first eight (file lines 23–30:
`D D D D M M M Y Y Y Y`). The rest come from letter-spaced words split into one-character lines
elsewhere on the page — file lines 195–198 read `A`, `L`, `U`, `T`, `A T I` where the page draws a
single word. Those body letters match the same furniture keys and are counted as furniture.

## What this run did NOT settle — and it is the whole of the next attempt

**It is not established whether the 125 is a writer defect or an instrument asymmetry.** The two are
indistinguishable from the number alone:

* If the `.txt` is splitting letter-spaced words into one-character lines that the page drew as one
  line, that is a `TxtWriter` line-assembly defect, and it is also a `t04_structure` risk on every
  document with tracking.
* If the split is faithful (the page really draws those glyphs separately) then the defect is in the
  check: `t09` restricts the *source* side to the top/bottom 12 % band and to keys repeating on ≥3
  pages, and then compares against a *whole-file* count on the `.txt` side, so any document that draws
  a single letter anywhere can never pass.

A crude band approximation was run to try to decide it — counting only the first and last six
non-blank lines of each `.txt` page — and it returned 11 present against 29 owed. That is neither 29
nor 125, so the approximation does not decide the question; the band on this form sits behind many
blank lines that a fixed six-line window does not reach. It is recorded so the next run does not
repeat it.

## The next attempt, stated as work

1. For `041122-Account_Opening_Form`, take the 247 single-character `.txt` lines and ask, for each,
   whether the source drew that glyph as its own line (faithful) or inside a longer drawn line
   (writer defect). The page model already answers this: `_src_pages` has the drawn line each glyph
   belongs to. That is a census, not a guess, and it decides which of the two repairs is the right one.
2. If it is the writer: the fix belongs in `TxtWriter`'s line assembly, and `t04_structure` is the
   independent check that it did not break line counts elsewhere.
3. If it is the check: `t09`'s `txt_furniture` must be restricted the same way the source side is, and
   the whole 213-document `.txt` table must be re-measured before and after — the number moves on any
   document that draws a single letter, not only on these two.

## What would prove this wrong

* A `.txt` for either document that carries 29 furniture lines once the check's two sides are made
  symmetric — that would mean the writer was never at fault and the 96 surplus copies were always the
  instrument.
* A source-side census showing every one of the 247 single-character `.txt` lines corresponds to a
  glyph the page drew on its own line — that would mean the `.txt` is faithful and the check is the
  only defect.
* A third document in the corpus that fails `t09` — the table says there is none, and this run
  confirmed the two named ones only.
