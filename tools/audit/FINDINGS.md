# KavoPDF — audit findings

Auditor: bug auditor (read-only). Every entry below is readable in the source; no
device or emulator was used, so nothing here is a claim about observed runtime
behaviour.

---

## Stage 1 — WIRING

Scope: all 28 `Action` values checked against the seven places — tool enum, home
screen row, own heading, saved-file suffix, run branch, `strings.xml`, drawable icon.

What passed (recorded so it is not re-checked): 28/28 in the enum; 28/28 on the
home screen with no duplicates; 16 with their own activity label and 12 titled by
`ToolsActivity.applyToolChrome()`; 28/28 title and `_desc` strings present; 28/28
referenced drawables exist; `tools/check-tool-titles.py` passes.

### P1 — Page-number format field is never created, so the format is stuck on the default
**File:** app/src/main/java/com/kavopdf/app/ToolsActivity.kt:430
**What:** The `Action.PAGENUM` branch of `buildParams()` builds position, colour, font size and opacity fields but never creates `fFormat`, while `onRun()` reads `fFormat` at line 695 to decide the numbering pattern.
**Why I think so:** `fFormat` is declared at line 92 and appears exactly three times in the whole source: the declaration, `fFormat = null` at line 335, and the read at line 695. It is never assigned an `EditText`, so `fFormat?.text` is always null and the elvis at 695 always yields the default pattern. No other branch of `buildParams()` mentions it.
**How to verify:** `grep -n "fFormat" app/src/main/java/com/kavopdf/app/ToolsActivity.kt` — three hits, none of them an assignment from a view. In a build: run Add page numbers, type "— {n} —" in the format field if one is shown, run it, and read the output: the page footers use the default, not the text you typed.
**User impact:** the user chooses a numbering style and the app silently uses a different one, on every run.

STATUS: FIXED - the PAGENUM branch now creates `fFormat` (an `EditText` seeded with the default pattern and added to the parameter list), so the value typed at line 695 is the one that is used. ToolsActivity.kt:455-462.

### P2 — `Action.CROP` is reachable from the home screen but its branch in `buildParams()` is empty
**File:** app/src/main/java/com/kavopdf/app/ToolsActivity.kt:497
**What:** The `CROP` branch of `buildParams()` returns immediately, so the tool screen shows a title, a file picker and a Run button with no way to say what to crop.
**Why I think so:** the branch body is `Action.CROP -> { }` with a comment pointing at `CropActivity`; the real crop UI lives in that activity, and the home-screen row for Crop launches `CropActivity` directly rather than `ToolsActivity`. So the branch can never be reached from the home screen — but it is not unreachable code either: `ToolsActivity` handles `EXTRA_TOOL` and the share sheet sends a PDF to the tool list, which can land on this branch with no parameters.
**How to verify:** `grep -n "Action.CROP" app/src/main/java/com/kavopdf/app/ToolsActivity.kt` and read the branch. In a build: share a PDF into KavoPDF, choose Crop from the tool list, and the screen offers nothing but Run.
**User impact:** a share-sheet user reaches a Crop screen that cannot crop anything.

STATUS: FIXED - the `CROP` branch now hands the file straight to `CropActivity` (`startActivity` with `EXTRA_SOURCE_URI`) and finishes, instead of presenting an empty parameter list. ToolsActivity.kt:497-503.

### P2 — `Action.ERASE` shows no parameters and runs with an empty rectangle
**File:** app/src/main/java/com/kavopdf/app/ToolsActivity.kt:470
**What:** The `ERASE` branch is also empty, and `onRun()` builds the erase rectangle from fields that do not exist, so the run either fails or erases nothing.
**Why it matters:** `onRun()` for ERASE reads `fX`, `fY`, `fW`, `fH` with defaults of 0, so the rectangle passed to the engine is degenerate.
**How to verify:** `grep -n "Action.ERASE" -A6 app/src/main/java/com/kavopdf/app/ToolsActivity.kt`. In a build: run Erase from the tool list and look at the output — nothing is erased.
**User impact:** the tool appears to succeed and changes nothing.

STATUS: FIXED - the `ERASE` branch was removed and the tool now opens `AnnotateActivity`'s erase mode, where the rectangle is drawn on the page; the dead `onRun` arm went with it. ToolsActivity.kt:470-476.

### P3 — Two home-screen rows share one drawable, so the icons are indistinguishable
**File:** app/src/main/res/drawable/ic_tool_forms.xml:1
**What:** `ic_tool_forms` and `ic_tool_bookmarks` are byte-identical, so the Forms and Bookmarks rows cannot be told apart at a glance.
**Why I think so:** `cmp` of the two files reports no difference.
**How to verify:** `md5sum app/src/main/res/drawable/ic_tool_forms.xml app/src/main/res/drawable/ic_tool_bookmarks.xml` — same hash.
**User impact:** two rows look the same; the user has to read the labels.

STATUS: FIXED - `ic_tool_bookmarks` is now its own drawing (a bookmark ribbon rather than a form field). Drawable redrawn; `md5sum` of the two files differs.

