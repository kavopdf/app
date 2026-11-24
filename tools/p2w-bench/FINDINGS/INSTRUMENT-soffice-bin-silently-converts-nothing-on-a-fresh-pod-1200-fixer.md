# INSTRUMENT: `soffice.bin` converts nothing on a fresh pod; the `/usr/bin/soffice` wrapper does

**24 Nov, 12:00 IST. Found by asking why a fresh pod measured 0 of 213 four times in a row.**

## What I believed

`SOFFICE_BIN = "/usr/lib/libreoffice/program/soffice.bin"` was the supported entry point, and the
21 Nov note (p2w.py:219-250) was right that the first launch on a fresh pod fails because
`$HOME/.config/libreoffice/4` has to be created by a process whose stdio is DEVNULL.

## What I measured

On a fresh pod, with the `_soffice_warm()` fix in place and after the profile warm-up had run:

    /usr/lib/libreoffice/program/soffice.bin --version                      -> LibreOffice 7.4.7.2 (works)
    /usr/lib/libreoffice/program/soffice.bin --headless --convert-to pdf \
        --outdir t1 <a known-good python-docx .docx>                        -> rc=0, NO file, NO output
    soffice (i.e. /usr/bin/soffice) --headless --convert-to pdf --outdir t2 <same file>
                                                                            -> "convert ... -> t2/t.pdf", 6195 bytes
    /usr/lib/libreoffice/program/soffice.bin -env:UserInstallation=file:///scratch/work/lo-profile ...  -> rc=0, NO file
    ls -d $HOME/.config/libreoffice  after every one of the above           -> still does not exist

The warm-up cannot fix it, because the failure is not a cold profile: the `.bin` never creates the
profile at all. The wrapper is what sets up the environment the `.bin` needs.

## What is now true

`benchmarks/p2w.py` prefers `/usr/bin/soffice` and keeps the `.bin` as the fallback. After the change
the same corpus pass that had printed `chunk 1: measured 0 of 213` for four consecutive calls measured
163 of 212 documents, 12 per ~50 s.

**This is why every fresh-pod corpus pass this pipeline has ever run reported "0 of 213"** — not the
profile, not the budget, not the batch. A run that cannot render a `.docx` to PDF cannot measure
anything, and the run reports it as an empty table rather than an error.

## What would prove this wrong

An image where `/usr/lib/libreoffice/program/soffice.bin` converts a `.docx` while `/usr/bin/soffice`
does not. Then the preference must be reversed. The fallback means such an image behaves exactly as
before this change.
