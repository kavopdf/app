# `HANDOFF.json["next"]` concatenates instead of replacing, so every run re-reads hundreds of copies of one instruction

**26 Nov 2026, relay slot 14:18.** Found while resolving a rebase; measured on the committed history.

`tools/p2w-bench/HANDOFF.json` carried **645 lines** on 26 Nov, of which the `next` field alone was
hundreds: the same paragraph — "READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md … PENDING FIRST: N
item(s) you can close …" — repeated, each copy differing only in the pending count it was written with
(34, 33, 31 …). Each run appends its own paragraph to the previous one instead of replacing it.

Why it matters beyond untidiness: `next` is the first thing the fixer brief tells a run to read. A
field that is 95 % duplicated text is a field a run skims, and the instruction that matters — the
pending count — is buried in hundreds of stale copies of itself, each with a different number. It is
also why a rebase on this file conflicts every time.

The remote had already been compacted to 16 lines by the time this run pushed (commit `f1a61ca4`,
08:10 UTC). This run did **not** restore the 645-line version: the long file is a corrupted
accumulator, not history, and restoring it would have put the corruption back. The two agents this run
deployed were added as `R-01`/`R-02` with `deployed_at` and `landed_at`, and the run's own attempt
lines were appended to `TRACE.md` rather than replacing it.

**The fix, for whoever owns `round.py`/`attempt.py`:** the write of `next` must be an assignment, not
an append. `grep -n '"next"' tools/p2w-bench/*.py` will find it; the append is in the handoff writer.
Until it is fixed, every run should treat `HANDOFF.json["next"]` as untrusted and read `pending.py`
instead — which is what this run did.
