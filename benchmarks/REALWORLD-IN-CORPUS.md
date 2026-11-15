# The nine-page form class is now in the corpus

## Why

`REALWORLD-FINDINGS.md` established that the synthetic corpus could not see the
largest defect in the project. Nine real documents read median `share@5px` 10.3%
against 0.3% synthetic, and the two worst read **98.7%** and **97.6%** -- both
nine-page bank forms. The corpus had no nine-page form, so it scored those
documents as if they did not exist.

That made the highest-value defect in the project invisible to the fixer. A
fixer that never sees a nine-page form cannot fix nine-page forms.

## What changed

Two documents now travel with the repository in `benchmarks/realworld/`:

    041122-Account_Opening_Form.pdf            9 pages   98.7 %@5, max 937.9 pt
    Account_Opening_Form_Fillable_filled.pdf   9 pages   97.6 %@5, max 358.1 pt

They are copied into the corpus by `corpus()`, which now expects
`211 synthetic + however many real ones exist` instead of a hard 211.

They travel in the repository rather than the release zips on purpose: a cron
that clones the repo gets them with no extra download and no network step that
can fail.

## They are in one directory but they are not one population

The measurement does not care where a PDF came from, so one corpus directory is
right. But the two populations must never be averaged together:

    synthetic 211   median share@5px  0.3 %   120 clean
    real 9          median share@5px 10.3 %     3 clean

`RANKING.csv` covers everything measured. `REALWORLD-RANKING.csv` holds the real
subset's own ranking. Quote both, never one as if it described the other.

## Verified

    corpus() rebuilt:  0/213 -- rebuilding
    corpus count:      213
    041122-Account_Opening_Form.pdf              present
    Account_Opening_Form_Fillable_filled.pdf     present

The patch needed one extra line: `HERE=os.path.dirname(os.path.abspath(__file__))`.
Without it the script could not find the directory beside itself and silently
rebuilt 211 instead of 213 -- which is the failure mode this whole exercise is
about, so it is worth naming: a corpus that quietly stays at the old size looks
exactly like a corpus with nothing new in it.

## A risk this creates, stated before it bites

These two documents are nine pages of dense form each, and measuring one of them
end to end exceeded a 295-second command budget twice while this was being
written. `gate.py` runs under `--budget 250`.

**If the baseline cron cannot fit them, they will land as MEASURE-ERROR rows.**
That is the correct behaviour -- a document that fails to measure is recorded,
never dropped -- but it means the fixer still would not see them. The next piece
of work is to make the per-document measurement resumable page by page, the way
the 18-page screenshot was measured, so a nine-page form completes across two
commands instead of failing inside one.
