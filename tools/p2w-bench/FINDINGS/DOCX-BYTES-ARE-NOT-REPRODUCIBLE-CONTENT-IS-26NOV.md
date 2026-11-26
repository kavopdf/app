# The .docx writer is not byte-deterministic. The content is.

The 12:16 relay run asked the right question and left it open:

> "Two conversions of 600, one patched and one at HEAD, produced different bytes - 8cdb2dd8e49e3605...
> against ca292defbde202803... The sha256 comparison the earlier finding relied on is therefore not
> reproducible across runs, and scope.py --prove rests on exactly that comparison. That is the first
> question the next run must settle: convert one document twice at one engine and compare. If the writer
> is not deterministic, every byte-identity claim in FINDINGS/ needs re-reading."

## Answered: convert one document twice at one engine

`600_reviewed_invoice_with_annotations.pdf`, engine `a4d8fca469bba636`, two runs back to back:

    run 1  sha256 2b1fd92ff99dc79f7797a734...   6983 bytes
    run 2  sha256 b8e7860dd45e9f4ab1d56f19...   6983 bytes

    DETERMINISTIC: False

## And the cause is not the content

Unpacking both and comparing file by file: **no inner file differs**. Nine entries, all nine
byte-identical. What differs is the zip metadata:

    run 1  every entry date_time = (2026, 11, 26, 8, 52, 28)
    run 2  every entry date_time = (2026, 11, 26, 8, 52, 32)

The writer stamps each entry with the moment it was written. Four seconds apart, two different files,
one identical document.

## What this means for every byte-identity claim

They are all unreliable as stated, and none of them are wrong about the thing they meant. A claim that
"the .txt-only change cannot move a .docx byte" is still true about the content; it just cannot be tested
by hashing the file.

The test that works is to unpack and compare the parts. `tools/p2w-bench/docx-diff.py` does that:

    $ python3 tools/p2w-bench/docx-diff.py /tmp/det/r1 /tmp/det/r2
      compared by content (zip metadata ignored): 1 documents
      identical in content: 1
      PROVEN - the untouched format did not move

    $ diff -rq /tmp/det/r1 /tmp/det/r2
      Files .../600_reviewed_invoice_with_annotations.docx and .../600_reviewed_invoice_with_annotations.docx differ

Same two files. The old instruction says they differ; they are the same document.

## What was changed

`scope.py --prove` used to print `diff -rq /tmp/scopeA /tmp/scopeB` as the proof. It now prints
`docx-diff.py`, with the measurement above and the reason in the output, because a proof that reports
every document as changed proves nothing and the next run would have read it as a regression.

The engine was not touched. Making the zip entries carry a fixed timestamp would make the bytes
reproducible and is the right fix, but it is an engine change and it needs its own measurement.
