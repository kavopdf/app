# What is pending, and what blocks each one

Written 18 Nov by the agent, not by a fixer run. Every item here was found by reading the
files, not by guessing, and each one names the command that closes it.

The short version: **nothing on this list can be closed without `java`.** The agent's sandbox
has no `java` and no `scipy`, so it cannot build the engine, cannot convert, and therefore
cannot measure. Every item below is a measurement or a build. They belong to a fixer run.

---

## 1. The cause census covers almost nothing

`tools/p2w-bench/CAUSES.md` opens with its own coverage line, and that line is the problem.
A cause table built from a sample sends a run at the wrong class.

**Close it with:**

    python3 tools/p2w-bench/cause.py --open --limit 25
    python3 tools/p2w-bench/cause.py --report

Run it against docx built by **this** engine. The census reads the rendered docx, so a docx
built by an older engine answers a question nobody asked.

---

## 2. The .docx ratchet cannot compare

    python3 tools/p2w-bench/ratchet.py --check
    DENOMINATOR DRIFT: rows claim x/59, the live instrument reports 47

The stored marks were stamped against 59 checks; `verify_google.py --list-checks` reports 47
today. The gate refuses to compare, which is correct behaviour and not a pass. A reset does
not help - the drift lives in the rows of `RESULTS.jsonl`, not in `RATCHET.json`, and a reset
was tried and changed nothing.

**Close it by re-measuring**, so every row is re-stamped against the live universe:

    python3 benchmarks/p2w.py --budget 250

Then `ratchet.py --check` has something it can compare.

---

## 3. RANKING.csv was published by a different path than the pipeline's own

The 19:12 report says this itself, in its own words:

> The corpus number is real but it was not produced by `benchmarks/p2w.py`. `p2w.py --budget 260`
> does not resume: it restarts `docx 0/213` on every call and spends the whole budget converting,
> so it measured **0 of 213 twice in a row**. The 212-document ratchet was run with
> `screen.py --docs` over the full `RANKING.csv` list instead... That is the same instrument
> `p2w.py` uses, but it is not the pipeline's own publisher, and the next run should confirm
> the two agree.

**What is already checked, and holds:** `RANKING.csv` has 212 rows, no duplicates, no document
in the baseline that is missing from the ranking and none the other way, and **0 documents
worse** than the 15 Nov baseline. So the table is complete and nothing regressed. What is not
checked is whether `p2w.py` would produce the same numbers.

**Close it with:**

    python3 benchmarks/p2w.py --budget 250      # repeat until it reports 213/213
    git diff benchmarks/RANKING.csv             # the two must agree, row for row

If they disagree, `p2w.py` is the publisher and its numbers win; find out why the other path
differed before trusting either.

---

## 4. `416_many_tiny_pages` has never been measured

300 pages in one command, no result written. It is the one document in `EXEMPT.json`, so it is
excluded from every count - but excluded is not measured, and a document nobody has looked at
is a document nobody knows the state of.

**Close it by measuring it alone**, so the per-command limit is not the thing that decides:

    python3 tools/p2w-bench/screen.py --docs 416_many_tiny_pages

If it still cannot finish, say so and leave it exempt. What is not acceptable is leaving it
exempt without ever having tried.

---

## 5. The documents themselves

    benchmarks/RANKING.csv           72 open of 212
    tools/p2w-bench/txt/RANKING-TXT.csv   64 failing of 213

The .txt has one lever worth more than the rest: **`t13_amount_columns` holds 30 documents, and
24 of those fail on nothing else.** One fix that clears that check takes the .txt from 64
failing to 40. The next-largest are `t02_position` (15) and `t12_word_invention` (15).

**No two checks in the .txt move together enough to be called one defect.** Measured on the
corpus: `t02_position` fails alone on 67% of its documents and `t08_line_order` on 50%, and the
two occur together on four. Naming them one cause would hide the second from whoever fixes the
first. `classify_txt.py` therefore names a cause for the set that actually failed.

---

## 6. The .txt setup is written and proved, and is not committed

The whole .txt measurement setup - baseline, marks, ratchet, class table, census, causes,
unmeasured record, `classify_txt.py`, `step_txt.py` - exists in the working tree and is proved
by seven hand-run cases:

    no marks                    -> exit 3, "an empty marks file proves nothing"
    marks present and held      -> exit 0
    a lowered mark              -> exit 1, and the document is named
    a fake universe sha         -> exit 3, both shas printed
    baseline after a scoring pass -> unchanged, byte for byte
    gate with marks missing     -> exit 3
    gate with the store empty   -> exit 3

**It IS committed as of 19 Nov.** It was held back for four days by a 403 that turned out to be the
Sarvam GitHub App missing from the `kavopdf` organization rather than a repository permission; the
app was installed and the work landed as commits 57a0507 and 199d611. The patch file is kept only as
a record of what changed. If you are reading this because a push failed again, check
`gh api /user/installations` first - an empty list means the app is gone, and no retry will help.

    git apply /scratch/saved/TXT-FULL-PARITY.patch

Nothing in it touches `app/`.

---

## What is not on this list, and why

* **`ReadingOrder.apply()` is not called by the app or by `ConvertOne`.** That is real, and it
  is not a defect: the stamp is written as an anchored box whose `positionH`/`positionV` are both
  `relativeFrom="page"`, so its place in the block list decides which page it attaches to and not
  where on that page it lands. Every stamp document scores the same with and without the pass.
  Do not wire it up to "fix" a side effect that is not happening - `SECTOR19.md` section 0.1.
* **The `.txt` scores are quotable.** `TXT-FALSIFIABILITY.md` carried a standing rule saying they
  were advisory because `t09_page_furniture` was blind. `t09` was fixed twenty minutes after that
  rule was written, re-tested, and now fails when a head is duplicated. The result is 12 of 12.
  The rule is withdrawn in that file, with its history, rather than deleted.
