**Google verification - stage `classify`.** The Google side is complete and both renderers are on one engine. This run's deliverable, the capability table, is regenerated and byte-identical to the committed one, so no document needed re-measuring and the table is current.

| | documents |
|---|---:|
| corpus | 214 |
| measured through Google | 214 |
| scored | 206 |
| refused on page count | 8 |
| pass every check offered | 48 |
| fail at least one check | 158 |

## Where the two renderers disagree

LibreOffice passes 86 of 206; Google Docs passes 48 of 206. Engine in the tree `a05b20eb05fe0fc8`, carried by both halves on all 206 pairs.

| check | LibreOffice fails | Google fails |
|---|---:|---:|
| `18\_displacement` | 89 | 108 |
| `60\_text\_column\_right\_edge` | 18 | 59 |
| `04\_chars\_missing` | 2 | 54 |
| `59\_shape\_anchor` | 39 | 50 |
| `45\_char\_accuracy` | 2 | 33 |
| `13\_text\_colours` | 1 | 32 |
| `17\_matched\_runs` | 5 | 30 |
| `47\_margins` | 15 | 27 |
| `26\_text\_overlap` | 3 | 19 |
| `44\_header\_footer` | 0 | 19 |
| `27\_text\_off\_page` | 2 | 17 |
| `43\_within\_10pt\_x` | 7 | 13 |

A zero in the LibreOffice column is the point of the table: LibreOffice honours a construct Google drops. That set is `44\_header\_footer` 19 documents, `10\_font\_sizes` 6, `46\_text\_crossing\_rule` 6, `32\_stroke\_lines` 5, `23\_line\_pitch` 4, `31\_pages\_lost\_their\_text` 1 and `42\_justification\_edges` 1. Google honours `14\_filled\_shapes` on 3 documents that LibreOffice does not.

`gverify.py --lo-stale` re-measured 0 documents: the LibreOffice half already carries the engine in the tree everywhere it could be checked, so the pair names a construct for every document it covers.

**Next:** classify - 158 failing documents to group into classes. That is the classifier's table, not this cron's; measuring work here is finished and no engine code was touched.
