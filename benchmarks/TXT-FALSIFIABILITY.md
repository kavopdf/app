# .txt falsifiability — final result

A check that cannot fail is not a pass; it is a bug in the check. The 47 docx
checks were measured at 66 % unfalsifiable passes. The 12 .txt checks had never
been tested. This is the finished test.

## Result: 11 of 12 proven able to fail

| check | verdict | how it was proven |
|---|---|---|
| t01_word_accuracy | **PROVEN** | deleting five common words |
| t02_position | **PROVEN** | stripping leading spaces |
| t03_symbols | **PROVEN** | replacing every non-ASCII character with `?` |
| t04_structure | **PROVEN** | deleting every second line |
| t06_encoding | **PROVEN** | prepending raw `\xff\xfe\x00\x00` bytes |
| t07_symbol_counts | **PROVEN** | appending 40 rupee signs |
| t08_line_order | **PROVEN** | reversing line order |
| t10_page_completeness | **PROVEN** | blanking a whole middle page |
| t11_page_breaks | **PROVEN** | removing every U+000C |
| t12_word_invention | **PROVEN** | already failing at baseline: 5 invented words |
| t13_amount_columns | **PROVEN** | already failing at baseline |
| t09_page_furniture | **BLIND** | three mutations, none flipped it |

## The one that would not fail

`t09_page_furniture` claims: "one copy of each running head per page it belongs
to." On `324_loan_amortisation_schedule` -- a document where the check reports
itself APPLICABLE -- these three mutations all left it passing:

1. duplicating the first line of every page twice
2. duplicating it three times on every page
3. injecting the first non-blank line of each page three times

Two possible explanations, and they are not the same thing:

* the check tests "at least one copy is present" rather than "exactly one", in
  which case its stated meaning and its implemented meaning differ; or
* it cannot see duplicate furniture at all, in which case it is not a check.

Deciding which requires reading its predicate, not another mutation. Until that
is done it must not be quoted as evidence that page furniture is correct.

## What changed between round 1 and this round

Round 1 reported `12/12` in its first run, which was wrong -- it counted
harness write-failures as successes. Corrected to count only PASS. Round 1 then
reported 8/12 with four unresolved, and every one of the four was a harness
defect, not a check defect:

* `t06_encoding` was written back as UTF-8, so the check never received invalid
  bytes. Fixed by writing raw bytes with `open(path,'wb')`.
* `t10_page_completeness` was truncated, which does not remove a page marker.
  Fixed by blanking an entire middle page.
* `t09` and `t13` were run on a document that did not exercise them. Fixed by
  finding documents where each reports itself applicable.

Three of the four are now proven. The fourth is the one above.

## t09 was fixed 20 minutes after this was written

This table was the state at 21:03. At 21:23 the `min()` cap in `t09` was removed and the check was
re-tested: duplicating every running head 2x and 3x on `412_page_labels_roman` now fails it, where it
passed before. See `benchmarks/T09-FURNITURE-FIX.md` for the three-row proof.

**The result is 12 of 12, not 11 of 12.** The row above is left as it was measured because a record
that gets edited to match the present is not a record.

## Standing rule - withdrawn

The rule that stood here said "until t09 is resolved, the .txt checks remain advisory and no score
may be quoted from them". t09 is resolved, so the rule no longer holds and the .txt scores may be
quoted. It is withdrawn, not deleted: it was the right rule while it was true, and a reader who saw
it quoted somewhere should be able to find out why it stopped.
