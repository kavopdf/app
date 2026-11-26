# A full 212-document pass does not publish RANKING.csv, so the commit gate cannot pass

**26 Nov 2026, relay/fixer run claimed 19:24 IST. Engine HEAD `c63fc337`, app/src/main/java tree
`1fb268b6de2ab5d0ceb59972ea4a716605b72bd9`.**

## What was done

`python3 benchmarks/p2w.py --budget 250` was run nine times until it reported
`corpus 213/213  docx 213/213  measured 212/212  remaining 0`. Every scored document was
rendered and compared on this pod in this run: the count went 12, 22, 46, 64, 124, 163, 199,
211, 212. The last call ended with no `PARTIAL` line, which is the signal that the pass is
complete and the published table may be written.

## What the gate said afterwards

```
$ python3 tools/p2w-bench/measure_gate.py
docx   212/212 scored, 1 exempt, 0 blocking, 212 expected
engine docx a4de7df896875a39, tree 7e0de1abdeb221ae
  - RANKING.csv was measured on docx engine a4de7df896875a39 and the tree is 7e0de1abdeb221ae
NOT READY

$ python3 tools/p2w-bench/regress.py --check
  ENGINE CHANGED (docx): table measured on a4de7df896875a39, the tree is 7e0de1abdeb221ae
  docx: no document worse than baseline
  google-safe : no construct Google ignores has spread
REFUSED.
```

`git diff --stat benchmarks/RANKING.csv` is **empty**: a complete 212-document measurement left the
published table byte-identical, stamp included.

## Why the stamp cannot match

`regress.py:73 engine_fingerprint()` is a sha256 over the `.java` files in
`app/src/main/java/com/kavopdf/app/engine/`, truncated to 16 hex. Computed on this tree now:

| call | value |
|:--|:--|
| `engine_fingerprint()` (every `.java`) | `025fe9deda5ac7b1` |
| `engine_fingerprint("docx")` (excludes `TxtWriter.java`) | `7e0de1abdeb221ae` |
| the stamp `RANKING.csv` carries | `a4de7df896875a39` |

The table's stamp equals **neither** current fingerprint, and the engine sources are not in doubt:
`git rev-parse HEAD:app/src/main/java` is `1fb268b6…` in this clone **and** in
`/scratch/work/p2w/repo`, the copy `p2w.py` builds its engine from. The engine the corpus was
measured with is the engine the gate reads.

So the refusal is not "an unmeasured engine". It is a table that was not rewritten after a
complete measurement. Two separate defects, either of which alone reproduces the permanent
`NOT READY` every run has hit:

1. **`p2w.py` does not publish.** It reported `measured 212/212 remaining 0` and `RANKING.csv`
   did not change. Until the publish step is found and fixed, no number of measurement slices
   can stamp the table, and the gate cannot pass however much work a run does.
2. **The stamp and the check may be different namespaces.** `p2w.py:1480 _engine_stamp()` returns
   `git log -1 --format=%h -- app/src/main/java/.../engine/`, a **commit** id; `measure_gate.py`
   compares it against `regress.engine_fingerprint("docx")`, a **content hash** of the same
   directory. A commit id and a content hash are never equal. `a4de7df896875a39` is 16 hex and so
   is a fingerprint, so this one is not proven — it is the next thing to read, at
   `p2w.py`'s write site for the table, and it costs one `grep` to settle.

**Not settled here:** which of the two it is. Both are consistent with every observation above and
the run ran out of slot before the publish site was read. Whoever picks this up should start at the
line in `p2w.py` that writes `benchmarks/RANKING.csv` and print the stamp it writes.

## Operational finding: orphaned soffice makes every render fail in 1 s

The pass stalled at 199/212 with `soffice gave no render in 1s` for 13 documents. Sixteen
`soffice.bin` / `oosplash` processes left behind by earlier 300-second calls that were killed
mid-conversion were holding the profile. After `pkill -9 -f soffice.bin; pkill -9 -f oosplash` the
same pass took the corpus from 199 to 212 in two calls, and the documents that had "failed twice"
rendered normally. **A render that fails in about one second is a stale process, not a bad
document.** `PRE/.soffice-fail` then skips that document on every later call, so the corpus can
never reach 212 on that pod until the file is cleared or the processes are killed first.

## Also measured, not resolved

`GOOGLEDRIVE_CREATE_FILE` returns `400 Bad Request` for a docx upload-and-convert
(`mimeType=application/vnd.google-apps.document`, `parents=[1OoSHtsv-qEUwk8CnNa9d5hsCKu8PFeij]`,
`file_to_upload` from a successful `upload` call). Retried once with a filename without a path
separator; same 400. The Google half of the two-sided probe below could not be run this run.
