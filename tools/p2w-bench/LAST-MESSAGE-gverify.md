**gverify: the Google side is complete at 197 verified, and the last 16 documents all fail more checks on the engine in the tree than on the one before it.**

`stage.py` reads `measure-google`, `next: measure 16 more through Google` — because those 16 measurements were refused by the commit gate, not because they were not taken. All 213 documents have now been through Google; 197 carry a result on the engine in the tree, 189 scored and 8 refused on page count. 42 pass every check offered, 147 fail at least one.

**Which checks cost the most documents** (Google, committed results)

| check | documents |
|---|---:|
| 18\_displacement | 95 |
| 60\_text\_column\_right\_edge | 54 |
| 04\_chars\_missing | 46 |
| 59\_shape\_anchor | 44 |
| 13\_text\_colours | 32 |

**The pair, both renderers**

LibreOffice 135 of 205 pass every check; Google 47 of 205. On the engine in the tree that is 130 of 205 pairs for LibreOffice and 189 of 205 for Google, up from a LibreOffice half that was mostly on an older engine when this run started.

**The finding this run exists to report**

The 16 documents measured this run went from engine `025fe9deda5ac7b1` to `a4d8fca469bba636` and every one of them fails more checks on the new engine — 16 of 16. `18_displacement` is on all 16, and on `412_page_labels_roman` the median vertical shift moved from 2.3 pt to -59.0 pt across every page. That is a page-geometry change, not a per-construct misplacement. `regress.py --check` refused the commit and I did not override it: the 16 committed results were left at their old values so the LibreOffice half and the table could land, and the refused measurements are committed beside the write-up at `FINDINGS/GOOGLE-REGRESSION-16-OF-16-ON-a4d8fca-27NOV.md`. The fixer should re-measure those 16 before touching anything.

**Next**: stage `matrix` work is the LibreOffice half — 130 of 205 pairs are on the engine, so the remaining pairs are still a backlog for the next run.
