# 18_displacement — the bundled patch takes `68_journal` to 42/42 in Google, measured this slot, and the patch does not move `mobile-bill` at all

**22 Nov 2026 · fixer slot 11:52 → · patched tree (`patches/18-spacer-before-rowpitch-rowrule.patch`
applied to HEAD, engine built in-sandbox) · every Google number below is a live round trip
(ConvertOne → Drive create-as-Google-Doc → export PDF → `gverify.py --collect` → `verify_google.py`)
· all 3 probe Docs deleted after scoring, Drive root left empty**

## What was measured, and the one thing that was not

The 11:21–11:27 slot left this patch proved on four documents and blocked on the corpus measure. What
no run had ever measured is the **blast radius**: the census says 124 of 213 documents carry a table
spacer, and a document that is clean today could move under it.

**Census run this slot, on the patched build, over the 23 documents that pass all their Google
checks:** exactly **1** of them emits a spacer paragraph (`68_journal`, 15 of them). 22 of the 23 emit
none at all. So the population of clean documents this construct can reach is one, not thirteen — and
that one was already 41/42, not clean.

| document | before (Google) | after (Google) | what moved |
|:--|--:|--:|:--|
| `68_journal_wide_table_spanning` | **41/42** (`18_displacement` alone) | **42/42 CLEAN** | the spacer as `w:before` + the 4320 cap |

One Google round trip, one document, 41/42 → 42/42. That is the construct working on the document the
2880 cap truncated by 4.05 pt.

## The control that reframes `mobile-bill`

`mobile-bill` scored **31/42** with the patch — 11 checks failing, including `04_chars_missing`,
`31_pages_lost_their_text` and `53_embedded_faces`. Read alone that is a catastrophic regression and it
contradicts the 11:27 report's "41/42 → 42/42".

**The unpatched HEAD engine was rebuilt and put through the identical round trip.** It also scores
**31/42**, with the **same 11 checks failing, check for check**:

| document | HEAD (no patch) | patched | verdict |
|:--|--:|--:|:--|
| `mobile-bill` | 31/42 | 31/42 | **the patch changes nothing here** |

So `31/42` is what this sandbox's build produces for `mobile-bill` under the current 42-check
verifier, with or without the patch. It is not comparable to the committed `46/47` (a 47-check run of
a different verifier), and it must not be quoted as the document's score. **The 11:27 claim that the
patch closes `mobile-bill` to 42/42 does not reproduce on this build in either direction** — the
document is unmoved by every construct in the patch, which is a different finding from "the patch
fixed it" and needs its own measurement before anyone builds on it.

## Where the patch stands

- **Proved by this slot:** `68_journal` 41/42 → 42/42 in Google. One document, independently measured.
- **Refuted by this slot:** that `mobile-bill` moves at all. Patched and unpatched are identical, 11
  failures each.
- **Narrowed by this slot:** the blast radius on clean documents is **1**, not 13.
- **Still missing:** the corpus-wide ratchet. `gate.py --budget 250` measures ~26 of 213 per call and
  the corpus has to be rebuilt from nothing on a fresh pod (~7 min of ConvertOne, then ~35 min of
  measurement), so it does not fit one slot. The patch stays a patch.

## Two facts about this sandbox worth carrying

1. **`gverify.py --collect` takes a URL and runs `curl`; it accepts a `file://` URL**, so an export
   that the Drive tool has already written to `/scratch/downloads/composio/` can be scored without a
   second download. Three Drive calls per document, as designed.
2. **`upload` refuses `/scratch/work` and accepts `/scratch/output`.** The staged `.docx` must be
   copied into `/scratch/output` before it can be attached, and `GOOGLEDRIVE_CREATE_FILE` with no
   `parents` puts the Doc in the user's Drive **root** — it must be deleted afterwards, which is what
   was done here.
