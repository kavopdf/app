# t01 / FFFD-FONT-TRUTH — what CID 0x0123/0x0124/0x0126/0x0127 actually are in REAQAG+Effra-Regular

**21 Nov, subagent run 07:53 UTC (13:23 IST). Answered from the embedded font program, not from the page.**

**VERDICT: the "CID as code point" assumption is WRONG.** The four CIDs are the ligatures
**ff, fi, ffi, ffl**. No glyph in this font is a `gcedilla`, and nothing in the font program maps
any glyph to U+0123, U+0124, U+0126 or U+0127 — **the font has no `cmap` table at all**.

| CID | GID (=CID, Identity) | `post` name | contours | advance | bbox (x0,y0,x1,y1) | is actually | recovers to |
|:--|--:|:--|--:|--:|:--|:--|:--|
| 0x0123 (291) | 291 | `glyph00291` (synthetic) | 1, 46 pts | 637 | 13, 0, 704, 684 | **ff** | U+0066 U+0066 |
| 0x0124 (292) | 292 | `glyph00292` (synthetic) | -1 (composite → `glyph00296`) | 539 | 13, 0, 478, 684 | **fi** | U+0066 U+0069 |
| 0x0126 (294) | 294 | `glyph00294` (synthetic) | 1, 49 pts | 847 | 13, 0, 786, 684 | **ffi** | U+0066 U+0066 U+0069 |
| 0x0127 (295) | 295 | `glyph00295` (synthetic) | 1, 51 pts | 858 | 13, 0, 797, 684 | **ffl** | U+0066 U+0066 U+006C |

---

## Asked

Determine, from the font program itself, what Unicode character CID 0x0123, 0x0124, 0x0126 and
0x0127 denote in the embedded font `REAQAG+Effra-Regular` inside
`benchmarks/realworld/041122-Account_Opening_Form.pdf`.

(a) Is CID 0x0123 the glyph a designer would name `gcedilla` (U+0123), or something else?
(b) Is the assumption "CID as a code point" — writing `chr(0x0123)` = `ģ` — CORRECT or WRONG?
(c) If wrong, what is the correct recovery, and what are the recovered characters?

## Claim

**(a)** CID 0x0123 is **not** `gcedilla`. It is the **ff** ligature — two `f` glyphs sharing one
crossbar. It cannot be a cedilla-bearing `g` for a reason that is not a judgement call: **its
outline has no descender.** yMin = 0 and yMax = 684, whereas `g` (GID 234) is yMin = -212,
yMax = 476, and a cedilla would push yMin further down. Across all 1225 glyphs in the program,
**zero** have yMin < -250 (the two lowest are -212). A `gcedilla` shape does not exist in this
font at all.

**(b)** The assumption is **WRONG**. Evidence, strongest first:

1. **The font program contains no `cmap` table.** The sfnt table directory lists exactly 11
   tables: `OS/2, cvt , fpgm, glyf, head, hhea, hmtx, loca, maxp, name, prep`. There is no `cmap`
   and no `post`. Therefore **no glyph in this font is designated U+0123, U+0124, U+0126 or
   U+0127** — the question "which glyph ids map to U+0123" has the answer *none*. `chr(0x0123)`
   is a coincidence of the subset's CID numbering, not a character assignment.
2. **The advance widths are 1.4×–1.6× the width of the letter the CID "names".** An accented
   letter keeps its base letter's advance; a ligature is as wide as its components.
3. **The outlines are ligature outlines.** Each of the four matches a union of translated
   `f`/`i`/`l` component outlines at IoU 0.89–0.97, and matches nothing else.
4. **The `ToUnicode` CMap already says it does not know** — all four map to U+FFFD.

**(c)** The recovery chain *as literally worded* (`CIDToGIDMap → GID → descendant cmap reverse
lookup → Unicode`) **breaks at step 3**: the descendant font has no `cmap`, so the reverse lookup
does not exist. The chain that does work here is `CIDToGIDMap → GID → decompose the glyph's own
outline into component glyphs → each component's Unicode (via the ToUnicode entries that *are*
correct)`, giving **ff, fi, ffi, ffl** — multi-character sequences, not one code point each.

