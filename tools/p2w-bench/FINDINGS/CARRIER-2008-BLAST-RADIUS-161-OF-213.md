# The carrier patch rewrites 161 of 213 documents, and one of them is CLEAN

**22 Nov 2026, fixer slot 02:50 IST. Measured, not reasoned.**

The handoff carried `rule-carrier-horizontal-only-2008.patch` as "13 of 16 documents to 42/42 in
Google, one build away". Both of those numbers are true and both are about the same 16 documents.
Nobody had measured the other 197. This run did.

## Method

A `.docx` that is byte-identical under two engines cannot score differently in any renderer, so the
blast radius is exactly the set of documents whose `.docx` CONTENT changes. Container bytes are not
stable between runs (zip entry mtimes differ), so the hash is canonical: sha256 over every zip
entry's name and bytes in sorted order (`canon.py`).

    corpus            213 PDFs (4 release zips + benchmarks/corpus-extra + benchmarks/realworld)
    engine A          HEAD c55e1916                 docx fingerprint 226f7f2df3013ad7
    engine B          HEAD + horizontal-only patch  docx fingerprint 78ab519d6e92a2ee
    conversion        ConvertOne, one JVM per document (state is carried between documents
                      inside ConvertAll - a batch is not the same measurement), W=2
    timings           build 36-38 s warm; convert 213 docs p50 7.2 s, mean 7.8 s, max 23.8 s

Instrument check: HEAD was converted twice, once here and once in an independent pod, and the
canonical hashes agree on all 16 documents both runs converted (`head.jsonl` vs `head-check.jsonl`).
A conversion of the same document twice with the same engine gives a different raw sha256 and the
same canonical hash - that is why the hash is canonical.

## Result

    changed    161 of 213
    unchanged   52 of 213

Cross-referenced against `benchmarks/gverify/` (Google, the authority):

| changed documents | count | what it means |
|---|---:|---|
| currently FAIL `32_stroke_lines` | 143 | gain candidates - the construct the patch targets |
| pass `32_stroke_lines`, Google scores them | 5 | **pure risk: the rule already renders, and is replaced anyway** |
| `page_count_refused` - no Google score at all | 13 | invisible risk, including the three heaviest horizontal-rule documents |

The five that change while already passing `32_stroke_lines`:

    51_two_cm_margins            42/42 TODAY  <- one of the six clean documents
    77_arabic_rtl_document       39/47  fails 05 17 18 26 43 47 59 60
    373_leave_application_form   43/47  fails 05 18 23 60
    374_org_chart                39/42  fails 05 18 26
    382_architecture_diagram     41/42  fails 05 only

## Why this matters more than the 13

`51_two_cm_margins` passes all 42 checks in Google today. The patch replaces one of its two
floating `<w:drawing>` rules with a 1x1 bordered table (`document.xml`: 2 drawings / 0 tables ->
1 drawing / 1 table). Nothing in the 16-document measurement could see that, because 51 was not in
it - the 16 were selected as "fails exactly {05, 32}".

A document that is already right, rewritten by a patch that is supposed to fix documents that are
wrong, is the definition of the trade the gate forbids. `regress.py` would not catch it either: the
Google regression check reads `benchmarks/gverify/`, and a changed document with no new result keeps
its old count.

## The three ways forward, and what each costs

1. **Measure Google on all 161.** The only complete answer. At the measured 36-45 s per document
   through Drive that is 100-120 minutes - two full slots, and the upload/export loop is the part
   that has failed runs before.
2. **Narrow the predicate so it cannot fire on a rule that already renders.** The carrier exists
   because some rules are dropped in Google; `51`'s are not. What separates them is a property of
   the drawing (and is measurable in the `.docx` bytes), not of the check. This is the build the
   next slot should make, and `benchmarks/blast-carrier-2008.json` gives it the exact 5 + 13
   documents to be right about.
3. **Land it and accept the risk.** Not available: it changes a clean document and 13 unscored
   ones, and the gate has no Google result to justify either.

## The files

    benchmarks/blast-carrier-2008.json     all 213 rows: head hash, patched hash, changed, Google status
    tools/p2w-bench/patches/rule-carrier-horizontal-only-2008.patch   the patch, unchanged

The engine is reverted to HEAD; `regress.py --check` passes; nothing in this finding is a commit of
the patch.
