# The refused-spacer lead is already committed - and the hunk it asks for is a LibreOffice regression

**Class:** `18_displacement` · **Outcome:** lead closed, do not apply · **26 Nov 2026, slot 08:35**

## What the previous run asked for

`FINDINGS/18_displacement-REFUSED-SPACER-PARTIAL-SPEND-083900-a7c2.md` (written 03:09 UTC) closed with
a four-step resume, step 1 of which is: *apply the two hunks in `DocxWriter.java` around line 6121
(refused branch only)*. It measured the change as 62 documents / 141 instances, 37 documents gaining
gap, largest gain +51.04 pt on `374_org_chart`, and reported it as a lead because the slot ran out
before a full Google re-measure.

## What I measured

### 1. The 37-document gain is already in HEAD, and it is commit `9f0a8207`

`git show 9f0a8207` (committed **02:54:47 UTC**, fifteen minutes *before* the finding was written)
contains exactly the spendable-branch change:

    -            int roomWantTw = Math.max(0, spacerTw - 20);
    +            int roomTw = Math.max(0, slackTw - ctx.spacerSplitTw - rowExcessTw);
    +            int spendTw = Math.min(wantTw, roomTw);
    +            if (spendTw > 0) { ... w:before="spendTw" ... w:line="spacerTw - spendTw" ... }

So the finding's `before` engine `981ff1fa35e2cf67` is the tree *before* `9f0a8207` and its `after`
engine `2c7141b7eeb9a0fe` is the tree *after* it. The 62 documents / 141 instances / 37 gaining
documents it reports are that commit's effect. It was measured correctly and attributed to the wrong
change: the gain is the **spendable** branch, and that branch is committed.

### 2. The refused branch it asks you to patch is now a 19-document population, not 62

Census on the corpus as converted at HEAD (engine `a4d8fca469bba636`, 213 documents), reading the
spacer emitter's own shape from `word/document.xml`:

    spendable  <w:before="spendTw" w:line="1"      w:lineRule="exact"/>   117 instances / 85 documents
    refused    <w:before="0"       w:line="spacerTw" w:lineRule="exact"/>    64 instances / 19 documents

`9f0a8207` moved 43 of the 62 documents out of the refused branch. What is left is 19 documents and
64 instances.

### 3. On those 19, the hunk gains Google nothing and costs LibreOffice 77% of the gap

The hunk is self-cancelling by construction. It sets

    floorTw = round(20 * 2.74663 * max(spacerTw/240, 0.06))

which is the old construct's Google charge converted back to twips, then emits `before = floorTw - 3,
line = 1`. Google draws `w:before` 1:1 and an exact line box at `2.74663 * max(L/240, 0.06)` pt, so the
patch's Google charge is `floorTw/20 - 0.15 + 0.1648`, which is `floorTw/20` to four decimals - and
`floorTw/20` **is** what Google already draws. The patch relocates the gap between two properties; it
cannot add to it.

Computed over all 64 remaining instances, from the declarations in the corpus at `a4d8fca469bba636`:

| | now | with the hunk | delta |
|:--|--:|--:|--:|
| **Google** draws | 402.3 pt | 402.8 pt | **+0.592 pt, over 19 documents** |
| **LibreOffice / Word** draws | 1757.5 pt | 401.9 pt | **−1355.5 pt** |

- Largest single-instance Google change: **0.0392 pt** - 38× below `18_displacement`'s own 1.5 pt
  tolerance, so it cannot turn a failing document into a passing one.
- Largest single-instance LibreOffice loss: **111.0 pt**.
- Worst documents: `041122-Account_Opening_Form` and `Account_Opening_Form_Fillable_filled`, 17
  spacers each, **−511.0 pt** each; `330_cad_drawing_sheet` −111.0; `80_gstin_pan_cin_ifsc_table` −52.5.

Word and LibreOffice honour `w:lineRule="exact"` at the full `L/20` pt. The old refused declaration
`line=spacerTw` therefore draws the whole gap in the renderers the user's own editor uses, and the
patch replaces it with a declaration of 22.9% of that gap. That is non-negotiable 3 (no document may
get worse) broken on 19 documents, in exchange for a Google change 38× below the check's floor.

## What is now true

- The refused-spacer work is **done and committed** (`9f0a8207`). Do not re-open it.
- The remaining refused branch is 19 documents and 64 instances, and the hunk in the 083900 file is
  **not** the fix for them. It is a LibreOffice regression with no Google effect.
- `18_displacement`'s 25 solo documents do not carry this construct at all. They are
  `w:trHeight w:hRule="atLeast"` re-laid on a 0.75 pt ladder - see
  `18-displacement-SOLO-TAIL-26NOV-onyx-node.md`, committed this run.

## What would prove this wrong

- A refused-spacer document where the patch changes Google's rendered `med_dy` by more than 1.5 pt.
  The arithmetic says the maximum possible is 0.0392 pt on the corpus as it stands, so this would
  mean the Google charge law is wrong, not that the hunk is right.
- A measurement showing Google draws `w:lineRule="exact"` at more than 22.9% when the paragraph
  carries other content. All 64 instances here are faceless `<w:sz w:val="2"/>` marks, the case the
  law was fitted on.
- Evidence that `2c7141b7eeb9a0fe` is not `9f0a8207`'s tree. `9f0a8207` is the only commit in the
  history that touches this emitter between the two fingerprints, and its diff is the spendable
  branch line for line.
