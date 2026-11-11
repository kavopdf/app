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
**Why I think so:** `fFormat` is declared at line 92 and appears exactly three times in the whole source: the declaration, `fFormat = null` at line 335, and the read at line 695. It is never assigned an `EditText`, so `fFormat?.text` is always null and the elvis at 695 always yields "Page {n} of {total}". The `Action.PAGENUM` branch (430–443) adds `fPagenumPlace`, `fPagenumColour`, `fFont`, `fPagenumOpacity` and stops. There is no `hint_format`-style string in `strings.xml` either, so the field was never wired.
**How to verify:** `grep -n "fFormat" app/src/main/java/com/kavopdf/app/ToolsActivity.kt` — three hits, no assignment from `addField`. Or open the Page numbers screen: the only fields are position, colour, size, opacity.
**User impact:** The user can never choose the numbering text — no "1", no "- 3 -", no "Page 3", no roman numerals. Every document gets "Page 1 of N" whether they want it or not, and line 695's format handling is unreachable code.

STATUS: FIXED - the `Action.PAGENUM` branch now creates `fFormat` via `addField(getString(R.string.hint_pagenum_format), …, "Page {n} of {total}")`, so the read at the run branch gets real user input; string added at `strings.xml:341`; verified at ToolsActivity.kt:444 (field) and :702 (read).

### P3 — "Image to searchable PDF" has no icon of its own; it reuses the Images-to-PDF icon
**File:** app/src/main/java/com/kavopdf/app/MainActivity.kt:188
**What:** `Action.IMAGE_OCR` is built with `R.drawable.ic_image_pdf`, the same drawable as `Action.IMAGES_PDF` at line 155; there is no dedicated icon for it.
**Why I think so:** Counting the drawables across the 28 `ToolItem` rows gives 27 distinct values — `ic_image_pdf` is the only one used twice. `ic_ocr` exists and is used by `Action.OCR`, and `ic_image_pdf` is otherwise the Images-to-PDF mark, so one of the two rows is borrowing the other's icon.
**How to verify:** Read the two `ToolItem` lines 155 and 188 side by side, or grep `R.drawable.ic_image_pdf` in `MainActivity.kt`.
**User impact:** Two different tools sit on the home screen with the same picture, so a glance at the grid cannot tell "Images to PDF" from "Image to searchable PDF".

STATUS: FIXED - `Action.IMAGE_OCR` now uses its own `R.drawable.ic_image_search` (`drawable/ic_image_search.xml` exists), leaving `ic_image_pdf` to Images-to-PDF alone; MainActivity.kt:188.

### P3 — Hyperlinks screen saves under two different suffixes
**File:** app/src/main/java/com/kavopdf/app/LinksActivity.kt:548
**What:** Three save paths in the same activity use "_links" (lines 381, 398, 409) and the image-link path uses "_linked" (line 548), so one tool produces two naming schemes.
**Why I think so:** All four calls are `Files.suggestName(sourceName, ...)` in `LinksActivity` for the same output type (a PDF with links added). `_links` appears three times and `_linked` once, in `applyImageLink()`.
**How to verify:** `grep -n "_linked\?" app/src/main/java/com/kavopdf/app/LinksActivity.kt` — three `_links`, one `_linked`.
**User impact:** A link added from a picture is named `report_linked.pdf` while the same operation from text gives `report_links.pdf`; users get a folder of near-duplicate names that look like different operations.

STATUS: FIXED - the image-link path now saves under "_links" like the other three, so all four `Files.suggestName` calls in the activity agree; LinksActivity.kt:381, 398, 409 and 548.

### P3 — Section heading "Security & output" now heads only security tools
**File:** app/src/main/res/values/strings.xml:8
**What:** `section_security` still reads "Security & output", but the group it heads (`MainActivity.kt:173-179`) contains only sign, verify, protect, unlock, watermark and redact; the actual output tools were moved to a separate `section_output` group at line 181.
**Why I think so:** `MainActivity.buildRows()` closes the `section_security` group before adding `HomeRow.Header(R.string.section_output)`, which is "Output & tools". Two headings both claiming output, and one group whose label does not describe its contents.
**How to verify:** Compare `strings.xml:8` with the rows under `MainActivity.kt:173` and the next header at line 181.
**User impact:** A section labelled "output" contains no output tool, which reads as a missing feature rather than a stale label.

STATUS: FIXED - `section_security` now reads "Security", matching the sign/verify/protect/unlock/watermark/redact rows it heads; the output group keeps its own `section_output` heading; strings.xml:9.

### P3 — Metadata labels and the output-folder hint bypass `strings.xml`
**File:** app/src/main/java/com/kavopdf/app/ToolsActivity.kt:425
**What:** Four visible labels in the metadata editor — "Creator (application)", "Producer", "Creation date (yyyy-MM-dd HH:mm)", "Modified date (yyyy-MM-dd HH:mm)" — and the output-folder line at line 219 ("Output folder: ") are hardcoded English instead of string resources.
**Why I think so:** Lines 425–428 pass bare literals to `addField(...)` where every sibling field uses `getString(R.string.hint_*)`, and line 219 concatenates "Output folder: " directly. Nothing in `strings.xml` holds these texts, so they are also untranslatable and un-reusable.
**How to verify:** Read `ToolsActivity.kt:420-429` and `:219`; grep `strings.xml` for "Creator", "Producer", "Output folder" — no match.
**User impact:** Nothing breaks on an English device, but these five labels never follow a language change or a copy edit, unlike the rest of the screen.

STATUS: FIXED - all five moved to string resources (`hint_creator`, `hint_producer`, `hint_creation_date`, `hint_modified_date`, `output_folder_prefix` at strings.xml:342-346) and referenced via `getString`; ToolsActivity.kt:425-428 (fields) and :219 (output folder line).

---

## Stage 2 — WIRING (second half)

Scope: launchers, intent filters, the `EXTRA_SOURCE_URI` hand-off, manifest
activities declared vs. started, and the seven places for the newest tools.

What passed (recorded so it is not re-checked): 19 activity classes exist and all
19 are declared; every `Intent(this, X::class.java)` target in the source
(`MainActivity`, `ViewerActivity`, `ShareChoiceActivity`, `PagesActivity`,
`MergeActivity`, `ImagesToPdfActivity`, `AnnotateActivity`, `FormsActivity`,
`ToolsActivity`, `QrScanActivity`, `ScanToPdfActivity`, `BookmarksActivity`,
`LogActivity`, `RedactActivity`, `LinksActivity`, `ImageOcrActivity`,
`OcrActivity`, `CropActivity`, `CreatePdfActivity`) is declared, and no declared
activity is unreachable — `PdfActivity` is abstract and correctly absent. All five
launchers registered in `PdfActivity` (`openPdfLauncher`, `openPdfsLauncher`,
`openImagesLauncher`, `openTreeLauncher`, `createDocLauncher`) and both save
launchers (`createDocxLauncher`, `createTxtLauncher`) are actually launched. Every
`Action` routed to `ToolsActivity` by the `else` branch has a `applyToolChrome()`
heading and an `onRun()` branch. All fifteen `tools/check-*.py` guards pass on
this commit (`check-tool-titles`, `check-pdf2word`, `check-repair`,
`check-link-schemes`, `check-layouts`, `check-file-names`, `check-quality-paths`,
`check-main-thread`, `check-preview-paths`, `check-render-quality`,
`check-cache-sweep`, `check-detectors`, `check-background-work`,
`check-bitmap-config`, `check-apk-config`).

