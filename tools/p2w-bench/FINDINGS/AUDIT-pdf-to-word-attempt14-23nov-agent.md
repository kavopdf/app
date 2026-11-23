# PDF-to-Word — deep audit, attempt 14 of 15

Agent, 23 Nov 2026. Read-only. Fourth of five on `DocxWriter`. The target was character accounting —
`04_chars_missing` (65 documents) and `05_chars_extra` (43).

---

## N1 — the drop rules are narrow and each one is documented with its measurement

I looked for text the writer throws away, and found a codebase that has already done this work honestly. Two
examples, both in the fill code:

    "Measured over corpus-v1's 3,192 shape fills, the old rule dropped 402 fills in 87 [documents]"

    "202 of the 402 fills the old lightness rule dropped were cell fills with a word inside them, and every one
     of them sat 9 levels or more off the page"

The current rule is `isPageColour` (3013): a fill is dropped only when
`255 - min(r,g,b) <= PAGE_TOL`, i.e. only when it is the page's own white to within tolerance. The old rule
dropped 402 fills; the new one drops the ones a reader cannot distinguish from paper.

**So fills are not the missing-character mechanism, and this is worth recording: the obvious suspect was already
investigated and narrowed with numbers.** A run that starts by re-examining fill drops is repeating finished work.

---

## N2 — the pattern in the 65 failing documents is text that lives inside a graphic

Counted from `benchmarks/gverify`:

    documents failing 04_chars_missing : 65
    stamp documents                    : 16
    of those, failing 04               : 14      <- 87.5%
    failing 04 that are NOT stamp      : 51

**Fourteen of the sixteen stamp documents lose characters.** And the non-stamp fifty-one are, by name, the same
shape of document: `311_fir_police_form`, `318_court_summons_form`, `322_mutual_fund_factsheet`,
`323_credit_card_statement`, `330_cad_drawing_sheet`, `331_pid_diagram`, `344_customs_declaration`,
`352_certificate_ornate_border`, `25_signature_block_underscores_txtpos`, `28_value_overflows_cell_txtpos`.

**Forms, statements, drawings, certificates.** What they have in common is not a font or a colour or a language:
it is that their text sits inside a graphic — a stamp, a box, a diagram, an ornate border.

---

## N3 — one mechanism for the stamp half is in the code, and it is a measurement guard

At 3432, inside the line-measuring pass:

    boolean skip = false;
    for (PdfToWord.Box b : p.boxes) {
        if (b.rotated || b.runs.isEmpty() || b.text().trim().isEmpty()) {
            skip = true;
            break;
        }
        … measure …
    }

A paragraph containing **any** rotated box aborts its measurement. **This is a guard, not a drop** — the paragraph
is still written — so it is not the missing-character mechanism by itself. But it is the clearest evidence that
`rotated` is a first-class special case in this writer, and stamps are exactly the rotated case.

**What I could not establish from code alone:** whether a rotated box's text reaches the document as text at all,
or is written as an image. The user's own standing rule is that stamp text must be text and not a screenshot, and
fourteen of sixteen stamp documents failing `04_chars_missing` is what that rule failing would look like.

**This is the one question worth a measurement, and it is small:** open the `.docx` of
`01_stamp_rotated_15deg_upright` and look for the stamp's words inside `w:t`. If they are not there, N2's stamp
half is confirmed and the mechanism is "rotated text is rasterised".

---

## N4 — `05_chars_extra` (43) is the other direction and I found nothing to say about it

Searched for places that invent characters — padding, filler, synthetic spaces — and found none that would
plausibly add characters to a document. `05_chars_extra` is 43 documents and I have no mechanism to offer.

**Saying so is more useful than a guess.** The next run should read `05_chars_extra`'s own definition in
`verify_google.py` first — what it counts as "extra" may not be invented text at all but duplicated text from a
second pass, which would make it a different defect entirely.

---

## For the fixer

1. **N2 is the lead:** 14 of 16 stamp documents lose characters, and the user's rule is explicit that stamp text
   must be text. One `.docx` inspection settles whether it is rasterised.
2. **N1 says do not start with fills.** That work is done and measured.
3. **N4:** read the check before hunting the cause. A check that counts duplicates is not a check that counts
   inventions.

Verify before changing. This attempt read code and counted verdicts; it ran nothing.
