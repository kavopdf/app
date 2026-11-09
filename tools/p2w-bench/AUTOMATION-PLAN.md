# KavoPDF — 100% Automatic Self-Healing Pipeline

Nothing in this document is manual. Every step runs unattended. The only human
input is the decision queue, and that is deliberately small.

---

## 0. The one sentence

Convert through the real APK, render through Google's own engine, judge by ink
and not by text, name the cause, fix the cause, prove nothing broke, ship.

---

## 1. Why the previous attempt failed

The P2W cron ran twelve times, succeeded twelve times, and fixed nothing. Three
reasons, and this plan exists to not repeat them:

1. **It was document-driven.** One or two documents per run, fifteen to thirty
   minutes each. Two hundred and eight documents would take about a hundred runs.
2. **Its metric was blind.** The gate counts words and pages. It cannot see
   position or reading order, so it passed documents the user could see were
   wrong.
3. **It measured a proxy.** LibreOffice, not Google Docs. LibreOffice will not
   rotate glyphs in a docx text box and renders continuous section breaks
   correctly; Google Docs does the opposite of both. Every conclusion drawn from
   that render was suspect.

---

## 2. Architecture — four layers

```
LAYER 1  CONVERT    APK on Android emulator (GitHub Actions)
LAYER 2  RENDER     docx -> Google Drive -> PDF export
LAYER 3  SEE        region by region, six ink measures
LAYER 4  DIAGNOSE   six deltas -> pattern -> cause
```

### Layer 1 — the real app, not a harness

A Java harness tests the engine. The user runs an app. The app has its own layer
that a harness never exercises: opening the PDF, the OCR path, saving the file,
permissions, memory, and crashes. The `PDFRenderer` `IllegalStateException` that
killed the stamp work appeared **only on device** and never in the harness.

```
FAST loop    engine harness     iteration       ~5 min
TRUTH loop   APK on emulator    confirmation    ~15 min per batch
```

**Agreement check, defined precisely:** run the same document through both, take
both docx files, put both through Layer 2 and Layer 3, and compare the
**per-region PASS/FAIL verdict**, not the bytes. Bytes will never match —
ordering, ids, timestamps. A verdict disagreement means the app layer has a bug
the harness cannot see, and it goes to the decision queue.

One emulator boot per batch. Ten documents converted in that one session.

### Layer 2 — Google's engine

Drive export is Google's renderer. That is what the phone shows. LibreOffice is
a proxy and a poor one.

**Setup:** a service account, and a folder on the user's Drive shared with the
service account's email as Editor. The service account has its own 200,000
exports/day quota, so the user's own quota is untouched. Each document is
uploaded, exported, downloaded and deleted in the same job — nothing accumulates.

**Google Docs app:** Firebase Test Lab, **two documents per batch**, not all ten.
Drive and Docs share the engine; the app differs only in interaction, and two
documents per batch catches that. Forty-two runs, not four hundred and sixteen.

### Layer 3 — see by ink

A region is a text block or a drawn object in the source PDF. Both renders are
made at 150 dpi, the region is cropped from each, binarised, and six numbers are
taken. Text is not consulted, which is why repeated lines, curved seal glyphs and
font substitution cannot fool it.

| # | Measure | Catches |
|---|---|---|
| 1 | Coverage | text missing, extra, white patch |
| 2 | Centroid | drift, and its direction |
| 3 | Bbox | wrapping, size |
| 4 | Density profile, 8x8 | the shape of the ink |
| 5 | Edge density | stroke thickness |
| 6 | Colour, delta-E | wrong colour, faded rule |

**Matching, two passes:**

```
Pass 1  exact text      ~80 % of regions
Pass 2  ink signature   the rest
Pass 3  whatever is left is UNMATCHED - and that is the defect
```

Unmatched needs no threshold. Three categories fall out on their own: in the
source but not the output is **missing**; in the output but not the source is
**extra**; in both but not matched is **wrong**.

**Tolerance comes from data, not from me.** Ten documents verified by hand, their
own deltas measured, the 95th percentile of each becomes the tolerance.