### P1 — "Fill in Annotate" hands over a cache file that the sending screen deletes on its way out
STATUS: FIXED - `PdfActivity.keepCacheFile()` (PdfActivity.kt:353) takes a tracked copy out of the delete-on-close set; FormsActivity keeps the file before it hands it over (FormsActivity.kt:65) and Annotate now tracks it as its own (AnnotateActivity.kt:70), so the last screen to close removes it.
**File:** app/src/main/java/com/kavopdf/app/FormsActivity.kt:62
**What:** When a form has no AcroForm fields, the screen offers "Fill in Annotate" and passes `source.absolutePath` to `AnnotateActivity` — but `source` is a cache copy that `FormsActivity.finish()` deletes immediately afterwards, so the screen it just opened may find the file already gone.
**Why I think so:** `FormsActivity.kt:91` sets `source = f`, where `f` came from `openPdf()`; `PdfActivity.kt:201` wraps that copy in `trackCacheFile(...)`, which adds it to `sessionFiles` (`PdfActivity.kt:318`). The hand-off puts `here.absolutePath` in the intent (`FormsActivity.kt:62`) and the very next statement is `finish()` (`FormsActivity.kt:67`). `PdfActivity.onDestroy()` then runs `CacheSweep.deleteNow(sessionFiles - keptFiles)` (`PdfActivity.kt:322-325`), and `CacheSweep.deleteNow` calls `f.delete()` on every entry (`util/CacheSweep.kt:66-69`). Nothing on this path adds the file to `keptFiles` — that set is only filled by the Open/Share buttons (`PdfActivity.kt:277`, `:284`). On the receiving side, `AnnotateActivity.kt:65` guards with `File(direct).exists()` and `AnnotateActivity.kt:339` opens the file with `ParcelFileDescriptor.open(f, MODE_READ_ONLY)` inside a background `runTask`, i.e. after a dispatcher hop — so whether the fd is opened before or after the sender's `onDestroy` is a race, and losing it means `FileNotFoundException` and "this file couldn't be read".
**How to verify:** Read `FormsActivity.kt:56-68` next to `PdfActivity.kt:318-325`. Or, in a build, open any XFA form (an Indian bank or government form), tap "Fill in Annotate", and watch `adb logcat` for the `Annotate` open failing; the file under `cacheDir/work` is removed the moment Forms closes.
**User impact:** The one route offered for XFA and field-less forms — the forms the app explicitly calls out as the common Indian case — either opens Annotate on an empty screen with a file picker, or shows "this file couldn't be read", depending on which thread wins.

### P2 — Seven tool screens open the file picker on top of the PDF the share sheet already delivered
STATUS: FIXED - the picker is now behind `incomingUri == null` on all seven (PagesActivity.kt:54, CropActivity.kt:48, FormsActivity.kt:38, BookmarksActivity.kt:50, RedactActivity.kt:65, OcrActivity.kt:55, LinksActivity.kt:76) and in AnnotateActivity.kt:150, matching ToolsActivity's existing guard. The two image screens were left alone: they never consume a shared PDF, so suppressing their picker would have left them empty.
**File:** app/src/main/java/com/kavopdf/app/PagesActivity.kt:51
**What:** `PagesActivity`, `CropActivity`, `FormsActivity`, `BookmarksActivity`, `RedactActivity`, `OcrActivity` and `LinksActivity` call `pickAfterEnter { pickPdf() }` unconditionally, so when they are opened with a shared PDF they both load that PDF and throw the system picker at the user.
**Why I think so:** `PdfActivity.onCreate` posts `onPdfChosen(uri)` for the `EXTRA_SOURCE_URI` extra (`PdfActivity.kt:172-174`), and `MainActivity.dispatch()` attaches that extra to every tool intent whenever a file was shared in (`MainActivity.kt:137-143`). `pickAfterEnter` launches the picker synchronously during `onCreate` (`PdfActivity.kt:421-427`), so the picker appears first and the shared document loads behind it. Two screens already guard against exactly this — `ToolsActivity.kt:131` (`if (incomingUri == null)`) and `AnnotateActivity.kt:146` (`if (direct == null)`), and `ViewerActivity.kt:56` chooses between the two — but the other seven do not, at `PagesActivity.kt:51`, `CropActivity.kt:45`, `FormsActivity.kt:35`, `BookmarksActivity.kt:47`, `RedactActivity.kt:62`, `OcrActivity.kt:52` and `LinksActivity.kt:73`.
**How to verify:** `grep -rn "pickAfterEnter" app/src/main/java/com/kavopdf/app/` — nine hits; only the three above are conditional. Or share a PDF into the app, tap "Tools", then "Rotate pages", and watch the file picker open over a document that is already loading.
**User impact:** The user is asked to choose a document they just chose, and if they pick a different one it silently replaces the file they shared.

### P3 — `onNewIntent` in MainActivity and ViewerActivity cannot run: no launchMode is declared and nothing sends `FLAG_ACTIVITY_SINGLE_TOP`
STATUS: FIXED - `android:launchMode="singleTop"` on both (AndroidManifest.xml:29 MainActivity, :40 ViewerActivity). MainActivity.onNewIntent now assigns `sharedUri` instead of only overwriting it (MainActivity.kt:105), so an intent that carries no file clears the earlier one and a tool tapped later cannot pick up a stale document.
**File:** app/src/main/AndroidManifest.xml:26
**What:** Both activities override `onNewIntent`, but neither declares `android:launchMode` (nor `singleTop`), and the only flag any caller adds is `FLAG_ACTIVITY_CLEAR_TOP`, so the override is unreachable and a second PDF opens a second reader instance instead.
**Why I think so:** `MainActivity.kt:100-107` and `ViewerActivity.kt:83-87` both override `onNewIntent`, which the framework only calls when the intent carries `FLAG_ACTIVITY_SINGLE_TOP` or the activity is `singleTop`/`singleTask`/`singleInstance`. The manifest entries for `.MainActivity` (`AndroidManifest.xml:25-33`) and `.ViewerActivity` (`:35-46`) set no `launchMode`. `grep -rn "SINGLE_TOP" app/src` returns nothing; `ShareChoiceActivity.kt:78` uses `FLAG_ACTIVITY_CLEAR_TOP`, which under the default `standard` mode finishes and recreates the activity — `onCreate` gets the extra, not `onNewIntent`.
**How to verify:** `grep -n "launchMode" app/src/main/AndroidManifest.xml` (no hit) and `grep -rn "onNewIntent\|SINGLE_TOP" app/src/main/java`. Then open two PDFs in a row from a file manager and press Back: two readers are stacked.
**User impact:** Opening a second document from a file manager leaves the first reader buried in the back stack, and the careful "a file shared in while the home screen is already running" comment at `MainActivity.kt:103-104` describes a path that never executes.

### P3 — ShareChoiceActivity reads `intent.data`, but it is only registered for ACTION_SEND, so that branch is dead
STATUS: FIXED - the unreachable `else -> intent.data` branch is gone; `sharedPdf()` reads `EXTRA_STREAM` only and says why in the doc comment (ShareChoiceActivity.kt:55).
**File:** app/src/main/java/com/kavopdf/app/ShareChoiceActivity.kt:52
**What:** `sharedPdf()` falls back to `intent.data` "from either the share or the open intent", but the VIEW filter belongs to `ViewerActivity`, so this activity never receives an open intent and the `else` branch can never be taken.
**Why I think so:** The manifest gives `ShareChoiceActivity` a single filter, `ACTION_SEND` with `application/pdf` (`AndroidManifest.xml:58-62`); the `ACTION_VIEW` filter with the same mime type is declared on `ViewerActivity` (`AndroidManifest.xml:41-45`). `ShareChoiceActivity.kt:50-53` still branches `when (intent.action) { Intent.ACTION_SEND -> …; else -> intent.data }`.
**How to verify:** Compare the two intent filters in the manifest with `ShareChoiceActivity.kt:47-55`. Or tap a PDF in a file manager: it goes straight to the reader and this dialog never appears.
**User impact:** Nothing breaks today, but the comment promises a shared/open parity the manifest does not provide — the "open" half of the dialog is unreachable, and the code that looks like it handles it cannot be tested.

