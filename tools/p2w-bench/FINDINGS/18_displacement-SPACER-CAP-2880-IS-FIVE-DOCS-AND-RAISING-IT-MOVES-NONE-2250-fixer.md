# 18_displacement — the 2880-tw spacer cap binds FIVE documents, and raising it to 4320 moves none

**24 Nov 2026, fixer slot 22:20.** Measured locally over all 213 emitted `word/document.xml`, and in
Google on the one document the raise changes construct on.

## What I believed

`FINDINGS/18_displacement-table-spacer-CONFIRMED-6of16-TWO-PAGES-EXACTLY-FULL-1005-f1x.md` says the
2880-twip cap on the table-gap spacer truncates `68_journal_wide_table_spanning` by 4.05 pt, and that
"that cap is reached by exactly one document in the 16". So raising the cap to 4320 looked like a
one-document change with a measured clean behind it.

## What I measured

A census of the `sz=2` spacer paragraph in all 213 emitted files: **133 documents carry one, and FIVE
hit the cap at exactly 2880** - `68_journal_wide_table_spanning`, `330_cad_drawing_sheet`,
`360_restaurant_menu`, `041122-Account_Opening_Form`, `Account_Opening_Form_Fillable_filled`. The
"exactly one" was one *within the 16 solo-18 documents*, not one in the corpus.

Then the change: `Math.min(2880L, ...)` -> `Math.min(4320L, ...)` at `DocxWriter.java:6033` and `:6047`,
engine rebuilt, all 213 re-converted, emitted XML diffed against the pre-change outputs.

**Exactly 4 documents changed, and only one of them changed construct:**

| document | before | after |
|:--|:--|:--|
| `360_restaurant_menu` | `w:line=2880`, refused | `w:line=3159` + `w:before=516` - **now spent** |
| `330_cad_drawing_sheet` | `w:line=2880` | `w:line=3734`, still refused |
| `041122-Account_Opening_Form` | `w:line=2880` | `w:line=3320`, still refused |
| `68_journal_wide_table_spanning` | `w:line=2880` | `w:line=2960`, still refused |

(`Account_Opening_Form_Fillable_filled` was capped but unchanged - its gap was already exactly 2880.)

## The Google measurement

`360_restaurant_menu`, Drive create-as-Google-Doc -> export PDF -> `gverify.py --collect`, probe Doc
deleted:

| | before (HEAD, stored) | after (4320 cap) |
|:--|--:|--:|
| score | 38/42 | **38/42** |
| `worst_dy` | 109.9 | **106.7** |
| failures | 18, 43, 47, 60 | 18, 43, 47, 60 (identical) |

So spending 25.8 pt of gap the page drew bought **3.2 pt of worst displacement and no check**. The
document's 18_displacement failure is not this gap.

## What is now true

1. **The cap is not a one-document defect.** Five documents reach it; four of the five are exactly-full
   pages whose guard refuses the split anyway, so raising the cap only enlarges a `w:line` that Google
   delivers at ~22 % - up to +42.7 pt of declared gap on `330_cad_drawing_sheet` - with no measured
   Google result on any of the three.
2. **A spent gap is not a clean document.** The one document the raise does flip into the spent branch
   gains 3.2 pt and stays 38/42. Whatever fails `18_displacement` on `360_restaurant_menu` at
   `worst_dy` 106.7 pt is not a gap the engine failed to declare.

## What I did with it

**Reverted.** The change moves no document towards clean and leaves three documents' Google behaviour
unmeasured in the direction of more declared gap. An unmeasured change in the worse direction is not a
lead worth a corpus. Engine back at HEAD, `regress.py --check` PASS.

## What would prove this wrong

A Google measurement of `330_cad_drawing_sheet` and `041122-Account_Opening_Form` under the 4320 cap
showing either of them CLEANER. Both were skipped for time, not for evidence.
