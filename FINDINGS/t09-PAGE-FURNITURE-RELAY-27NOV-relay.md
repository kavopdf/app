> RELAYED BY A SUB-AGENT THIS RUN. The two claims that matter were checked by the fixer and are
> confirmed: verify_txt.py:939 drops the form-feed separator line, and TxtWriter.java emits "\f\n".

# `t09_page_furniture`: the remaining work, and whether the `.docx` half has a defensible patch

**Analysed:** 27 Nov 2026, repo `https://github.com/kavopdf/app` cloned at `a554f74` ("report 27 Nov relay…"),
`--depth 1` then deepened to 73 commits. **No corpus, no JVM, no Drive.** Every claim below is either a
ledger quote with file+line, a code reading with file+line, or a fact I computed in this sandbox — and each
is labelled. Nothing was built, converted, or measured against a PDF.

---

## 0. The framing, stated first, because the question's premise is half-wrong

`t09_page_furniture` **exists only in the `.txt` instrument.** `verify_txt.py:218` lists it in `CHECKS`;
`verify_google.py` has no check of that id — a `grep` for `t09` over `verify_google.py` returns exactly one
line, `verify_google.py:1784`, an unrelated comment about a form field's inset ("the box's own rule is
furniture, not content").

So there is no "`.docx` half of t09". What exists is one **construct** — page furniture, the lines a page
repeats in its top/bottom band — measured on two surfaces by two different checks with two different
instruments:

| surface | check | where | population it is judged on |
|:--|:--|:--|:--|
| `.txt` | `t09_page_furniture` | `verify_txt.py:1307-1353` | PDF band lines vs `.txt` line counts |
| `.docx` → Google | `44_header_footer` | `verify_google.py:3886-3931` | PDF band lines vs the render's band lines |

The construct is the same object; the code, the instrument and the failure mode are not. Everything below
keeps those two apart, because conflating them is what produced the two contradictory leads in the ledger.

---

## (a) The last recorded lead, verbatim, and where it is

**File:** `tools/p2w-bench/ATTEMPTS.json`, class `t09_page_furniture`, `history[1]`, key `reason`.
**Line 2166** (the history entry), and repeated verbatim at **line 2176** (the class-level `reason`) and
**line 2179** (first element of `reasons`). Recorded `at: "2026-11-26 20:35"`, `attempt 2`, `outcome:
"lead"`, `moved: 0`, `changed.files: []`.

> `the band arm the FINDINGS patch uses reads 0 of 29 (the .txt has no form feeds: segs=1), and dropping one-char keys alone leaves Date 6 vs 3; a correct fix needs an aligner plus a full 213-doc .txt re`

Line 2166 is **truncated mid-word** at 200 characters — the ledger's writer cut it. The complete sentence is
at line 2176:

> `…a correct fix needs an aligner plus a full 213-doc .txt re-measure, which did not fit`

