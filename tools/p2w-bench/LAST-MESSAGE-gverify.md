# Google verify - run report

**Stage: `classify`.** All 213 documents now have a Google result: 191 scored, 22 refused on page count. stage.py's next line is "classify 155 failing documents - the table is older than the results", so this run measured nothing. Its remaining job was the capability table, and that is what it wrote.

**The pair, from `gverify.py --matrix`** - same source PDF, same .docx, same instrument, only the renderer differs:

| renderer | pass every check offered |
|---|---:|
| Google Docs | 36 of 191 |
| LibreOffice | 125 of 191 |

**What landed.** `benchmarks/GOOGLE-VS-LIBREOFFICE.md` regenerated verbatim from `gverify.py --matrix` and committed. No number in it changed - the diff is row order only, because the previous copy had been hand-sorted.

**Where Google is the stricter renderer** - top rows of `gverify.py --report`:

| check | Google fails | LibreOffice fails |
|---|---:|---:|
| `18\_displacement` | 103 | 20 |
| `04\_chars\_missing` | 64 | 2 |
| `60\_text\_column\_right\_edge` | 56 | 18 |
| `59\_shape\_anchor` | 45 | 9 |
| `25\_invisible\_text` | 43 | 0 |
| `44\_header\_footer` | 29 | 0 |

`32\_stroke_lines` is 9 in Google against 1 in LibreOffice and `05\_chars\_extra` is 5 against 3 - both are the floating drawing whose shape Google drops and whose anchor it keeps, already recorded in `FINDINGS/`.

**The counts, quoted.** `gverify.py --report`: 209 verified | 36 pass every check offered | 151 fail at least one | 22 refused (page count). stage.py counts 155 failing from every result on disk; the difference of 4 is results whose stamp `--report` will not accept as current.

**Next.** Classify those failing documents - `benchmarks/DEFECT-CLASSES-GOOGLE.md` is older than the results, which is the classifier's slot. No engine code was touched and no Drive file was created this run.
