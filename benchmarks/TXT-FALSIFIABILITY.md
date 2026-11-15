# Can each .txt check actually fail?

A check that cannot fail is not a pass; it is a bug in the check. The 47 docx
checks were measured and 66 % of their passes could not have failed. The 12
.txt checks had never been tested the same way. This is that test.

Method: take a source PDF and the .txt the engine wrote for it, confirm the
baseline, then apply one mutation per check -- each designed to break exactly
that check -- and see whether its verdict flips.

Document: `12_stamp_across_page_break` (2 pages).
Baseline: `10/12 applicable, 9 passed, 2 abstained  FAIL`
`t12_word_invention` was already failing at baseline (5 invented words).

## Result, stated exactly

| check | verdict | evidence |
|---|---|---|
| t01_word_accuracy | **PROVEN** | deleting words flips it |
| t02_position | **PROVEN** | stripping leading spaces flips it |
| t03_symbols | **PROVEN** | replacing non-ASCII with '?' flips it |
| t04_structure | **PROVEN** | deleting half the lines flips it |
| t07_symbol_counts | **PROVEN** | adding 40 rupee signs flips it |
| t08_line_order | **PROVEN** | reversing the lines flips it |
| t11_page_breaks | **PROVEN** | removing U+000C flips it |
| t12_word_invention | **PROVEN** | failing at baseline: 5 invented words in the .txt |
| t06_encoding | **INCONCLUSIVE** | applicable (source 2842, txt 0), but the mutation did not produce invalid bytes -- my harness wrote the file as UTF-8, which re-encoded them. The check was never actually given bad input. |
| t10_page_completeness | **INCONCLUSIVE** | applicable (source 2, txt 2); removing a page did not change the counted value, so the mutation did not reach the condition the check tests |
| t09_page_furniture | **NOT TESTED** | abstained -- source 0, no running heads on this document |
| t13_amount_columns | **NOT TESTED** | abstained -- source 0, no money column on this document |

**8 of 12 proven able to fail. 2 inconclusive because the harness, not the
check, was at fault. 2 untested because this document does not exercise them.**

## Why this is reported as a partial result

The first run of this harness printed `12/12 checks can fail`. That was wrong:
it counted harness write-failures as successes. A test that reports its own
broken cases as passes is exactly the disease this whole exercise is about, so
the summary was corrected to count only `PASS` as proof, and the two
inconclusive rows are stated as inconclusive rather than folded into either
column.

## What must happen before these checks are quoted

1. `t06_encoding` needs a mutation that writes genuinely invalid UTF-8 bytes
   (`open(path,'wb').write(b'\xff\xfe')`), not a str round-trip.
2. `t10_page_completeness` needs a document with three or more pages so that
   removing one changes the count.
3. `t09_page_furniture` and `t13_amount_columns` need documents that exercise
   them: one with running heads, one with a money column.
4. Until all twelve are proven, the .txt checks stay advisory and no score may
   be quoted from them.