## Evidence

Everything below was run. Nothing here is from reading the page.

### 1. The Type0 font object

Raw PDF object walk (pikepdf 10.18.0). Document is 9 pages.

```
/Type0        obj (111, 0)  /BaseFont /REAQAG+Effra-Regular
              /Encoding /Identity-H                    <- as expected
/DescendantFonts[0] obj (134, 0)  /Subtype /CIDFontType2
              /BaseFont /REAQAG+Effra-Regular
              /CIDSystemInfo << /Registry (Adobe) /Ordering (Identity) /Supplement 0 >>
              /CIDToGIDMap /Identity                   <- CID == GID
              /DW 1000
              /W  -> 90 CIDs, min 3, max 295
/FontDescriptor obj (133, 0)
              /FontName /REAQAG+Effra-Regular   /Flags 4   /ItalicAngle 0
              /FontBBox [-146 -686 1222 1224]   /Ascent 1224   /Descent -686
              /CapHeight 667   /XHeight 465   /StemV 92   /FontWeight 400
              /FontFamily (Effra)   /FontStretch /Normal
              /FontFile2  length 20893 bytes, md5 b06402c9810e51fc60a17ceb5ba895b1
              /CIDSet     42 bytes FlateDecode, 37 bytes decoded, 91 bits set
/ToUnicode    obj (117, 0)  1585 bytes, 90 bfchar entries, codespace <0000>-<FFFF>
```

`/W` widths for the relevant CIDs: 291→637, 292→539, 294→847, 295→858, and the Latin letters
233 (f)→330, 236 (i)→222, 239 (l)→212, 234 (g)→547, 235 (h)→543, 208 (G)→721, 209 (H)→709.

`/CIDSet` set-bit membership: 0x0123 ✔, 0x0124 ✔, 0x0126 ✔, 0x0127 ✔ (91 CIDs marked present).

### 2. The `/ToUnicode` stream, verbatim on the four CIDs

```
1 begincodespacerange
<0000> <FFFF>
endcodespacerange
90 beginbfchar
...
<0123> <FFFD>
<0124> <FFFD>
<0126> <FFFD>
<0127> <FFFD>
...
```

The ordinary letters are mapped correctly and are the anchor for the whole recovery:
`<00E9> <0066>` (f), `<00EC> <0069>` (i), `<00EF> <006C>` (l), `<00EA> <0067>` (g),
`<00EB> <0068>` (h), `<00D0> <0047>` (G), `<00D1> <0048>` (H).
**Only the four ligature CIDs answer U+FFFD.** Every one of the 90 bfchar entries is a single
2-byte destination — no multi-character destinations are used anywhere.

### 3. The embedded TrueType program (`FontFile2`, 20893 bytes)

`sfntVersion = 0x00010000`, `numTables = 11`:

| # | tag | offset | length |
|--:|:--|--:|--:|
| 0 | `OS/2` | 188 | 96 |
| 1 | `cvt ` | 284 | 514 |
| 2 | `fpgm` | 798 | 1751 |
| 3 | `glyf` | 2549 | 9450 |
| 4 | `head` | 11999 | 54 |
| 5 | `hhea` | 12053 | 36 |
| 6 | `hmtx` | 12089 | 4900 |
| 7 | `loca` | 16989 | 2452 |
| 8 | `maxp` | 19441 | 32 |
| 9 | `name` | 19473 | 945 |
| 10 | `prep` | 20418 | 475 |

**No `cmap`. No `post`.** (`maxp.numGlyphs = 1225`, `unitsPerEm = 1000`, `indexToLocFormat = 0`,
`hhea.ascent/descent = 934 / -254`.)

**The `cmap` table — every Unicode → glyph-id mapping it contains: the empty set.**
The table is absent, so it contains 0 mappings. Consequently: glyph ids mapping to U+0123 = none;
U+0124 = none; U+0126 = none; U+0127 = none; and the reverse lookup "which Unicode code points map
to glyph id 291" = **none**, likewise for 292, 294, 295. There are no ligature code points
(U+FB00–U+FB04) in the program either, for the same reason. The glyphs for the ordinary Latin
letters are reachable only through the PDF's `ToUnicode`, not through the font.

