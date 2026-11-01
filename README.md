# KavoPDF

**A serious, offline-first PDF editor for Android.** Everything runs on the device —
no accounts, no uploads, no network permission. Open any PDF and read it with smooth
pinch-zoom, then actually edit it: merge, split, reorganise pages by dragging them,
annotate, sign, fill forms, watermark, protect, compress and more.

Package: `com.kavopdf.app` · Display name: **KavoPDF** · Licence: Apache-2.0

> The package id is kept stable so the app upgrades cleanly in place and the signing
> key stays valid. It can be renamed before the first Play Store upload on request.

---

## What's new in 3.30.1

- The automatic-mode note now reads: *"In automatic mode, the Picture height option is
  disabled. To enable it, please select manual mode."* — in both the watermark and the
  picture link.
- **New signing key.** The old certificate carried a previous project's name inside it
  (`CN=`), which cannot be edited without replacing the key. A fresh key with
  `CN=KavoPDF` now signs the app. The app has to be **uninstalled once** before installing
  this build, because Android only accepts an update signed by the same key.

## What's new in 3.30.0

**The filled form now shows.** This was the real cause of "I fill it and the PDF is
still empty", and it was never in the form screen:

- `refreshAppearances()` can refuse to build a visible appearance — an unusual `/DA`, a
  font it cannot load, a widget with no rectangle. The value is stored, but nothing is
  drawn, and `setNeedAppearances(true)` is ignored by most Android viewers. Every value
  is now checked after the save, and any field still without a visible appearance has its
  text drawn onto the page directly.

**Page numbers come from the widget, not the field name.** Reading `txt_p3_Address_1` only
ever worked for the one generator that names fields that way; every other form got page 0
and lost its headings. A field's page is where its widget annotation sits.

Fields are also listed in reading order (page, then top-down) when every field can be
placed, and the file's own order is kept otherwise.

Both are covered by self-contained JVM tests that build their own forms.

## What's new in 3.29.9

- **Two fingers now zoom and drag the page.** The scroll detector is deliberately silent
  while a pinch is in progress, so moving two fingers did nothing — you had to switch to
  Move page (Annotate) or Pan (Create PDF) to reach a corner. The pinch focus is tracked
  frame to frame instead, which pans without the two detectors fighting. Read PDF gets the
  same behaviour, so one finger is no longer the only way to slide around.
- Zoom still happens wherever your fingers are, not in the middle of the screen.
- **Ruled and grid lines have an opacity field** (5–100%, empty keeps the old 55%).

## What's new in 3.29.8

Detector work — five changes, all covered by thirteen JVM checks that now run in CI.

- **Cold-start runs are ignored.** Anything within 60 s of process start measures JIT and
  dexopt warm-up, not the app. Learning from it made every later healthy run look fast.
- **File size gets its own norm bucket.** One 50 MB scan and one text page were both
  "1 page" and compared against each other.
- **A fast tool is judged relatively.** The absolute 1500 ms floor meant a 1200 ms run of a
  tool that normally takes 105 ms — eleven times slower — was never reported.
- **Repeated identical failures are counted, not re-written.** A startup crash loop used
  to write one entry per launch and bury everything else.
- **History is 9 samples instead of 5**, so one heavy run moves the norm less.

The log now records the device's **free RAM** next to the app heap. `memory=3/512MB` was
the app's own heap, not system pressure — a distinction that was impossible to make before.

## What's new in 3.29.7

- **Smoother page zoom.** The drawing overlay only repainted when it handled a gesture
  itself, so during a pinch the page moved while the ink stayed put. It now repaints on
  every matrix change, in Create PDF and Annotate.
- **Ruled and grid lines are yours to set up.** Adding them now asks for the number of
  lines and the space between them (mm). Leave the spacing empty to spread them evenly.
- **No eraser removes a guide line.** They were plain strokes, so the whole-stroke eraser
  wiped an entire grid in one touch while the partial eraser left it alone. Guides are
  now marked as page furniture and every eraser skips them.

## What's new in 3.29.6

- **The automatic-mode note says what to do:** *"In automatic mode, the height option is
  disabled. To enable it, please select manual mode."* (watermark and picture link).
- **Fill forms no longer assumes one form's layout.** Read-only fields are never written
  back, a blank box no longer overwrites a value typed into another box for the same
  field, the required check ignores read-only fields, and the date/number hints match
  whole words — so "Company" and "Shipping" stop raising false warnings.

