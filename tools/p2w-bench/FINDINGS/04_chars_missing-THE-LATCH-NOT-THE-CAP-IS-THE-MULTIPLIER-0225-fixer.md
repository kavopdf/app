# 04_chars_missing — the latch, not the 120 pt cap, is the multiplier. And on 47 of 64 the box is a stamp, not body text.

**25 Nov 2026, 02:20–02:55 IST, fixer.** Two sub-agents plus a direct conversion census. No engine change
landed. This file corrects a premise the FIXER-BRIEF carries, and it corrects it with counts.

## The premise in the brief

> "Six of the ten docx classes are one construct … a vertical gap wider than `gapCapTw()` = 120 pt …
> That single threshold is ~166 document-failures across `04_chars_missing`, `45_char_accuracy`,
> `13_text_colours`, `44_header_footer` and `17_matched_runs`. **It is the largest engine defect anyone
> has found.**"

The construct is real and the cap does contribute. **The cap is not what puts most of the text in the
boxes.** Two independent measurements agree:

| source | cap-attributable | latch-attributable (`ctx.positioned`) |
|---|---:|---:|
| sub-agent census over 213 (`-Dp2w.pagepos=0` counterfactual) | 1,469 chars over 23 of 35 positioned pages | **24,920 chars over 655 lines** |
| the cap rule judged per line, shipped build | 12 lines / 358 chars | — |

`ctx.positioned` is a **page-local latch read in exactly three places, all in `para()`**
(`DocxWriter.java:3101`, positioned branch 3126–3133 and 3144). Once one line on a page is anchored —
by the cap, by the zero-gap rule, or by a stamp — **every later line on that page is anchored too.** The
counters do not show this: `zeroGapAnchored` reads 2 on a document carrying 189 boxes, because the
counters see the rule and not the latch.

That is why `-Dp2w.pagepos=0` (do not latch) is worth 4,762 characters while `-Dp2w.zganchor=false` is
worth 0 documents: the rule is 12 lines, the latch is 655.

## The other half: most of the 64 boxes are stamps

Every one of the 64 documents failing `04_chars_missing` was converted at HEAD and its
`word/document.xml` read for `<wps:txbx>` count and characters inside `<w:txbxContent>`:

| boxed characters at HEAD | documents |
|---|---:|
| 0 (box removed by an earlier fix — check fails for another reason) | 7 |
| 4–92 (one to three small boxes — **stamps, ticks, a footer line**) | 30 |
| 194–627 | 20 |
| 1358–2942 (body text routed into boxes) | 3 |

**47 of the 64 carry fewer than 200 boxed characters.** On those, emptying the boxes cannot make the
document clean — the 04 deficit is a stamp whose text Google rasterises, and a stamp is *supposed* to be
a box. The "54 of 65 carry text-box text and 0 of 125 that pass" separation is true and it is not the same
statement as "54 documents are one construct": 37 of those 54 carry under 200 characters.

## What the switches actually do — measured on the carriers

`java -Dp2w.pagepos=0 -Dp2w.anchorkeep=0 ConvertOne <pdf> <out>`, boxes and boxed characters in
`word/document.xml`:

| document | HEAD | pagepos=0 + anchorkeep=0 | + zganchor=false |
|---|---|---|---|
| `69_two_col_legal_numbered_clauses` | 36 boxes / 1358 c | 9 / 367 | **7 / 242** |
| `academic-paper-ieee-2col-abstract` | 51 / 2942 | **3 / 181** | — |
| `323_credit_card_statement` | 13 / 222 | 6 / 35 | **4 / 26** |
| `311_fir_police_form` | 3 / 206 | **1 / 30** | — |
| `322_mutual_fund_factsheet` | 8 / 362 | 5 / 292 | — |
| 47 other 04-failing documents | 1–31 boxes | **unchanged** | — |

Page counts unchanged on every document converted (ConvertOne `pages=` identical in both builds).

**None of the three switch combinations reaches zero boxes on any document measured.** So the pair is a
real, large reduction on the body-text carriers and it is **not** a fix on its own: 04 still fails because
the residual box still rasterises.

## The patch that was written and not kept

A sub-agent wrote a 102-line `spendWideGap()` patch (foot-band pitch sites only, behind
`-Dp2w.spendfoot`). It was applied, the engine rebuilt, and **it is a no-op on all three documents
tested** (`69`, `323`, `311` — box counts identical to HEAD) because its foot-band guard does not fire on
them. Reverted. The patch is in the handoff, not in the tree.

## What this means for the next run

1. **Stop quoting "166 document-failures from the 120 pt cap".** The cap is ~1.5k characters; the latch is
   ~25k. A run that spends its slot on the cap is working the smaller half.
2. **The target is the latch**: after anchoring a line, flow should resume at the anchored baseline
   (`anchorkeep=0` semantics) rather than anchoring the rest of the page. That change exists as a flag and
   is measured above; it needs a corpus pass and a Google read, not more analysis.
3. **Do not expect 04 to close by removing boxes.** On 47 of 64 the box is a stamp. `04_chars_missing`
   needs a rule about *what kind* of text a box may carry — body text may not, a stamp may — or the class
   is partly unsatisfiable by construction, exactly as `04_chars_missing` already records for `601_fillable`.
4. The honest ceiling of the switch pair on the body-text carriers measured here: 69 goes 1358 → 242
   characters of boxed body text, i.e. 82 % of the exposure removed and the document still not clean.
