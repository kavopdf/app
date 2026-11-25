# A cold pod cannot commit, and the missing step is corpus-slice.py

From the 09:02 run, which lost its first 25 minutes to this and then measured the fix:

    "install-gate.sh runs the hook, the hook builds all 213 .docx, and that build is what timed out.
     corpus-slice.py finished it in one slice (11 documents) and the same check now takes 11 s instead
     of over 4m40s. That is the mechanical reason a fresh pod cannot commit - run corpus-slice.py
     before install-gate.sh."

## What is in place

install-gate.sh calls pod-prep.sh, which is the documented "three scripts, one order" caller. It runs
corpus-fetch, jdk-fetch, the maven jars, the AAR unzip, the stubs and the engine build.

## What is not

corpus-slice.py. So the first commit on a fresh pod runs regress.py --check with no .docx to compare,
the hook builds all 213 itself, and that build exceeds the call limit - which reads from outside as
"REFUSED. This commit would land a regression or an unmeasured engine" for a tree nobody touched. Four
earlier runs wrote that up as a claim failure before anyone read the gate.

The 09:02 measurement is the fix and its size: one slice of 11 documents takes the check from over 4m40s
to 11 s.

## The change

One line in pod-prep.sh, after the engine build and before it returns:

    bash "$HERE/corpus-slice.py" || true

The `|| true` is deliberate: a slice that cannot run must not stop pod-prep, because pod-prep's job is
to leave the pod usable, and a partial corpus is still better than none. The gate then either has
something to compare or says so honestly, instead of building the corpus inside the hook.

## Not applied

Recorded rather than edited. pod-prep.sh is the first thing every commit path runs, and a wrong change
there breaks every run at once; the 09:02 run already proved the fix and the size of it, so this is a
one-line change with a measurement behind it rather than a guess.
