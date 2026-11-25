# The spendWideGap look-ahead is sound, and it cancels the fix it was meant to protect

**Agent B, fixer slot 25 Nov 06:07. Measured, not argued.**

## The handover said

"Implement the look-ahead in spendWideGap: spend the gap only when no line remaining on this page targets a
baseline below this one. Keep `-Dp2w.footband=0.80`. Target: 39/42 on 69 with `26_text_overlap` back to 0,
`330_cad` unchanged."

## Two facts that change the task

1. **`spendWideGap` does not exist at HEAD.** The engine was reverted after the 03:15 run; the function lives
   only in `FINDINGS/04_chars_missing-GAPCAP-PATCH-0225-agent.patch` (+102 lines), which applied cleanly.
2. **The look-ahead refuses the one spend that produced the result.** Doc 69
   (`69_two_col_legal_numbered_clauses`) makes exactly one wide-gap decision on the whole page:

   ```
   LA-REFUSE y=716.0 lowestBelow=805.89 gap=380.61874
       text=IN WITNESS WHEREOF the parties have set their hands on the date first above written.
   ```

   The signature block's gap is refused because the **running footer at 805.89 pt** is below it. The
   handover's premise — "on the last block of a two-column page that is true" — is **false for 69**: a
   footer line does remain below.

## Before / after

Doc 69 at `-Dp2w.pagepos=0 -Dp2w.anchorkeep=0 -Dp2w.zganchor=false -Dp2w.footband=0.80`:

| build | `wps:txbx` boxes / chars |
|---|---|
| BEFORE (`-Dp2w.lookahead=0`) | **0 / 0** — reproduces the 03:15 finding |
| AFTER (`-Dp2w.lookahead=1`) | **7 / 242** — back to the `footband=0.85` state |

Witness `330_cad_drawing_sheet`: 2 boxes / 75 chars before and after, `word/document.xml`
**byte-identical** (154,571 bytes). Witness held.

Full corpus A/B, 213 documents, own conversion: **209/213 byte-identical**; 4 changed —
`322_mutual_fund_factsheet` 2->4, `66_two_col_footnotes_bottom` 0->8, `69` 0->7,
`70_magazine_drop_cap_photo_caption` 0->2. Every change is a **refusal**: the guard only ever moves in the
conservative direction.

Doc 69 under LibreOffice: 40/42 both builds, identical failures (`18_displacement` source=0 render=1;
`60_text_column_right_edge` source=1 render=0). `26_text_overlap` fired for neither build — it is a
Google-specific effect and LibreOffice cannot discriminate it.

## Verdict: REJECT as a fix, LEAD on the mechanism

4 corpus documents altered, **zero improved**. The target (39/42 *with* overlap at 0) is not reachable by
this rule as specified.

**Lead, unmeasured:** the condition that matters on 69 is not "no line below" but **"no *flow* line below"**.
A guard that ignores a running foot — a line sitting in the foot band that is the page's last — would still
spend 69's signature gap while keeping `330_cad` intact. That is a new hypothesis, and it is the next thing
to try.

**Still unresolved from 03:15:** whether `18_displacement` and `60_text_column_right_edge` on 69 are caused
by this line of work at all.

## Not measured

Google render. `GOOGLEDRIVE_CREATE_FILE` rejects a sandbox path —
`s3key '/scratch/work/out-before69/...docx' belongs to another project or session` (HTTP 403) — so the
decisive check (`26_text_overlap`) has no Google value in either direction from this pod.