Corroborating records of the same attempt:
- `tools/p2w-bench/CLASS-HISTORY.jsonl:233` — `{"at": "2026-11-26 20:35", "attempt": 2, "class": "t09_page_furniture", "outcome": "lead", "requeues": 0, "round": 1, "status": "OPEN"}`
- `tools/p2w-bench/HANDOFF.json:74` — agent `t09_A-01`, class `t09_page_furniture`, `status: "running"`, deployed `20:47`, `finding: null`, question: *"is the 125 single-char present a TxtWriter line-assembly defect or a t09 band asymmetry - census every one of the .txt single-character lines against the drawn line it came from"*.
- The answer to that question **is already in the tree**: `FINDINGS/t09_page_furniture-SINGLE-CHAR-CENSUS-agent-26NOV.md` (verdict: *"Instrument asymmetry. The writer is not at fault"*, 29 in-band / 96 outside / writer's share **0**). `HANDOFF.json` still reads `running` / `finding: null`, so the handoff record is one step behind its own agent.

The lead has two clauses, and they are of very different quality:

| clause | status after this analysis |
|:--|:--|
| "the band arm … reads 0 of 29 (the `.txt` has no form feeds: segs=1)" | **The measurement is right, the cause is wrong.** `segs=1` reproduces on a file that carries every separator, because the reader throws them away. See (c-ii). |
| "dropping one-char keys alone leaves Date 6 vs 3" | **Correct**, and it is a whole-file count. See (c-ii). |
| "a correct fix needs an aligner" | **Not established.** No aligner is needed if the page segmentation the writer already emits is put back into the reader. |
| "plus a full 213-doc re-measure, which did not fit" | **Correct and still true.** |

---

## (b) Is the `.docx` half independent of the blocked `.txt` half? **Yes — five code facts, no inference**

1. **Different consumers of the same model.** `tools/engine-verify/ConvertOne.java:33-37` converts one PDF to
   both formats from one `PdfToWord.Result`, calling `DocxWriter.write(r, …)` then `PdfToWord.writeTxt(r, …)`.
   Neither writer calls the other.
2. **The `.txt` writer contains no reference to the furniture machinery.** `grep -n "inFootBand\|FOOT_BAND\|gapCapTw\|pageHeightPt" app/src/main/java/com/kavopdf/app/engine/TxtWriter.java` → **no output**. The band rule is `DocxWriter`'s alone (`DocxWriter.java:399, 420-425`).
3. **The band guards are four sites, all in `DocxWriter`:** `DocxWriter.java:3623`, `:3649` (the `flowRow` edge-gap and pitch branches) and `:4506`, `:4543` (the `flowFromBox` equivalents), each reading `!inFootBand(ctx, …)`. Confirmed present at HEAD by reading the file. The commit the ledger credits (`85b8735f`, "foot-band four-site patch") is **not reachable** from this 73-commit clone, so I confirm by code, not by history.
4. **The architecture is documented and was measured.** `ReadingOrder.java:16-32`: the reading-order pass was moved out of `DocxWriter.write` precisely so that *"the same PDF gave two different `.txt` files depending on call order"* would stop happening — *"Both writers are then functions of the document"*. The measurement behind keeping it: with the pass, *"the `.txt` is byte-identical to what the shipped pipeline produced (docx first) on all 211 documents"* (`ReadingOrder.java:36-40`, citing `tools/p2w-bench/SECTOR19.md`). **A change in `DocxWriter` cannot change a byte of the `.txt`** — measured on the corpus, not asserted.
5. **The two checks read disjoint inputs.** `t09` is computed by `compare(src_pdf, txt_path)` (`verify_txt.py:1036`) from the PDF and the `.txt`; it never opens a `.docx`. `44_header_footer` compares the PDF to Google's exported render. Neither can observe the other's patch.

**Consequence for the question as asked:** the `.docx` half is *not blocked* by the `.txt` half. It is also
*not pending* — it is already landed and already measured. See (c-i).

---

## (c) The exact patch — and, for the `.docx` half, a refutation

### (c-i) The `.docx` half: **refuted as a patch site. I would not apply a patch here.**

What the ledger claims is left, and what is true of it:

| ledger claim | source | status at HEAD |
|:--|:--|:--|
| "the same defect has a second site — `flowFromBox` — which this change does not touch" | `FINDINGS/RUNNING-FOOT-IS-A-ROW-GOOGLE-DROPS-THE-BOX-1855-fixer.md` (23 Nov, engine `b7699196`) | **Refuted.** `flowFromBox` has carried `!inFootBand(ctx, b.y)` at both its oversized-gap sites since the four-site patch; removing both guards changes **no byte of `document.xml`** on 17 documents (`FINDINGS/44_header_footer-FLOWFROMBOX-ALREADY-GUARDED-AND-INERT-1815-relay.md`). |
| "`61_two_col_abstract_spanning` … still carry 4 text boxes" | same file | **Stale.** 27/46/55/61/67 all read `w:txbxContent` = 0 at HEAD (`FOOTBAND-FOUR-SITES-61-IS-CLEAN-24NOV.md`, ablation row 1). |
| the four-site patch "not landed" | `FOOTBAND-FOUR-SITES-61-IS-CLEAN-24NOV.md` | **Stale.** It is in the tree (fact 3 above). |
| `44_header_footer` still open | `ATTEMPTS.json:989+`, attempt 3 at 2026-11-26 17:39: *"the 44_header_footer lead is closed on both halves"* | **Closed on the `.docx` half.** Its remaining text is entirely about `t09`. |

So the `.docx` half's construct is done: the anchor rule that made Google drop page furniture is guarded at
all four sites, five documents lost their text boxes, and two of them (`27_two_column_left_short_txtpos`,
`61_two_col_abstract_spanning`) went to 42/42 in Google through the real Drive path.

**The one candidate that survives, and why I still would not apply it.** The same finding argues the guard
would be wrong even where it fires, because *"the predicate is positional, not semantic — 'bottom tenth of
the paper', not 'page furniture' … A correct guard there needs a 'no baseline below this one on the sheet'
flag or the page's declared bottom margin; `Ctx` has neither."*

**That last clause is factually wrong at HEAD, and this is the one new code fact in this report.** `Ctx`
carries exactly that flag:

```java
// DocxWriter.java:830
/** The lowest ink on this page, in PDF points from the page top, taken from the page's own
 *  blocks before a single byte is written. This is the SOURCE's extent, not the writer's
 *  model of the page, and it is what the table-gap guard reads… */
float pageInkBottomPt;
```

set at `DocxWriter.java:1395` (`ctx.pageInkBottomPt = pageInkBottom(page);`), defined at
`DocxWriter.java:2488-2502`, and already used as a page-slack budget at `DocxWriter.java:6152`. A semantic
predicate is therefore expressible:

```java
// DocxWriter.java:420  BEFORE
private static boolean inFootBand(Ctx ctx, float y) {
    return y > FOOT_BAND_FRACTION * ctx.pageHeightPt;
}

// AFTER (candidate, NOT applied)
private static boolean inFootBand(Ctx ctx, float y) {
    // Furniture is the LAST mark on the sheet, not merely a low one: a packed last body line
    // sits inside the bottom tenth and is not furniture (44_header_footer-FLOWFROMBOX…).
    if (y <= FOOT_BAND_FRACTION * ctx.pageHeightPt) return false;
    return y + LAST_LINE_SLACK_PT >= ctx.pageInkBottomPt - INK_EPS_PT;
}
```

I would **not** apply it, for four reasons, in order of weight:

1. **It can only shrink the firing set, and every document in that set is already clean.** The measured
   firing set is 2 of 12 (`foot-band-spend-ab-01-MEASURED-NEUTRAL-25NOV.md`), and both of those documents
   (`27`, `46`) are the two measured wins. Narrowing the predicate risks the wins and cannot produce a new
   one: the ablation already showed that *widening* the guard's reach to `flowFromBox` changes nothing.
2. **The new predicate can misfire in the direction that costs text.** A page whose footer row is not the
   lowest ink (a page number drawn below it, a stamp, a footnote) would fail `isLastOnSheet`, lose the
   guard, and be anchored — which is precisely how Google comes to drop the text. `pageInkBottom` takes a
   `max` over `Table.bottom`, `Box.bottom` and `lineY + size`; a stamp or a rule below the footer wins that
   `max`. Nothing in the tree measures how many of the corpus's footers are not the lowest ink.
3. **It is an unmeasured engine change on a construct whose current form has two Google renders behind it.**
   The charter (`FIXER-BRIEF.md:21`) is explicit: *"an unmeasured change is not a pass"*. The commit gate
   also refuses it — `regress.py --check` demands a full-corpus `RANKING.csv` stamped on the new engine,
   ≈54 min by the repo's own arithmetic.
4. **There is nothing to gain.** `44_header_footer` has no open document on the `.docx` side; the documents
   that still fail near it (`46`, `55`, `67`) fail other checks (`45_char_accuracy`), so the box work does
   not make them clean.

**Verdict on (c) for the `.docx` half: no defensible patch. The construct is implemented, guarded at all
four sites, measured on five documents and two Google renders. What the ledger records as remaining is a
refuted second site plus one stale "not landed" note.**

### (c-ii) The `.txt` half: the lead's own premise is broken by the reader, and here is the exact patch

This is where the real remaining work is, and the ledger's stated blocker is partly wrong in a way that is
worth one line of code.

**The `.txt` does carry page separators, and the instrument throws them away.** `TxtWriter.write` emits one
at every page boundary (`TxtWriter.java:86-88`):

```java
// The separator owns its own line: "\f\n", never "\f" glued to the next page's first line.
sb.append("\f\n");
```

and the output sanitizer explicitly exempts it (`TxtWriter.java:114-119`):

```java
// U+000C is deliberately NOT in the ranges below. It used to be, which is why the page
// separators written above survived for exactly zero lines …
.replaceAll("[\\u0000-\\u0008\\u000B\\u000E-\\u001F]", " ")
```

The reader that every check uses, `verify_txt.py:937-939`, drops them on the floor:

```python
def _txt_lines(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return [l.rstrip("\n") for l in f if l.strip()]
```

`"\f".strip() == ""` in Python — **U+000C is whitespace** — so a line holding only a form feed is filtered
out before any check sees it. `compare()` binds `lines = _txt_lines(txt_path)` at `verify_txt.py:1043`, so
the `\f` the patch's band arm splits on is never in `lines`.

**Verified in this sandbox, on a synthetic three-page file in exactly the shape the writer emits:**

```
raw file            : "PAGE ONE HEAD\nbody one\n\f\nPAGE TWO HEAD\nbody two\n\f\nPAGE THREE HEAD\nbody three\n"
raw U+000C count    : 2
_txt_lines() ->       ['PAGE ONE HEAD', 'body one', 'PAGE TWO HEAD', 'body two', 'PAGE THREE HEAD', 'body three']
any line holding \f : False
segments after _txt_lines : 1          <- reproduces the lead's "segs=1"
patch's own splitter      : 1
```

**`segs=1` is reproducible on a file that carries every separator.** The last lead's inference — *"the .txt
has no form feeds"* — does not follow from its measurement, and the measurement is the only thing it
records.

Two further pieces of evidence say the separators really are in the corpus files at HEAD:

- **`t11_page_breaks` passes on the corpus.** `verify_txt.py:1414-1439` requires N−1 U+000C marks and counts
  them *"in the RAW file, not in `_txt_lines`: a separator that sits on a line of its own strips to nothing
  and the reader above drops it"* (`:1426`). `tools/p2w-bench/txt/RANKING-TXT.csv` (213 rows, the 27 Nov
  01:44 re-score — `RUN-LOG.md`: *"213 re-scored, 0 moved (205 clean, 8 failing)"*) contains **not one
  document failing `t11`**, including the two 9-page Account forms, which owe 8 marks each. Its own
  in-code comment (`verify_txt.py:1418`) still says *"MEASURED TODAY: 0 of the 211 documents carry a
  separator"* — that comment is stale.
