# The pass completes and then the tool deletes it: `ENGINE-STAMP` reads "unknown" and `_invalidate_if_engine_changed` treats that as a new engine

**22 Nov 2026 · fixer slot 00:50 → 01:58 IST · every number below was produced in this run and re-read from disk**

## The finding in one sentence

`benchmarks/p2w.py` writes the engine stamp to one global file, `/scratch/work/p2w/ENGINE-STAMP`,
derived from `ENGINE_SRC`; when that file holds `unknown` — which happens whenever the stamp is
computed against a tree the `git log` call cannot answer for — the next invocation reads it as a
*different* engine and runs `rm -rf` on `DOCX`, `DIST` and `PRE`, destroying a completed corpus pass
between two commands.

This is the reason the `32_stroke_lines` carrier fix has not landed in four slots. It is not the
construct. It is not the 25 minutes. It is that the 25 minutes are thrown away at the finish line.

## What happened, with the clock

| at | what | evidence |
|:--|:--|:--|
| 19:42 | patch `rule-carrier-followed-by-block-2008.patch` applied to HEAD, engine rebuilt (52 s), conversion begins | `git apply --check` clean |
| 19:42–19:56 | conversion, 4 slices, **213 of 213 docx** | 3.68 / 3.54 / 4.70 / 4.47 s per doc, logged per slice |
| 19:59–20:17 | measurement, 6 slices, **212 of 212** (416_many_tiny_pages exempt) | `PASS COMPLETE` from the driver |
| 20:15:31 | `rank()` returns **212 rows**, `status()` prints `measured 212/212` | this is a real, complete measurement |
| 20:15 | `ENGINE-STAMP` written as `unknown` by that call | file read back: `unknown` |
| 20:16:35 | `gate.py` resolves `ENGINE_SRC` to its own clone `/scratch/work/p2w/repo`, computes `462353f`, finds the stamp `unknown`, wipes | log: `engine changed unknown -> 462353f - discarding docx and measurements built on unknown` |
| 20:17 | `dist2` = 0 files, `out` = 0 docx | `ls` |

The pass was **complete**. It was not slow, it was not short of budget, and it did not hit the
`--budget` split that the previous run diagnosed. It was finished and then deleted by the tool.

## The mechanism, reproduced in ten seconds

```
BEFORE: dist2 files = 2   stamp = unknown
_engine_stamp() now = '462353f'
[20:17:01] engine changed unknown -> 462353f - discarding docx and measurements built on unknown
AFTER : dist2 files = 0
```

Two files were placed in `dist2`, the stamp set to `unknown`, and `_invalidate_if_engine_changed()`
called. Both files were gone. The guard is `if was and was != now:` — `unknown` is a value like any
other, so it is treated as the name of a previous engine.

## Why the stamp was `unknown`

`_engine_stamp()` shells `git -C ENGINE_SRC log -1 --format=%h -- app/.../engine/` and returns
`"unknown"` on any exception or empty stdout (`p2w.py:1114-1121`). `ENGINE_SRC` is whatever
`P2W_ENGINE_SRC` names, or `ROOT/repo` if it names nothing (`p2w.py:84, 961-992`). A run that exports
`P2W_ENGINE_SRC` to the tree it is measuring, and a tool that does not, are two different trees
writing the same stamp file. One of them answering `unknown` is enough to condemn the other's cache.

The direct `git` call in the same tree returns `462353f` on demand — verified. So the stamp is not
wrong because the repository is odd; it is `unknown` because the call was made against a different
`ENGINE_SRC` than the cache was built under.

## The fix, and its measurement

`benchmarks/p2w.py`, one guard:

```python
if was and was != "unknown" and now != "unknown" and was != now:
```

An unreadable stamp says nothing about which engine the cache came from, so it may not be read as a
*different* engine. Measured before and after, on the same probe:

| test | before | after |
|:--|:--|:--|
| `dist2` = 2, stamp `unknown`, real stamp `462353f` | **0 files survive** | **2 files survive** |
| `dist2` = 2, stamp `deadbee`, real stamp `462353f` | 0 files survive | **0 files survive** — a real change still wipes |

The second row is the one that matters: the fix does not disarm the invalidation, it narrows it to
the case the invalidation was written for. A genuine engine change still discards the cache.

This is a tool change, not an engine change: `regress.py`'s fingerprint is over
`app/src/main/java/com/kavopdf/app/engine/*.java` and does not include `benchmarks/p2w.py`.

## What it cost, and what it bought

Cost: 213 docx and 212 measurements, 35 minutes, and the slot.

Bought: the reason every slot since 20 Nov has ended in a lead rather than a landed fix, and a
one-line guard that stops it happening again. **The next slot that runs the pass will keep its pass.**

## What is still true about the carrier fix

The patch is unchanged and still a measured lead, not a landed fix. Nothing about the construct was
disproved this run:

* `rule-carrier-followed-by-block-2008.patch` applies clean on HEAD and **is a superset** of
  `rule-carrier-per-rule-2008.patch` (both start `@@ -2770,6 +2770,18 @@`, both target blob
  `4ead19d..5405e26`). Applying both, as the 00:15 handoff says, will fail on the second. Apply the
  `-followed-by-block-` one only.
* It touches every document that draws a rule. The corpus census records `w:drawing` on **197 of
  213**, so there is no scoping shortcut: a scoped re-measurement would save at most 16 documents.
* `ctx.flowY` is **not** set by `ruleCarrier` and does not need to be. The brief's warning refers to a
  flow-positioned table; this carrier is floating (`w:tblpPr`, `vertAnchor="margin"`) and the block
  it appends is a 1-twip exact line, which is how `17` and `53` kept page count 1 at 42/42.
* `ConvertAll` must not be used to measure: it carries state between documents (392 scored share5
  1.61 alone against 28.39 inside a full batch, `p2w.py:1036-1046`). The census in `scope.py --prove`
  is a *differential* of two engines over one batch, which is sound; a score from it is not.

## The next run, exactly

    git apply tools/p2w-bench/patches/rule-carrier-followed-by-block-2008.patch
    bash tools/p2w-bench/build-engine.sh
    python3 /scratch/work/pass.py 270     # x ~9: 4 slices convert (3.7 s/doc), 5 measure (3.9 s/doc)

`pass.py` is the driver this run used. It runs `validate()` once, then loops `docx()` and `run()` with
a deadline, and skips the per-call `engine()` rebuild (50 s) and re-validation (5 s) that
`p2w.py main()` pays on every invocation — 7 minutes of a 35-minute pass. It must be recreated from
the recipe below; `/scratch/work` does not survive a pod.

    import p2w                      # with P2W_ENGINE_SRC=/scratch/work/<clone>
    p2w.validate()                  # once
    p2w._invalidate_if_engine_changed()
    while docx < 213: p2w.docx(deadline)
    while measured < 212: p2w.run(deadline)
    p2w.rank(); p2w.status()

**Do not call `gate.py` between `rank()` and `regress.py --stamp`** until this fix is on `main` and
the tree you are stamping is the tree `P2W_ENGINE_SRC` names.
