# Fixer report - 2026-11-18 13:48

```
=== FIXER REPORT - every number computed from committed files ===

1. classes total            : 7  (212 documents across them)
2. classes solved           : 0 clear, 6 still have an OPEN document
3. docs improved THIS run   : 0  (1 attempts, 0 kept)
4. this run total time      : 47 min  (12:58 -> 13:45)
5. subagents this run       : 0
6. working on class         : single-element-far-out
7. corpus improvement       : +6.85%  (mean share5 6.15 -> 5.73 over 212 docs)
8. docs improved total      : 2 of 212  (0 regressed, 210 unchanged)

   best so far:
     415_inline_images                           89.04 ->  0.00
     newsletter-3col-header-footer                3.45 ->  3.13
 9. looked dead, was not    : 22 beats, 1 silence(s) over 2 min
     longest silence        : 46.2 min from 12:58:01, after gaps.py: reading the timeline
10. obstacles this run     : 4 cleared by the run, 2 need a human
     still a wall           : `classrow.py` marks FIXED only when the document was ABOVE 5.0 share@5 at baseline and is at or below it now. 

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
