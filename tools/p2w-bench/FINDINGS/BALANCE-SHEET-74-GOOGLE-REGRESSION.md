# 74_balance_sheet_indented_subitems: 42/42 -> 41/42 in Google on engine 98be7c3c

**Measured 23 Nov 2026, gverify run.** Same source PDF, same .docx built by ConvertOne at engine
`98be7c3c`, uploaded as a Google Doc, exported to PDF, scored by the 42 checks.

    engine 462353f9 (committed result)   42/42   no failing check
    engine 98be7c3c (this run)           41/42   18_displacement

Re-measured twice more in the same run, from the same exported PDF: 41/42 both times, the same
single check. It is reproducible, not a borderline reading.

## Why the result is not in `benchmarks/gverify/`

`regress.py --check` refuses the commit:

    docx: 1 document(s) fail MORE of Google's 42 checks than the committed results:
      74_balance_sheet_indented_subitems  0 -> 1 failing
    Google is the renderer the user opens. LibreOffice agreeing is not a defence.

The gate has no override and this run did not look for one. The document's committed result was left
at its `462353f9` value so the other nineteen documents of the batch could land; the refused result is
stored beside this note as `74_balance_sheet_indented_subitems.google-98be7c3c.json`.

## What this is

A real Google-side regression introduced between engine `462353f9` and `98be7c3c`. It is the fixer's
class, not this cron's: the fix is a change to whatever construct now places the sub-item rows on that
balance sheet wrongly, measured before and after like any other.

What would overturn this: a measurement of the same document on the current engine that reads 42/42,
or a gate run that reports it clean.
