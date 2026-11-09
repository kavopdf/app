# PLAN-DECISIONS — running record

One entry per step. Append only. Nothing is deleted. When every step is FINAL,
these entries are assembled into AUTOMATION-PLAN.md — the master plan is built
from decisions, not debated in one sitting.

Status values: FINAL (settled), OPEN (still discussing), BLOCKED (waiting on
something), REVISIT (decided, but the decision may change if a later finding
contradicts it).

---

## F1 — APK ABI on the emulator

**Status: FINAL**

**Finding.** `app/build.gradle` declared `abiFilters 'arm64-v8a', 'armeabi-v7a'`.
No x86_64. The GitHub Actions Android emulator is x86_64. **The app would not
have installed at all** — the whole of Layer 1 would have failed on its first run.
This was assumed safe in the plan and was not.

**Decision.** Add `x86_64` to the shipping APK, not to a separate test build.

**Why.** A test build is not the artefact the user runs, and "the fix shipped" has
to be proven on the thing that ships. A separate test build would make the
pipeline's central claim untestable.

**Cost, measured not guessed.** The ARM-only APK is 38 MB. The build file's own
comment estimated the extra slice at about 22 MB, so expect roughly 60 MB. My
earlier estimate of 45–48 MB was wrong and is corrected here.

**Revisit if** 60 MB becomes unacceptable to users. The right answer then is an
Android App Bundle for Play, which delivers per-device ABIs — **not** dropping
x86_64, which would leave the pipeline unable to test the app at all.

**Open question.** The real size after the change is unknown until an APK is
built. Recorded as a follow-up, not a blocker.

---

## F2 — Does Google Drive drop `w:framePr`?

**Status: BLOCKED** — needs Drive authorisation.

**Why it matters.** The stamp fix rests on `w:framePr`. Google's docx importer may
drop it or move it. If it does, the stamp breaks again in the very renderer the
pipeline measures with, and the pipeline would report a pass while the user sees
a broken stamp.

**Test.** Upload one stamp docx, export it as PDF, and check whether the framed
paragraphs kept their position.

---

## F3 — Can `uiautomator` see inside Google Docs?

**Status: OPEN**

**Why it matters.** Docs renders in a WebView. The accessibility tree may expose
nothing useful, in which case the "is the stamp editable" check is not fragile —
it is impossible.

**Test.** Open Docs on an emulator, run `uiautomator dump`, inspect the XML.

---

## F4 — How slow is the emulator?

**Status: OPEN**

**Why it matters.** If a complex PDF takes 60 s on a real phone it may take 3–5
minutes on an emulator, making a ten-document batch 1.5 hours instead of 15
minutes, and the whole plan 3x longer.

**Test.** Convert one document on an emulator and time it.

---

## F5 — Will the pixel comparison ever converge?

**Status: OPEN**

**Why it matters.** Font substitution means some regions may never match. The
loop would chase them through all five attempts, forever. They need to be
identified and put on a known-different list rather than fixed.

**Test.** Measure one document three times and see which regions fail every time.

---

## A1 — Convert path

**Status: REVISIT** — depends on F1, which is now FINAL, and on F4.

**Leaning.** APK on emulator as the truth loop; engine harness as the fast loop.
The harness tests the engine, the app tests the app, and a disagreement between
them is itself a signal — the app layer has a bug the harness cannot see.

---

## Remaining steps, not yet discussed

A2 Render · A3 See · A4 Diagnose · B1 Tolerance · B2 Self-test · B3 Holdout ·
B4 Agreement · C1 Classification · C2 Grouping · C3 Attempts · C4 Regression ·
C5 Ratchet · C6 Progress · D1 APK build · D2 Secrets · D3 Second pass ·
E1 Scope · E2 Intake · E3 Checkpoints · E4 Queue