- The surrounding prose is stale in the same direction, which dates the separator's arrival: `PdfToWord.java:10010` still describes `writeTxt` as *"…no page separators - text is a flow, and a page break in the middle of a sentence would be a lie."*

*Caveat, stated because it matters:* the `t11` inference assumes the instrument that stamped
`RANKING-TXT.csv` included `t11`. The store shows `applicable = 12` on three documents and only current
check ids in `failed_ids`, and `RATCHET-TXT.json` reports `checks: 12` — but that file's `sha`
(`9f988a43056f`) does **not** match the live `CHECKS` list (`ddb64cc6f116`, computed here), so the ratchet
was stamped by a different instrument generation. The decisive test is one command, in (d).

**The patch I would apply — Patch A, the reader. Defensible on its own, changes no score:**

```diff
--- a/tools/p2w-bench/verify_txt.py
+++ b/tools/p2w-bench/verify_txt.py
@@ -937,6 +937,26 @@ def _txt_lines(path):
     with open(path, encoding="utf-8", errors="replace") as f:
         return [l.rstrip("\n") for l in f if l.strip()]
 
+def _txt_page_segments(path):
+    """The .txt's lines, with the U+000C page separators KEPT as segment boundaries.
+
+    _txt_lines() cannot see them: U+000C is whitespace in Python, so `if l.strip()` is false
+    for a line that holds only a form feed and the separator is dropped before any check runs.
+    The writer emits one per boundary (TxtWriter.write: "\f\n") and the output sanitizer
+    exempts it (TxtWriter.java:114-119), so the bytes are in the file and the reader is what
+    loses them - reproduced here on a three-page synthetic file in the writer's own shape:
+    raw marks 2, marks surviving _txt_lines 0, segments after _txt_lines 1.
+
+    Read again rather than changed, for the reason _txt_bytes() gives above: every number
+    t01-t05 has ever reported came through _txt_lines, and changing that reader would move
+    them without the engine changing.
+    """
+    with open(path, encoding="utf-8", errors="replace") as f:
+        raw = f.read()
+    return [[l.rstrip("\n") for l in seg.split("\n") if l.strip()]
+            for seg in raw.split(PAGE_BREAK)]
```

