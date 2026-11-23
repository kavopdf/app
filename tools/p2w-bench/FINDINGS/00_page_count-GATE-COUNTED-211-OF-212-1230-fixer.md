# gate.py counted 211 of a 212-document corpus, and counted a page window as a measurement

**23 Nov 2026 · fixer run 12:14 → · instrument defect, not a document defect**

Two defects in `benchmarks/gate.py`, both measured, both fixed, neither of which moves a document on
its own — and both of which let a table be published that is missing a document while the verdict says
the corpus is finished.

## 1. The corpus is 212. gate.py said 211.

`_expected_docs()` starts at `n = 211` (synthetic) and adds the real documents, counting them from a
list of four hard-coded paths:

    /scratch/work/realworld
    /scratch/work/base/benchmarks/realworld
    /scratch/work/p2w/repo/benchmarks/realworld
    /scratch/work/cls/benchmarks/realworld

`p2w.py`'s `_realworld_dirs()` looks at `HERE + "/realworld"` **first**. A clone at `/scratch/work/CS`
is none of the four, so gate.py found `real = 0` while p2w.py found 2, and the two tools counted the
same corpus from two different lists.

Measured, three independent sources agreeing:

| source | count |
|---|---|
| `ls /scratch/work/p2w/corpus/*.pdf` | **213** |
| `EXEMPT.json` → `docx: {416_many_tiny_pages}` | **1** exempt |
| 213 − 1 | **212** |
| `p2w.py` / `report.py` ("212 compared", "corpus 212") | **212** |
| `_expected_docs()` at HEAD, from this clone | **211** |
| `_expected_docs()` after this fix | **212** |

So `complete` was reachable at 211 of 212: gate.py would publish `RANKING.csv` with one document never
measured in it, under a verdict saying the measurement was complete. The fix adds the clone's own
`benchmarks/realworld` as the first entry, the same rule p2w.py already uses.

## 2. A page window was counted as a measurement

    measured = len(glob.glob("/scratch/work/p2w/dist2/*.json"))

`p2w.py` keeps a resumable window for a document over 80 pages in `dist2/<doc>.partial.json` —
`{"first": n, "merged": {...}}`. That is a progress note, not a measurement: no `doc`, no numbers, no
verdict. `p2w.py`'s own `results()` excludes it for exactly that reason. The bare glob above did not,
so a 300-page document that had walked 60 of its 300 pages counted as a document measured.

Proved directly, with a probe pair written into `dist2/` and removed afterwards:

    _result_files() sees: ['__probe__.json']     (one of the two)
    partial counted? False
    the old glob would have counted: 2

The fix is `_result_files()`, which is the same rule as p2w's `results()`, and `measured` now uses it.

## What the fix does not do

It does not make the corpus measurable inside one 290 s call. That is the next lever, and it was
attempted this run and **not landed** — recorded here so no run derives it again.

## The resume work: measured, not landed

`gate.py` has no way to carry a partial measurement across the 290 s call limit: `p2w.py` already
persists one result per document, but gate.py writes `STATE.json` only at the end and publishes
`RANKING.csv` only when `measured >= expected`, so a killed invocation leaves nothing behind and the
next one pays for the same conversion again. A `--resume` / `--chunk` patch was written and compiles
(165 lines), and it was **not** landed, because the measurements below say the shape is wrong.

What was measured:

| what | result |
|---|---|
| `build-engine.sh` cold | **38 s** |
| conversion, one JVM per document | **~9–10 s per document** |
| `p2w.py`'s inner group size (`CHUNK`) | **12** documents, rendered *then* measured |
| `gate.py --resume --budget 110 --chunk 45` | **0 of 212** measured, `p2w.py` exit 124 |
| `gate.py --resume --budget 250 --chunk 200` | **0 of 212** measured, no progress file written |

The reason a short chunk measures nothing is `p2w.py`'s own loop, not the reporting:

    for i in range(0, len(todo), CHUNK):
        if time.time() >= end: break
        grp = todo[i:i+CHUNK]
        got = prerender(grp, end)          # 12 documents through soffice
        for b in grp:
            if time.time() >= end: break   # <- the whole group is abandoned here
            ...
            json.dump(r, open(jf, "w"))    # only now is anything written

A chunk shorter than the time to prerender and measure **one group of twelve** (~120 s + measurement)
breaks on the first document of the group and writes nothing. That is why the 45 s and the 200 s chunk
both came back at 0. Resuming therefore needs chunks of ~200 s, i.e. **one chunk per 290 s call**, and
212 documents at ~12 per call is **~18 calls** — not the 2–3 the previous report's plan assumed. That
number is the thing to design against, and it is why this patch was left out rather than landed
unproven.

One more measured fact, against the patch itself: on one `--resume` invocation whose guard reads
`_write_state(S, repo=not (a.resume and not meas.get("complete")))` — i.e. *do not write the repo's
copy* — `benchmarks/STATE.json` changed anyway (`c0c27d72…` → `54a0dfad…`, an `INCOMPLETE` record with
`engine: 5beb8b9d` and `ran_at: 07:16:49`, eight seconds after the run's last log line). It was restored
with `git checkout`. A guard that does not hold is worse than no guard, and it is a second reason the
patch is not in this commit.

## Next run, in this order

1. `--resume` with `--chunk 200` and a chunk floor that refuses to start a chunk it cannot finish a
   group in (≥150 s), and prove progress: docs measured must rise across two consecutive invocations,
   and `benchmarks/STATE.json`'s md5 must be unchanged by an unfinished one.
2. Only then: apply `FINDINGS/00_page_count-MERGE-SHAPE-PARAGRAPHS.patch`, `build-engine.sh`, and run
   the table to completion across ~18 calls.
3. `regress.py --stamp` with engine + `RANKING.csv` + `STATE.json` in one commit.
