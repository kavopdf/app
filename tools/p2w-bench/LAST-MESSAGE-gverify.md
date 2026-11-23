# P2W Google Verify — Run Report

**23 Nov 2026 · stage classify**

160 of 213 documents now carry a Google result measured on the current engine stamp: 28 pass all 42 checks, 107 fail at least one, 25 were refused on page count and are counted separately, never as passes.

| | |
|:--|--:|
| verified on the current engine | 160 |
| pass all 42 | 28 |
| fail at least one | 107 |
| refused on page count | 25 |

Top failing checks in Google, by document count:

| check | Google |
|:--|--:|
| 18\_displacement | 56 |
| 04\_chars\_missing | 47 |
| 59\_shape\_anchor | 35 |
| 60\_text\_column\_right\_edge | 34 |
| 25\_invisible\_text | 28 |

## What this run did

Measured the next block of the corpus through both renderers on engine 98be7c3c — Google Doc upload, PDF export, the 42 checks, and the LibreOffice render of the same .docx for the pair. Results for both directories are committed and pushed.

One document did not land. 74\_balance\_sheet\_indented\_subitems now fails 18\_displacement in Google on this engine, where its committed result was clean. The commit gate refused it as a Google regression and has no override, which is the gate working. That document's committed result was left as it was so the rest of the batch could land, and the refused measurement is written up in full in FINDINGS with its result file beside it. It is the fixer's class, not this cron's.

## Why the capability table was not written

stage.py says classify, but that count comes from result files, not from results stamped with the current engine — the fault BLOCKERS already records against it. The documents outside the 160 verified above still carry a result from an older engine, so a matrix over them would print a Google/LibreOffice pair measured on two different engines and call it "same engine". That is a table the fixer would act on wrongly, so it was not generated.

Next: keep measuring. The remaining documents need a Google result on this engine before the table is worth writing.
