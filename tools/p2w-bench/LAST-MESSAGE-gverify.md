# Google verify - run report

**Stage `measure-google`.** 72 of 213 documents carry a Google result on the current engine: 64 scored, 8 refused on page count. The stage has not moved; `stage.py` says measure 20 more.

## What this run measured

Two documents, both collected and committed:

`33\_sans\_nondefault\_body` now fails one check in Google and none in LibreOffice.
`344\_customs\_declaration` fails four in Google and none in LibreOffice. A document's check set is
not always the same size, so a document can score out of more than 42 checks and that is not a
regression.

Then the platform file-upload bridge stopped resolving its keys and no further document could be
measured. The exact calls, the exact errors and what would overturn it are in
`tools/p2w-bench/BLOCKERS.md`. The short version: uploading a .docx gives a single-slot key that a
second upload kills, so the four Drive calls per document cannot be batched; and after the first two
documents every key, including fresh ones, answered storage not-found. Nothing in this repository can
route around it, because every path that puts a local .docx into Drive needs a key from that bridge.
So this run measured two of the sixty it was aimed at. It did not reach the cap and was not cut off by
it.

## Checks Google fails, by how many documents

| check | documents |
|:--|--:|
| `18\_displacement` | 32 |
| `04\_chars\_missing` | 23 |
| `60\_text\_column\_right\_edge` | 21 |
| `13\_text\_colours` | 19 |
| `59\_shape\_anchor` | 17 |
| `45\_char\_accuracy` | 14 |
| `35\_rotation` | 11 |
| `17\_matched\_runs` | 11 |
| `47\_margins` | 9 |
| `43\_within\_10pt\_x` | 6 |

Of the 64 scored documents, 13 pass every check offered and 51 fail at least one.

## The capability table, as it stands

Constructs LibreOffice honours and Google does not: `44\_header\_footer` on 13 documents,
`10\_font\_sizes` on 6, `32\_stroke\_lines` on 5, `23\_line\_pitch` on 3, `46\_text\_crossing\_rule` on 2,
`31\_pages\_lost\_their\_text` on 1, `42\_justification\_edges` on 1.

Constructs Google honours and LibreOffice does not: `14\_filled\_shapes` on 3 documents.

That is the table the fixer works from, and it is the reason this measurement exists: a check Google
fails and LibreOffice does not is a construct Google drops.

## What is next

`measure-google` again, and the first thing the next run should do is try one upload -> create ->
export -> collect cycle. If that cycle works, measure as many as the bridge allows and no more; if it
fails the same way, the bridge is the blocker and the slot belongs to something else rather than to a
retry loop. `--plan` is the count to trust, not the number of `.json` files on disk.
