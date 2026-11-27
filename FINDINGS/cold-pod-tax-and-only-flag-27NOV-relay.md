# The cold-pod tax is 32 minutes of every run, and `--only` is the way out of it

**27 Nov 2026, relay run (slot 14:28).** Measured on this pod, 2 cores.

## The tax

Every fixer run starts on a fresh pod: `/scratch/work` is empty, so the corpus cache
`/scratch/work/p2w/` does not exist and neither does the JDK. The engine cannot be measured
until all of it is rebuilt. Measured this run, in the order it happened:

| step | wall clock | what it leaves behind |
|:--|--:|:--|
| `git clone --depth 1` | ~15 s | the tree |
| `corpus-fetch.sh` | ~16 s | 213 PDFs, 0 missing |
| `jdk-fetch.sh` | ~23 s | `/scratch/work/.p2w-jdk/jdk` |
| libs + aar + stubs + engine compile (`pod-prep.sh` steps 3-6) | ~50 s | `out/ConvertAll.class` |
| **corpus conversion, 213 documents** | **~27 min** | `.keys/*.json` + the `.stamp` |
| **total before the first measurement is possible** | **~32 min** | |

The conversion is the whole tax. It ran in six slices because no single call may exceed 300 s:

    103 -> 133 -> 161 -> 187 -> 208 -> 213   (stamp written 09:57:51Z)

At the measured ~4.5 s/document and 4 workers this is irreducible: 213 x 4.5 / 4 is not the number,
because the cost is not linear in workers on 2 cores - the observed rate was ~0.14 documents/second
regardless of `-j 2` or `-j 4`.

**Consequence for the slot.** 32 of the 90 minutes are gone before any document can be touched, and
a 45-minute silence window reaps a run that goes quiet during it. That is why runs report one attempt:
there is no room for a second.

**Consequence for an engine change.** `corpus-convert.py` keys each document on the engine source
hash. A one-line change under `app/src/main/java` invalidates **all 213** keys, so the rebuild is
another ~27 minutes *and the commit gate refuses to run until it finishes*. On a 90-minute slot that
is: 32 min setup + 27 min rebuild = 59 min, leaving 31 min for the change itself, its Google
verification and the report. That arithmetic, not unwillingness, is what keeps runs at one attempt.

## The instrument that removes half of it

`corpus-slice.py` had no way to name a document. `--budget 0 -j 1` converts exactly one document, but
it converts `todo[0]` - the first *pending* document alphabetically - so the document is chosen by the
filesystem, not by the person fixing it.

`--only <stem>` now names it. Landed this run, three hunks in `main()` only:

* the flag, beside `--status`;
* a filter that narrows `todo` to the one named document, placed **after** the `--status` block so
  `--status` still reports the whole corpus, and it exits 1 on an unknown stem rather than silently
  converting nothing;
* a guard that returns **before** `write_stamp()`: a one-document run must never certify a corpus.
  `write_stamp()` means "every document in this cache is this engine's output"; one document is not
  evidence for the other 212, and a stamp written here would make the next `--ensure` read WARM over a
  corpus that is 212 documents short. The per-document key `convert_one()` already wrote atomically is
  the whole of that run's claim.

### What was verified on this tree, and what was not

| branch | how | result |
|:--|:--|:--|
| flag parses, unknown stem | `--only no_such_doc` | `no such document: no_such_doc (not in /scratch/work/p2w/corpus)`, exit 1 |
| already-converted stem | `--only 415_inline_images` | `already converted on this engine - nothing to do, no stamp written`, exit 0 |
| the stamp is not rewritten | `cat /scratch/work/p2w/.stamp` before and after both calls | byte-identical, `at: 2026-11-27T09:59:13` unchanged |
| **the post-conversion stamp guard** | **not exercised** | the corpus was fully converted and stamped before the patch landed, so no unconverted document existed to name, and inventing one would have meant invalidating a real key (deleting a file) or adding a probe PDF to a corpus of 213 |

The convert branch is the existing, unmodified loop with `todo` narrowed to one element; that loop
converted 213 documents on this pod an hour earlier. The guard is the only new behaviour and it is the
only thing above that has not been run.

## What this is worth

A fixer that wants to see one document after a change now pays **4.5 s**, not 27 minutes. That is the
difference between one attempt and four to six. It does not shrink the rebuild an engine change forces
- the gate still needs all 213 - but it means the *first* look at a fix is free, which is where most
attempts die today.
