# Google verify - run report

**Stage: measure-google.** The corpus is 213 documents. 88 are measured through Google: 82 scored, 6 refused. Next: measure 20 more through Google.

## Where the measurement stands

| | documents |
|---|---:|
| verified | 88 |
| pass every check offered | 17 |
| fail at least one | 65 |
| refused (page count) | 6 |

A refused document is not a pass. The 6 are counted apart from the 65, so nothing in the pass column depends on a refusal.

## Which check costs how many documents

| check | documents |
|---|---:|
| 18\_displacement | 37 |
| 60\_text\_column\_right\_edge | 31 |
| 04\_chars\_missing | 27 |
| 59\_shape\_anchor | 22 |
| 13\_text\_colours | 21 |
| 45\_char\_accuracy | 17 |
| 17\_matched\_runs | 13 |
| 35\_rotation | 11 |
| 47\_margins | 11 |
| 43\_within\_10pt\_x | 7 |

The class to fix is 18\_displacement: 37 of 88 documents, and the widest gap against LibreOffice below.

## The pair - and the caveat that governs it

Google Docs against LibreOffice, 207 documents: LibreOffice 135 pass every check offered, Google 42.

| check | LibreOffice fails | Google fails |
|---|---:|---:|
| 18\_displacement | 20 | 113 |
| 04\_chars\_missing | 2 | 54 |
| 60\_text\_column\_right\_edge | 18 | 62 |
| 59\_shape\_anchor | 11 | 47 |
| 45\_char\_accuracy | 2 | 33 |
| 13\_text\_colours | 1 | 32 |

No row is yet a same-engine pair. Google is on the engine in the tree for 82 of 207 pairs; LibreOffice is on it for 0 of 207. The LibreOffice column therefore describes the .docx an older engine wrote, and it may be read as a construct Google drops only where both halves sit on one engine. Filling the LibreOffice side is the matrix stage, not this one, so this run did not touch it.

## What this run did

Measured 88 documents through the Drive loop and committed every verdict to benchmarks/gverify. It did not change engine code, did not touch the LibreOffice half, and left no Google Doc behind - each one was created in the corpus folder, exported to PDF, and trashed.
