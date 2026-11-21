# Google Verify - run report

**Stage: classify.** This run measured nothing and changed no engine code. At classify the last job is
the capability table, so it was regenerated from the committed results and pushed.

## The corpus, as the tools count it

| | |
|:--|--:|
| documents in the corpus | **213** |
| scored in Google | **192** |
| refused on page count | **21** |
| fail at least one check | **186** |
| pass all 42 in Google | **6** |
| pass all 42 in LibreOffice | **122** |

## Where the two renderers disagree

| check | LibreOffice fails | Google fails |
|---|---:|---:|
| `32\_stroke\_lines` | 1 | **145** |
| `05\_chars\_extra` | 3 | **141** |
| `18\_displacement` | 20 | **124** |
| `04\_chars\_missing` | 2 | **66** |
| `25\_invisible\_text` | 0 | **49** |
| `59\_shape\_anchor` | 11 | **58** |
| `60\_text\_column\_right\_edge` | 18 | **58** |
| `45\_char\_accuracy` | 2 | **37** |

The first row is the class to take first: `32\_stroke\_lines`, 145 documents in Google against 1 in
LibreOffice. A rule is emitted as a floating drawing, Google drops the shape and keeps the anchor.

## The stamp, stated plainly

`gverify.py --report` is stricter than the table and counts only results written under the current
engine stamp: 81 verified, of which 1 passes all 42, 59 fail at least one and 21 were refused on page
count. The table joins all 192 scored documents, because the pair of renders is what names a construct
and the stamp does not say which construct failed. So 81 is a re-measurement queue, not a second corpus.

## What is next

`stage.py` says: classify 186 failing documents - the table is older than the results. That table is
`DEFECT-CLASSES-GOOGLE.md`, written by the classifier cron. Until that cron rewrites it the stage cannot
advance to fix, and this cron's classify action repeats. Nothing in this run's remit can move it.