### P3 — The share and open filters accept only PDFs, so a shared image never reaches the two image tools
STATUS: FIXED - `ImagesToPdfActivity` and `ImageOcrActivity` are exported ACTION_SEND targets for `image/*` (AndroidManifest.xml:71-79 and :118-127) and stage the shared photo instead of opening the picker (ImagesToPdfActivity.kt:38, ImageOcrActivity.kt:47), reading the stream through `PdfActivity.sharedStreamUri` (PdfActivity.kt:190).
**File:** app/src/main/AndroidManifest.xml:61
**What:** Both entry-point filters declare `application/pdf` and nothing else, so `ImagesToPdfActivity` and `ImageOcrActivity` — the only tools that consume images — cannot be reached from the gallery's share sheet or an "open with" on a photo.
**Why I think so:** The three `<data>` elements in the manifest are all `android:mimeType="application/pdf"` (`:44`, `:61`); there is no `image/*` filter anywhere. Both image screens read their input only through `openImagesLauncher` (`PdfActivity.kt:56-60`, launched by `ImagesToPdfActivity.kt:33`/`:36` and `ImageOcrActivity.kt:43`/`:45`), which is an in-app picker. `ShareChoiceActivity.sharedPdf()` would also reject a non-PDF, since it is registered for `application/pdf` only.
**How to verify:** `grep -n "mimeType" app/src/main/AndroidManifest.xml` — three hits, all `application/pdf`. Then try "Share → KavoPDF" on a photo: the app is not in the list.
**User impact:** A user who photographs a page and wants it turned into a searchable PDF must first open KavoPDF and hunt through the tool list; the share route they would naturally use is not offered.

---

## Stage 3 — CRASH PATHS

Scope: the app's own screens and views (`app/src/main/java/com/kavopdf/app/*.kt`,
`ui/*.kt`, `util/*.kt`) — null dereferences, `get()`/`first()` on possibly empty
lists, array indexing, number parsing, stream lifetime, bitmap and cursor handling,
`findViewById` and intent-extra null checks. The PDF engine (`engine/*.java`) is
stage 4 and was not read here except where a caller depends on its return shape.

What passed (recorded so it is not re-checked): no `!!` outside a `runCatching`
(one site, `LinksActivity.kt:518`, and it is inside the `runCatching` that guards
it); every number taken from a text field goes through `toIntOrNull` /
`toFloatOrNull` — there is no bare `Integer.parseInt` or `String.toInt()` on user
input anywhere in the Kotlin; every stream is opened inside `.use`
(`openInputStream`, `openOutputStream`, `FileInputStream`, `FileOutputStream` —
grep without `.use` returns only imports); every `uris.first()` / `files.first()` /
`pages[0]` / `items[pos]` site is preceded by an `isEmpty` or `indices` check
(`ImagesToPdfActivity.kt:73`, `MergeActivity.kt:64`, `OcrActivity.kt:82`,
`PagesActivity.kt:125`, `CreatePdfActivity.kt:265-266`, `AnnotateActivity.kt:190`+`:218`);
every id used with `findViewById` exists in its layout (`pwInput`, `busyText`,
`confirmTitle`/`confirmMessage`/`confirmNegative`/`confirmPositive`,
`successMsg`/`successIcon`/`successOpen`/`successShare`/`successClose`,
`statusIcon`/`statusTitle`/`statusSub`/`details`/`btnClose`); `view_spinner.xml`
really has a `<Spinner>` root, so the five `inflate(...) as Spinner` casts cannot
throw `ClassCastException`; `parseRanges`/`parsePages` (`ToolsActivity.kt:1095`,
`OcrActivity.kt:126`) use `getOrNull`/`toIntOrNull` and clamp to the page count, so a
range like `1-999999999` builds no huge list.

### P2 — Opening a second document in the reader leaks the first document's PdfRenderer and file descriptor
STATUS: FIXED - show() now closes the previous PageRenderer and ParcelFileDescriptor before assigning the new pair (and closes what it opened if the open fails), and the same close was added to RedactActivity.kt:87, OcrActivity.kt:69, CropActivity.kt:66, PagesActivity.kt:107 and AnnotateActivity.kt:319/:356. ViewerActivity.kt:101-118
**File:** app/src/main/java/com/kavopdf/app/ViewerActivity.kt:101
**What:** `show()` opens a new `ParcelFileDescriptor` and a new `PdfRenderer` for every document and assigns them over `pfd` and `renderer` without closing the previous pair, so each document opened in the same activity instance leaks one renderer and one descriptor.
**Why I think so:** `show()` does `pfd = descriptor` (line 102) and `renderer = pr` (line 105) with no `renderer?.close()` before either, and the only close is in `onDestroy()` (lines 435-436), which closes just the last pair. `onNewIntent` (line 83) reaches `openUri` → `show()` on the same instance because the manifest now sets `launchMode="singleTop"` (`AndroidManifest.xml:40`), so tapping PDF B in a file manager while A is open re-enters `show()` and drops A's renderer. The same shape appears in the five other screens that can open a second file from their own choose button: `RedactActivity.kt:86-90` (closes the old `pfd` but never the old `renderer`), `OcrActivity.kt:68-72`, `CropActivity.kt:62-65`, `PagesActivity.kt:103-106`, `AnnotateActivity.kt:308-312` and `:343-347`. In all six, `renderer?.close()` appears exactly once, in `onDestroy`.
**How to verify:** `grep -n "renderer = \|renderer?.close" app/src/main/java/com/kavopdf/app/ViewerActivity.kt` — one assignment at 105, one close at 435 inside `onDestroy`. In a build, open a PDF, then tap a second PDF in a file manager, and watch `adb shell ls /proc/<pid>/fd | wc -l` and `adb shell dumpsys meminfo <pkg>` grow by one descriptor and one renderer per document.
**User impact:** Each document opened in a session leaves a native renderer and an open descriptor behind. After enough documents the process runs out of descriptors and pages stop opening at all — "this file couldn't be read" on a file that is perfectly fine — while native memory climbs until the reader is killed in the background.

### P2 — A tap on a page whose size is unknown re-launches itself forever
STATUS: FIXED - onPageTap's retry is now bounded by a tapRetryCount (MAX_TAP_RETRIES = 2, ViewerActivity.kt:472), incremented before each background pass and reset when a document opens or a tap finally gets its data, so a document whose page sizes never resolve can no longer re-enter itself for as long as the screen is open. ViewerActivity.kt:333-340
**File:** app/src/main/java/com/kavopdf/app/ViewerActivity.kt:314
**What:** When the size of the tapped page is not known yet, `onPageTap` starts a coroutine that fetches the sizes and then calls `onPageTap` again with no attempt counter, so if the size never arrives it re-enters itself for as long as the screen is open.
**Why I think so:** lines 314-337: the retry branch sets `tapRetryPending = true` (316), launches (318), clears the flag in `finally` (332-334) and then calls `onPageTap(position, fx, fy)` (335). The re-entry sees the same `pw <= 0f` (312-314) with the flag already cleared, so it takes the retry branch again — there is no counter and no `return` after the recursive call. The size list is what can stay empty: `PdfEngine.pageDisplaySizes` (`engine/PdfEngine.java:269-279`) reads `p.getCropBox()` for every page and throws if any page has none, and the caller wraps the call as `runCatching { … }.getOrDefault(emptyList())` (`ViewerActivity.kt:321-323`), storing an empty list that is fetched again on every pass. `linksReady` meanwhile does become true, because `PdfEngine.allPageLinks` swallows its own exceptions and returns an empty map (`PdfEngine.java:2037-2050`), so only the size half of the condition keeps the loop alive.
**How to verify:** Read `ViewerActivity.kt:311-337` — no counter, no `return` after the recursive call. In a build, open a PDF that pdfbox rejects but `PdfRenderer` still draws (a repaired or hand-edited file), tap a page, and watch the activity log: one "Reader: page sizes" entry per pass, indefinitely.
**User impact:** On such a document one tap becomes a loop that re-parses the whole PDF on a background thread over and over until the user leaves the reader: the phone heats up, the battery drains, and the tap never does anything.

