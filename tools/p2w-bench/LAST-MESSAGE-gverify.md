# Google verification — the measurement is complete

**214 of 214 documents have a Google result: 206 scored, 8 refused on page count.** The stage moved from `measure-google` to `classify`.

This run converted the rest of the corpus and measured every document that had no current-engine result. Nothing was re-run to make a number agree, and no engine code was touched.

## The corpus, through the renderer the user opens

| | documents |
|---|---:|
| measured through Google | 214 |
| scored on all checks offered | 206 |
| refused (page count) | 8 |
| pass every check offered | 46 |
| fail at least one | 160 |

## Which check costs how many documents

| check | documents failing |
|---|---:|
| `18\_displacement` | 108 |
| `60\_text\_column\_right\_edge` | 62 |
| `04\_chars\_missing` | 54 |
| `59\_shape\_anchor` | 50 |
| `45\_char\_accuracy` | 33 |
| `13\_text\_colours` | 32 |
| `17\_matched\_runs` | 30 |
| `47\_margins` | 27 |
| `26\_text\_overlap` | 19 |
| `44\_header\_footer` | 19 |

## The capability table

Google Docs vs LibreOffice, same source, same instrument, 206 documents:

| | pass every check offered |
|---|---:|
| LibreOffice | 107 |
| Google Docs | 46 |

| check | LibreOffice fails | Google fails |
|---|---:|---:|
| `18\_displacement` | 53 | 108 |
| `04\_chars\_missing` | 2 | 54 |
| `60\_text\_column\_right\_edge` | 18 | 62 |
| `59\_shape\_anchor` | 16 | 50 |
| `45\_char\_accuracy` | 2 | 33 |
| `13\_text\_colours` | 1 | 32 |
| `44\_header\_footer` | 0 | 19 |

## What is next

Stage is `classify`: 160 failing documents, and the class table is older than these results. Grouping them into classes is the classifier's slot, not this one.

## The commit did not land, and the reason is not this run

`regress.py --check` refuses at this tree with the results removed as well, so it is not a verdict on these measurements. It prints two things:

- `ENGINE CHANGED (docx): table measured on d28ca7516c3f9165, the tree is a05b20eb05fe0fc8`
- `ENGINE CHANGED (txt): table measured on 74a152e7d3fb3d26, the tree is 72ff003db5871587`

The engine in the tree has never been stamped against the tables, so the gate refuses every in-scope commit — including a report. With these results in place it also lists documents that fail more of Google's checks than the committed results did; that list is the same engine drift seen from the other side, and it is the fixer's to resolve, not this cron's.

The measurements are preserved outside the sandbox so the next run does not pay for them again.
