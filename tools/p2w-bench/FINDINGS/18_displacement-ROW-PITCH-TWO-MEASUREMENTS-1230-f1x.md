# 18_displacement — the row pitch, measured twice in Google, and why the +0.75 pt constant does not transfer

**22 Nov 2026 · fixer slot 12:50 · engine back at HEAD · two Google round trips, one probe document
created and deleted · nothing committed to the engine**

## What was measured

mobile-bill is one of the two documents the 11:53 handoff named as blocking a spacer construct worth
6 clean documents. It scores **46/47 in Google with `18_displacement` the only failure** (source=0,
render=1). That is the smallest gap in the class, which is why it is the right probe.

### 1. The row pitch was quantised to WHOLE POINTS before DocxWriter ever saw it. CONFIRMED, and fixed.

The page draws its row rules at `74.52, 92.92, 111.32, 129.72, 148.12, 166.52` — 18.40 pt apart.
The model came out `75, 93, 111, 130, 148, 167`, pitches of **18, 18, 19, 18, 19**, and DocxWriter
faithfully wrote `w:trHeight` **360, 360, 380, 360, 380**.

The cause is `PdfToWord.pointKey(x, y)`:

```java
return ((long) Math.round(x) << 32) | (Math.round(y) & 0xffffffffL);
```

Every table-cell corner is an intersection keyed by this, so every cell rectangle carried
whole-point corners. `snapEdges()` has already merged every collinear edge within `SNAP_TOL` (3 pt)
onto one average, so two corners that should coincide carry the *same float* and round identically
at any precision: the rounding bought nothing and cost 0.4 pt a row.

Keying at milli-points instead (`POINT_KEY_SCALE = 1000f`, both pack and unpack) makes the model
carry `18.40` and DocxWriter write **368 on all 24 rows** — verified by reading the emitted
`document.xml`. This is a correctness fix in the model and is renderer-independent. Patch:
`patches/row-pitch-google-charge-and-pointkey-precision.patch`.

**Not landed**, because it changes the geometry of every table in the corpus and a corpus pass does
not fit a slot. It is measured at the model, not at the corpus.

### 2. Google does NOT lay a ruled row at `declared + 0.75 pt` on a real row. REFUTED.

`18_displacement-TRHEIGHT-HONOURED-LINEBOX-FLOOR-1130-relay.md` measured `laid = declared + 0.75 pt`
on a 28-row synthetic probe and every run since has carried that constant. On mobile-bill it does not
hold, and it does not hold consistently even with itself:

| declared trHeight | declared pt | laid mean pitch (off the exported PDF's rule gaps) | implied charge |
|--:|--:|--:|--:|
| 353 tw (rule charge 15) | 17.65 | **18.69** (19.0 ×20, 18.0 ×6) | +1.04 pt |
| 346 tw (rule charge 22) | 17.30 | **18.04** (18.0 ×24, 20.0 ×1, 17.0 ×1) | +0.74 pt |

Source pitch is **18.40** on every row. So the charge is not a constant, and a 0.35 pt change in the
declaration moved the laid pitch by 0.65 pt — the response is not even slope 1.

The difference from the probe is the row itself: the probe's cells carried `w:before=0 w:after=0` and
no hairline `w:line`; a real row here carries `w:before` 194-210 and `w:line=10` with
`w:lineRule="exact"`. A synthetic row is not a row.

**This is the finding that matters**: the constant every run has been subtracting since 11:14 is
calibrated to a probe that does not resemble the thing it is applied to.

## What did not happen

**No document became clean.** mobile-bill reads 46/47, `18_displacement` source=0 render=1, on the
unpatched engine and on both patched builds. The mean laid pitch moved from 19.1 (HEAD) to 18.69 to
18.04 against a source of 18.40 — closer, and still one check short. By the charter's own test that
is not a fix.

## The next step, stated so the next run does not re-derive it

The law is not "declared + k". Measure it on a **real-shaped row**: a probe whose cells carry
`w:before` and a hairline `w:line="10" w:lineRule="exact"`, sweeping the declared height across
**and** sweeping the border `w:sz`, and read the laid pitch off the exported PDF's rule positions.
If the laid pitch snaps to whole points, an 18.40 pt source pitch is unreachable by any declaration
and `18_displacement` on mobile-bill is a renderer limit, not an engine bug — `calibrate.py` is the
tool that decides that, and it has not been run on it.
