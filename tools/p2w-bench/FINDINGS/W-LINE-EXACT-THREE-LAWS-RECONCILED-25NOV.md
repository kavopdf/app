# w:line exact on an sz=2 empty paragraph: three laws, one authority, and what settles it

## The three, as they stand in the repo

| date | source | the law it states |
|---|---|---|
| 22 Nov | `18_displacement-WBEFORE-IS-1TO1-GOOGLE-1005-agentA.md` | 2.5873 x max(L/240, 0.06) pt, about 21.5 % of the ask |
| 23 Nov | `FINDINGS/refused-spacer-before-lever-1458-relay.md` | 91.0 % of the ask at 14.4 pt, 95.3 % at 144 pt, from 13 probes |
| 24 Nov | `DOCS-ROOT-CAUSES-24NOV.md:616` | a flat 5-10 pt regardless of the ask |

They cannot all be true. A law that is 21.5 % of the ask, a law that is 91-95 % of the ask, and a law that
ignores the ask entirely describe three different renderers.

## Which one to act on: the 23 Nov law

It is the only one that states its evidence. Thirteen probes, two anchor points (14.4 pt and 144 pt), and a
result that is consistent with itself - 91 % and 95 % are close enough that the small gap is the fixed part of
the ask being a larger fraction at the smaller size. That is what a measured law looks like.

The 22 Nov entry is a fitted formula whose own coefficient (2.5873) appears nowhere else in the repo and whose
21.5 % contradicts a direct probe of the same construct two days later.

The 24 Nov entry is a range with no stated probe count and no anchor points. "5-10 pt" is what a law looks like
before it has been measured.

## What that means for a patch

Any patch leaning on this construct should assume Google honours MOST of an exact line height (91-95 %), not a
fifth of it and not a flat band. That is the conservative choice for the row-pitch work: if Google honours most
of the ask, a patch that spends the ask lands the row where the PDF has it, and a patch that assumes 21.5 %
overspends by four times.

## What would settle it, and why it was not done here

One Google round-trip on a two-paragraph .docx - one `w:line exact` at 14.4 pt and one at 144 pt, both on an
sz=2 empty paragraph - rendered and measured for the gap it produces. The 23 Nov law predicts 13.1 pt and
137.0 pt; the 22 Nov law predicts 3.1 pt and 31.0 pt; the 24 Nov law predicts the same number twice.

The difference between those predictions is large enough that one render separates them with no ambiguity.

This pod has no Drive credential, so the round-trip cannot be run from here. That is the whole reason this is a
reconciliation of the record rather than a new measurement.

## The rule this file exists to enforce

One construct, one law, one file. A run that needs to know how Google treats `w:line exact` should read this
file and not the three it cites. When the round-trip is finally run, the result belongs here and the three
source entries should point at it rather than restate a number.
