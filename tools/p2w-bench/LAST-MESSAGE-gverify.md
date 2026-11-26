# Google verify - run report

**27 Nov 2026 · stage measure-google**

The Google measurement is finished for every document that can land: **197 of 213** carry a result on
the engine in the tree. The remaining **16** are measured but held back, because the commit gate reads
them as worse than the committed verdicts they replace - see "The 16 that cannot land" below.

## Where the corpus stands

| | |
|:--|--:|
| documents in the corpus | **213** |
| carry a Google result on the current engine | **197** |
| scored against the 42 checks | **189** |
| refused on page count (not a pass, not a score) | **8** |
| pass every check offered | **42** |
| fail at least one | **147** |

## What this run did

The pod came up cold: no corpus, no compiled engine. The corpus was built in slices to **213 of 213**
.docx, then the rest of the corpus was rendered through Google Docs and scored. Nothing in the engine
was touched - this cron measures, the fixer changes.

## The checks Google fails, worst first

| check | documents |
|:--|--:|
| `18\_displacement` | **95** |
| `60\_text\_column\_right\_edge` | **54** |
| `04\_chars\_missing` | **46** |
| `59\_shape\_anchor` | **44** |
| `13\_text\_colours` | **32** |
| `45\_char\_accuracy` | **32** |
| `17\_matched\_runs` | **28** |
| `47\_margins` | **26** |

The first row is the class to take: `18\_displacement` is 95 documents and the next is 54.

## The 16 that cannot land

Sixteen measured results are held out of the commit. The committed verdicts they would replace were
measured on engine 025fe9deda5ac7b1 (commit aa496ebe, the page-gap change), which the release commit
ee5a00d6 reverted; the tree's engine is a4d8fca469bba636. Measured on the tree, those 16 fail more of
Google's checks than the committed numbers say, and the gate refuses them with no override.

They keep their stale committed values, so `--plan` picks them up again and they are re-measured and
refused until the engine regression is settled. That is the gate working, but it is also why the corpus
cannot report 213 of 213: `stage.py` reads the committed results, so it stays on measure-google with
**16 to go** and the classify stage cannot open. The row is in `BLOCKERS.md` with the per-document
counts and what would overturn it.

## Next

Measure those 16 again once the engine question is settled, then the stage moves to classify and the
capability table gets written from a complete corpus.
