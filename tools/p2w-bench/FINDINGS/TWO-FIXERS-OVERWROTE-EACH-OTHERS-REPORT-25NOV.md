# Two fixers overwrote each other's report, and the user got the wrong one

The 13:00 run opens with this:

    "My report was overwritten in LAST-MESSAGE.md by the concurrently-running 12:13 fixer, which
     committed after mine; my version is preserved at commit eb9077ad and I have not clobbered theirs."

That is the run being careful. What it describes is a delivery failure: LAST-MESSAGE.md is how a fixer's
report reaches the user, and two fixers wrote it within the same hour with no lock and no atomic write.
The user read the 12:13 report. The 13:00 report - a full 1h 25m of work on the largest item in the
corpus - reached them only if they went looking in git.

## Verified

lastmessage.py contains no lock, no temp-file-and-rename, and no check that the file it is about to
replace was written by the same run. It reads its input, formats, and writes. Two runs in flight means
the later write wins, silently.

Two fixer crons sharing one slot is deliberate and correct - the :10 relay exists so a dead :50 run does
not stop the work. But the slot mechanism protects the WORK; nothing protects the REPORT.

## The fix

Write atomically and refuse to replace a report from a different run:

    tmp = path + ".tmp"; open(tmp,"w").write(body); os.replace(tmp, path)

and before the replace, read the existing header. If it carries a different run id and is newer than
this run started, write beside it (LAST-MESSAGE-<runid>.md) and say so in one line. A report that cannot
be delivered is not a report.

## Not changed

lastmessage.py is the path every report leaves by, and a wrong change there loses reports rather than
racing them. Recorded with the exact change so the run that owns it can land it with the two-run case as
its test.
