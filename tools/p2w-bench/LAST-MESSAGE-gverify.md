# Google verify - run report

Stage **measure-google**: 143 of 214 documents now carry a Google result on the engine in the tree (137 scored, 6 refused on page count). Next: measure 20 more.

## What this run did

Took the next 60 documents from the planner, imported each into Google Docs, exported the PDF and collected the 42-check verdict. All 60 result files are committed under `benchmarks/gverify/` on main. The pod is fresh every hour, so the corpus was converted in slices before any upload started.

Two things the next run should not have to rediscover:

- `GOOGLEDRIVE_CREATE_FILE` exists and does convert a docx into a Google Doc. The staging upload behind it failed on most files today ("the file does not exist in storage"), and re-trying the same key never worked.
- So the docx were staged on a temporary branch of this repository and pulled into Drive with `GOOGLEDRIVE_UPLOAD_FROM_URL`. That branch is deleted; nothing was written to the Drive root and nothing in Drive was deleted.

## Corpus (gverify.py --report)

143 verified | 37 pass every check offered | 100 fail at least one | 6 refused (page count).

| check | documents failing |
|---|---:|
| `18\_displacement` | 62 |
| `59\_shape\_anchor` | 39 |
| `60\_text\_column\_right\_edge` | 38 |
| `04\_chars\_missing` | 37 |
| `13\_text\_colours` | 23 |
| `47\_margins` | 20 |
| `45\_char\_accuracy` | 20 |
| `17\_matched\_runs` | 18 |
| `35\_rotation` | 12 |

## Capability table (gverify.py --matrix)

207 documents compared: LibreOffice passes 107, Google passes 42.

Read it as a single-renderer table for now. 0 pairs are measured on both renderers on the current engine (Google 137 of 207, LibreOffice 0 of 207), so the LibreOffice column still describes the docx an older engine wrote. The pair comparison becomes real when the matrix stage fills the LibreOffice side.