**Images:** SSIM of 0.92 or better, **and** the docx image resolution must be at
least the PDF's — a re-compressed image that looks close is still a quality
regression.

**Vector graphics** — charts, logos, seals — are not images: ink coverage, edge
density, centroid and colour.

### Layer 4 — diagnose, never judge

Math runs only on regions the visual check already failed. It answers "how much,
in which direction", nothing else.

```
dx, dy         pt, signed     position and direction
d-coverage     %              missing (-) or extra (+)
d-bbox         %              wrap or resize
d-edge         %              weight
dE             CIE76          colour
d-density      0..1           shape match
```

The pattern names the cause:

```
d-coverage ~ -100%          MISSING
d-coverage ~ +100%          EXTRA
dy != 0, rest ~ 0           DRIFT
d-edge < -20%               TOO THIN / FADED
dE > 3                      WRONG COLOUR
d-density < 0.6, d-bbox ~ 0 WRONG CONTENT, RIGHT BOX
d-bbox > 5%                 WRAPPED
d-density > 0.85, all ~ 0   THE TOLERANCE IS WRONG, NOT THE DOCUMENT
```

That last line is the most important one in this document. It fired three times
in one session: a reading-order metric that capped a perfect document at 21 %,
a gate that called its own fix a regression, and a curved seal that inflated a
matching metric while sitting exactly where the page put it.

---

## 3. Metric self-test — every run

Ten known-good documents must score zero failures. Ten known-bad documents must
all fail. If either condition breaks, **the pipeline stops and the metric is
repaired — not the document.**

---

## 4. Cause grouping — the algorithm

Grouping is the heart of the loop, so it is defined rather than left to
judgement. Two failures are the same cause only when **all four keys agree**:

```
1  failing region set        which regions, by identity
2  delta pattern             drift / missing / thin / colour
3  code path                 table / paragraph / stamp / shape / column
4  document class            digital / scanned / form / table-ledger
```

All four agree: same cause. Any one differs: different cause.

**Grouping suggests, diagnosis confirms.** No fix is attempted on a group until
one document from it has been diagnosed to a specific line of code. This matters
because two documents can fail identically for unrelated reasons, and fixing the
wrong one wastes an attempt from a budget of five.

---

## 5. Document classification — before the loop

Not every document is fixable, and a scanned page with no text will burn five
attempts producing nothing.

```
digital    text extractable          normal loop
scanned    image only                OCR path, separate loop
empty      no content                queue
corrupt    will not open             queue
```

Each class gets its own loop. Classification runs once, at the start, and is
recorded.

---

## 6. The loop

```
BATCH  (ten documents, ordered by severity)

  1  emulator boots once, converts ten            ~12 min
  2  Drive export, ten PDFs                        ~2 min
  3  metric self-test                              ~1 min
  4  visual check, ten documents                   ~5 min
  5  classify any failures, group into causes
  6  for each cause: up to five attempts
       fix -> targeted regression -> commit
  7  whole-corpus regression at batch end          ~30 min
  8  all clear -> commit
  9  compile, sign, release APK
 10  same batch again on the new APK (steps 1-8)
 11  Firebase: two documents, Google Docs app
 12  next batch
```

Two to three hours per batch. Twenty-one batches, two passes, roughly a hundred
hours — four to five days continuous.

### Batch order is not arbitrary

```
severity = median dy * 0.5 + worst dy * 0.3 + unmatched_count * 0.2
```

Worst batch first. Inside a batch, worst document first. The 298 pt certificate
before the 2 pt ledger.

### Attempts are per cause, not per problem per document

Five attempts per **cause**. A cause is fixed once and helps every document in
its group. The alternative — five attempts per problem on every document — is
thirteen hours for a single document.

**Each attempt records why it failed**, and attempt N+1 may not repeat attempt
N's approach. An attempt that fails for the same reason twice is not an attempt,
it is a loop.

---

## 7. Regression — targeted, then whole

A whole-corpus regression after every document is 208 x 208 = 43,264
measurements, sixty hours per pass. It will never finish.

