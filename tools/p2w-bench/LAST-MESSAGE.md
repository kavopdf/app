# P2W Fixer - Run Report

**26 Nov 2026 · slot 04:27 → running IST**

> No change was kept this run. The numbers below say what was tried, and the gate is why.

## Progress

| | |
|:--|:--|
| Check-instances passing | **3018** of 3256 (92.7%) on 73 documents |
| Check-instances still failing | **238** |
| Kept attempts vs documents clean | **15** classes with a kept attempt, **52** documents clean |
| Document-moves this run | **0** — 2 attempt(s), 0 kept |
| Regressions | **none** |
| **Fixed - Google, every applicable check** | **7** of the **73** re-measured on this engine — **135** of the 208 scored are still on an older engine |
| Who re-measures them | the **:20 gverify** cron, about **3** run(s) for the 135 outstanding |
| Classes solved | 0 of 40 clear — 40 class(es) still have an OPEN document |
| Working on | `t12_word_invention` - taken from the pending list (28 still open), not a new class |
| The rotation says | `18_displacement` - the run chose `t12_word_invention` by hand instead |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 05:12 | **refuted** | 0/213 | U+FFFD -> raw character code in `PdfToWord.processTextPosition`. 041122-Account_Opening_Form went from 2 failing checks to 5: t01 99.9 -> 98.2, t03 pass -> fail, t07 pass -> fail, t12 14 -> 141. Reverted. The glyph truth's own record says why: `unnameable: 127` — the source's 127 glyphs have no name, so U+FFFD is the faithful answer and t06 counting it is the instrument's inconsistency, not the writer's defect. |
| 05:33 | **lead** | 0/213 | annotation-meta .txt patch. `600_reviewed_invoice_with_annotations` FAIL(t12 83) -> **PASS**, and `word/document.xml` byte-identical on 600 / 041122 / 601. Predicted 204 -> 205 of 213 .txt clean. Not committed: the gate needs the .docx table re-measured on the new fingerprint, and `p2w.py` measured 24 then 18 of 212 with `remaining` rising 188 -> 194 — it does not carry progress between calls, so a 212-document re-score does not fit a slot. `PATCHES/txt-meta-annotation-26NOV-relay.patch`, `FINDINGS/TXT-600-ANNOTATION-META-MEASURED-CLEAN-UNLANDABLE-26NOV-relay.md`. |

## The txt

| | |
|:--|:--|
| Measured | **1.3 h ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **204** (95.8%) |
| Failing at least one check | **9** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 3 documents |

## Subagents

| Agent | Sent to find | Landed | Finding |
|:--|:--|:--|:--|
| A | is `04_chars_missing` a real Google defect or a check blind to text boxes | yes | Google does not drop the shape: it rasterises `<w:txbxContent>` to a picture, so the characters never reach the text layer. A check fix flips **21** `04` rows and **0** documents clean, because `04` is never a document's only failure — and it would hide a real engine defect. `FINDINGS/04-chars-missing-GOOGLE-RASTERISES-THE-BOX-CHECK-FIX-IS-NOT-THE-FIX-26NOV-relay.md` |
| B | root-cause `59_shape_anchor` | yes | Not its own construct. On HEAD only **17** documents fail it, **12** of those also fail `18_displacement`, and **0** have `59` as their only failure, so clearing it flips **0** documents. The charge is vertical, i.e. 18's line construct. One real writer defect found: `stampBox:5475` takes the box from the text frame's union, not the path (72.94 pt vs the source's 63.60). `FINDINGS/59-shape-anchor-IS-NOT-ITS-OWN-CONSTRUCT-26NOV-relay.md` |

## Timing

| | |
|:--|:--|
| Slot window | 04:27 → running · 1h 06m |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 1 |
| Longest silence | **38.0 min** — from 04:29:30, after `heartbeat before any claim: reverted engine rebuilt, corpus reconverte` |
| Silences over 2 min | 2 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |

### Where the time went

| Phase | Time | |
|:--|--:|:--|
| report - the report and the chain | **1h 05m** | `######################` |

## Verdict

The class was chosen because `classpick.py` refuses a new class while 28 pending items are open, and
`step_txt.py` ranked `t12_word_invention` worst — 3 documents, worth **11.7** clean documents, with
`600_reviewed_invoice_with_annotations` one check away from clean. It is one check away no longer: the
patch that clears it is measured and in `PATCHES/`. What stopped it is not the construct but the gate's
input — see `BLOCKERS.md`, "the .docx table cannot be re-scored inside a slot". Until `p2w.py` resumes
across calls, **every** engine change is unlandable, including one that cannot move a `.docx` byte, and
that is the largest single thing in front of this pipeline.
