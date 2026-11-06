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
**Why I think so:** `fFormat` is declared at line 92 and appears exactly three times in the whole source: the declaration, `fFormat = null` at line 335, and the read at line 695. It is never assigned an `EditText`, so `fFormat?.text` is always null and the elvis at 695 always yields `"Page {n} of {total}"`. The `Action.PAGENUM` branch (430–443) adds `fPagenumPlace`, `fPagenumColour`, `fFont`, `fPagenumOpacity` and stops. There is no `hint_format`-style string in `strings.xml` either, so the field was never wired.
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
