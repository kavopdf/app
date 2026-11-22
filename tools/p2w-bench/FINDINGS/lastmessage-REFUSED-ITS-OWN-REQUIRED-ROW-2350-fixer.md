# lastmessage.py refused the row it requires: the .txt table says "of 213" and the corpus check wants 212

**22 Nov 2026, fixer slot 22:50.** `lastmessage.py --file` refused this run's report twice for a number
the run had not typed:

    corpus: 'of 213' appears, the corpus is 212 (compared: 212)

The offending text was `| Scored | **213** of 213 |` — a row of the **`## The txt` table that
`verify_sections` demands appear in the report verbatim**, written by `report.py:937` from the .txt store,
whose corpus genuinely is 213. The corpus check compares against `co["docs"]` = 212, the .docx corpus,
which is one smaller because `416_many_tiny_pages` is exempt in the baseline. Two different quantities,
one word — the same collision the file's own comment at line 228 records for prose, now between two of its
own checks.

So no fixer report could pass: the section was required and its row was refused.

**Fixed** in `lastmessage.py`: a line that appears in `REPORT.md` is skipped by the corpus scan, because
`verify_sections` already compares those lines character for character against report.py. A row copied
from the tool is not a number a run typed, and the check exists to catch typed numbers.

**Measured:** with the change, this run's report passes (`numbers: 6 Progress row(s) match report.py`,
`facts: header clock, corpus size, .txt and agent timings all match report.py`, 7664 characters written);
without it, the same report is refused. Nothing else in the validator was touched.
