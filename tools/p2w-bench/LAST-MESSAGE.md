# Fixer report - 2026-11-20 21:57

**20 Nov 2026 · slot 21:57 → running IST · 46 min**

> No engine change was kept this run. What the slot bought is a proven root cause and a patch that
> needs a corpus pass the slot could not afford - and a named wall that has now eaten three runs.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 1 attempt(s), 0 kept |
| Documents improved, round total | 60 of 213 |
| Corpus improvement vs 15 Nov | **+39.61%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **7**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 32 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `t01_word_accuracy` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 22:39 | **reverted** | 2/7 | The U+FFFD is the /ToUnicode CMap's own destination value, not a missing or malformed CMap |

## The finding: the U+FFFD is the CMap's answer, not a failure to parse one

Both bank forms carry 127 tokens of U+FFFD. The carry-over said the source declares U+0124, U+0126,
U+0123 from REAQAG+Effra-Regular, a Type0/Identity-H font. That much was right. What was not known is
where the replacement character comes from, and it is not a missing CMap:

- REAQAG+Effra-Regular carries 91 well-formed beginbfchar entries, one per CID. Four of them map
  their code to FFFD outright: 0123, 0124, 0126, 0127. WWLUSW+Effra-Medium adds 0124 and 0126,
  IWIJEY+Effra-Bold adds 0124.
- pdfbox-android 2.0.27.0 returns that value verbatim. PDFont.toUnicode returns the CMap's mapping at
  PDFont.java:474, and PDType0Font.toUnicode returns at PDType0Font.java:489 before its own
  embedded-cmap fallback can run. A non-null mapping is authoritative.
- The engine then trusts it: PdfToWord.processTextPosition takes the string at line 2101, and
  isJunk() at line 2501 returns false for U+FFFD, so the existing re-decode fallback at lines
  2107-2110 never fires.

Identity-H says the code is the CID, so the code is the only handle the font still gives - which is
also what PDFBox already does for an Identity font with no /ToUnicode at all (PDFont.java:459). The
patch makes the two cases agree, keyed on the font's structure and never on a document id, with
control codes (below 0x20, and 0x7F-0x9F) deliberately keeping their U+FFFD.

Measured with the engine built from the patched tree, both documents converted with ConvertOne and
scored by verify\_txt.py - the live .txt check, not a proxy:

| Document | Before | After |
|:--|:--|:--|
| 041122-Account\_Opening\_Form | 7 of 10 checks failing | 3 of 10 checks failing |
| Account\_Opening\_Form\_Fillable\_filled | 7 of 10 checks failing | 3 of 10 checks failing |
| U+FFFD in our .txt, both documents | 127 and 127 | 0 and 0 |

Four checks close on each document - t01\_word\_accuracy, t03\_symbols, t06\_encoding,
t07\_symbol\_counts - and both leave the t01 class. The patch is committed as
FINDINGS/fffd-cmap-destination-2300-fixer.patch and applies clean to e5268fe.

## Why it was reverted, and the wall the next run must go round

The engine change moves the docx fingerprint, so it needs a corpus pass, and the corpus pass is the
part this slot could not buy. screen.py --docs on these two documents did not get past prerender in
three consecutive 295 s calls: soffice takes about 80 s to start and these are nine-page forms, so the
call limit is gone before one document is scored. restamp\_txt.py --run needs /scratch/work/p2w/out,
which only p2w.py --budget populates, and that would have taken four or five more calls.

That is why the change was reverted rather than left in the tree: no RANKING.csv, no STATE-TXT.json,
no ratchet, so the class rows stay OPEN and an unmeasured engine change must not ship. The next run
should budget the whole slot for p2w.py --budget 250 repeated to completion - it fills the .docx and
the .txt for all 213 in one pass - then restamp\_txt.py --run and --apply, classrow.py --write, and
regress.py --check before any commit.

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **186** (87.3%) |
| Failing at least one check | **27** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t08_line_order` - 10 documents |

## Subagents


| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `t01_ToUnicode CMap destination-01` | Is the U+FFFD the CMap's own answer or a parse failu | 22:39 | 17:09 | 0 min |
| `t01_adversarial patch review-01` | How can this Identity-H recovery write wrong text in | 22:43 | 17:13 | 0 min |

Two agents, and they disagree - which is the most useful thing this slot produced.

The first found the mechanism, the file and line, the CMap bytes, and a patch that compiles and
moves the .txt number. The second saw only the diff and says do not land it: the helper writes the
CID as a code point, and the CIDs here are 0x0123/0x0124/0x0126/0x0127, which are g-with-cedilla,
H-circumflex, H-stroke and h-stroke. A bank form does not draw those. If the page really draws a
ligature, this replaces 127 visible U+FFFD with 127 wrong letters - wrong text that looks like text,
which nothing downstream can detect.

The measurement above cannot settle that argument, and this is the part worth carrying forward:
t01\_word\_accuracy passes because our .txt now agrees with the source extraction, and the source
extraction is pymupdf, which resolves an Identity font the same way. Two extractors making the same
assumption agree with each other whether or not the assumption is true. The check moved; the
question did not.

So the first thing the next run does is not measure anything. It renders page 1 of
041122-Account\_Opening\_Form at 150 DPI and looks at the 127 glyph sites with an eye. Ligature or
not decides which of the two agents is right, and it costs one page.

## Timing




| | |
|:--|:--|
| Slot window | 21:57 → 22:43 · 46 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 22 |
| Longest silence | **23.3 min** — from 21:57:13, after `pending.py: reading the pending gate` |
| Silences over 2 min | 3 |
| Obstacles | 0 cleared · 0 need a human |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **42 min** | `####################` |
| record - attempt, handoff, class rows | **0 min** | `#` |
| report - the report and the chain | **3 min** | `##` |

The 23 minute silence is the subagent running inline, not a dead run.

## One thing the pipeline got wrong today, worth a person's eye

The 21:36 run pushed its final report at 16:19:40 UTC and exited without releasing the fixer slot.
This run's claim was refused at 21:57 because the slot still read busy - and the busy check takes the
newest of the claim, the last beat and the mtime of TIMELINE.jsonl, so a run that has already
finished its report can hold the slot for another ten minutes. The claim was cleared by hand after
checking that HEAD was that run's report commit and that no beacon had been written for eight
minutes. A release at the end of a run matters as much as the claim at the start of one.

## Next run

Do not apply the patch first. Render page 1 of 041122\_Account\_Opening\_Form at 150 DPI and look at
the 127 glyph sites - STEP 4c, one page, and it decides which of the two agents is right. If the page
draws a ligature, the fix is the CIDToGIDMap plus the descendant font's own cmap, and
FINDINGS/fffd-cmap-destination-PATCH-REVIEW-2325.md lists the guards the helper would need anyway.
If it draws what the CID names, apply FINDINGS/fffd-cmap-destination-2300-fixer.patch and budget the
whole slot for p2w.py --budget 250 repeated to completion, then restamp\_txt.py --run and --apply,
classrow.py --write, regress.py --check, and commit RANKING.csv with STATE-TXT.json.
