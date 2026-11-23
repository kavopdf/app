# measure_gate demanded 213 rows from the table gate.py publishes with 212

**Instrument defect. Measured 23 Nov 2026.**

## The contradiction, in one file

`gate.py` publishes `benchmarks/RANKING.csv` and, after the copy, re-applies `EXEMPT.json`: the exempt
document (`416_many_tiny_pages`, 300 pages) is **dropped** rather than written with `share5 = 0.0`,
because a zero means "unknown" and would read as a perfect score.

`measure_gate.py` reads the same `EXEMPT.json` twice. `exempt()` feeds `blocked`, which correctly skips
the exempt document — and `expected_docs()` returned `SYNTHETIC + real`, ignoring it. So the gate held
two answers to one question:

    docx   212/212 scored, 1 exempt, 0 blocking, 213 expected
    - RANKING.csv holds 212 documents, the corpus should hold 213

`NOT READY`, on the publisher's own honest table.

## Why this is the whole of two lost slots

An engine change cannot be committed until the table is committed with it, and the table cannot be
called complete while this fires. That is the mechanism behind "measured, fix not landed" appearing
twice in the ledger for this same class. A gate that cannot accept its own publisher's output blocks
every engine change, and it looks exactly like a dead pipeline from outside.

## The fix

    return SYNTHETIC + n - len(exempt()["docx"])

## What it prints now

    docx   212/212 scored, 1 exempt, 0 blocking, 212 expected

## What would prove this wrong

A corpus where an exempt document *is* in `RANKING.csv`. Then the exemption has changed policy and
`expected_docs` should count it again — but `gate.py`'s drop is the authority, and it drops.
