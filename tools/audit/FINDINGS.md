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