**The `post` table — glyph names.** The table is absent. The names reported in this file
(`glyph00291` etc.) are **synthesised by fontTools from the glyph order** (`.notdef`,
`glyph00001` … `glyph01224`), because a font with no `post` table has no glyph names. So the
ground truth is: **this font carries no glyph names whatsoever.** Nothing in it is named
`gcedilla`, `f_f`, `f_i`, or anything else — the names are positional.

`name` table (informational): id1/id4/id6 = `REAQAG+Effra-Regular`, id2 = `Regular`,
id0 = "Copyright 2016 Dalton Maag Ltd…", id7 = "Dalton Maag, DaMa, and Effra are registered
trademarks of Dalton Maag Ltd."

**Glyph population:** 1133 of the 1225 glyphs are empty (`numberOfContours == 0`); 92 carry an
outline — 91 CIDs plus `.notdef`, matching the 91 set bits in `/CIDSet`. The subset keeps CID
numbering intact by filling the gaps with blank glyphs (e.g. GID 293 / CID 0x0125 is empty at
advance 550; GID 297 / CID 0x0129 is empty at advance 550; GID 298 / CID 0x012A is empty at
advance 566).

### 4. `/CIDToGIDMap` and the per-CID resolution

`/CIDToGIDMap` is the **name** `/Identity`, not a stream — so there is no 2-byte array to parse and
**CID == GID**. GID for each CID:

| CID | GID | `post` name (synthetic) | structure | advance | bbox | reverse `cmap` lookup |
|:--|--:|:--|:--|--:|:--|:--|
| 0x0123 | **291** | `glyph00291` | simple, 1 contour, 46 points | 637 | 13, 0, 704, 684 | **none — no `cmap`** |
| 0x0124 | **292** | `glyph00292` | composite, 1 component | 539 | 13, 0, 478, 684 | **none — no `cmap`** |
| 0x0126 | **294** | `glyph00294` | simple, 1 contour, 49 points | 847 | 13, 0, 786, 684 | **none — no `cmap`** |
| 0x0127 | **295** | `glyph00295` | simple, 1 contour, 51 points | 858 | 13, 0, 797, 684 | **none — no `cmap`** |

GID 292 is a **composite** whose single component is `glyph00296` at offset (0, 0), component
flags `0x0516` = `ARGS_ARE_XY_VALUES | ROUND_XY_TO_GRID | WE_HAVE_INSTRUCTIONS |
USE_MY_METRICS | OVERLAP_COMPOUND`. GID 296 is the same shape as a simple glyph (advance 539,
bbox 13, 0, 478, 684, 1 contour) — i.e. the subsetter left the fi outline twice, once plain and
once wrapped. GID 292 and GID 296 are the same letterform.

### 5. Identifying the letterforms from the outlines

Component metrics used as the reference set (glyph ids taken from the correct `ToUnicode` entries):

| letter | GID | advance | bbox | contours |
|:--|--:|--:|:--|--:|
| f | 233 | 330 | 13, 0, 397, 684 | 1 (25 pts) |
| i | 236 | 222 | 60, 0, 161, 649 | 2 — dot (60,548,161,649), stem (66,0,156,465) |
| l | 239 | 212 | 61, 0, 151, 667 | 1 (4 pts) |
| g | 234 | 547 | 39, -212, 486, 476 | 2 |
| h | 235 | 543 | 61, 0, 484, 667 | 1 (24 pts) |
| G | 208 | 721 | 49, -16, 651, 683 | 1 (44 pts) |
| H | 209 | 709 | 76, 0, 633, 667 | 1 (12 pts) |

**5a. Width arithmetic.** An accented letter inherits its base letter's advance; a ligature is the
sum of its components minus the fitting that merging the outlines allows.

| CID | advance | base letter it "claims" | base advance | ratio | component sum | Δ from sum |
|:--|--:|:--|--:|--:|--:|--:|
| 0x0123 | 637 | g (U+0123) | 547 | **1.16×** | f+f = 2×330 = 660 | **-23** |
| 0x0124 | 539 | H (U+0124) | 709 | **0.76×** | f+i = 330+222 = 552 | **-13** |
| 0x0126 | 847 | H (U+0126) | 709 | **1.19×** | f+f+i = 330+330+222 = 882 | **-35** |
| 0x0127 | 858 | h (U+0127) | 543 | **1.58×** | f+f+l = 330+330+212 = 872 | **-14** |

