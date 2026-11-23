gverify run — 23 Nov 2026

Stage: classify. 213 measured through Google, 190 scored, 23 refused on page count. 160 documents still fail at least one check. The capability table is regenerated and committed; measuring is finished for this cron.

The 86 results that carry the current engine stamp read: 13 pass all 42, 50 fail at least one, 23 refused. The 190 scored figures below include results from earlier engine commits, which is what the table reads.

| renderer | passes all 42 |
|---|---:|
| LibreOffice | 122 of 190 |
| Google Docs | 30 of 190 |

## Where the renderers disagree

| check | LibreOffice fails | Google fails |
|---|---:|---:|
| 18\_displacement | 20 | 101 |
| 04\_chars\_missing | 2 | 65 |
| 60\_text\_column\_right\_edge | 18 | 56 |
| 25\_invisible\_text | 0 | 48 |
| 32\_stroke\_lines | 1 | 47 |
| 59\_shape\_anchor | 9 | 45 |
| 05\_chars\_extra | 3 | 43 |
| 45\_char\_accuracy | 2 | 37 |
| 13\_text\_colours | 1 | 32 |
| 44\_header\_footer | 0 | 31 |
| 17\_matched\_runs | 4 | 30 |

Constructs LibreOffice honours and Google does not: 25\_invisible\_text on 48 documents, 44\_header\_footer on 31, 10\_font\_sizes on 6, 23\_line\_pitch on 3, 31\_pages\_lost\_their\_text on 1, 46\_text\_crossing\_rule on 1. Google honours 14\_filled\_shapes where LibreOffice does not, on 2 documents.

## Current-engine failures, by check

18\_displacement 28, 04\_chars\_missing 24, 60\_text\_column\_right\_edge 21, 25\_invisible\_text 19, 59\_shape\_anchor 19, 13\_text\_colours 18, 45\_char\_accuracy 14, 35\_rotation 10, 17\_matched\_runs 10, 47\_margins 8, 43\_within\_10pt\_x 5, 44\_header\_footer 5.

Next: the classifier cron groups the 160 failing documents into classes. No engine code touched.
