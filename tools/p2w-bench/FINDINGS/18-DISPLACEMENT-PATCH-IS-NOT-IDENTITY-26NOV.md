# The 18_displacement pgMar-top patch is NOT a LibreOffice identity, and it destroys one document

Run 26 Nov, slot 03:01 IST. Two independent measurements, one agent forensic pass, one local rebuild.

## What the previous run claimed, and what is true

The 25 Nov run committed `FINDINGS/18-displacement-PGMAR-TOP-REMEASURED-26NOV.md` §2 with

> LibreOffice, 212 scored: **0 worse, 0 better, 212 unchanged** — what an exact identity must produce

and left the patch unlanded only because the gate refused on "a pre-existing 3-doc regression".

**The three regressed documents ARE the patch.** They are not pre-existing, and they are not a
committed engine change. Read from the two CSVs already in the repository, no render needed:

| document | `benchmarks/RANKING.csv` (committed) | `FINDINGS/evidence-26NOV/RANKING-26NOV-patched-engine.csv` |
|:--|--:|--:|
| `newsletter-3col-header-footer` | **0.20** share5, signature `clean` | **86.30** share5, signature `content-loss` |
| `601_fillable_admission_form` | 52.39 | **55.32** |
| `401_trifold_brochure` | 0.03 | **0.79** |

`share5` is the percentage of ink outside tolerance, so higher is worse. 0.20 → 86.30 is a document
turned from clean to destroyed: the patched corpus row reports `chars_missing 0` and `text_recall 100`
while 86.3 % of the source's ink has no counterpart — the page kept its words and lost its picture.

## The engine is not the cause — measured

The engine at HEAD (`85b8735f`, "foot-band four-site patch") was scored against the published baseline
engine `b7699196` on the three documents. Both produce, to the digit:

    newsletter 0.20   601 52.39   401 0.03

which is the committed ranking exactly. HEAD + the pgMar patch produces 86.30 / 55.32 / 0.79. So the
foot-band commit — the previous run's named suspect — is cleared, and the patch is convicted.

## The mechanism, and why "identity" was a false assumption

The patch moves the page's top gap out of the first paragraph's `w:before` and into the section's
`w:pgMar w:top`, on the assumption that

    pgMar_top_after + before_after  ==  before_before

Measured in the produced XML: newsletter `pgMar top 0→1200`, first `w:before 1199→0`; 601 `0→1230`,
`1230→0`; 401 `0→1190` with its first `w:before` left at **1790** — the reduction never reached the
paragraph that positions the page, so 401's first band drops by its full `max_pt` of 59.52.

The assumption fails in LibreOffice because **space-before at a page top is suppressed**. The old
`w:before` was never being spent; the new `w:pgMar w:top` is net-new offset. On the newsletter, whose
content already reached y = 785 pt of an 842 pt sheet, 60 pt of new margin overflows: the render goes
to two pages, page 1 keeping only the top band (0 dark px in the masthead band against 105 094 in the
source). That is the 86.3.

## What would make it land

Two changes, both in `DocxWriter.java`:

1. next to `ctx.flowTw = 0;` (~line 1183), the section margin is real height and must come out of the
   flow's budget:
   `ctx.budgetTw = max(1, round(ph*TWIPS_PER_PT) - PAGE_ROUNDING_TW - max(0, ctx.pageTopTw));`
2. `sectionTopTw` must return 0 unless the page-first paragraph's own `w:before` is what places the
   page — otherwise 401 and 601 keep the gap twice.

Change 1 alone was measured: newsletter **86.30 → 0.20**, back to one page with the band restored.
601 stays 55.32 and 401 stays 0.79 with change 1 only, so change 2 is required before this patch can
be called safe. **Do not land the patch until both are in and the 213-document corpus is re-measured.**

## The standing cost

`classpick.py --leverage` values 18_displacement at **54.8 clean documents** — the largest single prize
in the table. It is now known to be blocked on a two-line accounting fix, not on a mystery regression.
That is the next run's first job, and it is a code job, not a research job.
