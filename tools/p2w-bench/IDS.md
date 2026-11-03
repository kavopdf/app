# ID integrity — the metric that catches what totals cannot

A wrong GSTIN, CIN, IFSC, account number or invoice number makes a business document
useless. `char volume` and `word recall` cannot see it: they measure totals, so appending
four digits to a CIN moves neither.

    python3 tools/p2w-bench/score_ids.py <folder-with-.txt>

The reference is PyMuPDF's text; each identifier found there must appear in our output as a
**whole token** — the same string with a non-alphanumeric character on both sides. A
substring test is not enough: `CIN U28129HR2004PTC` followed by `0412` is a different CIN.

Patterns checked:

    gstin    12 digits + 5 letters + 4 digits + letter + digit + Z + alnum
    pan      5 letters + 4 digits + letter
    cin      L or U + 5 digits + 2 letters + 4 digits + 3 letters + 6 digits
    ifsc     4 letters + 0 + 6 alnum
    acct     11-18 digits
    invoice  XX/YY-ZZ/NNNN
    eway     12 digits
    uin      12-14 digits

## Floor at KavoPDF 3.47.0

    25 documents carry identifiers
    107 identifiers found in the reference
    107 survive in our output         100.00 %
    documents with a lost or corrupted ID: 0 / 25

That is a real result, and it is worth more than any percentage of characters: an invoice
with one wrong GSTIN is not 99 % correct, it is wrong.

## What it does not catch

A CIN whose reference form is incomplete. `gst-invoice-3line-items` has
`CIN U28129HR2004PTC` in the reference and `CIN U28129HR2004PTC0412` in our output — we
appended four digits that belong to a different field on the same line. The reference
string fails the CIN pattern (it has no six-digit suffix), so no identifier is tested there
and the metric reports a pass.

That is a **merge** bug, not a lost ID, and it belongs to line order: two fields on one
baseline welded together. It is on the list.