### P2 — Annotate writes the tap point into the instance state but never reads it back, so a photo chosen after a recreate is dropped
STATUS: FIXED - onCreate now reads pendingFx/pendingFy back with savedInstanceState.getFloat(key, -1f), the restore half that onSaveInstanceState was missing. AnnotateActivity.kt:63-69
**File:** app/src/main/java/com/kavopdf/app/AnnotateActivity.kt:157
**What:** `onSaveInstanceState` stores `pendingFx`/`pendingFy` so the "tap where the picture goes" survives the image picker, but `onCreate` never reads either key, so after a recreate the point is gone and the chosen photo is discarded without a word.
**Why I think so:** `pendingFx`/`pendingFy` appear in exactly five places — declared at 55-56, assigned in `startStamp` at 502-503, written to the bundle at 157-158, and read as a fallback in `onImagesChosen` at 538. There is no `savedInstanceState?.getFloat(…)` anywhere in the file, and `onCreate` takes `savedInstanceState` at 58-59 and does not touch it. The comment at 154-156 says "The image picker can have the system recreate us; without this the tap point was lost" — the restore half of that fix is missing. `onImagesChosen` then takes the `point == null` branch at 540 and returns without placing anything.
**How to verify:** `grep -n "pendingFx\|savedInstanceState" app/src/main/java/com/kavopdf/app/AnnotateActivity.kt` — no `getFloat`. In a build, enable Developer options → "Don't keep activities", open a PDF, choose the Image tool, tap the page, pick a photo and come back: no picture is placed and nothing is said.
**User impact:** On a low-memory phone — exactly the case the comment was written for — the image tool silently loses the picture the user just chose, and the only way forward is to tap and pick again.

### P2 — The gallery QR scan decodes the photo at full resolution, so ordinary phone photos fail with "could not read image"
STATUS: FIXED - the gallery pick now goes through a decodeBounded(uri, GALLERY_MAX_DIM = 1600) helper (inJustDecodeBounds + inSampleSize), and the bitmap is recycled in addOnCompleteListener and on the scanner-null path. QrScanActivity.kt:106-150 (helper :130, cap :238)
**File:** app/src/main/java/com/kavopdf/app/QrScanActivity.kt:106
**What:** `pickImageLauncher` decodes the chosen picture with a bare `BitmapFactory.decodeStream`, with no `inJustDecodeBounds`/`inSampleSize` pass, unlike every other image path in the app.
**Why I think so:** lines 106-110 open the stream and decode it whole; there is no bounds pass. Every other decode is bounded — `AnnotateActivity.decodeBounded` (`AnnotateActivity.kt:548-566`), `CreatePdfActivity.decodeBounded` (`CreatePdfActivity.kt:296-313`), `PdfEngine.decodeImage(file, OCR_MAX)` (`ImageOcrActivity.kt:86`), `PdfEngine.decodeUpright(file, 400)` (`ScanToPdfActivity.kt:135`). A 48 MP photo (8000×6000) is 192 MB as ARGB_8888, and because the decode is wrapped in `runCatching`, the `OutOfMemoryError` is swallowed and the user is shown `msg_failed` instead of a scan. The bitmap is also never recycled after `scanner.process(...)` (line 120).
**How to verify:** Read `QrScanActivity.kt:103-126` next to `AnnotateActivity.kt:548-566`. In a build, put a QR code in a full-resolution photo from a recent phone and use QR → from gallery: the app says it could not read the image, while the same photo shrunk in a gallery editor scans.
**User impact:** The one way to scan a code you cannot point the camera at — a screenshot, a photo of a poster, an image someone sent — fails on the photos people actually have, and reports only that the image could not be read.

### P3 — Applying a shaped image link decodes the picture whole and recycles neither bitmap
STATUS: FIXED - shaped() decodes through decodeBounded(pic, SHAPE_MAX_DIM = 1600) and recycles both src and outBmp in a finally block. LinksActivity.kt:561-604 (helper :593, cap :83)
**File:** app/src/main/java/com/kavopdf/app/LinksActivity.kt:563
**What:** `shaped()` decodes the source image at full size, allocates a second full-size square bitmap for the mask, and recycles neither `src` nor `outBmp`.
**Why I think so:** line 563 is `BitmapFactory.decodeFile(pic.absolutePath)` with no bounds pass; line 565 allocates `side × side` ARGB_8888 where `side` is the image's short edge; and after the PNG is written at 578 the function returns at 579 with both bitmaps still allocated. Every other place that builds a bitmap from a picture recycles it (`AnnotateActivity.kt:592`, `CreatePdfActivity.kt:344`, `OcrActivity.kt:109`, `RedactActivity.kt:195`). A 4000×3000 photo therefore holds 48 MB for `src` and 36 MB for `outBmp` at the same moment, on top of the page bitmap the screen is already showing.
**How to verify:** `grep -n "recycle" app/src/main/java/com/kavopdf/app/LinksActivity.kt` — no hit inside `shaped()` (561-580). In a build, add an image link from a large photo with the Circle or Rounded shape and watch the heap: both bitmaps stay until a GC.
**User impact:** Adding a circle or rounded image link from a full-size photo can push a mid-range phone into an `OutOfMemoryError`, and the failure surfaces from the surrounding task as "this file couldn't be read" — nothing about the picture, which is what actually went wrong.

---

## Stage 4 — CRASH PATHS (PDF engine)

Scope: `app/src/main/java/com/kavopdf/app/engine/*.java` — glyph and text arrays,
font and resource lookups, page-tree walks, and every place a malformed PDF could
reach an unchecked index or an unclosed stream.

What passed (recorded so it is not re-checked): every byte scan is bounded
(`indexOf`/`lastIndexOf` loop to `hay.length - needle.length`, `countEndobj` keeps a
5-byte carry so a split match is found once and never twice); every
`Integer.parseInt`/`Long.parseLong` on file bytes sits in a `try` with a `break`,
`continue` or `return -1` (`PdfRepair.java:854, 879, 952, 1202, 1302, 1342, 1370,
1412, 1818, 1962, 1994`); the object-stream and xref rebuilds clamp both ends to
`data.length` and skip `end <= start`; `dedupeNode` carries a `seen` set, so its
recursion terminates on a cyclic page tree, and `countLeaves` is only ever reached on
the de-duplicated (acyclic) copy; every file, zip and random-access stream in the
engine is opened in try-with-resources (`grep` for `new FileInputStream` /
`new FileOutputStream` / `new RandomAccessFile` returns only `try (...)` sites);
`PdfSigner.verify` validates `/ByteRange` length, sign and bounds before use
(`PdfSigner.java:133-139`); `DocxWriter.esc` strips XML-illegal control characters
(`:1788-1792`); `PdfToWord`'s content-stream tokenizer bounds every `charAt` and
`substring` (`skipString`/`skipDict`/`skipArray`/`skipInlineImage` all return
`<= length`, and `num(ops, -k)` returns 0 for a short operand list); the
`get(0)` / `get(i - 1)` / `get(i + 1)` sites I read in `PdfToWord` are each preceded
by an `isEmpty()`/size check or live in a loop bounded by `size() - 1`
(`:337, :890, :921, :1236, :2494, :2648, :2950, :4357, :4418, :5593`);
`cellsToTables` cannot spin, because a pass that adds no cell flushes the group
(`:4503-4508`); all `(COSDictionary)`/`(COSArray)`/`(COSString)` casts are
`instanceof`-guarded or inside `catch (Throwable)`.

