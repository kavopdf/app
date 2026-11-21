# The carrier fix is right on 2 documents and destroys 59

**22 Nov 2026, relay slot 01:16.** Measured, not argued. Engine built from HEAD plus
`patches/rule-carrier-followed-by-block-2008.patch`, all 213 `.docx` rebuilt, XML read back.

## What the previous slot handed over

`17` and `53` go 40/42 -> **42/42** in Google when one empty block follows each rule carrier.
That measurement stands. What was never measured is what the carrier does to the other 211
documents, because the slot ran out before the corpus was rebuilt.

I rebuilt it. The answer is that the construct, as patched, converts **4595** shapes into
floating carrier tables across **183 of 213** documents. It is not a rule fix at that scale;
it is a structural rewrite of every ruled table in the corpus.

## The damage, per document

| document | HEAD | patched | |
|:--|:--|:--|:--|
| `375_attendance_register` | 1 table, 13 rows, 456 drawings | **443 tables, 455 rows, 14 drawings** | a 13-row register becomes a 455-row one |
| `341_shipping_manifest` | 1 table, 25 rows, 301 drawings | **276 tables, 300 rows, 26 drawings** | |
| `324_loan_amortisation_schedule` | 6 tables, 246 rows, 1483 drawings | **1236 tables, 1476 rows, 253 drawings** | |
| `17_three_column_widths_txtpos` | 0 tables, 2 drawings | 2 tables, 2 carriers | the intended fix |

The character count is preserved in all of them (`text=88 / 75 / 45` unchanged), so
`05_chars_extra` will not fire and the `.txt` is unchanged. **The regression is invisible to
every check the gate runs except a full Google render**, which is exactly why it needed one.

## The cause: the predicate is symmetric

```java
float lo = Math.min(s.wPt, s.hPt), hi = Math.max(s.wPt, s.hPt);
return lo <= RULE_MAX_PT && hi > 2f && hi >= lo * 4f;
```

A table cell's **vertical** separator is 0.4 pt wide and a row tall - one side under 4 pt, the
other four times longer. It satisfies the test. `ruleCarrier` then writes it as a floating 1x1
table 8 twips wide, and `32_stroke_lines` is not about it at all.

Widths, read out of the carriers the patch actually wrote:

| document | carriers | `w:tcW` |
|:--|--:|:--|
| `17_three_column_widths_txtpos` | 2 | 9666 twips |
| `bank-statement-horizontal-rules-only` | 39 | 10091 twips |
| `boq-horizontal-rules-only` | 33 | full width |
| `375_attendance_register` | 442 | **8 twips** |
| `341_shipping_manifest` | 275 | **8 twips** |
| `324_loan_amortisation_schedule` | 1230 | **8 twips** |

The corpus separates cleanly: **987 horizontal carriers in 160 documents, 3608 vertical ones in
59 documents, 23 documents that have only verticals and would be left untouched.**

## The guard, and the test of it

A rule is horizontal. `if (s.wPt < s.hPt) return false;` before the ratio test.

Prediction written to `/scratch/work/PREDICTION.txt` **before** the build: the three destroyed
documents become byte-identical to HEAD, `17` keeps its 2, `bank-statement` keeps its 39.

| test | expected | measured |
|:--|:--|:--|
| `324` guarded vs HEAD | identical | **identical** |
| `341` guarded vs HEAD | identical | **identical** |
| `375` guarded vs HEAD | identical | **identical** |
| `17` guarded carriers | 2 | **2** |
| `bank-statement` guarded carriers | 39 | **39** |

Saved as `patches/rule-carrier-horizontal-only-2008.patch` (211 lines, applies to the pristine
tree, supersedes `rule-carrier-followed-by-block-2008.patch`).

## What is still unproven

The 987 remaining horizontal carriers, in 160 documents, are **not measured in Google**. The
guard removes the destruction; it does not show that a horizontal carrier is harmless where the
page drew a table's own row rule rather than a standalone line. That is the next measurement and
it is cheap now: 160 documents, and `17`/`53` are already known-good.

## A second, unrelated finding

`patches/rule-carrier-per-rule-2008.patch` and `patches/rule-carrier-tblppr-2008.patch` are
**byte-identical** (md5 `8473b14274c0aa827432895733cbba7f`) under two names, and both conflict
with `followed-by-block-2008` on the same hunk. LAST-MESSAGE.md's "apply `per-rule` then
`followed-by-block`" fails `git apply`; only one of the three can ever land.
