# P2W Google Verify - Run Report

**24 Nov 2026 · 04:26 IST · stage classify**

> 190 of 213 measured in Google, 23 refused on page count. Google passes all 42 on 29; LibreOffice on 124.

## Measured

| | |
|:--|--:|
| scored | **190** |
| refused on page count | **23** |
| clean in Google | **29** |
| clean in LibreOffice | **124** |

## Checks Google fails and LibreOffice does not

| check | Google | LibreOffice |
|:--|--:|--:|
| `18\_displacement` | **103** | 20 |
| `04\_chars\_missing` | **65** | 2 |
| `25\_invisible\_text` | **48** | 0 |
| `60\_text\_column\_right\_edge` | **56** | 18 |
| `59\_shape\_anchor` | **45** | 9 |
| `45\_char\_accuracy` | **37** | 2 |
| `13\_text\_colours` | **32** | 1 |
| `44\_header\_footer` | **30** | 0 |

The first row is the class to take: `18\_displacement`, 103 documents in Google against 20 in LibreOffice.

## What this run did

`stage.py` said **classify**, so no document was measured and no engine code was touched.

- `classify_google.py --check` said **STALE, regenerate it**; it was run, it wrote `benchmarks/DEFECT-CLASSES-GOOGLE.md`, and a second `--check` said **up to date**. The table now covers 190 documents with both renders.
- `benchmarks/GOOGLE-VS-LIBREOFFICE.md` was rewritten from `gverify.py --matrix` and diffs clean against it, keeping the engine-coverage note it carries.

## Where the numbers come from

| source | what it says |
|:--|:--|
| `gverify.py --report` | 209 verified, 29 pass all 42, 157 fail at least one, 23 refused |
| `stage.py` | corpus 212, measured 213, scored 190, refused 23, failing 161 |
| `gverify.py --matrix` | 124 of 190 clean in LibreOffice, 29 of 190 clean in Google |

The two failing-document counts differ because the populations differ: `--report` scores everything with a Google result, the class table only the 190 that have both renders. A refused document is counted separately and is not a pass.

## Next

The class table is now newer than the results, so the evidence moves the pipeline to **fix** - one class at a time, starting with `18\_displacement`. That is the fixer's stage, not this cron's.
