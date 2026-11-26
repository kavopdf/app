**gverify — all 213 documents now have a Google result; the last 16 cannot land past the commit gate**

Every document in the corpus was uploaded to Google Docs, converted, exported as PDF and scored this run. The measurement is complete on disk, but the gate refused the last sixteen results, so the committed corpus still reads 197 measured.

**Where the corpus stands**

| | count |
|---|---:|
| corpus | 213 documents |
| measured through Google (committed) | 197 |
| pass every check offered | 42 |
| fail at least one check | 147 |
| refused (page count) | 8 |
| stage | measure-google |
| next | measure 16 more through Google |

The sixteen still to go are not unmeasured — they are measured and blocked. Each one was re-measured this run on the engine in the tree and each came back with exactly the counts the earlier pass recorded, so the refusal is reproducible, not flaky. The gate's rule is that no document may fail more of Google's checks than its committed verdict did; all sixteen do, because their committed verdicts were measured on the engine the last release commit reverted. There is no override and none was used. The blocker row is in the repo, the results stay out of the commit, and the next pass will pick them up again.

**The pair table — the LibreOffice half was the stale one, and it is now being refreshed**

Until this run not one LibreOffice result carried the engine in the tree, so every row of the capability table compared a current Google render against a LibreOffice render of an older `.docx`. The table now reports 71 of 205 pairs on the engine above, up from zero; the rest is resumable and the next pass continues it.

| | LibreOffice | Google Docs |
|---|---:|---:|
| pass every check offered | 135 of 205 | 47 of 205 |

**Which check costs how many documents** (Google, committed results)

| check | docs |
|---|---:|
| `18\_displacement` | 95 |
| `60\_text\_column\_right\_edge` | 54 |
| `04\_chars\_missing` | 46 |
| `59\_shape\_anchor` | 44 |
| `13\_text\_colours` | 32 |
| `45\_char\_accuracy` | 32 |
| `17\_matched\_runs` | 28 |
| `47\_margins` | 26 |
| `26\_text\_overlap` | 16 |
| `44\_header\_footer` | 12 |

**Where the two renderers disagree, on the pairs that are both current**

| check | LibreOffice fails | Google fails |
|---|---:|---:|
| `18\_displacement` | 18 | 105 |
| `60\_text\_column\_right\_edge` | 18 | 60 |
| `04\_chars\_missing` | 2 | 47 |
| `59\_shape\_anchor` | 10 | 45 |
| `13\_text\_colours` | 1 | 32 |
| `44\_header\_footer` | 0 | 13 |
| `32\_stroke\_lines` | 0 | 5 |

A check Google fails and LibreOffice passes is a construct LibreOffice honours and Google drops — that is the column a fixer acts on, and `18\_displacement` remains the largest single class.

The capability table was regenerated and committed with the refreshed LibreOffice results; no engine code was touched. The next pass continues the LibreOffice backlog and re-attempts the sixteen.
