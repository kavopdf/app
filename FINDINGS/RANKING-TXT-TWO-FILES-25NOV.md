# Two files named RANKING-TXT.csv, 50 documents apart

**25 Nov 2026, fixer slot 14:17.** Measured, not remembered.

Pending item 4 has asked for two days: *"why do RANKING-TXT.csv and the report disagree by 50
documents"*. It is not a measurement drift and it is not a denominator change. There are two files
with the same basename, and the one a reader opens by name is the one nothing updates.

| path | documents failing | most common | last commit that wrote it |
|:--|--:|:--|:--|
| `tools/p2w-bench/RANKING-TXT.csv` | **64** | `t13_amount_columns` (30) | `13601fb4` - "the txt is scored across the whole corpus for the first time, and 64 documents fail" |
| `tools/p2w-bench/txt/RANKING-TXT.csv` | **14** | `t12_word_invention` (8) | `0cefe274` - "txt: restamp all 213 with current verifier (engine b7699196), 199/213 clean" |

64 - 14 = **50**. That is the disagreement, to the document.

## Which one is true

`tools/p2w-bench/txt/` is the store. Its `ENGINE-STAMP.json` reads `981ff1fa35e2cf67`, which is the
engine this pod has compiled and the fingerprint `regress.py --check` prints. The top-level file
carries no stamp and was last written by the first whole-corpus txt pass, before the verifier was
restamped.

Every reader already points at the store, which is why the pipeline's own numbers are right and only
a reader is wrong:

    cronreport.py:38   TXT = os.path.join(HERE, "txt", "RANKING-TXT.csv")
    health.py:35       TXT = os.path.join(HERE, "txt", "RANKING-TXT.csv")
    pending.py:260     _ta = _age_h(os.path.join(HERE, "txt", "RANKING-TXT.csv"))
    classify_txt.py:26 RANK = os.path.join(TXT, "RANKING-TXT.csv")

`grep -rn RANKING-TXT tools benchmarks` finds no reader of the top-level copy.

## Why it survived

Nothing deletes anything here, so the frozen copy cannot be removed - and it should not be, it is the
evidence for `13601fb4`. What was missing was a sign on it. `RANKING-TXT.csv.README` now sits beside
it and says, in one line, which of the two is live.

## What this changes

A run that opens `RANKING-TXT.csv` and works the biggest class in it works `t13_amount_columns`
across 30 documents that the current verifier passes. That is the shape of a wasted slot, and it
would look exactly like real work: 30 documents, one class, a plausible construct. The class list to
trust is the one in `txt/`, and `t12_word_invention` (8) is the biggest real one.
