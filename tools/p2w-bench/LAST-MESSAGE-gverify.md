# P2W Google Verify - Run Report

**21 Nov 2026 · 20:32 IST · stage classify**

> 192 of 213 measured in Google, 21 refused on page count. Google passes all 42 on 6; LibreOffice on 122.

## Measured

| | |
|:--|--:|
| scored | **192** |
| refused on page count | **21** |
| clean in Google | **6** |
| clean in LibreOffice | **122** |

## Checks Google fails and LibreOffice does not

| check | Google | LibreOffice |
|:--|--:|--:|
| `32\_stroke\_lines` | **145** | 1 |
| `05\_chars\_extra` | **141** | 3 |
| `18\_displacement` | **124** | 20 |
| `04\_chars\_missing` | **66** | 2 |
| `25\_invisible\_text` | **49** | 0 |
| `59\_shape\_anchor` | **58** | 11 |
| `60\_text\_column\_right\_edge` | **58** | 18 |
| `45\_char\_accuracy` | **37** | 2 |

The first row is the class to take: `32\_stroke\_lines`, 145 documents in Google against 1 in LibreOffice.

## What this run did

The stage is `classify`, so this run did no measuring and changed no engine code. It regenerated the
capability table from the committed results of both renderers and committed it as
`benchmarks/GOOGLE-VS-LIBREOFFICE.md`, so the classifier cron reads a table that matches the results
on disk. The counts are unchanged from the previous run; only the ordering of tied rows moved.

One caveat about the engine stamp. `gverify.py --report` counts only results written under the current
engine stamp, while the table joins every scored document, because a renderer pair is what names a
construct and the stamp says nothing about which construct failed. The results committed before the
stamp existed were measured on a `.docx` the tree still produces byte-identically, so the pair is
sound; the stamp gap is a re-measurement queue, not a wrong table.

Next: the classifier groups the 186 failing documents into classes, and the fixer takes one class at a
time.
