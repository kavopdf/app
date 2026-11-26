# Google verification — 60 documents measured through Google Docs

This run took 60 documents end to end: the `.docx` uploaded, converted to a Google Doc, exported as
Google's own PDF, and scored against the source PDF with the 42 checks. All 60 scored; none refused.

## Where the corpus stands

| | count |
|---|---:|
| verified — a Google result on the engine in the tree | 68 |
| pass every check offered | 18 |
| fail at least one | 42 |
| refused (page count) | 8 |

A refused document is not a pass. The 8 are carried as refusals and are not counted in the 18.

## Which check fails how many documents

| check | documents |
|---|---:|
| `60\_text\_column\_right\_edge` | 20 |
| `18\_displacement` | 18 |
| `04\_chars\_missing` | 13 |
| `59\_shape\_anchor` | 11 |
| `47\_margins` | 11 |
| `13\_text\_colours` | 7 |
| `45\_char\_accuracy` | 7 |
| `17\_matched\_runs` | 6 |
| `43\_within\_10pt\_x` | 5 |
| `35\_rotation` | 4 |
| `26\_text\_overlap` | 3 |
| `44\_header\_footer` | 2 |
| `05\_chars\_extra` | 1 |
| `27\_text\_off\_page` | 1 |
| `10\_font\_sizes` | 1 |
| `32\_stroke\_lines` | 1 |
| `23\_line\_pitch` | 1 |
| `66\_table\_cell\_width` | 1 |

## The capability table

| | |
|---|---:|
| documents in the table | 205 |
| LibreOffice pass every check offered | 135 |
| Google Docs pass every check offered | 47 |
| engine in the tree | `a4d8fca469bba636` |
| Google measured on that engine | 60 |
| LibreOffice measured on that engine | 0 |

The table cannot yet name a construct. A row is only readable as "Google drops this, LibreOffice
honours it" when both halves were measured on the same engine, and the LibreOffice half is measured on
that engine for 0 pairs. That is the matrix stage's work, not this one's.

## Stage and what is next

`stage.py` says **measure-google**: corpus of 213 documents, 68 measured through Google, 60 of them
scored and 8 refused. Next is to measure more through Google.

Two things this run changed for the next one. The `.docx` already sitting in Drive were built by an
older engine, so a re-measure needs the current `.docx` uploaded again — this run did that for all 60
and the route that works is the platform upload to an `s3key`, then Drive upload, then copy to a Google
Doc, then export. And the corpus cache is not complete on a fresh pod: this run had to convert a slice
before it had 60 documents to measure at all.
