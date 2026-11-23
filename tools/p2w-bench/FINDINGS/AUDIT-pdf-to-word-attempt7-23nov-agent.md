# PDF-to-Word — deep audit, attempt 7 of 10

Agent, 23 Nov 2026. Read-only. Attempts 1-6 were the writers, the page gate, the checks, the app layer, the OCR
interface and the page loop. This one is cancellation and lifecycle: what happens when the user leaves the screen
while a document is converting.

---

## G1 — the coroutine scope is right

    PdfActivity.kt:526   lifecycleScope.launch {
    PdfActivity.kt:528       withContext(Dispatchers.IO) { ... }

`lifecycleScope` is cancelled when the Activity is destroyed, and that is the correct scope to have chosen. On
paper the work stops when the screen goes away.

---

## G2 — but cancellation is cooperative, and nothing inside the conversion ever cooperates

Measured, not assumed:

    suspend functions in PdfToWord.java        : 0
    Thread.interrupted / isInterrupted /
    ensureActive / CoroutineScope in PdfToWord : 0

`PdfToWord.convert` is a plain blocking Java method. Coroutine cancellation takes effect at a suspension point;
`convert` has none. `withContext(Dispatchers.IO)` is cancellable on entry and on exit, and **not at all in
between**.

So the sequence when a user leaves a 200-page conversion at page 12 is:

1. the Activity is destroyed and `lifecycleScope` is cancelled;
2. `convert` does not notice — it is in a `for` loop with no check;
3. it reads pages 13 to 200, building the whole `Result` in memory;
4. it returns; the coroutine finally observes the cancellation at the next suspension point;
5. the result is discarded.

**The user's work is abandoned correctly. The phone's work is not.** For the remaining 188 pages the process burns
CPU and holds every page's glyphs and blocks, on a screen the user has already left. On a low-end device that is
the difference between a fast app and one that feels hot and slow for a minute afterwards.

---

## G3 — all nine lifecycle guards are for the UI, none for the work

Counted exactly: **9 lifecycle references, in two shapes.**

    8 x  if (isFinishing || isDestroyed) return      <- return guards
    1 x  if (!isFinishing && !isDestroyed) toast()   <- the toast guard, ToolsActivity:608

The eight return guards sit before a toast, a dialog or a UI refresh. The ninth is the
`runOnUiThread { if (!isFinishing && !isDestroyed) toast(...) }` at ToolsActivity:608, whose comment records that
it was added because toasting from a worker thread crashed.

They are correct and they were added for good reasons. **None of them can stop a conversion**, because none of
them is reachable from inside `convert`.

---

## G4 — the fix is one check per page, and the reporting for it already exists

The page loop is the natural place, and it costs nothing:

    for (int i = 0; i < count; i++) {
        if (Thread.currentThread().isInterrupted()) { report.notes.add("stopped at page " + (i+1)); break; }
        ...
    }

`Thread.currentThread().isInterrupted()` is what a cancelled coroutine's thread carries when it is dispatched
through `Dispatchers.IO` with interruption enabled — and even where it does not, an explicit flag passed into
`convert` costs one boolean read per page.

**The reporting machinery is already there.** `Report` already carries `skippedPages` and a `notes` list, and
`ToolsActivity` already turns those into a user-visible summary. A cancelled conversion could say "stopped at page
12 of 200" instead of returning nothing at all.

**And it composes with attempt 6's F1.** That finding was that the loop has no per-page guard, so one corrupt page
loses the document. The same `for` loop is the place where both a per-page guard and a cancellation check belong,
and a single edit covers both.

---

## What this attempt did NOT cover

- **memory on a genuinely large document.** Still unmeasured after seven attempts, and now more pointed: G2 says a
  cancelled conversion keeps building the full `Result`, so the peak-memory window is the *whole* document even
  when nobody is waiting for it.
- `DocxWriter`'s 7,671 lines as a body of code.
- `PdfRepair` and the seam that feeds a repaired file into the converter.
- the 47 Kotlin files outside the two activities.

---

## For the fixer

**G2 is the finding; G4 is the edit.** One check at the top of the page loop, reusing `report.notes` and the
summary that already exists. It fixes cancellation and, in the same loop, gives attempt 6's F1 its per-page guard.

**Do not cancel by throwing from inside the loop.** The loop's own `Result` is what a partial conversion would
report from; a throw discards it and returns the user to the same silent failure this audit keeps finding.

Verify before changing. This attempt read code; it ran nothing.