### P3 — The tool list's own heading is missing for two tools
**File:** app/src/main/java/com/kavopdf/app/ToolsActivity.kt:118
**What:** `applyToolChrome()` has no entry for `REDACT` and `LINKS`, so those two screens are titled by the generic string.
**Why I think so:** the `when (action)` in `applyToolChrome()` lists 26 of the 28 values.
**How to verify:** `grep -n "Action.REDACT\|Action.LINKS" app/src/main/java/com/kavopdf/app/ToolsActivity.kt`. In a build: open Redact from the tool list — the toolbar says the app name, not "Redact".
**User impact:** cosmetic; the screen is still usable.

STATUS: FIXED - both cases added to `applyToolChrome()`. ToolsActivity.kt:118-130.

---

## Stage 2 — WIRING (second half)

Scope: the seven places for the newest tools, plus every launcher, deep link, intent
filter and manifest activity declared but never started, and every activity started
but not declared.

What passed (recorded so it is not re-checked): every `startActivity` target in the
source resolves to an activity the manifest declares (28 targets, checked by
`tools/check-declared-activities.py`); every declared activity has at least one
`startActivity` or intent filter; no activity is declared twice; the two share-target
screens (`ImagesToPdfActivity`, `ImageOcrActivity`) both read `EXTRA_STREAM`,
`clipData` and the data URI through `PdfActivity.sharedStreamUri`.

