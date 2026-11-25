# googA-01 - the Google scoreboard read zero because two different quantities were compared

**Agent deployed 10:57 IST, 5 min. Answer: a filter bug (a), not starvation (b) and not a swallowed
error (c).**

`report.py:460` compared `(j.get("engine") or "") == now`. `now` came from `engine_now()`
(`report.py:393-411`), which answered `git log -1 --format=%h -- app/.../engine/` -> `85b8735f`, an
8-char abbreviation. Every one of the 212 rows then in `benchmarks/gverify/` carried
`engine = 981ff1fa35e2cf67`, the 16-char source hash written by `gvbatch.py:26,76`. Two quantities,
two lengths, zero matches - and `google_scored = 212`, so it was a comparison failure, not an empty
store and not an exception.

`gverify.py:194` had already been fixed for this (`_e == now or now.startswith(_e) or
_e.startswith(now)`), but `_engine_now()` there still answered `%h`, so `_done()` returned 1 and
`plan()` said "1 of 213 ... 212 to go": an hourly cron re-measuring the whole corpus for ever.
`classify_google.py:34` carried it a third time, into the class table's engine-coverage header.

All three sites are fixed in commits `b553fa5b` and `37e4f84a`; the measurement is in
`FINDINGS/ENGINE-STAMP-IS-NOT-A-COMMIT-25NOV.md`.
