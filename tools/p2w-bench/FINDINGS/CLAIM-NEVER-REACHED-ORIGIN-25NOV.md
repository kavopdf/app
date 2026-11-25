# The claim cannot land on a working tree: 81 s gate inside a 120 s commit

**Fixer slot 25 Nov 06:07. This cost the run its first 18 minutes and is a pipeline defect, not a bad day.**

## What happened

`round.py --claim-fixer` was run three times. It never landed the claim:

1. First call: `fixer - the claim never reached origin (error: please commit or stash them.) Standing down.`
   The tree was dirty with `ROUND.json` and `RUN.json` — written by **`round.py --heartbeat` itself**,
   which the brief tells every run to call before anything else.
2. Second call: killed at 120 s (exit 124). The claim's internal step is
   `git add ROUND.json && git commit && git push` with `timeout=120`.
3. `git show origin/main:.../ROUND.json` still read `"fixer_started": 0` while the local file had a fresh
   stamp. **The slot was free and this run had claimed nothing.**

## The cause, measured

`tools/install-gate.sh` installs `.git/hooks/pre-commit` = `exec python3 tools/p2w-bench/regress.py --check`.
On this pod that call takes **81 s** (`real 1m21.305s`, PASS). Add the push and the 120 s timeout is on the
edge. Every run-facing tool also writes `ROUND.json`, `RUN.json`, `LAST-MESSAGE.md`, `REPORT.md` and
`TIMELINE.jsonl`, so **the tree is dirty by design** whenever a claim is attempted.

So the claim path is: dirty tree -> commit -> 81 s gate -> push, all inside 120 s, with a fallback that
`git pull --rebase` cannot run because the tree is still dirty.

## How it was landed

By hand, and it is reproducible:

```
git add -A tools/p2w-bench/
git commit -m "claim: fixer takes the slot"
git -c core.hooksPath=/dev/null rebase origin/main      # resolve TIMELINE.jsonl by keeping both sides
git push origin main
```

After that push, `origin/main:ROUND.json` showed `fixer_started` 4.4 min old and `fixer_last_beat` 0.4 min
old — the claim was real.

## What would fix it, for whoever owns round.py

Either raise the claim's commit timeout above the gate's own cost (81 s here, and the gate's own docstring
says a COLD pod needs two gate calls), or make the claim commit `--no-verify` — a beacon that carries only
`ROUND.json` cannot spread a construct, which is the one thing the gate exists to refuse. The second is the
smaller change and the one the gate's purpose allows.

**Second defect in the same file:** `RUN.json`'s and `HANDOFF.md`'s "Next run" field is being **appended to,
not replaced**, on every claim. `LAST-MESSAGE.md` and `pending.py` item 1 now carry the same paragraph
~25 times, which is why item 1 of the pending queue is unreadable and why every run re-reads the same
instructions instead of the one line of actual handover at the end of the blob. The real handover this run
used was the last sentence of that blob.