### P1 — Crop on a page whose /Rotate is 180 crops the vertically mirrored region
**File:** app/src/main/java/com/kavopdf/app/engine/PdfEngine.java:221
**What:** `cropPages()` converts the rectangle the user drew from display coordinates to page coordinates with `py = h - yd` for a 180° page, while the three other display→page mappings in the same class use `py = yd` for 180, so on those pages the crop lands on the mirror image of the band the user selected.
**Why I think so:** the four cases in `cropPages` (216-222) are identical to `displayBoxToPage` (2108-2120) except at 180: `cropPages` has `px = w - xd; py = h - yd` (221), `displayBoxToPage` has `px = w - c[0]; py = c[1]` (2114), `addTextLayer` has `px = w - xd; py = yd` (1424) and the text-link writer uses `py = baseY` (2428). For 90 and 270 all four agree, so the frame convention is settled and only 180 disagrees. The algebra settles which one is right: display = rotate(flipY(page)); for r = 180 that gives `xd = w - px` and `yd = h - (h - py) = py`, so `py = yd`. The comment at 218-220 records that both axes were flipped to fix an earlier mirroring bug, which over-corrected the y axis.
**How to verify:** read `PdfEngine.java:216-222` next to `:2108-2120`. In a build: open a two-column page, rotate it 180° in the app, crop the top half, and look at the result — the bottom half is kept.
**User impact:** on any page whose /Rotate is 180 (an upside-down scan, or a page the user rotated twice), Crop keeps the wrong half of the page; the file is written without an error, so the user only finds out by opening the output.

**STATUS: FIXED** - `cropPages` now maps a 180 degree page as `px = w - xd; py = yd`, matching `displayBoxToPage`, `addTextLayer` and the text-link writer; the y axis was being flipped twice. Checked against a rendered 180 degree page: the page-space band that displays at the top-left is x 200-300, y 0-100, and cropping the displayed top-left 100x100 now returns exactly that band (fully black), not the blank mirror. PdfEngine.java:224.

### P2 — The text index assumes one glyph is one character, so a ligature or a surrogate pair shifts every later highlight and makes `wordsOnPage` read past its arrays
**File:** app/src/main/java/com/kavopdf/app/engine/PdfEngine.java:1841
**What:** `indexText` sizes `gx/gy/gw/gh/pageOf` from `pt.chars.size()` (one entry per TextPosition) but builds `TextIndex.text` by appending those same entries, and `TextPosition.getUnicode()` may be several characters long, so from the first ligature ("fi", "ffl") or surrogate pair on, every offset into `text` is larger than the glyph index it is used as.
**Why I think so:** `PositionedText.writeString` (1723-1732) adds one list entry per TextPosition (`chars.add(u)` at 1727), `indexText` takes `int n = pt.chars.size()` and allocates `new float[n]` for each array (1841-1842) plus `int[] pageOf = new int[n]`, then builds `StringBuilder b` by appending the same entries (1845-1846), so `b.length() >= n` with equality only when every unicode string is exactly one char. `wordsOnPage` loops `i <= idx.text.length()` and evaluates `idx.gw[i]` (1916) — for `i >= n` that is an `ArrayIndexOutOfBoundsException`. `searchIndex` (1885-1905) finds the match in `hay` (a copy of `text`, and a second length-changing copy when `matchCase` is false, e.g. 'İ'.toLowerCase()) and passes those offsets to `indexBox` (1866) and `pageOf[k]` (1895), which index the per-glyph arrays — so the highlight box is computed from the wrong glyph.
**How to verify:** `grep -n "float\[\] gx = new float\[n\]" app/src/main/java/com/kavopdf/app/engine/PdfEngine.java` (one hit, 1842) and read 1841-1858 against 1723-1732. In a build: open a LaTeX- or InDesign-set PDF, search a word that appears after the first ligature on the page — the highlight sits one glyph to the left for each ligature before it.
**User impact:** in the reader, search results are highlighted on the wrong word in any document with typographic ligatures or emoji, and the tap-to-copy word extractor would throw instead of returning words if it were called.

**STATUS: FIXED** - `indexText` now allocates `gx/gy/gw/gh/pageOf` and builds `text` per CHARACTER: every char of a multi-char `getUnicode()` gets its share of the glyph's advance, and the word-break marker keeps its index in the same arrays. Checked on a PDF whose ToUnicode maps one glyph to "fi": text.length() == gx.length (4 == 4), `searchIndex("Z")` now finds the hit the misaligned index dropped, and `wordsOnPage` returns "fiZ" instead of reading past the arrays. PdfEngine.java:1844.

### P2 — The repair page loop opens a content stream per page and never closes three of them
**File:** app/src/main/java/com/kavopdf/app/engine/PdfRepair.java:2235
**What:** Three sites in the per-page inspection loop take `page.getContents()` and never close it — the `contentMissing` probe at 2235, `drawsBrokenResource` at 2400 and `unbalancedContent` at 2487 — and the loop runs over every page of every document the repair path inspects.
**Why I think so:** the sibling call in `paintsSomething` does close its stream (`in.close()` at 2306); these three do not, and none is inside try-with-resources. `drawsBrokenResource` reads the stream to a byte array and drops it (2399-2406), `unbalancedContent` does the same (2487-2491), and the probe at 2235 evaluates `page.getContents() == null`, which creates and discards a stream whenever /Contents is present. All three are called from the loop at 2223-2253, once per page.
**How to verify:** `grep -n "page.getContents()" app/src/main/java/com/kavopdf/app/engine/PdfRepair.java` — five hits; only 2302 is followed by a close. In a build, run the repair path over a 300-page file and watch the open descriptor count and heap with `adb shell dumpsys meminfo <pkg>`.
**User impact:** a long damaged file leaves hundreds of streams open in the middle of the operation that already has the most memory pressure, which is where an out-of-memory kill is most likely to lose the work.

**STATUS: FIXED** - the `contentMissing` probe now closes the stream it creates, and `drawsBrokenResource` and `unbalancedContent` close theirs in a `finally`. All four `page.getContents()` sites in this file are now closed; only the one in `paintsSomething` already was. PdfRepair.java:2231, :2405, :2496.

### P3 — The saved reject streak is never read back, so the adaptive timing norm restarts on every launch
**File:** app/src/main/java/com/kavopdf/app/engine/NormStore.java:186
**What:** `fromText` splits each line at the first '=' and then tests `k.startsWith("rej=")`, but a streak line is written as `rej=<key>:<n>`, so the first '=' is the one after "rej" and `k` is always `"rej"` — the branch can never be taken and every streak is dropped when the store is loaded.
**Why I think so:** `toText` writes `"rej=" + key + ':' + value` (170-172). In `fromText`, `int eq = line.indexOf('=')` (186) is 3 for such a line and `String k = line.substring(0, eq)` (188) is `"rej"`; the test at 189 needs `"rej="`. The line then falls into the data branch, where `line.substring(eq + 1)` is `<key>:<n>` and `Long.parseLong` fails, so it is discarded silently (203-208).
**How to verify:** reason over one line, or run it on a JVM: `"rej=ocr|2-5|M:2".indexOf('=')` is 3, so `k` is `"rej"`. Then `grep -n "rej=" app/src/main/java/com/kavopdf/app/engine/NormStore.java` — two hits, writer at 170 and the unreachable test at 189.
**User impact:** the "three slow runs in a row and the stale norm is thrown away" rule only works inside one session; after the app is closed and reopened, a device that has genuinely become slower needs three more slow runs before it stops being measured against a norm it can no longer meet.

**STATUS: FIXED** - `fromText` tests `line.startsWith("rej=")` before splitting on '=', so the streak branch is reachable and `body` is the `<key>:<n>` part. TestNorms: 13 passed, 0 failed. NormStore.java:190.

### P3 — `attached` in `adoptOrphanContent` is always zero, and the repair log reports the page count as the number of streams attached
**File:** app/src/main/java/com/kavopdf/app/engine/PdfRepair.java:1783
**What:** `int attached = pages - empty.size() - (pages - empty.size());` subtracts the same expression from itself, so it is always 0 and the `if (attached >= 0)` guard under it can never fail; the message it then writes counts every page that now has content, not the streams this function attached.
**Why I think so:** 1783 is the only assignment of `attached` and 1784 is its only read. The text added at 1791-1792 is `"attached " + (pages - empty.size()) + " orphaned content stream(s)"`, and `empty` has had every adopted page removed from it, so `pages - empty.size()` is the number of pages with content after adoption — the intended number is that value minus the pages that already had content.
**How to verify:** read 1783-1793. In a build, repair a 5-page file that has one orphaned stream: the report says five streams were attached.
**User impact:** the repair summary shown to the user overstates what was repaired, so a partial recovery reads as a complete one.

