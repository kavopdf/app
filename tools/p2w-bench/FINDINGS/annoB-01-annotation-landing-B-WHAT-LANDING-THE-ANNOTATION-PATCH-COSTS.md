# annoB-01 - the gate is stamp-gated, not corpus-gated, and the docx pass is the whole slot

**Agent deployed 10:58 IST, 17 min. Answer: yes, the saved annotation patch can land in one
90-minute slot - but only if the run spends none of it on investigation.**

What `regress.py --check` demands, read from the code:

* `scope_of_change()` answers **both** for `PdfToWord.java` ("change outside a known method, model
  file"), so both table stamps must equal `engine_fingerprint(fmt)` (`regress.py:500-515`). That
  fingerprint hashes every `.java` in the engine; one edit invalidates both tables.
* `docx_regressions()` and `txt_regressions()` run unconditionally (`regress.py:240-262`,
  `316-334`), **per row**: a document may not be missing, may not exceed the 15 Nov baseline, and may
  not exceed the previous commit's value. It is a row comparison, not a whole-table hash.
* The corpus build inside the check (`regress.py:617-621`, `corpus-slice.py --budget 240`) is a
  **failed input, not a best-effort**: a nonzero exit sets `fail = 1` and refuses. A cold pod needs
  the JDK and the corpus fetched before the gate can pass at all - both were fetched in this run and
  the gate then printed PASS.

**No scoped re-stamp exists.** `corpus-slice.py` takes only `--budget/-j/--status`;
`corpus-convert.py` only `--ensure/--force/--status`; `restamp_txt.py` only
`--run/--report/--apply/--budget/--force`; `regress.py --only` scopes **formats, not documents**.
`EXEMPT.json` excuses a missing *score*, never an unmeasured engine. Two paths would pass without a
measurement and both are lies: `--allow-engine-change` skips the stamp check wholesale
(`regress.py:473`), and `--stamp` would succeed today with zero measurement because
`_newer_than_engine()` is already true (`regress.py:344-354`). Do not use either.

Timings measured in this pod, on this corpus: `jdk-fetch.sh` 24 s, `corpus-fetch.sh` 15 s,
`build-engine.sh` ~45 s, conversion **55 documents per 230 s at `-j 6`** (213 = five slices, ~16 min),
docx render + score **~15.8 s/document** on one-page documents (~56 min for 213), txt re-score
**0.37 s/document** (78 s for 212), `regress.py --check` 12.6 s once the corpus exists.

The order, and the beacon before each long step: apply the patch, build, five slices, `p2w.py` until
complete, `restamp_txt.py --run --force` (twice) then `--report --apply`, `regress.py --stamp`,
`regress.py --check`, `measure_gate.py`, `attempt.py`. Copy `RANKING-TXT.csv` before `--apply`:
`restamp_txt.py --apply` rewrites `RANKING-TXT-BASELINE.csv` from the same rows, which makes the
"no .txt document worse" line vacuous.
