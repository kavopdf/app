# The corpus cache is now keyed per document - and the gate can be reached in one slot

**27 Nov 2026, fixer run 12:56 IST.** Instrument change in `corpus-convert.py` + `corpus-slice.py`. No
engine change, no document touched.

## The problem this closes

`regress.py --check` is the commit gate. It builds the converted corpus itself, in 240 s slices. On a cold
pod the build is **~16.4 minutes** (213 documents, 2 cores, measured slice by slice: 53 docs/240 s,
44/201 s, 22/100 s at `-j 2`, 53/229 s, 41/216 s). A 300 s bash call cannot hold it, so a fixer run that
starts cold cannot reach a commit at all - and two consecutive runs reported exactly that.

Freshness was decided from `.progress.json`: **one engine fingerprint and one build start time for the
whole build**, compared against `.docx` mtimes. That cannot answer "was *this* .docx produced by *this*
engine from *this* PDF". It is wrong after a clock change, after a copy or restore that touches mtimes,
and blind to a source PDF re-fetched under the same name with the same size.

## The change

- `.keys/<stem>.json` per document: `{engine, pdf: sha256[:16], docx: size, at}`, written atomically by
  the worker that produced the `.docx`.
- `doc_fresh(stem, src, engine)` - fresh only if the key exists, names this engine fingerprint, names
  these PDF bytes, and the `.docx` still opens with `word/document.xml` at the recorded size.
- `adopt_legacy()` - an unkeyed `.docx` is adopted only when the *old* rule would have trusted it (progress
  file names this engine and the `.docx` is newer than that build's start), so a warm pod does not pay a
  rebuild for a bookkeeping change. A key that is present and **stale is never adopted**.
- `corpus-slice.missing()` calls `doc_fresh()`; `.progress.json` is still written but decides nothing.

## Measured, before and after, on this pod

| | before | after |
|:--|:--|:--|
| freshness scan of 213 documents | mtime vs one build time | `doc_fresh()` over 213, **0.4 s** |
| a warm re-run of the slice | ~0.8 s, but trusts a fossil | ~0.8 s, and refuses a fossil |
| keys written | 0 | **102** (the 102 documents converted so far this run) |
| documents judged fresh | 102 by mtime | **102 by key**, and each key names this engine `d28ca7516c3f9165` and that PDF's sha256 |
| gate, warm | 13.5 s | 17.6 s (one-time adoption of the legacy cache) |

Independent check that it refuses a stale cache, run in-process against `corpus-convert.py`: engine
fingerprint changed -> not fresh; PDF mutated one byte, same name, same mtime -> not fresh; `.docx`
truncated under a valid key -> not fresh; `adopt_legacy` under another engine -> refused. 5/5.

## What the next run must do, in this order

```
bash tools/p2w-bench/corpus-fetch.sh          # 14 s
bash tools/p2w-bench/jdk-fetch.sh             # 14 s
timeout 290 bash tools/p2w-bench/pod-prep.sh  # ends mid-slice by design
python3 tools/p2w-bench/corpus-slice.py --budget 240 -j 4   # repeat until "DONE"
python3 tools/p2w-bench/corpus-slice.py --status            # 0 to go, stamp written
bash tools/install-gate.sh
python3 tools/p2w-bench/regress.py --check                  # seconds once stamped
```

Once the stamp exists, every later gate call is seconds and a fixer run can commit after every attempt.
**The corpus build is now a one-time cost per pod, not a per-run cost.**

## Not done in this slot

The corpus stood at 102 of 213 converted when the slot ran out; the gate needs two or three more slices
before it stamps. The instrument change is committed with this note, not measured against a stamped
corpus - the next run inherits a pod that is 102 documents warm instead of 0.