**STATUS: FIXED** - the count is now `emptyBefore - empty.size()`, the pages this function actually gave a stream to, and the message uses it; the `attached >= 0` guard that could never fail is now `attached > 0`. TestRepair (188 passed) and TestRepairFixtures (1258 passed). PdfRepair.java:1730, :1788.

---

## Stage 5 — SECURITY

Scope: every exported component and whether it needs a permission; hardcoded keys,
passwords and tokens; file paths built from input; the FileProvider configuration;
WebView settings; `android:allowBackup`; and every place the app writes something
into a log or into a file that outlives the screen.

What passed (recorded so it is not re-checked): no WebView anywhere in the source,
so there is no `setJavaScriptEnabled`, no `addJavascriptInterface` and no
file-access setting to get wrong. No hardcoded key, password or token — the only
`password` strings in the tree are resource lookups and PDFBox arguments; the
release signing config reads every secret from `System.getenv` (app/build.gradle:38-44)
and no keystore, `.jks` or credential file is tracked. `android:allowBackup="false"`
and `android:usesCleartextTraffic="false"` are both set (AndroidManifest.xml:17,21)
and INTERNET is removed from the merged manifest with `tools:node="remove"`, pinned
by `tools/check-permissions.py`. The FileProvider exposes exactly one path,
`<cache-path name="work" path="work/"/>`, with `exported="false"` and
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

STATUS: FIXED - the × handler now deletes the JPEG it drops from the list (`val gone = pages.removeAt(index); runCatching { gone.delete() }`) before refreshing the strip, so a page the user discards is gone from `cache/work` at once instead of waiting for the 45-minute sweep. ScanToPdfActivity.kt:153-160.

### P2 — Denying the camera permission leaves the scan screen with no way forward
**File:** app/src/main/java/com/kavopdf/app/ScanToPdfActivity.kt:61
**What:** When the camera permission is denied both camera screens only show a toast (`msg_camera_needed`); there is no rationale, no "open settings" button and no second request, so Scan-to-PDF — which has no other input — is a dead preview for the rest of its life, and after a second denial the system will not show the dialog again.
**Why I think so:** the request result is `if (granted) startCamera() else toast(getString(R.string.msg_camera_needed))` (ScanToPdfActivity.kt:43-46, the same at QrScanActivity.kt:47-49). `shouldShowRequestPermissionRationale` and `ACTION_APPLICATION_DETAILS_SETTINGS` appear nowhere in the source, and the only request is the one fired from `onCreate` (61-63), so re-entering the screen after "Don't allow" asks nothing and says nothing new. `shoot()` begins `val ic = capture ?: return` (line 87) — with no camera bound, tapping Capture does nothing at all, not even a toast.
**How to verify:** `grep -rn "shouldShowRequestPermissionRationale\|ACTION_APPLICATION_DETAILS_SETTINGS" app/src/main/java` — no hits. In a build: deny the camera prompt twice, then tap Capture — the button is enabled and silently does nothing; the only recovery is Settings ▸ Apps ▸ KavoPDF ▸ Permissions, which the app never points at.
**User impact:** a user who taps "Don't allow" once — a normal reflex — is left on a black rectangle with a Capture button that does nothing and no sentence telling them how to fix it. The QR screen survives the same denial only because it also has a gallery button; Scan-to-PDF has no second way in.

STATUS: FIXED - a refusal now opens a dialog instead of a toast: `cameraDenied(ask)` explains why the camera is needed and offers the action that can still work - another request while `shouldShowRequestPermissionRationale` is true, `Settings ▸ Apps ▸ KavoPDF ▸ Permissions` once it is not (`openAppSettings`). Both camera screens use it, both re-bind the camera in `onResume` when the user comes back having allowed it, and Scan-to-PDF's Capture button no longer does nothing silently when no camera is bound. PdfActivity.kt:473-512 (helpers), ScanToPdfActivity.kt:48, :64-68, :91-96, QrScanActivity.kt:48, :80-83; strings msg_camera_needed_body, action_allow_camera, action_open_settings at strings.xml:278-280.

### P2 — Redaction removes the page but leaves the same words in the bookmarks and the form
**File:** app/src/main/java/com/kavopdf/app/engine/PdfEngine.java:2960
**What:** `applyRedaction()` replaces the page's content stream, resources and annotations, but nothing on the redaction path touches the catalog's `/Outlines`, `/AcroForm` or `/Names/EmbeddedFiles`, so text the document also carries at document level — bookmark titles, filled form values, attached files — is still in the redacted output.
**Why I think so:** `applyRedaction` (2960-2986) changes five things on the *page* and nothing on the catalog; `redactPages` (2896-2921) and `redactPagesLazy` (2934-2958) then call only `clearDocumentMetadata(d)` and `d.save(out)`. The same file writes bookmark titles into the catalog (`setBookmarks`, 2564-2585, `getDocumentCatalog().setDocumentOutline`) and field values with `f.setValue(v)` (1330). PDFBox 2.0.27's writer walks reachability from the trailer's `/Root` and `/Info` (`COSWriter.write` → `addObjectToWrite(root)`, pdfbox-2.0.27 sources, COSWriter.java:470-496), so every object still hanging off the catalog is serialised into the redacted file. Nothing detaches them.
**How to verify:** `grep -n "ACRO_FORM\|setDocumentOutline\|EMBEDDED" app/src/main/java/com/kavopdf/app/engine/PdfEngine.java` — the only removal is at 1218 (the form-fill path); the redaction block at 2896-2986 has none. In a build: bookmark a page with the title "Aadhaar 1234 5678", redact that page, save, then `strings out.pdf | grep Aadhaar` (or `mutool show out.pdf trailer/Root/Outlines`) — the title is still there while the page itself is a flat image.
**User impact:** the tool promises the characters are deleted from the file, not covered with a black box (README:181). For a document that also names the same thing in a bookmark, a form field or an attachment, that promise is false in exactly the way that matters: whoever receives the file can still read the words the user believed they had destroyed.

STATUS: OPEN - verified real: `applyRedaction` (PdfEngine.java:2960) replaces only page-level content, and neither `redactPages` (:2915) nor `redactPagesLazy` (:2954) touches `/Outlines`, `/AcroForm` or `/Names`. NOT fixed in this run: it is an engine change, and this sandbox has no JDK and no `/scratch/work/corpus`, so tier 2 (compile + TestPdfToWord) and tier 3 (G2 against base208.json) of tools/precommit.sh cannot run. An engine change must not be committed unverified, so it is left for a run that has the toolchain and the corpus.

### P2 — Nothing stops the open document from appearing in the recents thumbnail or a screenshot
**File:** app/src/main/java/com/kavopdf/app/ViewerActivity.kt:47
**What:** No screen sets `FLAG_SECURE`, so the page being read is captured into the system recents thumbnail — visible to whoever picks the phone up after the app is backgrounded — and any screenshot or screen recorder can capture it.
**Why I think so:** `grep -rn "FLAG_SECURE" app/src/main/java` returns no hits and there is no `window.setFlags` or `WindowManager.LayoutParams` call anywhere in the source; `ViewerActivity.onCreate` (47-60) inflates the binding and sets the content view without touching the window, and neither does `PdfActivity.onCreate` (162-175) that every other screen inherits.
**How to verify:** `grep -rn "FLAG_SECURE" app/src/main/java` — no hits. In a build: open a bank statement, press Recents — the thumbnail is the statement page; or take a screenshot with the reader open — it succeeds.
**User impact:** the app's premise is that a document stays private on the device, but a picture of the last page read stays in the system's recents list after the app is closed, and it can be photographed from the screen by anything the user has allowed to capture it.