## What's new in 3.29.5

- **Clear form actually clears now.** A second click listener left over from the removed
  profile feature was overwriting the first one, so the button said "Clear form" and
  filled the fields from the profile instead. The profile code is gone completely
  (`Profile.kt` deleted); the button clears.
- **Filled values are written to the file again.** The no-fields branch pointed the Save
  button at Annotate and never put it back, so after opening a form-less PDF the next
  form's Save button stopped writing the filled file — the typing went nowhere. Save is
  now reset for every file that has fields.

## What's new in 3.29.4

- **The greyed-out height field now explains itself.** In Automatic the height follows
  the width, so the field is disabled — which on its own reads as a broken app. Both
  the picture watermark and the picture link now show a one-line note under it:
  *"Height follows the width in Automatic, so the picture keeps its shape. Choose
  Manual to set the height yourself."* It disappears in Manual.

## What's new in 3.29.3

- **Hyperlinks buttons line up** — "Link icon / Link text / Link picture" and
  "Detect automatically / Add manually" now share one fixed height, so a two-line
  label no longer makes one button taller or clips its top edge.
- **Picture links can be sized** — the picture link has the same Sizing control as
  the picture watermark: Automatic keeps the picture's shape, Manual sets width and
  height independently. An empty field means the picture's own size.
- Width and opacity no longer start pre-filled; the labels stay.

## What's new in 3.29.2

- **4 MB smaller** — the APK no longer carries BouncyCastle's post-quantum lookup
  tables (SIKE and Picnic). PDF signing uses RSA/ECDSA, so those tables were never
  read. 44.8 MB → 40.8 MB, with no change to any feature.

## What's new in 3.29.1

- **Every old name is gone** — the theme styles, the Gradle project name, the class
  that starts the app and the default name for a newly created PDF no longer carry
  the project's previous names.
- **One visible side effect** — the settings file was renamed, so the app starts with
  the default theme and Amber accent once. Pick your theme again and it stays.

## What's new in 3.29.0

