# A corpus measurement was impossible for any unpushed engine patch - and one document could never finish

**21 Nov, fixer run claimed 07:58. Three tooling defects, each measured, each fixed. No engine change.**

The run before this one ended with the same sentence twice: "p2w.py builds the engine from
`origin main`, not from a working tree, so a corpus measurement of this patch is only possible after
it is pushed - and `regress.py --check` refuses an engine whose fingerprint is not the one the table
was measured on." Two rules, each correct alone, together making every engine patch uncommittable.
Three runs hit it. This run measured it and removed it.

## 1. The engine could only ever be built from `origin main`

    regress.py --check   "the gate demands a corpus measurement of the tree"
    p2w.py engine()      "git fetch origin main && git checkout -f FETCH_HEAD && build"

`git checkout -f` also discards the patch being measured, so there was no argument to p2w that could
measure a working tree.

**Fix:** `P2W_ENGINE_SRC=<path to a clone>` makes `p2w.py` build and convert from that tree and skip
the fetch/checkout entirely. Unset - the baseline cron, the apk cron, every run with nothing local to
measure - it is the clone it always was, and the behaviour is unchanged. The gate is untouched: it
still refuses an engine whose table was not measured on it. What changed is that the measurement can
now be made.

## 2. A 300-page document could never be finished, and it was measured first

`measure_doc_chunked(first=...)` reported `pages_done` and then threw away every window before it, so
a second call re-measured the same first 60 pages. `run()` did not persist progress either: it logged
"60 of 300 pages - not cached, next run resumes" and the next run started at page 0.

`416_many_tiny_pages` is alphabetically first in the remaining set, so **every** pass began with it and
ended on it. Measured this run: six consecutive 290 s passes, each reporting `measured 114 of 213`,
each leaving nothing behind. That is the mechanical reason the corpus has been stuck at 114 for days
while every pass honestly said it was working.

**Fix:** `measure_doc_chunked(..., seed=None)` now accepts the windows already paid for, `run()` writes
`dist2/<name>.partial.json` with `{"first": pages_done, "merged": ...}`, and the queue is ordered
**shortest document first** so a long document cannot consume a pass before anything is measured.

**Effect, measured:** 114 -> 169 -> 205 -> 212 of 213 in four passes, and 212 documents scored.

`416_many_tiny_pages` still cannot be measured inside one command - 300 pages at ~5 s each - and it
now resumes instead of restarting. It was carried unchanged in the table this run, which is safe
because the change being measured cannot reach it (it carries no annotations at all, measured).

## 3. `EXEMPT.json` is empty, and two comments in `p2w.py` still describe it as populated

Not a defect by itself - the 19 Nov commit deliberately removed the exemption when 416 became
measurable - but the comments in `rank()` and `run()` say "EXEMPT.json lists 416_many_tiny_pages under
`docx`", which is false, and reading them sends the next run looking for a skip that is not there. The
exempt-set filter added to `run()` is correct and inert today; it will do its job the moment anything
is exempted again.

## 4. The construct ratchet refused every commit, because it did not record what it was recorded over

`google_safe.py` is called by `regress.py --check` on every commit and refuses when more documents
carry a construct Google ignores than the mark allows. Its mark said `w:drawing` on **28** documents;
the corpus carries it on **197**. The mark was recorded over a partial output directory in an earlier
sandbox and carried no record of that, and the mark may only ever fall - so once a full corpus existed,
**every commit was refused**, including this run's report commit, which changes no engine code and no
`.docx` at all.

**Fix:** the mark now records `corpus_docs`. `--check` compares only within the same population and
says so plainly when the population differs, instead of reporting a spread that is not one. `--mark`
re-bases when the recorded population differs, prints `RE-BASE` with both counts, and the mark may
still only fall from there. Re-based this run at 213 documents: 197 carry `w:drawing` / `wp:anchor`,
213 carry `w:before-page-top`, 22 carry `w:spacing-letter`, 629 document-carried constructs in total.
That is the honest baseline for the engine work ahead, not a 28-document sample being compared with a
213-document corpus.
