# RETRY — what to do when something fails

Read this before you retry anything. Half of all failures clear by themselves and
half never will, and the two look identical in a log until you read the reason.

---

## Classify first, then act

```
TRANSIENT    rate limit, 429, 502/503/504, connection reset, timeout
             These clear. Wait 5s, 15s, 45s and try again. Three tries.

PERMANENT    bad credentials, 401, "Resource not accessible by integration",
             404, "no space left on device", a permission denial
             These never clear. Stop at once. Say what it was. Do not retry.

ALREADY DONE "destination path already exists"
             Not a failure. The state you wanted is the state you have. Continue.

UNKNOWN      neither pattern matched
             One retry, then stop. A command that fails twice for an unknown
             reason is not about to succeed on the third.
```

`bash tools/retry.sh --classify "<the error text>"` answers which of these it is,
so you do not have to guess:

```
bash tools/retry.sh --classify "API rate limit exceeded for 1.2.3.4"   -> transient
bash tools/retry.sh --classify "403 Resource not accessible"           -> permanent
```

---

## The rule that matters more than the retry

**Never retry a write without checking whether the first one landed.**

A write that failed to answer may have succeeded. The second attempt then either
does the work twice or fails for a reason that looks like a new problem.

```
commit      re-read the file, or list the commits, and look for yours
release     GET the release by tag. If the asset is there, it landed.
            Publishing twice creates a second release for the same version.
upload      list the Drive folder. If the file is there, it landed.
            Uploading twice leaves an orphan that eats quota and gets deleted
            by nobody.
```

A read is always safe to repeat. A write is not.

---

## Waiting has a ceiling

Bash stops at 300 seconds in this environment and nothing survives the kill. So a
rate limit that resets in twenty minutes cannot be waited out inside a run.

```
inside a run     5s, 15s, 45s. Three tries. That is 65 seconds, and it is enough
                 for a blip, not for a quota.
beyond that      stop cleanly, release your claim, record it, and let the next
                 scheduled run try again. That run is free and it is already set.
```

This is why the baseline commits every five documents and why every claim expires
on its own: a run that dies must not take its work or the next run with it.

---

## Wrapping a command

```
bash tools/retry.sh -- git clone https://github.com/kavopdf/app /scratch/work/base
bash tools/retry.sh --tries 4 -- gh release download corpus-v1 --repo kavopdf/app
```

It prints the command's own output, then what it decided and why. Exit 0 means the
command eventually succeeded or was already done; any other code is the command's
own, after the last attempt.

---

## When it still fails

```
one document    SKIP it. Leave its row empty. Do not write a score you did not
                measure. Record one line in INCIDENTS.md and move on to the next.

the whole run   Release your claim, write what happened in INCIDENTS.md, and stop.
                Do not leave a claim held - the next run will wait for nothing.
```

A run that spends twenty minutes retrying one document has done nothing for the
other nine. One skipped document with a recorded reason is a result; a run that
died retrying is not.

---

## INCIDENTS.md

Every skip gets one line, so a document that quietly never got measured can be
found later instead of being discovered as a gap in the table:

```
| time | cron | item | class | what happened |
|---|---|---|---|---|
| 11 Nov 09:14 | baseline | 366_menu | transient | 403 rate limit, 3 tries, row left empty |
```

No line, no skip. If it is not written down, it did not happen.
