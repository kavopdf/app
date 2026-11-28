# P2W Classifier - Run Report

**28 Nov 2026 · 08:06 IST**

> 35 classes cover 158 failing documents across 206 measured in Google.

This run regrouped the measurement rather than re-taking it. The .docx class table was refreshed from the ranking and now carries the handbook the baseline added, which had no row before and was the single reason the classify gate was refusing; the .txt classes and the Google table were regenerated from the same engine, and the round moved on to fix.

## Classes, biggest first

| class | open | documents |
|:--|--:|--:|
| `18\_displacement` | 108 | **89** |
| `59\_shape\_anchor` | 50 | **39** |
| `60\_text\_column\_right\_edge` | 59 | **18** |
| `47\_margins` | 27 | **15** |
| `35\_rotation` | 12 | **12** |
| `43\_within\_10pt\_x` | 13 | **7** |
| `66\_table\_cell\_width` | 6 | **6** |
| `17\_matched\_runs` | 30 | **5** |
| `63\_table\_rows` | 4 | **4** |
| `53\_embedded\_faces` | 4 | **4** |
| `26\_text\_overlap` | 19 | **3** |
| `62\_table\_columns` | 3 | **3** |
| `05\_chars\_extra` | 3 | **3** |
| `04\_chars\_missing` | 54 | **2** |
| `45\_char\_accuracy` | 33 | **2** |

## Where the measurement stands

| | |
|:--|--:|
| measured in Google | **206** |
| refused on page count | **8** |
| clean in Google | **48** |
| round | 1 of 3 |
| phase | `fix` |

The top class is `18\_displacement` at 89 documents. Take one class at a time and let the gate decide.