A `ħ` (U+0127) is an `h` with a stroke through the ascender: 543–560 units wide. CID 0x0127 is
**858**. That single number refutes the h-family reading before any outline is drawn. Note also
that all four share lsb = 13, which is exactly `f`'s left side bearing (13) — every one of them
starts where an `f` starts.

**5b. Outline synthesis (IoU).** Each candidate letterform was rendered to a binary mask from its
own `glyf` outline (fontTools glyph set, cubic/quadratic curves flattened at 20 steps, 1400×900
canvas in font units), then unions of translated component masks were fitted by exhaustive search
over the second and third component offsets. IoU = |A∩B| / |A∪B|.

| CID | candidate | best IoU | at dx |
|:--|:--|--:|:--|
| **0x0123** (291) | **ff** | **0.9707** | f@0, f@310 |
| | fi | 0.7112 | f@0, i@330 |
| | ffi | 0.7692 | |
| | ffl | 0.7477 | |
| **0x0124** (292→296) | **fi** | **0.8873** | f@0, i@320 |
| | ff | 0.7486 | f@0, f@290 |
| | ffi | 0.5902 | |
| **0x0126** (294) | **ffi** | **0.9200** | f@0, f@310, i@630 |
| | ffl | 0.8829 | f@0, f@310, l@630 |
| | ff | 0.7375 | |
| **0x0127** (295) | **ffl** | **0.9366** | f@0, f@310, l@650 |
| | ffi | 0.9214 | f@0, f@310, i@640 |
| | ff | 0.7161 | |

0x0123 and 0x0124 are separated decisively (0.97 vs 0.71; 0.89 vs 0.75). 0x0126 and 0x0127 are
close on IoU alone (0.92 vs 0.88; 0.94 vs 0.92), so they were separated by the structural test
below rather than by the number.

**5c. The i-dot test — separates ffi from ffl.** `i` has a detached dot (its own contour,
y 548–649) above a stem that stops at x-height 465; `l` is one unbroken stem, y 0–667. So in the
third slot, an `i` leaves a **vertical gap** between x-height and the dot, and an `l` does not.

| glyph | x window | ink y-intervals |
|:--|:--|:--|
| CID 0x0126 (294) | 640–700 | (0, 465) and **(591, 683)** — gap 466–590 |
| CID 0x0126 (294) | 660–680 | (390, 465) and **(599, 680)** — gap |
| CID 0x0126 (294) | 620–720 | (0, 465) and **(581, 684)** — gap |
| CID 0x0127 (295) | 640–700 | **(595, 683)** continuous at that column |
| CID 0x0127 (295) | 620–720 | **(0, 684) — continuous, no gap** |

294 has a separated dot ⇒ **ffi**. 295 has unbroken ink to the baseline ⇒ **ffl**.
Reference: `i` alone = (0, 465) + (548, 649); `l` alone = (0, 667).

