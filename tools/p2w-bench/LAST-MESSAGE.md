# P2W Google Verify - Run Report

**20 Nov 2026 · 14:24 IST · stage classify**

> 192 of 213 measured in Google, 21 refused on page count. Google passes all 42 on 7; LibreOffice on 122.

## Measured

| | |
|:--|--:|
| scored | **192** |
| refused on page count | **21** |
| clean in Google | **7** |
| clean in LibreOffice | **122** |

## Checks Google fails and LibreOffice does not

| check | Google | LibreOffice |
|:--|--:|--:|
| `32\_stroke\_lines` | **145** | 2 |
| `05\_chars\_extra` | **141** | 9 |
| `18\_displacement` | **125** | 21 |
| `04\_chars\_missing` | **67** | 9 |
| `25\_invisible\_text` | **49** | 1 |
| `59\_shape\_anchor` | **58** | 13 |
| `13\_text\_colours` | **32** | 1 |
| `45\_char\_accuracy` | **38** | 9 |

The first row is the class to take: `32\_stroke\_lines`, 145 documents in Google against 2 in LibreOffice.

## Where this leaves the pass

Every document now has both renders: `213` through Google (`192` scored, `21` refused on page count)
and `213` through LibreOffice. This run added no new document - the measurement was already complete
when the slot opened - so what it produced is the capability table,
`benchmarks/GOOGLE-VS-LIBREOFFICE.md`, regenerated from the committed JSON and committed.

Two LibreOffice denominators, and both are the tool's:

| source | clean in LibreOffice | of |
|:--|--:|--:|
| the generated report above | 122 | 213 |
| the capability matrix | 108 | 192 |

The matrix counts only the `192` that Google scored; the `21` Google refused still have a good
LibreOffice render, and most of them pass there. Neither figure is a Google pass.

## Stage and what is next

`stage.py` says `classify`, corpus `213`, `185` documents failing at least one check. The table this
run owns is written; the stage turns over when the classifier's own table, `benchmarks/DEFECT-CLASSES.md`,
is newer than the results and names a class for every failing document. Until then the measuring cron
has nothing left to measure, and the fixer has nothing to take.

The class to take first is still `32\_stroke\_lines`: `145` documents in Google against `2` in
LibreOffice - a rule emitted as a floating drawing, which Google drops and keeps the anchor of. It is
already recorded in `FINDINGS/`, so a fixer run must read that before touching it.