- **Fill forms** — every field on every page is shown (the old 300-field cap hid 52 of
  the SBI form's 352), labels are readable instead of raw keys, each page gets a
  heading, duplicate names carry their page, and saved values are now written as real
  appearance streams so every reader displays them.
- **Create PDF** — vertical lines, horizontal lines and grid are three separate
  options; Add a page is reachable from the overflow menu as well as the long-press.
- **Zoom** — the scale and scroll detectors no longer both move the page on the same
  frame, which was the jitter that made pinch-zoom feel heavy.
- **Hyperlinks** — Link picture is a visible button next to Link icon and Link text;
  both mode buttons share one fixed height.
- **Reader** — Amber is the default accent.

## Installing

Download the newest APK from the [latest release](https://github.com/kavopdf/app/releases/latest).
Android asks once for permission to install from this source. Android 7.0+ (API 24).

The website at <https://kavopdf.github.io/> reads that same release, so its download
button always hands over the newest build.

## Features

| Tool | What it does |
|---|---|
| **Read PDF** | Fast viewer with pinch-zoom, pan, double-tap, page swipe **and rotate**. Pages are supersampled and re-rendered on zoom, so text stays crisp. Also opens PDFs shared from other apps. |
| **Organize pages** | Thumbnail grid — **long-press a page and drag to reorder**, plus rotate, delete, extract and undo. |
| **Merge PDFs** | Combine any number of PDFs, in any order. |
| **Split PDF** | Break a document into files by page ranges (e.g. `1-3, 4-6, 9`). |
| **Images to PDF** | Turn photos/scans into a PDF, one page per image. Bounded decoding keeps large batches from running out of memory. |
| **Annotate & sign** | Pen, highlighter, text, **cover-and-retype**, signature and images — each with **colour, size and opacity**, plus **undo/redo**, **select / move / pinch-to-resize** and erase. Two-finger pinch still zooms. |
| **Fill forms** | Detects AcroForm fields (text, checkbox, radio, combo, list) and fills them. |
| **Compress** | Three levels (Light / Balanced / Strong). Downsamples and re-encodes embedded images (including inside form XObjects) and strips metadata and thumbnails. |
| **Watermark** | Text watermark with **font**, **colour**, size, opacity and a **random position on every page** (or centred). |
| **Protect** | Adds a password and permissions (128-bit encryption). |
| **Unlock** | Removes a password. Works for owner-only protection (no password needed) and for files whose user password you know. |
| **Edit metadata** | Title, author, subject, keywords. |
| **Extract images** | Pulls embedded raster images out of a PDF. |
| **Page numbers** | Number every page with a custom format (`Page {n} of {total}`). |
| **Create PDF** | Build a document from scratch — typed text, images, freehand drawing and shapes, then save it as a PDF. |
| **Crop page** | Trim a page's margins and write the crop into the file itself. |
| **Hyperlinks** | Find web and e-mail addresses and make them tappable, or place your own link as an icon, a caption or custom text at a position you choose — one page or every page. |
| **Bookmarks** | Add a navigation outline so the reader shows a table of contents. |
| **Digital signature** | Sign a PDF with a real certificate (self-signed on the device) so the signature can be verified later. |
| **Verify signature** | Check whether a file is signed, by whom, and whether the bytes changed after signing. |
| **Redact** | Permanently remove private text — the characters are deleted from the file, not covered with a black box. |
| **Repair PDF** | Rebuild a damaged file: lost cross-reference table, wrong offset, missing trailer, broken page tree. It verifies every page before saving and reports exactly what it recovered. |
| **PDF to Word** | Rebuild the document as an editable `.docx` (or `.txt`): paragraphs, heading levels, bold and italic, alignment, ruled and borderless tables, page breaks. Scanned pages go through on-device OCR. |
| **Make searchable (OCR)** | Add an invisible text layer to a scanned PDF so it can be searched and copied, using on-device ML Kit. |
| **Image to searchable PDF** | Read the text in a photo or screenshot and save it as a searchable PDF. |
| **QR & barcode scanner** | Read any code with the camera. |
| **Scan to PDF** | Photograph pages into a single PDF. |
| **Activity log** | See what the app has done — every run, how long it took, and any failure with its cause — and export it. |


**Dark mode** is supported throughout (follows the system, or pick Light / Dark from
the theme button on the home screen). All file access goes through the Storage Access
Framework, so **no storage permission is requested** and the app works fully offline.

## Building

Gradle 8.7 / AGP 8.6.1 / Kotlin 2.1.0, JDK 17, compileSdk 35, minSdk 24.

```bash
gradle :app:assembleDebug          # debug build
gradle :app:assembleRelease        # release (signed if keystore env vars are set)
```

### Signing

Release signing reads four environment variables; if they are absent the release
build is simply unsigned:

| Variable | Meaning |
|---|---|
| `KEYSTORE_PATH` | path to the `.jks` keystore |
| `KEYSTORE_PASSWORD` | keystore password |
| `KEY_ALIAS` | key alias |
| `KEY_PASSWORD` | key password |

In CI these come from repository secrets (`KEYSTORE_BASE64` is decoded to a file
first). Keep the keystore safe — it is the app's permanent identity.

## Verification

The document engine is verified independently of the UI. `tools/verify-engine.sh`
compiles the **real** engine source against the **real** `pdfbox-android` library on a
plain JVM (with tiny stubs for the handful of `android.*` classes the engine touches)
and runs **80 behavioural assertions**: merge, split, reorder, rotate, delete,
text/image stamping, watermark (centred, random, multiple fonts/colours), page
numbers, encryption, decryption (owner-only and user-password), compression
(asserting a real size reduction), metadata, images-to-PDF (single and multi-image),
image extraction, form filling, PDF creation, extended metadata, and digital signing/verification (including a tamper-detection test), page cropping, and page-range extraction.

```bash
bash tools/verify-engine.sh
```

It then renders the rotated and cropped output PDFs and **pixel-checks** them with
PyMuPDF, so rotation-aware overlay placement and cropping are verified visually
rather than assumed.

This runs automatically on every push in GitHub Actions, before the APK is built.

## CI

`.github/workflows/android.yml` runs on every push to `main`:

1. verifies the engine (80 checks + rendered rotation/crop checks),
2. builds a **signed** release APK,
3. uploads it as a build artifact and attaches it to a GitHub Release.

## License

The PDF engine is built on [Apache PDFBox](https://pdfbox.apache.org/) via the
Android port [PdfBox-Android](https://github.com/TomRoush/PdfBox-Android)
(Apache-2.0).