**Patch B — the counting side. This one is *not* landable without measurement, and I will not pretend
otherwise.** Two candidate formulations, both needing the segmentation from Patch A:

- **B1 (preferred, no positional proxy):** compare per page instead of per file. For each source page *p*
  and band key *k*, owed = drawn occurrences on *p*; present = occurrences of *k* in segment *p*. This is
  the check's own stated meaning (*"one copy of each running head per page it belongs to"*,
  `verify_txt.py:232`) and needs no *y* on the `.txt` side at all. Combined with the one-char-key drop the
  ledger already measured (`elements` keeps only keys with ≥2 non-`#` characters), it should take `Date`
  from 6-vs-3 to 3-vs-3 if the body `Date` header is not on the same three pages as the date boxes —
  **which is exactly the fact nobody has measured.**
- **B2 (the FINDINGS patch, `FINDINGS/t09-FIX-band-scoped-present-and-no-one-char-keys.patch`):** a fixed
  `FURNITURE_TXT_EDGE_LINES = 3` window at each segment edge. Its refutation in the ledger is invalid (it
  was never exercised — `segs=1`), but the census's own ordinal-window experiment is direct evidence that
  this family of proxies is document-sensitive: 29 (PASS) on `041122` and **22 (FAIL)** on
  `Account_Opening_Form_Fillable_filled` when the window is sized from the source band
  (`t09_page_furniture-SINGLE-CHAR-CENSUS-agent-26NOV.md` §4). The constant 3 is load-bearing and unmeasured.

