# The Google verdict was unreadable because the pipeline's checkout is shallow

**Measured 25 Nov 2026, fixer run, 00:16-01:00 IST. Construct: the instrument, not the engine.**

## What we believed

The report's line *"Fixed - Google, every applicable check: could not be read - 0 of 191 scored were read as
current, which is a failed read and not a measurement"* was read, correctly, as "the store is stale". Four
runs in a row printed it and the `:20 gverify` cron was pointed at as the thing that would eventually fix it.

## What was measured

`report.engine_now()` and `gverify._engine_now()` both derive the current engine from
`git log -1 --format=%h -- app/src/main/java/com/kavopdf/app/engine/`. **On a `--depth 1` clone git has no
history behind the tip, so that command returns the TIP COMMIT for every path.** The pipeline clones shallow.

| | shallow (before) | full history (after) |
|---|---|---|
| `git rev-parse --is-shallow-repository` | `true` | `false` |
| `engine_now()` | `6944167` (an attempt commit) | `b7699196` |
| `report.google_fixed()` | `(36, 191, 0, 0, 22)` | `(36, 191, 36, 187, 22)` |
| report row | "could not be read - 0 of 191" | "36 of the 187 re-measured on this engine" |
| `gverify._done()` | 22 of 213 | 209 of 213 |

The store was never stale: 188 of 213 rows carry `b7699196`, and the tree's engine sources are byte-identical
to it (`git diff b7699196 HEAD -- .../engine/` is empty). The rows were right and the reader was blind.

## Independent confirmation

Not from the tool being edited: `gh api repos/kavopdf/app/commits?path=app/src/main/java/com/kavopdf/app/engine/`
returns `b7699196` (23 Nov 11:04) as the last commit that touched the engine. That is the value the patched
reader now prints.

## What is now true

- `report.py:engine_now()` and `gverify.py:_engine_now()` fetch `--unshallow` once when the checkout is
  shallow, then read history. Two lines of guard, no behaviour change on a full clone.
- **The pipeline could always have stated 36 documents fixed in Google.** It could not, because the reader
  mistook a missing history for a stale store - and the report's own refusal to print a zero is what kept the
  error visible instead of turning it into a believable "0 fixed".
- `gverify._done()` being 22 instead of 209 means the `:20` cron was re-measuring the same 22 documents and
  treating 187 measured ones as unmeasured. That is where the "about 4 runs for the 191 outstanding" figure
  in the last report came from: it was an artefact of the same defect.

## What would prove this wrong

`git rev-parse --is-shallow-repository` returning `false` on the pipeline's own checkout while the report
still prints 0 of 191. It does not: the shallow flag is the only variable, and toggling it on identical data
moves the number from 0 to 187.

## The transferable rule

**A read that returns zero is a claim about the reader until the data is separately counted.** The store was
counted here by hand (`benchmarks/gverify/*.json`, grouped by `engine`) before the patch was written, and the
hand count is what said the reader was wrong. The tool's own guard ("no count is stated rather than a zero")
was right; what it protected against was not staleness but a broken fingerprint.