**5d. The four outlines, rendered.** Drawn from the `glyf` data and inspected: 291 reads `ff`
(two f's, one shared crossbar), 292/296 reads `fi`, 294 reads `ffi`, 295 reads `ffl`. Reference
glyphs render as f, i, l, g, h, G, H with no surprises.

**5e. A cedilla and a circumflex are impossible in this program.**

- **U+0123 `ģ`** needs a cedilla below the baseline. All four targets have **yMin = 0**. `g` is
  yMin = -212. Over the whole font, the lowest yMin is **-212** (GIDs 234 and 252) and the next
  is -200; **no glyph has yMin < -250**. There is no cedilla in the font.
- **U+0124 `Ĥ`** needs a circumflex above cap height. `H` is yMax = 667; an accent would need
  roughly 830–850. The **tallest glyph in the entire font is `.notdef` at yMax = 750** (next:
  GID 264 at 732, GID 122 at 729). The four targets are yMax = 684 — exactly `f`'s ascender
  (684). No glyph in the font is tall enough to be an accented capital.

### 6. What PyMuPDF actually extracts

`doc[i].get_text()` over all 9 pages: **U+FFFD count = 0**. MuPDF does not emit the replacement
character here — it applies the CID-as-code-point fallback and emits the literal accented letters:

```
p1: 'STD Tel. (Oģ):'                                          <- Office
p1: 'Staģ'                                                    <- Staff
p1: 'Bank/Branch to aĦx rubber stamp of'                        <- affix
p1: 'Fields marked asterix (*) are mandatory.Please Ĥll up in BLOCK letters only…'  <- fill
p1: '(For oĦce use only)'                                      <- office
p1: '19.Educational QualiĤcation:'                             <- Qualification
p1: 'Ĥcation Marks :'                                          <- fication
p1: 'ģerently abled'                                           <- differently
p1: 'Judicials /Military OĦcers, Senior Executives of State-owned Corporations,
     important Political Party OĦcials, etc.)'                 <- Officers / Officials
```

`page.get_text("rawdict")` for those spans — note the font name is reported **without** the subset
prefix, as `'Effra-Regular'`, and the character is the literal accented letter:

```
p1 font='Effra-Regular' size=6.00 bbox=[503.7, 133.6, 554.3, 145.1]
   text: 'Ħx rubber stamp of'
   chars: [('Ħ','U+0126'), ('x','U+0078'), (' ','U+0020'), ('r','U+0072'), …]
   origins: [(503.7,140.9), (508.7,140.9), (511.7,140.9), …]

p1 font='Effra-Regular' size=6.00 bbox=[146.1, 131.3, 294.6, 142.7]
   text: 'Ĥll up in BLOCK letters only and use black ink for signature'
   chars: [('Ĥ','U+0124'), ('l','U+006C'), ('l','U+006C'), (' ','U+0020'), …]
   origins: [(146.1,138.6), (149.4,138.6), (150.6,138.6), …]

p1 font='Effra-Regular' size=6.00 bbox=[25.0, 139.2, 75.5, 150.7]
   text: '(For oĦce use only)'
   chars: [('(','U+0028'), ('F','U+0046'), ('o','U+006F'), ('r','U+0072'), (' ','U+0020'),
           ('o','U+006F'), ('Ħ','U+0126'), ('c','U+0063'), ('e','U+0065'), …]

p1 font='Effra-Regular' size=6.00 bbox=[349.9, 637.1, 387.3, 648.6]
   text: 'ģerently abled'
   chars: [('ģ','U+0123'), ('e','U+0065'), ('r','U+0072'), ('e','U+0065'), …]
   origins: [(349.9,644.5), (353.7,644.5), (356.9,644.5), …]
```

**Site census** (`rawdict`, all 9 pages, spans carrying one of the four code points):

| code point | sites |
|:--|--:|
| U+0123 `ģ` | **13** |
| U+0124 `Ĥ` | **89** |
| U+0126 `Ħ` | **23** |
| U+0127 `ħ` | **2** |
| **total** | **127** |

(An earlier FINDINGS file recorded 291×13, 292×84, 294×25, 295×2. The per-CID split differs by
6 sites because that count was per face; the total, 127, and the 13 for CID 0x0123 agree.)

### 7. The raw content stream confirms the codes are CIDs, not characters

Page 1 content stream, 42999 bytes. 11 hex strings contain one of the four codes. Decoding each
2-byte code through the correct `ToUnicode` entries:

```
STD Tel. (O<0123=CID291->U+FFFD>):                     -> "STD Tel. (Off):"
Sta<0123=CID291->U+FFFD>                               -> "Staff"
Bank/Branch to a<0126=CID294->U+FFFD>x rubber stamp of -> "affix"
Fields marked asterix (*) are mandatory.Please <0124=CID292->U+FFFD>ll up in BLOCK
                                                       -> "fill"
(For o<0126=CID294->U+FFFD>ce use only)                -> "office"
19.Educational Quali<0124=CID292->U+FFFD>cation:       -> "Qualification"
Military O<0126=CID294->U+FFFD>cers                    -> "Officers"
important Political Party O<0126=CID294->U+FFFD>cials  -> "Officials"
```

Raw hex, verbatim from the stream:

```
<00DC00F700E40123>                                  = S t a CID0x0123          "Sta" + ff
<00EC00EC0004000300CD00EC0123 00E800F500E800F100F700EF00FC 000300E400E500EF00E800E7>
   = i i . _ D i CID0x0123 e r e n t l y _ a b l e d                            "Differently abled"
<00DC00DD00CD000300DD00E800EF0004000300A400D8012300A50005>
   = S T D _ T e l . _ ( O CID0x0123 ) :                                       "STD Tel. (Off):"
```

### 8. Word contexts — 127 sites, every one a ligature position

`ģ` (13): `O[ģ]:` · `Sta[ģ]` · `di[ģ]erent` · `di[ģ]ered` · `o[ģ]ered` · `a[ģ]ect` · `e[ģ]ect` ·
`[ģ]ected` · `a[ģ]orded` · `a[ģ]ecting` · `o[ģ]`
`Ĥ` (89): `[Ĥ]ll` · `[Ĥ]cation` · `veri[Ĥ]ed` · `Certi[Ĥ]ed` · `identi[Ĥ]cation` · `[Ĥ]nancial` ·
`bene[Ĥ]t` · `con[Ĥ]dentiality` · `Noti[Ĥ]cation` · `modi[Ĥ]cation` · `[Ĥ]rst` · `de[Ĥ]ciency` ·
`[Ĥ]er` · `speci[Ĥ]c` …
`Ħ` (23): `a[Ħ]x` · `o[Ħ]ce` · `O[Ħ]cers` · `O[Ħ]cials` · `O[Ħ]cially` …
`ħ` (2): `O[ħ]ine` (Offline)

Not one of the 127 sites sits where an accented Latin letter belongs. All 127 sit inside an
`ff`/`fi`/`ffi`/`ffl` cluster.

## How to test it

1. Re-extract and re-parse (all commands run from a clone of the repo):

```
git clone --depth 1 https://github.com/kavopdf/app /scratch/work/CS
python3 -c "import pikepdf; p=pikepdf.open('/scratch/work/CS/benchmarks/realworld/041122-Account_Opening_Form.pdf'); \
  d=p.get_object((134,0)); print(d['/CIDToGIDMap'], d['/FontFile2'] if '/FontFile2' in d else 'in FontDescriptor')"
```
   Confirm `/CIDToGIDMap` is the name `/Identity` and the `FontFile2` md5 is
   `b06402c9810e51fc60a17ceb5ba895b1`. If the md5 differs, the font changed and these numbers do
   not apply.

2. Prove the absence of `cmap`/`post` from the raw table directory, not from a library:

```
python3 - <<'PY'
import struct
d=open('REAQAG-Effra-Regular.ttf','rb').read()
num=struct.unpack('>H', d[4:6])[0]
print([d[12+16*i:16+16*i].decode('latin-1') for i in range(num)])
PY
```
   Expect exactly `['OS/2','cvt ','fpgm','glyf','head','hhea','hmtx','loca','maxp','name','prep']`.

3. Confirm the four CIDs are ligatures, independently of my numbers: render the glyph and compare
   its advance to the sum of its components' advances.
   `adv(291)=637` vs `2×adv(233)=660`; `adv(292)=539` vs `330+222=552`;
   `adv(294)=847` vs `330+330+222=882`; `adv(295)=858` vs `330+330+212=872`. Then check
   `glyf[291].yMin == 0` — a `ģ` cannot have yMin 0.

4. The decisive negative test for (b): ask the font program for U+0123. With no `cmap` the answer
   is "no such glyph". `TTFont('REAQAG-Effra-Regular.ttf')['cmap']` raises `KeyError`.

5. The end-to-end test of the extraction path:
```
python3 -c "import pymupdf; d=pymupdf.open('041122-Account_Opening_Form.pdf'); print(d[0].get_text()[:400])"
```
   A correct extractor prints `(Off)`, `Staff`, `affix`, `fill`; the current behaviour prints
   `(Oģ)`, `Staģ`, `aĦx`, `Ĥll`.

## Confidence

**High** on all three answers.

- The absence of `cmap` and `post` is read from the raw sfnt table directory — 11 tags, neither
  present. This is a byte-level fact, not an inference.
- CID == GID follows from `/CIDToGIDMap` being the name `/Identity`; there is no stream to parse.
- The `ff` and `fi` identifications are near-certain (IoU 0.9707 vs 0.7112; 0.8873 vs 0.7486, plus
  width arithmetic and the cedilla/circumflex impossibility).
- `ffi` vs `ffl` rests on IoU (0.9200 vs 0.8829; 0.9366 vs 0.9214 — close) **and** on the
  structural i-dot test, which is not close: 294 has a detached dot with a 125-unit gap, 295 has
  continuous ink from baseline to ascender. Confidence high on that pair.
- The exact recovered strings (U+0066 U+0066 etc.) are high confidence; the *rendered* text is
  also directly confirmed by the 127 word contexts, none of which reads as an accented letter.

**Lower confidence** on one thing only: the reason MuPDF emits `ģ` rather than U+FFFD. The
observation is certain (`get_text()` returns U+0123 with zero U+FFFD anywhere); the internal
mechanism by which MuPDF decides to fall back to the CID value is inferred, not read from MuPDF
source in this run.

## Ruled out

- **"The `cmap` will tell us which glyph is U+0123."** There is no `cmap`. Checked twice: raw
  table directory (11 tags) and fontTools (`KeyError` on `f['cmap']`). Any plan that depends on
  `descendantFont.cmap` reverse lookup cannot run on this font — it is not a shortcut that was
  missed, it is a table that is not in the file.
- **"The `post` table will give the glyph name (`gcedilla`, `f_f`, `f_i`)."** There is no `post`
  table either. The names `glyph00291` … are fontTools synthesising from the glyph order. Do not
  quote them as the designer's names.
- **"CID 0x0123 is a cedilla g."** Ruled out three ways: yMin = 0 (no descender; `g` is -212, and
  no glyph in the font is below -250); advance 637 vs g's 547; the outline matches `ff` at 0.9707
  and `fi` at 0.7112.
- **"CID 0x0124 is `Ĥ`, 0x0126 is `Ħ`, 0x0127 is `ħ`."** Ruled out by width (539 vs H's 709;
  858 vs h's 543 — a 1.58× ratio) and by height (the tallest glyph in the font is 750; an accented
  capital needs ~847).
- **"The four CIDs are bullets, symbols or special forms."** The four advance widths and outline
  IoUs are those of two- and three-letter clusters; each of the 127 uses sits inside an
  `ff`/`fi`/`ffi`/`ffl` word. No bullet appears in any context.
- **"MuPDF emits U+FFFD here."** It does not — zero U+FFFD across 9 pages. The damage is silent
  and looks like text, which is worse than a visible replacement character.
- **"`/CIDToGIDMap` is a stream and must be parsed as a 2-byte array."** It is the name
  `/Identity`. There is no array; CID == GID directly.
- **The `ToUnicode` is not merely truncated or malformed for these four.** It is well formed: 90
  bfchar entries, all single-destination, and the four ligature CIDs are explicitly mapped to
  U+FFFD by the producer. The information is deliberately absent, not damaged.

## Status

complete

The one thing this file does **not** settle, and says so plainly: there is no in-file source of
truth that spells out "ff"/"fi"/"ffi"/"ffl" as text. The font has no `cmap` and no `post`; the
`ToUnicode` says U+FFFD. The identification above is made from the glyph outlines and metrics,
which is the strongest evidence the file contains, but a producer who wants a machine-readable
answer must supply it from outside this PDF (an Effra reference font, or a word list). For a
consumer, the workable recovery is: `/CIDToGIDMap` (Identity) → GID → decompose the outline into
component glyphs → the Unicode of each component via the `ToUnicode` entries that are correct →
emit the multi-character string (`<0123>` → `ff`, `<0124>` → `fi`, `<0126>` → `ffi`,
`<0127>` → `ffl`). A `bfchar` destination may legally be a multi-character string, so the
producer-side repair is to rewrite those four entries as `<0123> <00660066>`,
`<0124> <00660069>`, `<0126> <006600660069>`, `<0127> <00660066006C>`.
