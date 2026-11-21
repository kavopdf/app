# The 127 U+FFFD sites on 041122-Account_Opening_Form are LIGATURES - and the destination patch would write the wrong letters

**21 Nov, fixer run 07:58, subagent `5WFHH5ZB8F8TXRDE8AMQ64RA8R`, completed. Answered by looking at the page.**

The handoff's first action was: "render page 1 of 041122-Account_Opening_Form at 150 DPI and look at
the 127 glyph sites - ligature or not. If ligature, the fix is CIDToGIDMap plus the descendant cmap;
if not, apply `FINDINGS/fffd-cmap-destination-2300-fixer.patch`." It is done, on 8 sites, at 600 DPI,
all four CIDs and all three faces.

**VERDICT: LIGATURE. 8 of 8 inspected sites are ligatures; 0 are single letters or symbols.**

| CID | width (/W, 1000 em) | crop shows | ligature |
|:--|--:|:--|:--|
| 291 (0x123) | 637 | "services o**ff**ered" - the two f's share one crossbar | ff |
| 292 (0x124) | 539 | "identi**fi**cation", "be **fi**led", "**fi**rm" | fi |
| 294 (0x126) | 847 | "Post o**ffi**ce", "(O**ffi**cially" | ffi |
| 295 (0x127) | 858 | "O**ffl**ine" | ffl |

127 sites in total: 291 x13, 292 x84, 294 x25, 295 x2, pages 1-9.

**So `fffd-cmap-destination-2300-fixer.patch` must NOT be applied.** It appends one character per CID,
which would write `O<wrong>ce` and `Sta<wrong>` at 127 places in a document that is visibly correct
today. That patch is refuted by the widths alone: each CID is one glyph cell 637-858 em wide against
components f=330, i=222, l=212, i.e. two or three letters wide, not one.

**And the identity is still not recoverable from the file**, which the earlier finding had right: all
three faces are `/Type0 /Identity-H /CIDFontType2` with `/CIDToGIDMap /Identity`, every one of these
CIDs carries a `/ToUnicode` entry that answers U+FFFD, the embedded TrueType programs contain **no
`cmap` table at all** (tables: OS/2, cvt, fpgm, glyf, head, hhea, hmtx, loca, maxp, name, prep), and
the glyph names are stripped to `glyph00291`/`00292`/`00294`/`00295`. So "CIDToGIDMap plus the
descendant cmap" as literally worded resolves to a lookup that does not exist here.

What this settles and what it does not: it settles that the sites are ligatures and that the
destination patch is wrong. It does not by itself licence a CID->letters table built from 8 inspected
sites; that is a per-face guess applied to 127 places, and the honest way to make it is with the Effra
reference outlines or a word list, neither of which is in the repository. A person should choose
between those two.