STATUS: REVERTED by the user's decision, 11 Nov. It was fixed as described - `PdfActivity.onCreate` set `FLAG_SECURE` on the window - and that fix worked, but it also made every screenshot and every screen recording of the app fail, which the user reported as a defect: they photograph their own documents, and a viewer that refuses to be photographed is one they cannot use. Android has no flag that hides a screen from the recents thumbnail without also blocking capture, so the thumbnail is the price of a usable app. `FLAG_SECURE` is gone from the source; the trade is recorded here so it is a decision rather than an oversight. If it is ever wanted again it must be a per-screen setting the user turns on, never a blanket flag on every document screen.

### P3 — Merge and four other screens leave full copies of the user's documents in the cache
**File:** app/src/main/java/com/kavopdf/app/MergeActivity.kt:67
**What:** `doMerge` copies every input with `Files.copyToCache` inside the producer and never registers the copies with `trackCacheFile`, so they outlive the screen; the same untracked pattern is at LinksActivity.kt:440, BookmarksActivity.kt:61, ImageOcrActivity.kt:83 and ImagesToPdfActivity.kt:76.
**Why I think so:** `PdfActivity.onDestroy` (358-366) deletes `sessionFiles` minus `keptFiles`, and `sessionFiles` is filled only by `trackCacheFile` (340-343). The screens that do track are PdfActivity.kt:108 and :224, ToolsActivity.kt:197 and AnnotateActivity.kt:77; none of the five above is among them, so nothing on those screens ever deletes what it copied — only `CachePolicy`'s 45-minute age rule does, and only when the sweep next runs (app start, KavoPdfApp.kt:20, or a screen closing, PdfActivity.kt:366).
**How to verify:** `grep -rn "copyToCache" app/src/main/java` and check each hit against `trackCacheFile` — the five listed have no tracking. In a build: merge two large PDFs, close the screen, `adb shell run-as com.kavopdf.app ls -l cache/work` — both copies are still there.
**User impact:** the cache comment says "a screen deletes the files it made when it closes" (CacheSweep.kt:16-18), and on these five screens it does not: the user's documents sit in the cache for another 45 minutes, so merging a handful of big files leaves their combined size behind after the merge is finished.

STATUS: FIXED - all five copies are registered with `trackCacheFile`, so `PdfActivity.onDestroy` deletes them: MergeActivity.kt:70 and ImagesToPdfActivity.kt:77 inside the producer, BookmarksActivity.kt:65, ImageOcrActivity.kt:87 and LinksActivity.kt:439 on the main thread once the copy exists. `sessionFiles` is now a synchronised list, with the read-and-clear in `onDestroy` inside `synchronized` (PdfActivity.kt:44, :378-383), because the first two register from a background task while `onDestroy` runs on the main thread.

### P3 — Three more copies are made and never tracked, so they outlive the screen
**File:** app/src/main/java/com/kavopdf/app/ToolsActivity.kt:167
**What:** `Files.copyToCache` is called at two more places in `ToolsActivity` that do not register the result with `trackCacheFile` — the Unlock path at 167 and the watermark picture at 1136 — and `ImageOcrActivity` makes its flattened working PDF with `Files.newFile(this, "imgflat.pdf")` (line 68) without tracking it either. All three are copies of the user's own file sitting in `cache/work` until the 45-minute sweep.
**Why I think so:** `grep -rn "copyToCache\|newFile" app/src/main/java` against `trackCacheFile`: the Repair path two branches below the Unlock one does track (ToolsActivity.kt:197), which is what makes the omission visible; the other two have no `trackCacheFile` anywhere near them.
**How to verify:** read ToolsActivity.kt:160-180 and :1130-1140, and ImageOcrActivity.kt:66-72, next to PdfActivity.kt:336-348.
**User impact:** the same as the entry above, at three sites the previous list missed: unlocking or watermarking a large document leaves a second full copy of it in the cache after the screen has closed.
**Status note:** noticed while fixing the entry above; not fixed in the same run, because it is outside what that finding listed.

STATUS: FIXED - all three sites now register the copy they make: ToolsActivity.kt:169 (Unlock) and ToolsActivity.kt:1140 (watermark picture) go through `trackCacheFile(...)`, and ImageOcrActivity.kt:71 registers `imgflat.pdf` the same way. `trackCacheFile` adds to the synchronised `sessionFiles`, which `PdfActivity.onDestroy` deletes, so all three are removed when the screen closes. `tools/check-cache-sweep.py` passes; no engine file was touched.
---

## Stage 7 — CONFIG (API level, SDK targets, build config)

Scope: `app/build.gradle`, `build.gradle`, `gradle.properties`, `AndroidManifest.xml` and every
`java.*` / `android.*` call in `app/src/main/java` checked against `minSdk 24`. Read for this
stage: all 8 `Build.VERSION` guards, the `signingConfigs` / `buildTypes` / `packaging` blocks,
`proguard-rules.pro`, and the `configChanges` list on all 22 activities.

What passed (recorded so it is not re-checked): every `tooltipText` use is guarded
(`SDK_INT >= 26`, AnnotateActivity.kt:126, CreatePdfActivity.kt:104); both
`getParcelableExtra(String, Class)` calls are guarded (`SDK_INT >= 33`, PdfActivity.kt:212,
ViewerActivity.kt:72) and fall back to the old form; `longVersionCode` is guarded
(`SDK_INT >= 28`, LogActivity.kt:155, CrashGuard.kt:365); `Context.getColor(int)` needs 23 and
`minSdk` is 24; `Map.getOrDefault` / `computeIfAbsent` need 24 and `minSdk` is 24; `resConfigs`,
`abiFilters` and the SEND/VIEW filters are pinned by `tools/check-apk-config.py` and pass.

### P1 — The app targets API 35, and Google Play has required API 36 for every update since 31 August 2026
**File:** app/build.gradle:14
**What:** `targetSdk 35` (and `compileSdk 35` at line 8) while Play now rejects any new app or app update that does not target Android 16 / API 36.
**Why I think so:** `defaultConfig` sets `minSdk 24` and `targetSdk 35`, and `compileSdk 35` at the top of the `android` block — the same numbers are restated in `README.md:197`. Play Console Help states that from 31 August 2026 new apps and app updates must target Android 16 (API level 36) or higher, with an extension to 1 November 2026 that has now also passed. Nothing in the repo mentions 36 at all: `grep -n "36" app/build.gradle` returns no hits, and there is no `android.suppressUnsupportedCompileSdk` or toolchain pin that would explain the lag.
**How to verify:** read `app/build.gradle:8` and `:14`. Upload a build to the Play Console internal track — the release is blocked with "your app must target API level 36" until both `compileSdk` and `targetSdk` are raised (raising `targetSdk` alone will not compile, because `compileSdk 35` cannot resolve the 36 APIs).
**User impact:** no update can be shipped at all. The version on Play stays at 3.53.4 (versionCode 294) — every fix in this audit, including the P0/P1 ones, is stuck on the developer's machine, and on devices running Android 16 the listing is already hidden for new users.

