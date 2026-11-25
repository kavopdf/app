# CORRECTED: p2w.py --force does not measure a stale build

This file claimed that --force measures a stale .docx and prints a success-shaped line. On re-reading the
code, both halves are wrong.

## The code

    _eng_mtime = os.path.getmtime(_eng) if os.path.exists(_eng) else 0.0      # p2w.py:1332

    def _need(p):
        ...
        if _force:
            if not (os.path.exists(dx) and os.path.exists(tx)):
                return True
            return min(os.path.getmtime(dx), os.path.getmtime(tx)) < _eng_mtime
        return not (os.path.exists(dx) and os.path.exists(tx))                 # p2w.py:1333-1341

That is the right comparison: if the compiled engine is newer than both outputs, the pair is stale and gets
rebuilt. Comparing against the engine binary - not against the source, and not against a commit - is what
makes it correct, because the binary is what produced the output.

## The line

    log(f"docx {len(pdfs)-len(miss)}/{len(pdfs)} -- converting {len(miss)}")   # p2w.py:1344

    docx 0/213 -- converting 213

reads as "0 of 213 present, converting 213". It states what is missing and what will be done. It is not a
success claim, and it was mis-read as one.

## Why this correction is kept

Two of my findings this session were produced by pattern-matching a symptom to a known disease without
reading the code that produced it - this one and the txt_rank "live" hash. The real defects were found the
other way: by reading the code and then measuring. The correction is recorded rather than deleted so the
next reader does not inherit the same wrong diagnosis.

## Status

No bug. No change made. If a future run does observe a stale measurement from --force, the cause is
elsewhere - start from _eng_mtime being 0.0, which happens when the compiled engine does not exist and
makes every comparison false.
