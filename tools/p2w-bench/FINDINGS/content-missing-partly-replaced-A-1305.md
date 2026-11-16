# content-missing-partly-replaced / A - the engine code path (partial)

Asked: which code path decides how TALL a block emitted from a PDF text box (a `wps:txbx`
       text box / anchored frame) is, and what structural condition makes source page 7 of
       `041122-Account_Opening_Form.pdf` overflow so our .docx emits 10 pages against 9?

Claim: The height of a block on page 7 is decided by the TABLE ROW height path, not by the
       text-box path: `DocxWriter.java:6086` (`rowHeightTw = Math.max(rowHeightTw,
       paraContentTw + ruleTwHere)`) computed from the page's own row edges at :6040, written at
       `DocxWriter.java:6123` as `<w:trHeight w:val=... w:hRule="atLeast"/>`. The page-fit
       guard then measures the page with `spacingTw` (`DocxWriter.java:449`), which charges
       `w:trHeight` and deliberately skips the paragraphs inside a cell or a `w:txbxContent`
       (:461-478), and the only repair it has left - `shaveToFit` (`DocxWriter.java:495`) - can
       take twips ONLY from `w:before` at `depth == 0`, i.e. never from inside a table. Page 7 is
       one table (24 rows, 16649 twips of `w:trHeight`, 107 twips of flow prose), so on that page
       there is nothing to shave and the residue survives into the file.

Evidence (MEASURED, this run, built engine at HEAD):
       `java ConvertAll` on the single PDF gives pages=9, 480 paragraphs. Unzipped
       `word/document.xml`, split on `<w:br w:type="page"/>` (9 segments) and re-ran
       `spacingTw`'s algorithm per segment:
         p1 16741  p2 16741  p3 6679  p4 16741  p5 16741  p6 16743  **p7 16756**  p8 16686  p9 13040
       Page 7 is the only page above the shaved target (842.14 pt * 20 = 16840 twips, minus the
       96-twip fit reserve = 16744), by 12 twips - the same 24-twip-scale residue the comment at
       `DocxWriter.java:495` describes for bank-statement-5-pages.
       Page 7's charge is not prose: `p.count('<w:tbl>') == 1`, `w:txbxContent` count 0,
       24 x `w:trHeight` summing 16649, and the 28 flow paragraphs outside the table sum to 107
       twips (27 of them are 1-twip carriers). Per row: 17.2-17.4 pt for the one-line form rows
       (the page's own 17.5 pt pitch), but row 1 84.1 pt, row 15 41.0, row 18 29.1, rows 19-21
       41.0, row 22 (the whole Verification block) 231.5, row 23 41.4 - row 23 holds the single
       character "7", the page number, charged 41.4 pt.
       Source page 7 (PyMuPDF) puts its last line at y 802.7 on an 842.14 pt sheet, so the page
       has ~40 pt of slack; the emitted table is 832.5 pt tall plus the 5.4 pt of flow, i.e. it
       is written against the paper's edge with nothing left.
       Code: `DocxWriter.java:6020-6130`, `:449-478`, `:495-560` (read).

Status: partial - the code path and the arithmetic are measured; the falsifying run below has
        not been executed yet.
