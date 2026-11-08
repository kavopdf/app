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
**What:** Three save paths in the same activity use `"_links"` (lines 381, 398, 409) and the image-link path uses `"_linked"` (line 548), so one tool produces two naming schemes.
**Why I think so:** All four calls are `Files.suggestName(sourceName, ...)` in `LinksActivity` for the same output type (a PDF with links added). `_links` appears three times and `_linked` once, in `applyImageLink()`.
**How to verify:** `grep -n "_linked\?" app/src/main/java/com/kavopdf/app/LinksActivity.kt` — three `_links`, one `_linked`.
**User impact:** A link added from a picture is named `report_linked.pdf` while the same operation from text gives `report_links.pdf`; users get a folder of near-duplicate names that look like different operations.

STATUS: FIXED - the image-link path now saves under `"_links"` like the other three, so all four `Files.suggestName` calls in the activity agree; LinksActivity.kt:381, 398, 409 and 548.

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
**Why I think so:** Lines 425–428 pass bare literals to `addField(...)` where every sibling field uses `getString(R.string.hint_*)`, and line 219 concatenates `"Output folder: "` directly. Nothing in `strings.xml` holds these texts, so they are also untranslatable and un-reusable.
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

