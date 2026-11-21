# The last lost word on 601 was the reference counting "General" twice

21 Nov 2026, fixer run claimed 10:02. Two changes, measured separately. Instrument change: a guard in
`verify_txt.py`. Engine change: a widget `/AP /N` walk, **measured but not committed** - see the last
section for why and for the exact patch.

## What was wrong on the source side

`glyph_truth()` builds the truth the .txt is scored against. It walks the page's content stream, then
adds, for every widget, `_ap_stream_text(d, w.xref)`:

    for w in widgets:
        t = _ap_stream_text(d, w.xref)
        if t.strip():
            stats["widget_glyphs"] += len(t)
            walked += "\n" + t

On `601_fillable_admission_form` the page's own content stream draws `General` at (258.0, 244.9) - one
copy, confirmed with `page.get_text("words")` - and one widget's appearance stream draws it a second
time. The truth therefore held `General` **twice**, and the .txt's single, correct copy read as a lost
word:

    82 of 83 words = 98.8%   against a 99% threshold
    lost = {'General': 1}

The document loses nothing. The instrument did.

## The guard, and what it measured

    if t.strip() and t.strip() not in walked:

Every .txt in the corpus scored twice, same files, same engine, only the verifier changing (211
documents, both passes complete):

| | clean | newly clean | newly failing |
|---|---:|---|---|
| old verifier | 186 | - | - |
| new verifier | 187 | `601_fillable_admission_form` | **none** |

Document-level failed-check sets were compared one by one: **exactly one document changed, and no
document's failed set grew.** On the base engine the same guard moves 601's t01 from 96.4 to 97.6 with
no pass/fail change anywhere - the tick glyphs below are the other half of that document.

This is not a threshold move and not an abstain. It removes a duplicate the page never drew twice.

## The engine half: the widget `/AP /N` walk, measured and NOT committed

The brief's rotation is on `t01_word_accuracy`. Four of its five documents are reference-side
(`t01-census-WHICH-SIDE-0150-fixer.md`: 411, 39 and 38 are the reference's). 601 is the only
engine-side one, and the shape of its fix was already named: read each widget's `/AP /N`.

`FINDINGS/widget-ap-glyph-walk-0436-f1x.patch` did that. Measured today on the corpus rebuilt from
`corpus-v1`:

| | 601 t01 | 601 .txt lines | docx paragraphs | new Google-unsafe constructs |
|---|---:|---:|---:|---|
| unpatched engine | 96.4 | 51 | 33 | - |
| patched engine | 98.8 | 188 | 32 | none (`google_safe.py` identical) |
| patched + this guard | **100.0 - 7/7 PASS** | 188 | 32 | none |

Blast radius, measured against the committed `txt/RANKING-TXT.csv` as an independent source: **211
documents, 0 differences in any document's failed-check set.** `Account_Opening_Form_Fillable_filled`
- the 137-widget document the blast-radius finding warned about - converts to an identical 17-line
.txt with and without the patch.

**It is not committed because the gate refuses it, correctly.** `regress.py --check` says:

    ENGINE CHANGED (docx): table measured on 6c6cf642e13b7ed2, the tree is 90918f93ffad2422
    ENGINE CHANGED (txt): table measured on 5f35907f1571ba7e, the tree is 024180cc485fc5e7
    REFUSED. ... Re-measure, then --stamp.

Re-measuring the docx half costs 211 soffice renders. This run converted all 211 with the patched
engine and measured 114 before the slot ran out; the `--force` resume fix in
`p2w-force-not-resumable-75-75-75-1147-f1x.md` is what makes that pass finishable in one slot from now
on. The patch is saved, complete, at
`FINDINGS/widget-AP-walk-PLUS-WHITESPACE-GUARD-1145-f1x.patch` - it is the 0436 patch plus one guard
that skips whitespace-only appearance glyphs.

## The known cost of the engine patch, and its fix

The patched .txt for 601 is **188 lines where the base is 51**, and the words are pushed down the page.
No check notices (t02 and t08 abstain on this document) and the .docx is unchanged in paragraph count,
so nothing measured got worse - but it is not right. The blank lines come from `TxtWriter.appendPara`'s
gap model: each appearance glyph becomes a line, and `blanks = round((ly - lastY) / pitch) - 1` opens
up to `MAX_BLANK_LINES` between them. The ring-glyph path already solved this exact problem at
`PdfToWord.java` line 4155 by leaving `lineY` empty for glyphs that are not a text line. **The next
attempt on this construct should do that: the widget glyphs belong in `lines` and `lineX`, not in the
pitch model.**

## What would overturn this

* The guard, if some document's .txt genuinely omits a widget value the page does not draw and the guard
  suppresses it. It cannot: the guard only suppresses text already present in `walked`, which is what
  the truth is.
* The engine patch, if any document's docx changes beyond 601. 114 of 211 were measured with no change;
  the remaining 97 are unmeasured, and that is the reason it is a patch and not a commit.
