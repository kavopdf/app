gverify run — 26 Nov 2026

Stage: classify. 213 measured, 208 scored, 5 refused on page count, 166 failing at least one check.
LibreOffice passes all 42 on 135 of 208; Google Docs passes all 42 on 42 of 208.

| check | Google | LibreOffice |
|---|---:|---:|
| 18\_displacement | 119 | 21 |
| 60\_text\_column\_right\_edge | 62 | 19 |
| 04\_chars\_missing | 55 | 3 |
| 59\_shape\_anchor | 49 | 12 |
| 45\_char\_accuracy | 34 | 3 |

**What this run found.** The capability table was a two-engine table under a header that said "same
engine": 0 of 208 pairs carried the LibreOffice half on the engine in the tree. The Google half is
re-measured on every engine move; the LibreOffice half is written once per document and the guard
returned "already have it" for ever, so no cron could refresh it — the matrix stage fills documents
with no LibreOffice result, and by count there were none.

**What it did.** Added the missing path to `gverify.py` — `collect_lo(force)`, a resumable
`--lo-stale N` that computes its work list from the engine stamps, and a serial retry, because four
concurrent soffice instances lose the odd conversion and the old json then stays in place looking
current. Re-measured the LibreOffice half in seven passes: 213 of 213 documents now carry
981ff1fa35e2cf67, 0 failed. `--matrix` now prints each half's engine coverage instead of asserting
they match, and its row order is stable across runs.

The refresh moved three LibreOffice counts by one document each — 25\_invisible\_text, 26\_text\_overlap,
59\_shape\_anchor — and left the headline where it was. Both halves are now 208 of 208 pairs on the
engine in the tree, so the next fixer reads a pair rather than a blend.

Next: classify — 166 documents fail at least one check and the class table is older than the results.
That is the classifier's stage; the measuring side of this cron is finished.