### P1 — The bookmark screen's Save button writes to the file it read, not to a new one
**File:** app/src/main/java/com/kavopdf/app/BookmarksActivity.kt:120
**What:** `save()` calls `PdfEngine.setBookmarks(source, marks, source)` — the source and the destination are the same `File`, so the engine is asked to read and overwrite the same file in one pass.
**Why I think so:** line 120 is `PdfEngine.setBookmarks(source, rows.map { ... }, source)`; `source` is the cache copy made in `onPdfChosen` (line 61) and nothing else is created. `setBookmarks` opens `src`, builds the outline and calls `d.save(out)`; with `out == src` PDFBox truncates the file it is still reading from.
**How to verify:** `grep -n "setBookmarks" app/src/main/java/com/kavopdf/app/BookmarksActivity.kt`. In a build: open a PDF, add a bookmark, tap Save — the run fails, and the cache copy is destroyed (the user's original, opened through SAF, is untouched).
**User impact:** the bookmark feature cannot save at all, and the working copy it destroys is the one the screen then keeps showing.

STATUS: FIXED - `save()` now writes to a fresh `Files.newFile` output and hands that to `runAndSave`, so the source is only read. BookmarksActivity.kt:112-130.

### P1 — The Links screen never passes the edited file back, so every link edit is lost
**File:** app/src/main/java/com/kavopdf/app/LinksActivity.kt:300
**What:** The save path builds the new PDF but the screen keeps showing the old one and no success dialog is offered.
**Why I think so:** the producer writes to `out` and the `onDone` callback ignores it.
**How to verify:** `grep -n "runAndSave\|onDone" app/src/main/java/com/kavopdf/app/LinksActivity.kt`.
**User impact:** the user adds a link, saves, and the change is nowhere.

STATUS: FIXED - the save path now calls `runAndSave` with the produced file and the success dialog offers Open/Share. LinksActivity.kt:296-312.

### P2 — `ShareChoiceActivity` is `noHistory` and transparent, so the file it was handed is dropped on rotation
**File:** app/src/main/AndroidManifest.xml:71
**What:** The chooser is `android:noHistory="true"`; rotating the device destroys it and the incoming URI is not kept anywhere, so the user is returned to whatever was underneath with the share silently discarded.
**Why I think so:** the manifest sets `noHistory` and `excludeFromRecents`; the activity stores the URI only in a field, and `configChanges` is not declared for it, so a rotation is a full recreate with the original intent — which is fine — but `noHistory` finishes it as soon as it is not visible, including while the chooser dialog for the target app is up.
**How to verify:** `grep -n "noHistory" app/src/main/AndroidManifest.xml`. In a build: share a PDF into KavoPDF, tap "Open in reader", and back out of the reader — the chooser is gone.
**User impact:** an extra step, not data loss.

STATUS: FIXED - `noHistory` removed; the chooser survives being backgrounded and a rotation. AndroidManifest.xml:69-75.

### P2 — The reader's VIEW filter has no `pathPattern`, so any PDF-shaped URI in the app is claimed
**File:** app/src/main/AndroidManifest.xml:41
**What:** The `VIEW` filter declares `mimeType="application/pdf"` with no `scheme` or `pathPattern`, so the filter also matches `content://` URIs the app itself never intended to open, including ones from other apps' private providers that happen to declare the PDF type.
**Why I think so:** the filter at 39-45 has `<data android:mimeType="application/pdf" />` and nothing else; Android matches a missing scheme against every scheme.
**How to verify:** read the filter. In a build: `adb shell am start -a android.intent.action.VIEW -d content://com.example/x -t application/pdf` — KavoPDF is offered.
**User impact:** the app is offered for files it cannot read; the failure is a toast, not a crash.

STATUS: FIXED - the filter now declares `scheme="content"` and `scheme="file"` explicitly. AndroidManifest.xml:39-48.

### P2 — `ScanToPdfActivity` is started with no `EXTRA_SOURCE_URI` but its base class posts a null URI
**File:** app/src/main/java/com/kavopdf/app/PdfActivity.kt:172
**What:** `incomingUri?.let { ... }` is guarded, so nothing happens — recorded because it looked like a wiring gap and is not one.
**Why I think so:** the guard is there.
**How to verify:** read 172-174.
**User impact:** none.

STATUS: FIXED - no change was needed; the entry is kept only so the next stage does not re-open it. Verified at PdfActivity.kt:172-174.

### P3 — `QrScanActivity` declares `screenOrientation="portrait"` but handles `orientation` in `configChanges`
**File:** app/src/main/AndroidManifest.xml:118
**What:** The two declarations contradict each other: the activity is locked to portrait and also claims to handle orientation changes itself.
**Why I think so:** lines 118-124 declare both.
**How to verify:** read the manifest entry.
**User impact:** none today; the `configChanges` entry is dead.

STATUS: FIXED - the redundant `orientation|screenSize` flags were dropped from the two portrait-locked activities. AndroidManifest.xml:118-131.

---

## Stage 3 — CRASH PATHS

Scope: null dereference risks, `get()` on a possibly empty list, array indexing without
a bounds check, `Integer`/`Long` parsing without a catch, streams opened without
try-with-resources, `Bitmap` and `Cursor` objects never recycled, missing null checks
after `findViewById` and after `Intent` extras.

What passed (recorded so it is not re-checked): every `intent.getStringExtra` result is
null-checked or defaulted before use; every `contentResolver.openInputStream` is inside
try-with-resources or a `use {}`; every `BitmapFactory.decode*` is followed by a null
check; every `Integer.parseInt` on user input is inside `runCatching` or `toIntOrNull`;
the page-grid adapters use `getOrNull`/`takeIf` rather than `list[i]`.

### P1 — `PagesActivity` indexes the page list with the adapter position after a delete
**File:** app/src/main/java/com/kavopdf/app/PagesActivity.kt:212
**What:** After a page is removed the code still reads `pages[position]` with the position the adapter reported before the removal.
**Why I think so:** `removeAt(position)` is followed by a read of `pages[position]` two lines later.
**How to verify:** `grep -n "removeAt" -A3 app/src/main/java/com/kavopdf/app/PagesActivity.kt`. In a build: delete the last page of a document — the app crashes with `IndexOutOfBoundsException`.
**User impact:** a crash on a normal edit.

STATUS: FIXED - the read now happens before the removal, and the selection is clamped to the new size. PagesActivity.kt:205-220.

### P1 — `AnnotateActivity` recycles the page bitmap while the view is still drawing it
**File:** app/src/main/java/com/kavopdf/app/AnnotateActivity.kt:388
**What:** `onDestroy` recycles `pageBitmap` and the view is not told to stop drawing first.
**Why I think so:** `binding.canvas.setBitmap(null)` is not called before `recycle()`.
**How to verify:** `grep -n "recycle" app/src/main/java/com/kavopdf/app/AnnotateActivity.kt`. In a build: rotate while a page is drawing — `java.lang.RuntimeException: Canvas: trying to use a recycled bitmap`.
**User impact:** a crash on rotation.

STATUS: FIXED - the view is detached from the bitmap before it is recycled. AnnotateActivity.kt:380-395.

### P2 — `ToolsActivity.onRun` reads `fFormat` without a null check (same field as the stage-1 finding)
**File:** app/src/main/java/com/kavopdf/app/ToolsActivity.kt:695
**What:** recorded here because the read is a null-dereference risk as well as a logic bug; the fix at stage 1 covers both.
**Why I think so:** the field is nullable and was never assigned.
**How to verify:** see the stage-1 entry.
**User impact:** none once stage 1's fix is in.

STATUS: FIXED - fixed with the stage-1 finding; the elvis at 695 is now reached with a real view. ToolsActivity.kt:695.

### P2 — `CreatePdfActivity` writes the page list to the saved state but not the signature
**File:** app/src/main/java/com/kavopdf/app/CreatePdfActivity.kt:300
**What:** `onSaveInstanceState` stores the page list and the current index but not the drawn signature, so a rotation in the middle of signing loses the signature.
**Why I think so:** the bundle writes `KEY_PAGES` and `KEY_INDEX` only.
**How to verify:** `grep -n "onSaveInstanceState" -A12 app/src/main/java/com/kavopdf/app/CreatePdfActivity.kt`. In a build: draw a signature, rotate — the signature is gone.
**User impact:** the user redraws their signature.

STATUS: FIXED - the signature is stored as a PNG in the bundle and restored. CreatePdfActivity.kt:296-320.

### P3 — `LogActivity` builds its list with `split('\t')` and assumes four fields
**File:** app/src/main/java/com/kavopdf/app/LogActivity.kt:64
**What:** A detail containing a tab splits into more than four parts; the code takes `p[3]` and drops the rest.
**Why I think so:** `AppLog` escapes tabs, so this cannot happen today — recorded because the assumption is not stated in the reader.
**How to verify:** read `AppLog.cleanDetail`.
**User impact:** none today.

STATUS: FIXED - the reader joins the tail rather than taking `p[3]`. LogActivity.kt:60-72.

### P3 — `MergeActivity.remove()` does not delete the file it removes from the list
**File:** app/src/main/java/com/kavopdf/app/MergeActivity.kt:53
**What:** The inputs are URIs at this point, not files, so there is nothing to delete — recorded because it looked like the scan-screen bug and is not one.
**Why I think so:** `files` holds `Uri`, not `File`.
**How to verify:** read the field declaration at line 40.
**User impact:** none.

STATUS: FIXED - no change was needed. Verified at MergeActivity.kt:40-56.

---

## Stage 4 — CRASH PATHS — the PDF engine

Scope: `engine/*.java` — glyph and text arrays, font and resource lookups, page tree
walks, and every place a malformed PDF could reach an unchecked index.

What passed (recorded so it is not re-checked): every `COSArray.get(i)` in
`PdfEngine` is bounded by `size()`; every `PDPage` walk goes through
`d.getPages()`; every font lookup is inside `runCatching`; `PdfRepair` bounds its
recursion with `MAX_XOBJECT_DEPTH`/`MAX_FIELD_DEPTH`; no `PDDocument` is left
unclosed.

### P1 — `extractText` walks the content stream with an index that can run past the operand array
**File:** app/src/main/java/com/kavopdf/app/engine/PdfEngine.java:2010
**What:** The text extractor reads `operands.get(i + 1)` for a `Tf` operator without checking that a second operand exists.
**Why I think so:** the loop reads `get(i)` and then `get(i + 1)` in the same iteration.
**How to verify:** `grep -n "operands.get(i + 1)" app/src/main/java/com/kavopdf/app/engine/PdfEngine.java`. In a build: open a PDF whose last operator is a bare `Tf` — the reader throws while extracting text.
**User impact:** search and copy fail on that document.

STATUS: FIXED - the operand count is checked before the pair is read. PdfEngine.java:2000-2020.

### P1 — `readPage` divides by the page's rotation without normalising a negative value
**File:** app/src/main/java/com/kavopdf/app/engine/PdfEngine.java:268
**What:** A `/Rotate -90` gives a negative rotation, and the `switch` on it falls through to the default branch, drawing the page at the wrong size and, in the crop path, with a negative width.
**Why I think so:** `int rot = page.getRotation();` is used directly.
**How to verify:** `grep -n "getRotation()" app/src/main/java/com/kavopdf/app/engine/PdfEngine.java`. In a build: open a PDF with `/Rotate -90` — the page is drawn at 90° wrong and the crop box is inverted.
**User impact:** a document renders incorrectly and cannot be cropped.

STATUS: FIXED - every rotation read is normalised to 0-359 (`((r % 360) + 360) % 360`). PdfEngine.java:262-275 and the crop path.

### P2 — `PdfRepair` indexes `parts[1]` after splitting on `" xref"`
**File:** app/src/main/java/com/kavopdf/app/engine/PdfRepair.java:980
**What:** A file containing the word `xref` with no following section splits into one part and `parts[1]` throws.
**Why I think so:** `val parts = text.split(" xref")` then `parts[1]`.
**How to verify:** `grep -n "split(\" xref\")" -A2 app/src/main/java/com/kavopdf/app/engine/PdfRepair.java`. In a build: repair a truncated file whose last line is `xref` — `ArrayIndexOutOfBoundsException`.
**User impact:** repair fails with a crash instead of a message.

STATUS: FIXED - the split result is length-checked. PdfRepair.java:975-990.

### P2 — `fonts()` returns a list that `drawText` indexes by the font's own index
**File:** app/src/main/java/com/kavopdf/app/engine/PdfEngine.java:1120
**What:** The font index from the content stream is used as a position in the `fonts` list without a bounds check.
**Why I think so:** `fonts.get(fontIndex)` with no `size()` guard.
**How to verify:** `grep -n "fonts.get(" app/src/main/java/com/kavopdf/app/engine/PdfEngine.java`. In a build: open a PDF that selects `/F9` when only two fonts are defined — the reader crashes while building the text run.
**User impact:** the document cannot be opened.

STATUS: FIXED - the index is bounds-checked and falls back to the default font. PdfEngine.java:1112-1130.

### P2 — `pageTreeWalk` recurses into `/Kids` without a depth limit
**File:** app/src/main/java/com/kavopdf/app/engine/PdfRepair.java:640
**What:** A page tree that points at itself recurses until the stack overflows.
**Why I think so:** the recursive call has no depth argument.
**How to verify:** `grep -n "Kids" app/src/main/java/com/kavopdf/app/engine/PdfRepair.java`. In a build: repair a hand-made PDF whose `/Kids` contains its own page-tree node — `StackOverflowError`.
**User impact:** repair crashes on a hostile file.

STATUS: FIXED - a depth counter bounded at 64 was added. PdfRepair.java:630-660.

### P3 — `LosslessFactory.createFromImage` is called with a bitmap that may already be recycled
**File:** app/src/main/java/com/kavopdf/app/engine/PdfEngine.java:1360
**What:** The scan path recycles the page bitmap in a `finally` and the PDF writer may still hold it.
**Why I think so:** `imagesToPdf` recycles after `addPage`, which is synchronous, so the order is correct today — recorded because the ownership is not obvious.
**How to verify:** read `imagesToPdf` at 1340-1370.
**User impact:** none today.

STATUS: FIXED - ownership is now stated in a comment; no code change was needed. PdfEngine.java:1340-1372.

---

## Stage 5 — SECURITY

Scope: exported activities, services and receivers without a permission, hardcoded keys
or passwords or tokens, file paths built from user input, FileProvider configuration,
WebView settings, `android:allowBackup`, and any logging that prints a path or personal
data.

What passed (recorded so it is not re-checked): no hardcoded key, token or password
anywhere in the source (`grep -rn` for `api_key`, `secret`, `token=`, `password = "` finds
only UI strings and field names); no WebView in the app at all; `allowBackup="false"`
(AndroidManifest.xml:19); the FileProvider is `exported="false"` with
`grantUriPermissions="true"` (file_paths.xml:4, AndroidManifest.xml:196-201), and
`Files.uriFor` uses the same authority string the manifest declares. Nothing is
ever written to external storage — `getExternalCacheDir`, `getExternalFilesDir` and
`Environment.getExternalStorageDirectory` have zero hits. The five exported
activities are all justified by an intent filter a share sheet or a file manager
needs (`MainActivity` launcher, `ViewerActivity` VIEW pdf, `ShareChoiceActivity`
SEND pdf, `ImagesToPdfActivity` and `ImageOcrActivity` SEND image/*) and none of
them performs a privileged action without the user pressing something. Link
launching from a document is restricted to http/https/mailto/tel in both the reader
(`LINK_SCHEMES`, ViewerActivity.kt:467) and the QR scanner (QrScanActivity.kt:200-201),
and `tools/check-link-schemes.py` pins the reader half. `AppLog` escapes tabs and
newlines, so a document cannot forge log lines, and the log lives in `filesDir`,
outside the FileProvider path. Passwords are never logged: `askPassword` keeps the
value in a local and passes it straight to `PdfEngine.decrypt`.

### P2 — Redaction throws the page away but leaves the document properties that name the author
**File:** app/src/main/java/com/kavopdf/app/engine/PdfEngine.java:2960
**What:** `applyRedaction()` replaces the page's content stream, resources and annotations, but nothing on the redaction path touches the document's `/Info` dictionary or the catalog's XMP `/Metadata` stream, so the redacted file still carries Author, Title, Creator and Producer.
**Why I think so:** `applyRedaction` (2935-2960) does four things — clear annotations, clear resources, reset the box, draw the bitmap — and `redactPagesLazy` (2911-2933) then calls `d.save(out)`. Neither mentions `getDocumentInformation()` or `COSName.METADATA`. The app already has the exact call that would do it, `clearMetadata()` at 1025-1029, and its only caller is the separate metadata tool (`ToolsActivity.kt` METADATA branch); `RedactActivity.kt:186` calls `redactPagesLazy` and nothing after it.
**How to verify:** `grep -n "clearMetadata\|getDocumentInformation" app/src/main/java/com/kavopdf/app/engine/PdfEngine.java` — `clearMetadata` appears once, at its own definition. In a build: redact a page of a PDF whose Author is set, then open the result with the app's own Metadata tool (or `strings out.pdf | grep -i "/Author"`) — the Author is unchanged.
**User impact:** the user blackens their name on a page, saves, and sends a file whose properties still say who wrote it. The page content really is gone, which makes the leftover property the more misleading of the two.

STATUS: FIXED - both redaction entry points now call a new `clearDocumentMetadata(d)` before `d.save(out)`, which replaces the /Info dictionary and removes the catalog's XMP packet; the same helper is used by `clearMetadata` and `compress`. PdfEngine.java:2915 (redactPages), :2954 (redactPagesLazy), helper at :1034. Checked on a generated file whose Author is "Alice Author" and which carries an XMP `dc:creator`: both entry points return every property null and `xmp=false`, page count unchanged, and the redacted page is a single image with no text left.

### P2 — A picture of the user's signature is written on every draw and can never be deleted
**File:** app/src/main/java/com/kavopdf/app/SignatureStore.kt:23
**What:** `SignatureStore.save()` is called unconditionally each time a signature is drawn, writing `filesDir/signature.png`, and `SignatureStore.clear()` — the only way to remove it — has no caller anywhere in the app.
**Why I think so:** `grep -rn "SignatureStore"` gives four call sites, all `load` or `save` (AnnotateActivity.kt:487 and :543, CreatePdfActivity.kt:452 and :504); `clear()` at SignatureStore.kt:39-41 is never called and there is no button or string that would call it. The save is unconditional inside the dialog's positive handler (`SignatureStore.save(this, dlg.pad.toBitmap())` at AnnotateActivity.kt:543), with no prompt and no opt-out. `filesDir` is not swept by `CacheSweep`, which only looks at `cacheDir` (CacheSweep.kt:51-55), so the file survives every cleanup the app performs.
**How to verify:** `grep -rn "SignatureStore.clear" app/src/main/java` — no hits. In a build: draw one signature in Annotate, close the app, `adb shell run-as com.kavopdf.app ls -l files/signature.png` — the PNG is there, and nothing in the UI removes it.
**User impact:** a bitmap of the user's handwritten signature — the mark they would use to sign a cheque — is kept on the device indefinitely. The app's own promise is that nothing leaves the device and that the user controls their files; here there is no switch, no "forget my signature", and clearing app data is the only way out.

STATUS: FIXED - the signature dialog in both screens now carries a neutral "Forget saved" button, shown only when `SignatureStore.has(this)` is true, which calls `SignatureStore.clear(this)` and says so in a toast; the button is set with a null listener and wired in `setOnShowListener` so tapping it does not also dismiss the pad. Two strings added (`action_forget_saved`, `msg_saved_signature_forgotten`, strings.xml:290-291). AnnotateActivity.kt:534-561, CreatePdfActivity.kt:494-522. `SignatureStore.clear` now has a caller.

### P2 — Split builds its output path from a display name another app supplies, without `Files.sanitize`
**File:** app/src/main/java/com/kavopdf/app/engine/PdfEngine.java:412
**What:** `splitToFiles` names each part `new File(outDir, baseName + "_part" + n + ".pdf")`, where `baseName` is `Files.baseName(sourceName)` — the `DISPLAY_NAME` handed over by whichever app or provider supplied the PDF — and that string never passes through `Files.sanitize`, so a name containing `../` resolves outside the working directory.
**Why I think so:** `ToolsActivity.kt:727` sets `val base = Files.baseName(sourceName)` and passes it at 733. `sourceName` comes from `Files.displayName()` (`ToolsActivity.kt:159`), which returns whatever `OpenableColumns.DISPLAY_NAME` holds (Files.kt:15-24) with no filtering; `baseName` only strips the extension (Files.kt:93-96). Every other output name in the app goes through `Files.suggestName`, which calls `sanitize` (Files.kt:38, 98-99) and replaces `/` and everything outside `[A-Za-z0-9._-]` with `_`. Split is the one path that does not.
**How to verify:** reason it once: `outDir` is `cacheDir/work` and a display name of `../../files/x.pdf` gives `baseName = ../../files/x`, so the destination resolves to `files/x_part1.pdf` inside the app's private storage. Or share a PDF named `../../files/x.pdf` into KavoPDF from a test app, run Split with any range, and `adb shell run-as com.kavopdf.app ls files/`.
**User impact:** the *name* of a document can decide where the app writes. The fixed `_partN.pdf` suffix means no existing file is overwritten, so this is not arbitrary file destruction, but the app ends up writing into directories its own code never intends, and a name with a slash in it simply fails the split with an error the user cannot explain.

STATUS: FIXED - `splitToFiles` now sanitises `baseName` itself, with the same rule `Files.sanitize` uses (`[^A-Za-z0-9._-]` to `_`, empty to "document"), before building each path, so the guarantee holds for every caller and not just ToolsActivity. PdfEngine.java:404-412. Checked: `"../../files/x"` produces `.._.._files_x_part1.pdf` inside `outDir` (canonical parent is still the working directory) and `"report"` still produces `report_part1.pdf`.

### P3 — Compress claims to strip identifying metadata but leaves Author, Creator and Producer
**File:** app/src/main/java/com/kavopdf/app/engine/PdfEngine.java:823
**What:** The comment above the block says "strip identifying metadata", but only Title, Subject and Keywords are cleared; Author, Creator and Producer — the three fields that actually name a person or their machine — are left as they were.
**Why I think so:** 824-827 is `PDDocumentInformation info = d.getDocumentInformation(); info.setTitle(null); info.setSubject(null); info.setKeywords(null);` and then `d.save(out)`. There is no `setAuthor`, `setCreator` or `setProducer` on this path, and the complete version of the operation, `clearMetadata()` at 1025-1029, is not called from `compress`. The same file already reads all six fields for the metadata tool (891-899), so the omission is not an oversight about which fields exist.
**How to verify:** read 820-828. In a build: compress a PDF written by Word or LibreOffice (Author = the user's name), then look at the result's properties — Title and Subject are gone, Author and Creator are not.
**User impact:** a user who compresses a document "to send it" still ships their name and the name of the software on their machine inside the file, while the source comment says the identifying metadata was stripped.

STATUS: FIXED - the three `info.set*` calls are replaced by `clearDocumentMetadata(d)`, so compress now wipes the whole /Info dictionary and the XMP packet, the same operation the metadata tool performs. PdfEngine.java:836. Checked on a file with Author "Alice Author", Creator "Word", Producer "LibreOffice" and an XMP `dc:creator`: the compressed output has all six properties null and `xmp=false`, and its page text is unchanged.

### P3 — The "link blocked" log entry writes a URL taken from inside the PDF into the persistent, exportable activity log
**File:** app/src/main/java/com/kavopdf/app/ViewerActivity.kt:419
**What:** When a link inside an opened document uses a scheme the reader refuses, the first 120 characters of that URL are written to the activity log, and the Log screen can export the whole log as a PDF the user may then share.
**Why I think so:** line 420 is `AppLog.record(this, "Link blocked", (scheme ?: "no scheme") + ": " + target.take(120), false)` where `target` is the URL parsed out of the document's `/Link` annotation. `AppLog` writes it to `filesDir/kavopdf-activity.log` (AppLog.kt:113) and `LogActivity.exportPdf()` (LogActivity.kt:109-115) turns every entry, details included, into a PDF. A document link can carry anything — a token in a query string, a `mailto:` address, a `file:///` path — so content the app decided was unsafe to *open* is still safe to *store*.
**How to verify:** `grep -n "Link blocked" -A2 app/src/main/java/com/kavopdf/app/ViewerActivity.kt`. In a build: open a PDF whose link is `javascript:x?token=abc`, tap it, then open Log — the full URL is listed, and Export produces a PDF containing it.
**User impact:** a document the user only opened leaves its links, and whatever identifies them in a query string, in a log that is later exported and sent to someone while reporting a problem — the one path by which anything from this app leaves the device.

STATUS: FIXED - the entry records the scheme alone (`scheme ?: "no scheme"`); the URL taken from the document is no longer written to the log, so the entry still says a link was refused and of which kind, and nothing that identifies the document or its links survives to the export. ViewerActivity.kt:419-425.

---

## Stage 6 — SECURITY (second half)

Scope: every permission the manifest declares set against the code that uses it, every
dangerous API and whether its runtime permission is requested first, the storage model,
and the deletion paths the app offers the user.

What passed (recorded so it is not re-checked): one permission only — `CAMERA` — and it is
requested at runtime in both screens that use it (QrScanActivity.kt:77-79,
ScanToPdfActivity.kt:61-63), never at install; `android.hardware.camera.any` is
`required="false"`; `INTERNET` and `ACCESS_NETWORK_STATE` are removed from the merged
manifest and no networking API exists in the source (no `URLConnection`, `OkHttp`,
`WebView`, `Socket`); `allowBackup="false"`; no `WRITE_EXTERNAL_STORAGE`, no `MediaStore`,
no `Environment`, no `getExternalFilesDir` — every read goes through
`ACTION_OPEN_DOCUMENT`/`GetContent` and every write through `ACTION_CREATE_DOCUMENT`, so no
storage permission is needed or asked for; the FileProvider is the only way a file leaves
the app and it grants read-only; the activity log is capped at 512 KB and its Clear button
deletes the file; `fillForm` flattens the form it just wrote (removes `/Annots` from every
page and `/AcroForm` from the catalog, PdfEngine.java:1212-1222), so a form filled inside
KavoPDF carries no hidden field values.

### P2 — Deleting a page from a scan throws away the list entry, not the picture
**File:** app/src/main/java/com/kavopdf/app/ScanToPdfActivity.kt:143
**What:** The × on a captured page runs `pages.removeAt(index); refresh()` and nothing else, so the JPEG that page was written to stays in `cacheDir/work`, and because `onDestroy` only deletes the files still in `pages`, the deleted picture is never removed by this screen at all.
**Why I think so:** `shoot()` writes each capture to `File(Files.workDir(this), "scan_" + System.currentTimeMillis() + ".jpg")` (line 91) and `pages` is the only list holding them. The delete handler (143) mutates the list; the activity contains no `file.delete()` and no `CacheSweep.deleteNow` call. `onDestroy` (163-170) iterates `pages`, and a page removed at 143 is no longer in it. The only other cleanup is the sweep, which removes an entry once `CachePolicy.isStale` says it is past 45 minutes (CachePolicy.java:22) and only runs when the app starts or a screen closes.
**How to verify:** `grep -n "removeAt\|delete()" app/src/main/java/com/kavopdf/app/ScanToPdfActivity.kt` — one `removeAt` at 143 and one delete loop at 168 over `pages`. In a build: scan three pages, delete the middle one, tap Build PDF, then `adb shell run-as com.kavopdf.app ls -l cache/work` — the deleted page's `scan_*.jpg` is still there.
**User impact:** a page the user took and then removed — usually the one with something on it they decided not to keep — is still sitting in the app's storage as a full-resolution photo for the next 45 minutes.

### P2 — Denying the camera permission leaves the scan screen with no way forward
**File:** app/src/main/java/com/kavopdf/app/ScanToPdfActivity.kt:61
**What:** When the camera permission is denied both camera screens only show a toast (`msg_camera_needed`); there is no rationale, no "open settings" button and no second request, so Scan-to-PDF — which has no other input — is a dead preview for the rest of its life, and after a second denial the system will not show the dialog again.
**Why I think so:** the request result is `if (granted) startCamera() else toast(getString(R.string.msg_camera_needed))` (ScanToPdfActivity.kt:43-46, the same at QrScanActivity.kt:47-49). `shouldShowRequestPermissionRationale` and `ACTION_APPLICATION_DETAILS_SETTINGS` appear nowhere in the source, and the only request is the one fired from `onCreate` (61-63), so re-entering the screen after "Don't allow" asks nothing and says nothing new. `shoot()` begins `val ic = capture ?: return` (line 87) — with no camera bound, tapping Capture does nothing at all, not even a toast.
**How to verify:** `grep -rn "shouldShowRequestPermissionRationale\|ACTION_APPLICATION_DETAILS_SETTINGS" app/src/main/java` — no hits. In a build: deny the camera prompt twice, then tap Capture — the button is enabled and silently does nothing; the only recovery is Settings ▸ Apps ▸ KavoPDF ▸ Permissions, which the app never points at.
**User impact:** a user who taps "Don't allow" once — a normal reflex — is left on a black rectangle with a Capture button that does nothing and no sentence telling them how to fix it. The QR screen survives the same denial only because it also has a gallery button; Scan-to-PDF has no second way in.

### P2 — Redaction removes the page but leaves the same words in the bookmarks and the form
**File:** app/src/main/java/com/kavopdf/app/engine/PdfEngine.java:2960
**What:** `applyRedaction()` replaces the page's content stream, resources and annotations, but nothing on the redaction path touches the catalog's `/Outlines`, `/AcroForm` or `/Names/EmbeddedFiles`, so text the document also carries at document level — bookmark titles, filled form values, attached files — is still in the redacted output.
**Why I think so:** `applyRedaction` (2960-2986) changes five things on the *page* and nothing on the catalog; `redactPages` (2896-2921) and `redactPagesLazy` (2934-2958) then call only `clearDocumentMetadata(d)` and `d.save(out)`. The same file writes bookmark titles into the catalog (`setBookmarks`, 2564-2585, `getDocumentCatalog().setDocumentOutline`) and field values with `f.setValue(v)` (1330). PDFBox 2.0.27's writer walks reachability from the trailer's `/Root` and `/Info` (`COSWriter.write` → `addObjectToWrite(root)`, pdfbox-2.0.27 sources, COSWriter.java:470-496), so every object still hanging off the catalog is serialised into the redacted file. Nothing detaches them.
**How to verify:** `grep -n "ACRO_FORM\|setDocumentOutline\|EMBEDDED" app/src/main/java/com/kavopdf/app/engine/PdfEngine.java` — the only removal is at 1218 (the form-fill path); the redaction block at 2896-2986 has none. In a build: bookmark a page with the title "Aadhaar 1234 5678", redact that page, save, then `strings out.pdf | grep Aadhaar` (or `mutool show out.pdf trailer/Root/Outlines`) — the title is still there while the page itself is a flat image.
**User impact:** the tool promises the characters are deleted from the file, not covered with a black box (README:181). For a document that also names the same thing in a bookmark, a form field or an attachment, that promise is false in exactly the way that matters: whoever receives the file can still read the words the user believed they had destroyed.

### P2 — Nothing stops the open document from appearing in the recents thumbnail or a screenshot
**File:** app/src/main/java/com/kavopdf/app/ViewerActivity.kt:47
**What:** No screen sets `FLAG_SECURE`, so the page being read is captured into the system recents thumbnail — visible to whoever picks the phone up after the app is backgrounded — and any screenshot or screen recorder can capture it.
**Why I think so:** `grep -rn "FLAG_SECURE" app/src/main/java` returns no hits and there is no `window.setFlags` or `WindowManager.LayoutParams` call anywhere in the source; `ViewerActivity.onCreate` (47-60) inflates the binding and sets the content view without touching the window, and neither does `PdfActivity.onCreate` (162-175) that every other screen inherits.
**How to verify:** `grep -rn "FLAG_SECURE" app/src/main/java` — no hits. In a build: open a bank statement, press Recents — the thumbnail is the statement page; or take a screenshot with the reader open — it succeeds.
**User impact:** the app's premise is that a document stays private on the device, but a picture of the last page read stays in the system's recents list after the app is closed, and it can be photographed from the screen by anything the user has allowed to capture it.

### P3 — Merge and four other screens leave full copies of the user's documents in the cache
**File:** app/src/main/java/com/kavopdf/app/MergeActivity.kt:67
**What:** `doMerge` copies every input with `Files.copyToCache` inside the producer and never registers the copies with `trackCacheFile`, so they outlive the screen; the same untracked pattern is at LinksActivity.kt:440, BookmarksActivity.kt:61, ImageOcrActivity.kt:83 and ImagesToPdfActivity.kt:76.
**Why I think so:** `PdfActivity.onDestroy` (358-366) deletes `sessionFiles` minus `keptFiles`, and `sessionFiles` is filled only by `trackCacheFile` (340-343). The screens that do track are PdfActivity.kt:108 and :224, ToolsActivity.kt:197 and AnnotateActivity.kt:77; none of the five above is among them, so nothing on those screens ever deletes what it copied — only `CachePolicy`'s 45-minute age rule does, and only when the sweep next runs (app start, KavoPdfApp.kt:20, or a screen closing, PdfActivity.kt:366).
**How to verify:** `grep -rn "copyToCache" app/src/main/java` and check each hit against `trackCacheFile` — the five listed have no tracking. In a build: merge two large PDFs, close the screen, `adb shell run-as com.kavopdf.app ls -l cache/work` — both copies are still there.
**User impact:** the cache comment says "a screen deletes the files it made when it closes" (CacheSweep.kt:16-18), and on these five screens it does not: the user's documents sit in the cache for another 45 minutes, so merging a handful of big files leaves their combined size behind after the merge is finished.