Both B1 and B2 must be preceded by the full 213-document `restamp_txt.py --force` the lead correctly
demands — a furniture-check change moves any document that draws a single letter anywhere.

**So the remaining work on `t09_page_furniture`, stated as work, in order:**
1. Patch A (reader keeps the separators). No score can move; it only makes the measurement possible.
2. Measure B1 and B2 on the two documents. Pick the one that reads 29/29 on **both**.
3. Re-stamp all 213 (`restamp_txt.py --force`) and diff against `RANKING-TXT-BASELINE.csv`. Accept only
   0 regressions.
4. Do not touch `TxtWriter`'s line assembly. The census settled that: the writer is faithful, and *merging*
   the letter-spaced runs would take `present` from 29 to 3 against an unchanged `owed` of 29 — it makes
   `t09` worse, not better (§5 of the census).

---

## (d) The single cheapest measurement, on ONE document

**Document:** `041122-Account_Opening_Form` (9 pages, the construct's canonical case, and the one whose
`.txt` the lead's `segs=1` was taken from).

**Question it decides:** does the writer put U+000C in the file? Yes → the last lead's premise is a reader
fact and Patch A is the whole first step. No → `t11_page_breaks` must be failing on a 9-page document,
which the store says it is not, and the writer is the defect instead.

```bash
cd /scratch/work/CS/tools/engine-verify
CP="out:libs/aar/classes.jar:libs/aar/assets:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar"
java -cp "$CP" ConvertOne /scratch/work/p2w/corpus/041122-Account_Opening_Form.pdf /scratch/work/t09
python3 -c "d=open('/scratch/work/t09/041122-Account_Opening_Form.txt','rb').read(); \
print('U+000C =', d.count(b'\x0c'), ' expected 8')"
```

One conversion, one byte count, one expected value: **8**. Eight refutes the lead's premise and makes
Patch A the first line of the fix. Zero confirms a writer defect and sends the run to `TxtWriter` instead.

*If the count is 8 and you want the second number in the same slot* — whether B1 or B2 reaches 29/29 — it is
`python3 ../p2w-bench/verify_txt.py <the.pdf> <the.txt>` after Patch A, reading the
`t09_page_furniture source=29 txt=?` pair. Same one document, one command, no corpus pass.

*For the `.docx` half, the cheapest confirmation that it is already done* (one conversion, one grep, no
Drive — this is the ablation, not a Google render):

```bash
java -cp "$CP" ConvertOne /scratch/work/p2w/corpus/27_two_column_left_short_txtpos.pdf /scratch/work/t09
unzip -p /scratch/work/t09/27_two_column_left_short_txtpos.docx word/document.xml \
  | grep -o "<w:txbxContent>" | wc -l      # expected 0 at HEAD
```

---

## What I verified, what I inferred, and what I could not check

**Verified here (code reading or computation in this sandbox):**
- `t09` is absent from `verify_google.py`; `44_header_footer` is its `.docx`-side counterpart and its band
  test is symmetric on both sides (`verify_google.py:3886-3887, 3931`) where `t09`'s is not.
- `_txt_lines` drops U+000C lines; reproduced on a synthetic three-page file (raw 2 → surviving 0 →
  segments 1).
- `TxtWriter` emits `\f\n` per boundary and exempts U+000C from its sanitizer; `PdfToWord.writeTxt`'s
  docstring still claims the opposite.
- `TxtWriter.java` contains no reference to `inFootBand`, `FOOT_BAND`, `gapCapTw` or `pageHeightPt`.
- The four `!inFootBand(...)` guards exist at `DocxWriter.java:3623, 3649, 4506, 4543` at HEAD.
- `Ctx.pageInkBottomPt` exists (`DocxWriter.java:830`), is set at `:1395`, defined at `:2488-2502`, used at
  `:6152` — so the flowFromBox finding's *"`Ctx` has neither"* is wrong at HEAD.
- The live `CHECKS` hash is `ddb64cc6f116`, not the ratchet's `9f988a43056f`.
- `RANKING-TXT.csv`: 213 rows, 205 clean, 8 failing, `t09` on exactly 2 documents, `t11` on **zero**.

**Inferred, flagged:**
- That `t11`'s passing on the 9-page forms means the `.txt` carries 8 separators. It follows only if the
  stamping instrument included `t11`; the store's `applicable = 12` and current-name `failed_ids` support
  it, the mismatched ratchet hash weakens it. The (d) command settles it.
- That B1 reaches 29/29. Nothing in the tree measures whether the body `Date` header shares pages with the
  date boxes.

**Not checkable here:** the corpus, a JVM build, any Google render, and the commit `85b8735f` (unreachable
in a 73-commit clone) — so the foot-band patch's landing is confirmed by the code's presence, not by history.

**Ledger defects this analysis turned up, worth fixing independently of the fix:**
1. `ATTEMPTS.json:2166` truncates its own `reason` at 200 characters, mid-word, while `:2176` holds the full
   sentence. A reader who trusts the history entry loses "re-measure, which did not fit".
2. `HANDOFF.json:74` records agent `t09_A-01` as `running` with `finding: null` although its finding
   (`FINDINGS/t09_page_furniture-SINGLE-CHAR-CENSUS-agent-26NOV.md`) is in the tree.
3. Three in-code comments describe a world that no longer exists: `verify_txt.py:1418` ("0 of the 211
   documents carry a separator"), `PdfToWord.java:10010` ("no page separators"), and the whole of
   `FOOTBAND-FOUR-SITES-61-IS-CLEAN-24NOV.md`'s "not landed". Two of the three are the *reason* the last
   lead concluded what it did.
4. `44_header_footer`'s attempt 3 (`ATTEMPTS.json:989+`) says *"whether that is a TxtWriter split or a t09
   asymmetry is not yet decided"* — the census decided it 30 minutes later and no ledger entry closed it.
