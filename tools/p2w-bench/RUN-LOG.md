# Run log

One line per stage, written and committed by the baseline cron as it works. It exists
because a run that dies before its first commit leaves no trace: on 11 Nov ten runs in a
row measured ten documents each and committed nothing, and there was no way to tell
whether they died in the conversion, in Drive, in the record step or in the commit
itself. The cron keeps no output of its own, so this file is the only witness.

A stage with no line is a stage that was never reached. That is the answer.

| when | run | stage |
|---|---|---|
| 12 Nov probe | probe | commit test |
| 12 Nov 07:25 | size-probe | testing a 796 KB commit payload |
| 12 Nov 08:02 | baseline | started | phase measure |
| 12 Nov 08:04 | baseline | corpus 208 pdfs unpacked, engine built |
