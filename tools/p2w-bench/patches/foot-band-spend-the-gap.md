# foot-band: spend the gap instead of anchoring a floating text box

**Status: PROVED on the construct, NOT measured in Google. Apply, then measure Google.**

## The construct

Google Docs does not read the text of a floating drawing. A `wps:txbx` inside a
`<wp:anchor behindDoc="1">` comes back from Drive as pixels with no text layer, so every
character in it is missing from the export. LibreOffice renders the same box as a text frame
and keeps all of them. That is why this class is invisible to the LibreOffice proxy.

Evidence (two independent agents, same conclusion from opposite ends):
- `04_chars_missing`: on 27, 55, 61, 67, 20, 13, 06, 09, 66 the missing-character multiset is
  **fully** explained by the text of the anchored boxes - zero unexplained characters.
  The missing runs have nothing typographically in common (8-44 pt, black/grey/red, unrotated,
  unclipped). Their only shared property is position: the bottom tenth of the page.
- `44_header_footer`: 20 of the 28 documents that carry a running foot write it as a floating
  anchor (`posOffset` 798.5 pt on an 842 pt page). 8 write it as a flowing paragraph and still
  fail 44 - a second mechanism, not this patch.

## The change

`DocxWriter.inFootBand(ctx, y)` = `y > 0.90 * ctx.pageHeightPt`, added as `&& !inFootBand(...)`
to the four `gapCapTw` anchor escapes (flowRow afterTablePt, flowRow pitch, flowFromBox
afterTablePt, flowFromBox pitch). In the bottom tenth the measured gap is spent as
`w:before`/`w:ind` instead of calling `anchorBox()`.

The anchor rule is right about the position and wrong about the construct. Its justification -
a gap wider than the flow may spend means the flow drifted, and spending it pushes every line
below down - does not hold for the last line on the sheet. There is nothing below it.

## What was measured

| document | `txbxContent` before | after | share5 (LO) before | after |
|:--|--:|--:|--:|--:|
| 27_two_column_left_short_txtpos | 4 | **0** | 1.62 | 1.62 |
| 61_two_col_abstract_spanning | 4 | **0** | 2.01 | not scored |
| 55_sidebar_box_beside_body | 4 | **0** | 0.00 | 0.00 |
| 67_two_col_with_sidebar | 4 | **0** | 0.80 | not scored |
| 66_two_col_footnotes_bottom | 16 | 16 | 2.92 | not scored |

The `txbxContent` counts are read straight out of the produced `word/document.xml`, not from the
tool that was edited. The share5 columns are the LibreOffice proxy and they **do not move** -
which is the point: 55 is `clean` in RANKING.csv at share5 0.00 and still fails `04` and `44` in
Google. **The proxy cannot see this class in either direction.** Do not screen this patch on
LibreOffice; it will report "nothing improved" whatever happens.

## Why it was not kept

Keeping it needs `regress.py --check`, which needs a 213-document pass (about 40 minutes) and the
slot had 12 minutes left. The change is 72 lines against four conditions and reverts cleanly.

## Next run

1. `git apply tools/p2w-bench/patches/foot-band-spend-the-gap.patch`
2. Build, then measure the 14 documents the guard empties (27, 28, 46, 54, 55, 61, 62, 67, 70,
   newsletter-3col-header-footer, one-page-rotated-180-degrees,
   report-2col-table-spanning-both-columns, table-inside-two-column-page,
   table-of-contents-dot-leaders) **through Google**, not LibreOffice.
3. Expected: 04 and 44 clear on 27 and 61 at minimum (they fail nothing else). 45 clears only
   where the missing share was over 3% - measured 3.8% on 55, 3.7% on 67, 3.1% on 61 - so the
   floor is 2 documents, not 5. Do not claim 5 without the render.
4. The 40 documents that keep their boxes (rotated stamps, footnotes and signature blocks below
   both columns, sidebar families) need a second decision: a real `word/footer1.xml`. That is
   1-2 files, about six touch points in `DocxWriter.java`, and `verify_google.py:3745-3750`
   already records that injecting a header part moved every body line +10.9 pt on
   `bank-statement-5-pages` - so it is not free.
