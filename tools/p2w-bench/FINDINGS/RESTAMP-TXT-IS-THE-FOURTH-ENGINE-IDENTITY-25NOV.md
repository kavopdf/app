# restamp_txt.py is the fourth copy of the wrong engine question

Running `restamp_txt.py --apply` to rebuild the missing RANKING-TXT.csv printed:

    wrote RANKING-TXT.csv (213 rows)
    wrote STATE-TXT.json (engine 85b8735f)
    199 of 213 clean (93.4%)

85b8735f is an 8-char git commit abbreviation. The tree is 981ff1fa35e2cf67. restamp_txt.py:246 ran
`git log -1 --format=%h -- app/.../engine/`, which answers a different question from the one the store,
RANKING.csv and the corpus are keyed on - sha256(name+bytes of every engine/*.java)[:16].

report.py, gverify.py and classify_google.py were each fixed for this exact line on 25 Nov. This is the
fourth, and it is the one that writes the .txt state file, so the .txt side has been stamping itself with
an id that matches nothing.

## Why it was not landed

Three patch attempts broke indentation and each was reverted to HEAD rather than left half-valid:

  attempt 1  replaced the block, joined `try:` and a comment on one line  -> IndentationError
  attempt 2  rewrote the same block with the helper inline               -> IndentationError
  attempt 3  inserted a one-line call after the assignment               -> unexpected indent

The surrounding code sits inside a nested try whose body indent does not match the line the edit anchored
on. Editing it blind is how the file gets broken, and a broken restamp_txt.py cannot write the .txt table
at all - worse than a wrong engine id.

## The fix, exactly

Add a module-level helper and call it once, so no existing indentation moves:

    def _stamp_engine():
        # read REPO/../.stamp ["engine"], else sha256 over engine/*.java [:16], else ""
        ...

then, immediately after the existing `eng = _sp.run([...]).stdout.strip()` line, at that same indent:

    eng = _stamp_engine() or eng

No block is restructured, so the nesting cannot break. Verify with `ast.parse` and then run
`restamp_txt.py --apply` and confirm it prints `engine 981ff1fa35e2cf67`.

## Done instead

lastmessage.py now writes atomically (_atomic_write, os.replace), so two fixers racing on LAST-MESSAGE.md
can no longer lose a report to a truncated write. That one landed and is verified.
