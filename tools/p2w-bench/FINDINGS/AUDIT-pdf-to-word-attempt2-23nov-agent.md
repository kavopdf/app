# PDF-to-Word — deep audit, attempt 2 of 5

Agent, 23 Nov 2026. Read-only. Attempt 1 covered error handling in the writers; this one covers the page-count
gate — the single largest hole in the instrument.

---

## B1 — all 23 refusals are the same defect, and it always goes the same way

Every document Google refused has **more pages in the `.docx` than in the PDF**. Not one has fewer.

    21 documents : 2 pages vs 1   ->  exactly +1 page
     2 documents : 14 pages vs 9  ->  +5 pages

The two +5 cases are `041122-Account_Opening_Form` and `Account_Opening_Form_Fillable_filled` — the same form
twice, so the corpus really has **one** document with a large overflow and **21** with a single extra page.

This is the defect the user has reported in his own words: *"original pdf me kai me sirf 1 page hai jabki docs
me 2 page hai"*. It is not a page-count arithmetic bug. It is content overflowing onto a page it does not
belong on.

---

## B2 — the source page is NOT full, so the overflow is accumulated height, not a full page

Measured on the source PDFs (`benchmarks/gverify` has the verdict; the PDFs have the geometry):

    314_tender_rfp_boq         content ends at 784 of 842 pt   ->  58 pt of slack
    305_vaccination_certificate            783 of 842          ->  58 pt of slack
    351_omr_answer_sheet                   808 of 842          ->  34 pt of slack

58 pt is roughly four lines of body text. So the PDF had room and the `.docx` still spilled. That means the
converted document is **more than 58 pt taller than its source** across one page — a difference accumulated
line by line, not a single wrong value.

**What that rules out:** a wrong page height, a wrong margin of the size that would show as a visible layout
error, a missing page break.

**What it points at:** per-line height — line pitch, or the space-after on each paragraph, or both — summing to
tens of points over ~40 lines. At 1.4 pt per line of drift, 40 lines is 56 pt, which is exactly the size of the
slack. This audit did not prove which of the two it is; that is the next measurement.

---

## B3 — a refusal means no check runs at all, so 11% of the corpus is not "unscored", it is unexamined

`gverify` refuses the document on page count and stops. The verdict it writes has four keys:

    {name, status, pages, want}

No `passed`, no `failed`, no `engine`. So for these 23 documents **nothing is known** — not the text, not the
tables, not the colours, not the displacement. They are not documents that failed the 42 checks; they are
documents the 42 checks never saw.

The consequence is bigger than 23 documents. The instrument reports "30 of 190 clean", and a reader takes 190 as
the population. The real population is 213, and 23 of them are invisible in a way that looks like exclusion
rather than blindness.

---

## B4 — the gate turns one defect into total blindness, and that is a design choice worth questioning

The page count is **one** check (`01_page_count`). When it fails, the other 41 do not run.

If they did, this corpus would say something far more useful about these 23 documents: whether their text is
right, whether their tables are real tables, whether their colours match. The page count would still be wrong —
and a reader would still see it — but the run would know 41 other things instead of one.

**What I am NOT saying:** that the refusal should be removed. A page-count mismatch makes the pixel comparison
meaningless, so the *pixel* checks cannot run. But text recall, table structure, colours, fonts and header/footer
do not depend on the page count lining up — and those are exactly the checks that would tell a run why the
document spilled.

**This is the largest single lever in the instrument:** 23 documents × 41 checks that currently produce nothing.

---

## What this attempt did NOT cover

- which of line pitch or paragraph space-after actually accumulates the 58 pt (the next measurement)
- whether the +5 form has the same cause or a different one
- the conversion pipeline's page-break logic
- whether the engine ever *writes* a page break that the PDF did not have

---

## For the fixer

B1 and B2 are measurements, not opinions: 21 documents with exactly +1 page, and 58 pt of slack in the source.
B4 is the one with the most value and the most risk — loosening a gate can let bad data through, so it needs the
same treatment as `measure_gate`: prove on a document where the page count is right that the other checks still
report the same verdict they report today.

Verify before changing. This audit read verdicts and PDF geometry; it did not run the engine.
