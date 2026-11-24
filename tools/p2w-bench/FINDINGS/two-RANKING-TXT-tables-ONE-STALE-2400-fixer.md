# Two `RANKING-TXT.csv` files disagree by 50 documents, and one of them is a month-old duplicate

Found 24 Nov 2026 while briefing a sub-agent on the .txt failure count. Both files have 213 rows.

| path | clean | failing | last commit that wrote it |
|:--|--:|--:|:--|
| `tools/p2w-bench/txt/RANKING-TXT.csv` | **199** | 14 | `0cefe274 txt: restamp all 213 with current verifier (engine b7699196), 199/213 clean` |
| `tools/p2w-bench/RANKING-TXT.csv` | 149 | 64 | `13601fb4 the txt is scored across the whole corpus for the first time, and 64 documents fail` |

**The `txt/` copy is authoritative.** `txt_gate.py:47` and `step_txt.py:29` read only that one, and
`report.py`'s 199/14 headline is reproduced exactly from it. The copy at the tools root is a
duplicate from an earlier epoch that was never retired, and 54 documents differ between them.

`report.py:910-914` prefers `txt/RANKING-TXT.csv` and then **silently falls back** to the root
copy. So the report cannot be wrong today, but anything else that globs the obvious path - a
sub-agent handed `tools/p2w-bench/RANKING-TXT.csv`, a new tool written by a future run, a human
reading the directory listing - gets 149/64 and concludes the .txt half is far worse than it is.
That is what happened here: an agent briefed on the root file reported "the CSV is right, the
report is wrong", and it was the other way round.

Nothing is deleted (the six non-negotiables). What is needed is one of: a `--txt-table` argument
that names the file explicitly everywhere, a header line in the stale copy saying it is superseded,
or removing the silent fallback at `report.py:912` so a missing `txt/` table reads as unavailable
instead of as a different measurement.
