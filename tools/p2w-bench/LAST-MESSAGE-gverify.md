# Google verification pass

**Stage.** `stage.py` reports `fix`, but it counts every result file on disk, including ones written by earlier engines. `gverify.py --report` counts only the results that carry the current engine stamp, and by that count the Google side is not finished — so measuring is still this cron's work. This run took a full batch: 60 documents.

| measured | value |
|---|---:|
| documents in corpus | 213 |
| Google results on the current engine | 146 |
| pass all 42 checks | 27 |
| fail at least one | 96 |
| refused, page count did not match | 23 |

**What failed, top five** (documents, from `gverify.py --report`):

| check | documents |
|---|---:|
| `18\_displacement` | 52 |
| `04\_chars\_missing` | 40 |
| `59\_shape\_anchor` | 33 |
| `60\_text\_column\_right\_edge` | 33 |
| `25\_invisible\_text` | 29 |

Both renderers are now measured for every document that has a Google result: the LibreOffice side holds a committed result for all 213, so no backlog is left on that half.

**Next.** A full batch finished comfortably inside the run, so the next run takes 60 again rather than fewer, and the remaining documents follow over the next runs.
