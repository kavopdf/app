# Google verify - 26 Nov, 09:23 IST

**Stage `measure-google`.** 127 of 213 documents now carry a Google result on the tree's engine. The next step is 20 more.

This run measured the next batch through Google Docs, collected every verdict, and committed the results.

| what | count |
|:--|--:|
| verified | 127 |
| scored | 122 |
| pass every check offered | 28 |
| fail at least one | 94 |
| refused on page count | 5 |

A refused document is not a pass: those 5 reflowed onto a different page count and are counted separately, not scored.

## Which check costs what

| check | documents failing in Google |
|:--|--:|
| `18\_displacement` | 52 |
| `60\_text\_column\_right\_edge` | 37 |
| `04\_chars\_missing` | 34 |
| `59\_shape\_anchor` | 33 |
| `13\_text\_colours` | 23 |
| `47\_margins` | 19 |
| `45\_char\_accuracy` | 19 |

The first row is still the class to take: `18\_displacement`, 52 of the 122 scored documents.

## The capability table

| renderer | pass every check offered |
|:--|--:|
| Google Docs - the renderer the user opens | 42 of 208 |
| LibreOffice - local proxy | 135 of 208 |

Only 80 of those 208 pairs have both halves measured on the tree's engine, so read the gap as a direction, not a per-document verdict.

## The one thing that needed a decision

The commit gate refused the batch on `390\_wide\_data\_appendix`: it fails 4 checks where the committed result failed 3, and that committed result was measured on an older engine. Re-running the verifier on the same export reproduced it, so it is not a flake - on this engine the document loses `59\_shape\_anchor` while its displacement improves. Two other documents improved, so the corpus is net better by 2, and it landed under the tool's own named opt-in, `P2W_ACCEPT_WORSE`, which is granted only when the corpus improves in Google. It is written into `BLOCKERS.md` for the fixer; nothing else was waived.

## What is next

`measure-google` again: 20 more documents through Google. Nothing in the engine was touched by this run.
