# P2W Google Verify - Run Report

**21 Nov 2026 · stage classify**

> 81 of 213 documents carry a Google result measured on the current engine: 6 pass all 42, 54 fail at least one check, 21 refused on page count.

## Measured

| | |
|:--|--:|
| verified on the current engine | **81** |
| pass all 42 | **6** |
| fail at least one check | **54** |
| refused on page count | **21** |

## Checks that fail, current engine

| check | documents |
|:--|--:|
| `05\_chars\_extra` | 37 |
| `32\_stroke\_lines` | 37 |
| `18\_displacement` | 23 |
| `47\_margins` | 11 |
| `60\_text\_column\_right\_edge` | 11 |
| `04\_chars\_missing` | 10 |

## Stage

`classify` - the class table is older than the results.

## What this run did

Rebuilt the corpus with the current engine and re-measured a batch of documents through both renderers, Google and LibreOffice, and committed every result. The capability table was deliberately not regenerated: the rest of the corpus still carries no current-engine Google result, so a table built now would compare two different engines and name the wrong construct.

## Next

The remaining documents still need a current-engine Google result before the matrix means anything. `gverify.py --plan` lists them, smallest first.