STATUS: FIXED - compileSdk 36, buildToolsVersion 36.0.0 and targetSdk 36 (app/build.gradle:21, :22, :27), AGP 8.6.1 -> 8.9.1 (build.gradle:4, the first AGP that supports API 36) and Gradle 8.7 -> 8.11.1 (android.yml:142, :144, required by AGP 8.9); CI now installs platforms;android-36 and build-tools;36.0.0 (android.yml:114) and README.md:197 states the new matrix. NOT compiled here - this sandbox has no Android SDK, so Android CI on push is the first compile of the raised SDK.
### P1 — PDF-to-text calls `java.nio.file.Files`, which does not exist on the app's own minimum SDK
**File:** app/src/main/java/com/kavopdf/app/engine/TxtWriter.java:88
**What:** `TxtWriter.write()` ends with `java.nio.file.Files.write(out.toPath(), …)`, but `java.nio.file` was only added to Android in API 26 and `minSdk` is 24, so on Android 7.0/7.1 the class is missing and the conversion fails every time.
**Why I think so:** `app/build.gradle:13` sets `minSdk 24`; `compileOptions` (lines 60-63) sets only `sourceCompatibility` / `targetCompatibility` and there is no `coreLibraryDesugaringEnabled` and no `coreLibraryDesugaring` dependency anywhere in either gradle file, so nothing back-ports `java.nio.file` (the desugarer covers `java.time`, `java.util.stream`, `java.util.function` and `Optional`, not `java.nio.file`). `java.io.File.toPath()` is likewise API 26. Three call sites are unguarded: TxtWriter.java:88 (`Files.write`), PdfEngine.java:816 (`Files.copy`, the "compressed file came out larger, keep the original" branch) and PdfRepair.java:253 (`Files.readAllBytes`, the orphaned-content scan). None is inside a `Build.VERSION` check — there are only 8 guards in the whole source and none covers these files. `TxtWriter.write` is on the direct path of the PDF-to-text tool (`ToolsActivity.kt:598`) and of `PdfToWord.java:6360`, so it is reached on every run, not on an edge case.
**How to verify:** `grep -n "coreLibraryDesugaring" app/build.gradle` — no hits. `grep -rn "java.nio.file" app/src/main/java` — the three lines above. On an API 24 or 25 device (or an emulator at API 24), run PDF to text on any PDF: it ends with the generic "could not read" toast and no .txt is written. `PdfActivity.runTask` catches `Throwable`, so this arrives as a failed tool rather than a visible crash — which is why it has not been noticed.
**User impact:** on Android 7.0/7.1 the PDF-to-text tool never works, repair silently skips its orphaned-content pass, and compress silently skips its keep-the-original safety net. The user sees "could not read" on a file that is perfectly fine.

STATUS: FIXED - all three sites are java.io now: TxtWriter.java:92 writes the bytes through a FileOutputStream, PdfEngine.java:819-820 copies the kept original with buffered streams, and PdfRepair.java:255 calls the class's own `readAll(File)` instead of `Files.readAllBytes`. `grep -rn "java.nio.file" app/src/main/java` returns no hits. Verified with a real toolchain this run: the engine compiles against pdfbox-android 2.0.27.0, TestPdfToWord reports 29 passed / 0 failed, and tier 3 (G2 over all 208 corpus documents against base208.json) reports no document got worse.
### P2 — Crop and Create PDF are rebuilt on a dark-mode switch or a window resize and come back with no document
**File:** app/src/main/AndroidManifest.xml:137
**What:** `CropActivity` and `CreatePdfActivity` declare `configChanges="orientation|screenSize|keyboardHidden"`, missing the `screenLayout|smallestScreenSize|uiMode` that the other 20 activities declare, so those three changes destroy and recreate the screen — and neither screen saves the document it has open.
**Why I think so:** every other activity in the manifest carries the full six-value list (lines 41, 68-132); only lines 137 and 142 are short. Both screens override `onConfigurationChanged` and rely on it: `CropActivity.kt:118-121` re-renders the current page from `current`, which only exists because the activity was not recreated. Neither class has an `onSaveInstanceState` — `grep -n "onSaveInstanceState" CropActivity.kt CreatePdfActivity.kt` returns nothing, and `source`, `sizes`, `current` and the whole `OverlayView` drawing are plain fields. On recreate `incomingUri` is null again, so `CropActivity.onCreate` (line 48) runs `pickAfterEnter { pickPdf() }` and the file picker opens on top of a screen that has forgotten everything.
**How to verify:** `sed -n '135,144p' app/src/main/AndroidManifest.xml` against `:41`. In a build: open Crop, pick a PDF, drag the crop handles, then toggle dark mode from the quick-settings tile (or drag the app into split-screen) — the picker reappears and the crop rectangle is gone. The same toggle on Annotate keeps the document.
**User impact:** a crop or a hand-drawn annotation is thrown away by something as ordinary as the phone switching to dark mode at sunset, and the user is dropped back on the file picker with no explanation.

STATUS: FIXED - both activities now declare the same six-value list as the other 20: `orientation|screenSize|screenLayout|smallestScreenSize|keyboardHidden|uiMode` at AndroidManifest.xml:137 (CropActivity) and :142 (CreatePdfActivity), so a uiMode, screenLayout or smallestScreenSize change reaches `onConfigurationChanged` instead of recreating the screen and losing `source`/`current`.
### P3 — Minification is off, so `proguard-rules.pro` is dead weight and the release APK ships unshrunk
**File:** app/build.gradle:47
**What:** `minifyEnabled false` and `shrinkResources false` in the release block, while `proguardFiles` still points at a 60-line rule file that therefore never runs.
**Why I think so:** lines 47-49 set `minifyEnabled false`, `shrinkResources false` and `proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'`; the rule file itself opens with "Minification is currently OFF, so none of this affects the shipped APK". Nothing verifies those `-keep` rules, so the first release built with R8 on is untested — and the same build file spends real effort on APK size elsewhere (`resConfigs "en"` with a comment about a megabyte, `abiFilters` with a comment about 22 MB, the BouncyCastle `pqc` exclusion with a comment about 4 MB). R8 is the one lever that is switched off, and it is worth more than all three.
**How to verify:** `grep -n "minifyEnabled\|shrinkResources" app/build.gradle`. Build a release AAB and compare its size with `minifyEnabled true` — the delta is the whole of the unused library code, which the keep-everything rules above would still trim only partly.
**User impact:** a larger download than the app needs, on the budget phones the `armeabi-v7a` filter exists to serve, and no obfuscation of the engine's class names.

STATUS: OPEN - verified real: app/build.gradle:75-76 still set `minifyEnabled false` and `shrinkResources false` next to `proguardFiles ... 'proguard-rules.pro'`, so those rules never run. NOT fixed in this run, on purpose: turning R8 on changes the shipped artefact, and its failure mode is reflection inside pdfbox-android and ML Kit - a release that builds, passes every guard here, and then fails to convert at runtime. This sandbox has no Android SDK, no device and no instrumentation test, so nothing available could catch that, and the zero-regression rule on the conversion path makes an unverified R8 config the wrong change to make blind. It needs a release build with R8 enabled plus a conversion smoke test on a device.

### P3 — A release build with no keystore configured succeeds and produces an unsigned APK
**File:** app/build.gradle:35
**What:** `signingConfigs.release` only sets `storeFile` when `KEYSTORE_PATH` is present and resolves to an existing file, and `buildTypes.release` only assigns `signingConfig` under the same condition — so a misconfigured or missing environment silently yields `app-release-unsigned.apk` with no warning.
**Why I think so:** lines 33-44 wrap the whole `storeFile`/`storePassword`/`keyAlias`/`keyPassword` block in `if (path != null && !path.isEmpty() && file(path).exists())`, and lines 50-53 repeat the same guard before `signingConfig signingConfigs.release`. A path that is set but wrong (a typo, a keystore not copied onto the build machine) falls through the `file(path).exists()` test exactly as an unset one does, and Gradle has nothing to fail on — an empty `signingConfigs.release` is legal.
**How to verify:** `sed -n '33,55p' app/build.gradle`. Set `KEYSTORE_PATH` to a path that does not exist and run `./gradlew assembleRelease` — the build succeeds and the output is named `app-release-unsigned.apk`.
**User impact:** a release that looks like it worked cannot be uploaded, and the failure only shows up at the Play Console upload rather than at the build.

STATUS: FIXED - the signing state is read once at script level (app/build.gradle:12-14) and a task-graph check (app/build.gradle:139-155) now fails any release build whose KEYSTORE_PATH is set but does not resolve - the typo or missing-keystore case the finding describes - and logs a named warning when KEYSTORE_PATH is unset, instead of both cases silently producing app-release-unsigned.apk. CI exports KEYSTORE_PATH only when the keystore was actually decoded (android.yml:156) and no longer hard-codes the path on the build step, so its deliberate unsigned build still succeeds.