```
after each fix:   the code path it touched
                  + every document that uses that path
                  + twenty random documents
after each batch: all 208
```

A fix to table borders cannot affect a text-only document. Not measuring what
cannot have changed is not laziness, it is arithmetic.

### The ratchet is per-region identity, not a count

A fix that repairs one region and breaks another leaves the count unchanged and
passes a count-based ratchet. So the ratchet compares **which** regions pass:
any region that passed before and fails now is a regression, whatever the total
says.

### Ship proof

```
gh api repos/kavopdf/app/compare/<tag>...main --jq '.ahead_by'
```

Zero. One API call, not a second full pass.

---

## 8. Progress — how we know it is working

The ratchet only says "not worse". It cannot say "better", and a loop that runs
a hundred hours to produce three fixes needs to be caught early.

```
commit     unmatched total
abc1234    1,847
def5678    1,203    -35 %
ghi9012    1,190     -1 %   <- this fix did nothing
```

**Rule:** if three consecutive fixes reduce the unmatched total by less than 5 %,
the loop stops and writes STUCK to the decision queue with the evidence.

---

## 9. Stopping condition

```
100 % documents   worst dy <= 10 pt      no slack
 95 % documents   median dy <= 3 pt      small slack on the median
  0  documents    wrong page count
  0  documents    missing text
self-test         10 / 10 pass
queue             empty
```

The worst-dy line has no slack on purpose. With slack there, ten documents can
fail completely and the plan still says done. Documents that miss the target are
listed by name in an ACCEPTED section — visible, not hidden.

---

## 10. Records — append only, never rewritten

`REMAINING-DEFECTS.md` was rewritten twenty-seven times a day by the old cron and
lost its own headings. Nothing in this pipeline rewrites a record.

```
causes/CAUSE-<n>.md        cause, documents, fix, commit, before/after
batches/batch-<n>.md       every attempt, and why it failed
decisions/QUEUE.md         what needs a human decision
metrics/<commit>.json      all 208 scores at that commit
ACCEPTED.md                documents that will not reach target, by name
COVERAGE.md                what ran, what did not, and why
```

---

## 11. The decision queue

The loop cannot make design decisions, and it must not pretend to. Anything that
needs one goes to the queue and is not attempted.

Expected: five to ten items over two to three weeks, each a ten-minute decision.
That queue is the only thing the user reads. Not a daily report of 208 documents.

---

## 12. Blind spots — named in every verdict

```
dark mode              unverified   structural rules say "may break", not how much
editing / selection    unverified   structural proxy plus a Firebase sample
android app rendering  unverified   emulator is a proxy, not the user's phone
```

These are not eliminated. They are printed, every run, so nobody mistakes a
passing document for a verified one.

---

## 13. Secrets

Never in the repository.

```
keystore (base64)      GitHub Secret
keystore password      GitHub Secret
Drive service account  GitHub Secret
Drive folder id        GitHub Variable
```

`.gitignore` carries `*.jks`, `*.json`, `local.properties`.

---

## 14. What the pipeline needs on day one

```
1  GitHub Actions workflow, public repo — unlimited minutes
2  service account + shared Drive folder
3  structural_pixel_diff.py    regions, six measures, six deltas
4  self-test set               10 known-good, 10 known-bad
5  cluster.py                  the four-key grouping
6  classifier.py               digital / scanned / empty / corrupt
7  ratchet                     per-region identity
8  emulator job                APK, one boot per batch
9  Firebase job                two documents per batch, optional
```

All free. No paid software anywhere.

---

## 15. Known dead ends, written down

**The emulator is flaky.** Some of the forty-two runs will fail. Three retries,
then the batch goes to the queue as CANNOT RUN. Those documents are not counted
as passed, and they appear in COVERAGE.md.

**Drive and Docs can diverge.** They are the same engine but not the same
product. The Firebase sample is the only check on that, and it is a sample.

**The measurement can be wrong.** It was, three times, in one session. That is
why the self-test exists and why a disagreement between the visual check and the
deltas resolves in favour of repairing the metric, not the document.
