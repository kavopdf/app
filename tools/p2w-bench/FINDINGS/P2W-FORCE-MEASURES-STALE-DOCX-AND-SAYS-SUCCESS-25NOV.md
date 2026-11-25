# p2w.py --force measures the previous build and prints a line that reads as success

Found in the 01:00-02:35 fixer report, confirmed in code, NOT fixed here - see "why not" at the end.

## The defect

    benchmarks/p2w.py, _need() around line 1040:

        if _force:
            if not (os.path.exists(dx) and os.path.exists(tx)):
                return True
            return min(os.path.getmtime(dx), os.path.getmtime(tx)) < _eng_mtime

    and the line it prints, around 1046:

        log(f"docx {len(pdfs)-len(miss)}/{len(pdfs)} -- converting {len(miss)}")

`--force` does not force. It re-converts a document only when the .docx is older than the COMPILED
CLASS, and nothing in p2w.py rebuilds that class. A patched engine source with an unbuilt class
therefore reads as "nothing to do", and the pass then measures the previous build while calling it the
new engine.

The second half is what makes it invisible. When nothing needs converting it prints
`docx 0/213 -- converting 213`, which a reader takes as "213 already done" rather than "213 were
measured against a build this run did not make".

Measured by the fixer on 25 Nov: a patch landed 19:59, `--force --budget 240` ran 20:06,
mobile-bill.docx was stamped 19:57 - older than the patch, newer than the class - so it was skipped.
The pass compared 165 documents as "0 worse, 0 better, 165 identical". That null was false: the same
document converted by hand at 20:29 with the dither on has row heights 345/360/375, while the file the
measurement scored has 360/380.

## The fix, exactly

Under `--force`, compare the engine SOURCE against the compiled class and refuse when the source is
newer, because every document measured after that point is a measurement of an engine the run did not
build. Replace the three lines above with:

    if _force:
        _src_dir = ENGINE_SRC + "/app/src/main/java/com/kavopdf/app/engine"
        _newest = 0.0
        for _r, _d, _fs in os.walk(_src_dir):
            for _f in _fs:
                if _f.endswith(".java"):
                    _newest = max(_newest, os.path.getmtime(os.path.join(_r, _f)))
        if _newest > _eng_mtime:
            log("REFUSED --force: engine source is newer than the compiled class "
                "(%.0f > %.0f). Build first; measuring now would score every document "
                "against an engine this run did not build." % (_newest, _eng_mtime))
            return -1
    miss=[p for p in pdfs if _need(p)]
    if not miss:
        log("docx 0/%d rebuilt -- every .docx already newer than the compiled engine; this "
            "pass measures the existing build, not a new one" % len(pdfs))
        return len(pdfs)
    log("docx %d/%d rebuilt -- converting %d" % (len(miss), len(pdfs), len(miss)))

## Why it is not landed here

The edit was applied and then reverted. This file is 6-space indented inside a nested function, and
two attempts to splice the block in left mixed indentation - it still parsed, but the refusal landed
outside the branch that prints the line, so the guard never ran. Proven by setting the java mtime two
hours into the future and watching `--force` proceed anyway. A measurement script that silently does
the wrong thing is worse than one that refuses, so the file was restored to HEAD and the exact patch is
written out above instead.

The next run should apply it with a patch tool that preserves indentation, then prove it the same way:
touch the java file forward, run `--force`, and expect REFUSED rather than "213/213 rebuilt".

## Note for whoever applies it

ENGINE_SRC is `/scratch/work/p2w/repo`, not the working clone. Touching a .java in /scratch/work/vv2
proves nothing - the first test here did exactly that and looked like the fix had failed.
