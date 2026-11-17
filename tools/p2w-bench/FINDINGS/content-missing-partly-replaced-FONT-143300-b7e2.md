# content-missing-partly-replaced / FONT - which mechanism makes the reader honour the page's widths

Source: `041122-Account_Opening_Form.pdf` (9 pp) against the engine's own .docx.
Reader measured against: LibreOffice at `/usr/lib/libreoffice/program/soffice.bin`.
PDF face: `Effra-Regular` (subset `EIMQAG+Effra-Regular`, no fsType in the FontDescriptor).
The docx names `Effra`; LibreOffice substitutes `NotoSans-Regular`, ~10.5 % wider.

One question was asked: which of `<w:w>` character scaling, an embedded font part, or
`<w:fitText>` makes LibreOffice render the source's 10 pt text at the source's advance widths?

## Result (measured, three variants, one cell changed at a time)

| mechanism | pages | lines in the verification block | block height pt | font rendered | works? |
|---|---|---|---|---|---|
| source PDF p7 (reference) | 9 | 17 | 239.1 (baseline span 220.0) | Effra | - |
| engine docx, unchanged | 12 | 26 | 338.0 | NotoSans | - |
| `<w:w w:val="91"/>` | 12 | 20 | 266.0 | NotoSans | no, insufficient |
| `<w:w w:val="88"/>` | 12 | 17 | 230.0 (span 220.0) | NotoSans | geometry yes |
| embedded `.odttf` (fontTable + embedRegular + settings/embedTrueTypeFonts) | 12 | 26 | 338.0 | NotoSans | **NO - ignored** |
| `<w:fitText w:val="10530"/>` | 12 | 26 | 338.0 | NotoSans | **NO - ignored** |

Verdict: LibreOffice honours per-run `<w:w>`; it ignores `<w:fitText>` outright and it
ignores an embedded TrueType font part completely (same page count, same substitute faces,
byte-identical geometry to the baseline). The required scale is 88, not 90 - computed from
per-paragraph Noto/Effra advance ratios (minimum 88.15 %) and confirmed by render.

## Commands

    # extract the subset (extract_font is on the Document, not the Page; returns a 4-tuple)
    python3 -c "import pymupdf; d=pymupdf.open('041122.pdf'); n,e,t,b=d.extract_font(112); open('112.ttf','wb').write(b)"
    # render - a FRESH LibreOffice profile exits 81 with no output on the first run and
    # succeeds on the second; one shared, pre-warmed -env:UserInstallation is the recipe.
    /usr/lib/libreoffice/program/soffice.bin --headless --norestore \
        -env:UserInstallation=file:///scratch/work/agent-font/out/lo-profile \
        --convert-to pdf --outdir OUT V.docx
    # measure: page count, lines and y-range of the block from "Verification" down, faces

## Ruled out

- `<w:fitText>`: no reflow whatsoever, identical to baseline in every measurement.
- Embedded font part: ignored by the reader. Do not build this into the engine.
- `w:w=90` and `w:w=91`: insufficient (20 lines, 266.0 pt).

## What would prove this wrong

A variant that changes page count without changing the block's line count - i.e. the pages
moved for another reason. That happened: at `w=88` the block matches the source exactly and
the document still renders 12 pages, because the folio of each page is itself body content
and is pushed onto its own sheet. Both mechanisms were needed; neither alone is enough.
