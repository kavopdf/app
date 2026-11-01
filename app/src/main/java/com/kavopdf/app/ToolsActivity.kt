package com.kavopdf.app

import android.net.Uri
import android.os.Bundle
import android.text.InputType
import android.view.Menu
import android.view.MenuItem
import android.view.MotionEvent
import android.view.View
import android.widget.ArrayAdapter
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.Spinner
import android.widget.TextView
import androidx.appcompat.app.AlertDialog
import androidx.documentfile.provider.DocumentFile
import com.google.android.material.switchmaterial.SwitchMaterial
import com.kavopdf.app.databinding.ActivityToolsBinding
import com.kavopdf.app.engine.PdfEngine
import com.kavopdf.app.engine.PdfRepair
import com.kavopdf.app.engine.PdfSigner
import com.kavopdf.app.model.Action
import com.kavopdf.app.util.Files
import java.io.File

/**
 * One-shot document tools: rotate, compress, watermark, protect, unlock, sign,
 * verify, metadata, extract images, page numbers and split.
 */
class ToolsActivity : PdfActivity() {

    companion object {
        const val EXTRA_TOOL = "tool"

        private val FONT_NAMES = listOf("Helvetica", "Helvetica Bold", "Times", "Times Bold", "Courier")
        private val SIZING_NAMES = arrayOf(
        "Automatic (keeps shape)", "Manual (width and height)"
    )
    private val IMAGE_PLACES = arrayOf(
        "Centre", "Top", "Bottom", "Left", "Right",
        "Top left", "Top right", "Bottom left", "Bottom right"
    )
    private val PAGENUM_PLACES = arrayOf(
        "Bottom centre", "Top centre", "Bottom left", "Bottom right", "Top left", "Top right"
    )
    private val COLOUR_NAMES = listOf("Black", "Red", "Blue", "Green", "Orange", "Purple", "Grey")
        private val COLOUR_VALUES = listOf(
            0xFF111111.toInt(), 0xFFE03131.toInt(), 0xFF1C7ED6.toInt(), 0xFF2F9E44.toInt(),
            0xFFF08C00.toInt(), 0xFF7048E8.toInt(), 0xFF868E96.toInt()
        )
        private val LEVEL_NAMES = listOf("Light — best quality", "Balanced", "Strong — smallest file")
    }

    private lateinit var binding: ActivityToolsBinding
    private lateinit var tool: Action

    /** Ten different tools live in this screen, so each must be timed separately. */
    override fun toolName(): String = if (::tool.isInitialized) tool.name else "ToolsActivity"
    private var source: File? = null
    private var sourceName: String = "document.pdf"
    /** The last repair report, shown on screen and again after saving. */
    private var repairReport: PdfRepair.Report? = null
    private var treeUri: Uri? = null
    private var pendingRun = false

    private var fText: EditText? = null
    /** Set when the user picked a picture to use as the watermark instead of text. */
    private var wmImage: File? = null
    private var fImgScale: EditText? = null
    private var fImgHeight: EditText? = null
    private var fImgSizing: android.widget.Spinner? = null
    private var fImgAutoNote: android.widget.TextView? = null
    private var fImgPlace: android.widget.Spinner? = null
    private var fPagenumPlace: android.widget.Spinner? = null
    private var fPagenumColour: android.widget.Spinner? = null
    private var fFont: EditText? = null
    private var fOpacity: EditText? = null
    private var fPw: EditText? = null
    private var fPw2: EditText? = null
    private var fRanges: EditText? = null
    private var fFormat: EditText? = null
    private var fTitle: EditText? = null
    private var fAuthor: EditText? = null
    private var fSubject: EditText? = null
    private var fKeywords: EditText? = null
    private var fCreator: EditText? = null
    private var fProducer: EditText? = null
    private var fCreated: EditText? = null
    private var fModified: EditText? = null
    private var fSignName: EditText? = null
    private var fSignOrg: EditText? = null
    private var fSignReason: EditText? = null
    private var fSignLocation: EditText? = null
    private var fSignContact: EditText? = null
    private var fFontSpinner: Spinner? = null
    private var fColourSpinner: Spinner? = null
    private var fRandom: SwitchMaterial? = null
    private var fLevelSpinner: Spinner? = null
    private var fPagenumOpacity: EditText? = null
    private var fSplitAll: SwitchMaterial? = null
    private var fExtractPages: EditText? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityToolsBinding.inflate(layoutInflater)
        setContentView(binding.root)
        setSupportActionBar(binding.toolbar)
        binding.toolbar.setNavigationOnClickListener { finish() }

        tool = try {
            Action.valueOf(intent.getStringExtra(EXTRA_TOOL) ?: Action.COMPRESS.name)
        } catch (_: Exception) { Action.COMPRESS }

        applyToolChrome()
        binding.btnChoose.setOnClickListener { pickPdf() }
        binding.btnRun.setOnClickListener { onRun() }
        pickAfterEnter { pickPdf() }
    }

    private fun applyToolChrome() {
        val (title, desc) = when (tool) {
            Action.COMPRESS -> R.string.tool_compress to R.string.tool_compress_desc
            Action.WATERMARK -> R.string.tool_watermark to R.string.tool_watermark_desc
            Action.PROTECT -> R.string.tool_protect to R.string.tool_protect_desc
            Action.UNLOCK -> R.string.tool_unlock to R.string.tool_unlock_desc
            Action.SIGN -> R.string.tool_sign to R.string.tool_sign_desc
            Action.VERIFY -> R.string.tool_verify to R.string.tool_verify_desc
            Action.METADATA -> R.string.tool_metadata to R.string.tool_metadata_desc
            Action.EXTRACT -> R.string.tool_extract to R.string.tool_extract_desc
            Action.PAGENUM -> R.string.tool_pagenum to R.string.tool_pagenum_desc
            Action.SPLIT -> R.string.tool_split to R.string.tool_split_desc
            Action.REPAIR -> R.string.tool_repair to R.string.tool_repair_desc
            else -> R.string.app_name to R.string.app_tagline
        }
        // The toolbar is the support ActionBar here, and the ActionBar owns the
        // title - setting it on the raw Toolbar is simply overwritten by the
        // activity label, which is why these screens showed the app name.
        supportActionBar?.setTitle(title)
        binding.toolDesc.setText(desc)
    }

    override fun onPdfChosen(uri: Uri) {
        sourceName = Files.displayName(this, uri)
        if (tool == Action.UNLOCK) {
            // Unlock needs the raw, still-encrypted file.
            runTask(getString(R.string.msg_processing), onDone = loaded@{ _ ->
                binding.fileName.text = sourceName
                buildParams(emptyMap())
                binding.btnRun.isEnabled = true
            }) {
                val f = Files.copyToCache(this, uri)
                if (!Files.looksLikePdf(f)) error(getString(R.string.msg_not_a_pdf))
                source = f
                Unit
            }
            return
        }
        if (tool == Action.REPAIR) {
            // Repair reads the file before it is asked to: the diagnosis is the useful
            // half of the feature, and doing it here means the user sees what is wrong
            // with their document before they commit to anything.
            openPdf(uri) { f ->
                runTask(getString(R.string.repair_reading), onDone = loaded@{ rep ->
                    binding.fileName.text = sourceName
                    repairReport = rep
                    buildParams(emptyMap())
                    binding.btnRun.isEnabled = rep?.readable == true
                    if (rep != null && !rep.readable) {
                        toast(rep.failure.ifEmpty { getString(R.string.repair_failed_title) })
                    }
                }) {
                    source = f
                    PdfRepair.diagnose(f, "")
                }
            }
            return
        }
        openPdf(uri) { f ->
            runTask(getString(R.string.msg_processing), onDone = loaded@{ meta ->
                binding.fileName.text = sourceName
                buildParams(meta ?: emptyMap())
                binding.btnRun.isEnabled = true
            }) {
                source = f
                if (tool == Action.METADATA) PdfEngine.getMetadata(f) else emptyMap<String, String>()
            }
        }
    }

    override fun onTreeChosen(uri: Uri) {
        treeUri = uri
        binding.outputHint.visibility = View.VISIBLE
        binding.outputHint.text = "Output folder: " + (uri.lastPathSegment ?: "folder")
        if (pendingRun) { pendingRun = false; onRun() }
    }

    // ---- dynamic parameter UI ---------------------------------------------

    /**
     * A pill-shaped text field.
     *
     * Built from a plain EditText on purpose: a Material TextInputLayout puts the
     * label in a floating box, and on this theme the label refused to float and
     * ended up drawn on top of the value. A hint inside a rounded field can never
     * overlap what you type, and the shape is ours.
     */
    private fun addField(hint: String, inputType: Int = InputType.TYPE_CLASS_TEXT, prefill: String = ""): EditText {
        val masked = (inputType and InputType.TYPE_TEXT_VARIATION_PASSWORD) != 0 ||
                (inputType and InputType.TYPE_TEXT_VARIATION_VISIBLE_PASSWORD) != 0
        val et = EditText(this).apply {
            this.hint = hint
            this.inputType = inputType
            background = getDrawable(R.drawable.bg_field_pill)
            setPadding(dp(18), dp(14), dp(18), dp(14))
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT
            ).also { it.topMargin = dp(16) }
            setTextColor(getColor(R.color.text_primary))
            setHintTextColor(getColor(R.color.text_secondary))
            textSize = 15f
            maxLines = 1
            setText(prefill)
            if (masked) attachRevealEye(this)
        }
        binding.params.addView(et)
        return et
    }

    /** A little eye on the right that shows or hides what was typed. */
    private fun attachRevealEye(field: EditText) {
        var shown = false
        fun paint() {
            val d = getDrawable(if (shown) R.drawable.ic_eye_off else R.drawable.ic_eye)
            d?.setBounds(0, 0, dp(22), dp(22))
            d?.setTint(getColor(R.color.text_secondary))
            field.setCompoundDrawables(null, null, d, null)
            field.compoundDrawablePadding = dp(8)
        }
        paint()
        field.setOnTouchListener { v, e ->
            val onEye = e.actionMasked == MotionEvent.ACTION_UP &&
                    e.x >= v.width - v.paddingEnd - dp(34)
            if (onEye) {
                shown = !shown
                val sel = field.selectionEnd.coerceAtLeast(0)
                field.inputType = if (shown)
                    InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_VARIATION_VISIBLE_PASSWORD
                else
                    InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_VARIATION_PASSWORD
                field.setSelection(sel.coerceAtMost(field.text?.length ?: 0))
                paint()
                true
            } else false
        }
    }

    /** True when a password would fall to a trivial guess. Length matters most. */
    private fun weakPassword(pw: String): Boolean {
        if (pw.length >= 12) return false
        var kinds = 0
        if (pw.any { it.isLowerCase() }) kinds++
        if (pw.any { it.isUpperCase() }) kinds++
        if (pw.any { it.isDigit() }) kinds++
        if (pw.any { !it.isLetterOrDigit() }) kinds++
        return pw.length < 9 || kinds < 3
    }

    private fun addSpinner(label: String, options: List<String>, selected: Int = 0): Spinner {
        val box = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT
            ).also { it.topMargin = dp(16) }
        }
        box.addView(TextView(this).apply {
            text = label
            textSize = 12f
            setTextColor(getColor(R.color.text_secondary))
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT
            ).also { it.bottomMargin = dp(6) }
        })
        // inflated from a layout so the pill shape and the rounded drop-down are
        // declared once, in XML
        val sp = layoutInflater.inflate(R.layout.view_spinner, box, false) as Spinner
        sp.adapter = ArrayAdapter(this, R.layout.item_dropdown, options)
        sp.setSelection(selected)
        box.addView(sp)
        binding.params.addView(box)
        return sp
    }

    private fun addSwitch(label: String, checked: Boolean = false): SwitchMaterial {
        val sw = SwitchMaterial(this).apply {
            text = label
            isChecked = checked
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT
            ).also { it.topMargin = dp(16) }
        }
        binding.params.addView(sw)
        return sw
    }

    private fun buildParams(meta: Map<String, String>) {
        binding.params.removeAllViews()
        fText = null; fFont = null; fOpacity = null; fPw = null; fPw2 = null
        fImgAutoNote = null
        fRanges = null; fFormat = null
        fTitle = null; fAuthor = null; fSubject = null; fKeywords = null
        fCreator = null; fProducer = null; fCreated = null; fModified = null
        fSignName = null; fSignOrg = null; fSignReason = null; fSignLocation = null; fSignContact = null
        fFontSpinner = null; fColourSpinner = null; fRandom = null; fLevelSpinner = null
        fPagenumOpacity = null; fSplitAll = null; fExtractPages = null

        when (tool) {
            Action.REPAIR -> {
                binding.btnRun.setText(R.string.repair_run)
                repairReport?.let { showDiagnosis(it) }
            }
            Action.WATERMARK -> {
                wmImage = null
                fText = addField(getString(R.string.hint_watermark_text))
                val useImage = com.google.android.material.button.MaterialButton(
                    this, null, com.google.android.material.R.attr.materialButtonOutlinedStyle
                ).apply {
                    text = getString(R.string.action_watermark_image)
                    layoutParams = LinearLayout.LayoutParams(
                        LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT
                    ).also { it.topMargin = dp(10) }
                    setOnClickListener { pickImages() }
                }
                binding.params.addView(useImage)
                fFontSpinner = addSpinner(getString(R.string.label_font), FONT_NAMES, 1)
                fColourSpinner = addSpinner(getString(R.string.label_colour), COLOUR_NAMES.toList(), 1)
                fRandom = addSwitch(getString(R.string.position_random), false)
                fFont = addField(getString(R.string.hint_font_size), InputType.TYPE_CLASS_NUMBER)
                fOpacity = addField(
                    getString(R.string.hint_opacity),
                    InputType.TYPE_CLASS_NUMBER or InputType.TYPE_NUMBER_FLAG_DECIMAL
                )
                // how wide the picture should be, as a percentage of the page
                fImgSizing = addSpinner(
                    getString(R.string.label_sizing), SIZING_NAMES.toList(), 0
                )
                // Both fields start empty: empty width and height mean "the picture's own
                // size", which is the least surprising default.
                fImgScale = addField(getString(R.string.hint_image_width), InputType.TYPE_CLASS_NUMBER)
                // a separate height lets the picture be squashed or stretched
                fImgHeight = addField(getString(R.string.hint_image_height), InputType.TYPE_CLASS_NUMBER)
                // Automatic greys the height field out; without a word of explanation that
                // reads as "the app is broken", so the reason sits right under it.
                fImgAutoNote = android.widget.TextView(this).apply {
                    text = getString(R.string.note_auto_height)
                    textSize = 12f
                    setTextColor(getColor(R.color.text_secondary))
                    setPadding(dp(4), dp(6), dp(4), 0)
                    layoutParams = LinearLayout.LayoutParams(
                        LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT
                    )
                }
                binding.params.addView(fImgAutoNote)
                fImgPlace = addSpinner(
                    getString(R.string.label_position), IMAGE_PLACES.toList(), 0
                )
                fImgSizing?.onItemSelectedListener = object : android.widget.AdapterView.OnItemSelectedListener {
                    override fun onItemSelected(p0: android.widget.AdapterView<*>?, v: android.view.View?, pos: Int, id: Long) {
                        // automatic keeps the picture's shape, so height is not the user's to set
                        fImgHeight?.isEnabled = pos != 0
                        fImgAutoNote?.visibility = if (pos == 0) android.view.View.VISIBLE
                                                   else android.view.View.GONE
                        if (pos == 0) fImgHeight?.setText("")
                    }
                    override fun onNothingSelected(p0: android.widget.AdapterView<*>?) { }
                }
            }
            Action.COMPRESS -> {
                fLevelSpinner = addSpinner(getString(R.string.label_level), LEVEL_NAMES, 1)
            }
            Action.PROTECT -> {
                fPw = addField(getString(R.string.hint_password), InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_VARIATION_PASSWORD)
                fPw2 = addField(getString(R.string.hint_password_confirm), InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_VARIATION_PASSWORD)
            }
            Action.UNLOCK -> {
                fPw = addField(getString(R.string.hint_password), InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_VARIATION_PASSWORD)
            }
            Action.SIGN -> {
                fSignName = addField(getString(R.string.hint_signer_name))
                fSignOrg = addField(getString(R.string.hint_organisation))
                fSignReason = addField(getString(R.string.hint_reason))
                fSignLocation = addField(getString(R.string.hint_location))
                fSignContact = addField(getString(R.string.hint_contact))
            }
            Action.METADATA -> {
                fTitle = addField(getString(R.string.hint_title), InputType.TYPE_CLASS_TEXT, meta["title"] ?: "")
                fAuthor = addField(getString(R.string.hint_author), InputType.TYPE_CLASS_TEXT, meta["author"] ?: "")
                fSubject = addField(getString(R.string.hint_subject), InputType.TYPE_CLASS_TEXT, meta["subject"] ?: "")
                fKeywords = addField(getString(R.string.hint_keywords), InputType.TYPE_CLASS_TEXT, meta["keywords"] ?: "")
                fCreator = addField("Creator (application)", InputType.TYPE_CLASS_TEXT, meta["creator"] ?: "")
                fProducer = addField("Producer", InputType.TYPE_CLASS_TEXT, meta["producer"] ?: "")
                fCreated = addField("Creation date (yyyy-MM-dd HH:mm)", InputType.TYPE_CLASS_TEXT, meta["creationDate"] ?: "")
                fModified = addField("Modified date (yyyy-MM-dd HH:mm)", InputType.TYPE_CLASS_TEXT, meta["modDate"] ?: "")
            }
            Action.PAGENUM -> {
                fPagenumPlace = addSpinner(
                    getString(R.string.label_position), PAGENUM_PLACES.toList(), 0
                )
                fPagenumColour = addSpinner(
                    getString(R.string.label_colour), COLOUR_NAMES.toList(), 1
                )
                fFont = addField(getString(R.string.hint_font_size), InputType.TYPE_CLASS_NUMBER)
                fPagenumOpacity = addField(
                    getString(R.string.hint_opacity),
                    InputType.TYPE_CLASS_NUMBER or InputType.TYPE_NUMBER_FLAG_DECIMAL
                )
            }
            Action.SPLIT -> {
                fSplitAll = addSwitch(getString(R.string.split_all_pages), false)
                fRanges = addField(getString(R.string.hint_ranges), InputType.TYPE_CLASS_TEXT, "1-3, 4-6")
            }
            Action.EXTRACT -> {
                fExtractPages = addField(getString(R.string.hint_extract_pages), InputType.TYPE_CLASS_TEXT, "")
            }
            else -> { }
        }
    }

    // ---- run ---------------------------------------------------------------

    private fun onRun() {
        when (tool) {
            Action.REPAIR -> {
                val src = source ?: return toast(getString(R.string.msg_pick_file_first))
                runAndSave(Files.suggestName(sourceName, suffixFor(tool))) { out ->
                    val rep = PdfRepair.repair(src, "", out)
                    repairReport = rep
                    // The engine only leaves a file behind when it verified it. If it did
                    // not, say why instead of saving a document that is worse than the one
                    // that came in.
                    if (!rep.readable || !rep.verified) {
                        throw IllegalStateException(
                            rep.failure.ifEmpty { getString(R.string.repair_not_ok) }
                        )
                    }
                }
            }
            Action.COMPRESS -> {
                val level = fLevelSpinner?.selectedItemPosition ?: 1
                single { PdfEngine.compress(it.first, it.second, level) }
            }
            Action.WATERMARK -> {
                val pic = wmImage
                if (pic != null) {
                    val op = (fOpacity?.text?.toString()?.toFloatOrNull() ?: 0.25f).coerceIn(0.05f, 1f)
                    // 0 means "not given": natural width, and a height derived from it
                    val pct = (fImgScale?.text?.toString()?.toIntOrNull() ?: 0).coerceIn(0, 100)
                    val auto = (fImgSizing?.selectedItemPosition ?: 0) == 0
                    val pctH = if (auto) 0 else
                        (fImgHeight?.text?.toString()?.toIntOrNull() ?: 0).coerceIn(0, 100)
                    val place = fImgPlace?.selectedItemPosition ?: 0
                    val rnd = fRandom?.isChecked ?: false
                    single {
                        PdfEngine.watermarkImage(
                            it.first, pic, op, pct / 100f, pctH / 100f, place, rnd, it.second
                        )
                    }
                    return
                }
                val text = fText?.text?.toString()?.trim().orEmpty()
                if (text.isEmpty()) return toast(getString(R.string.msg_enter_text))
                val o = PdfEngine.WatermarkOptions()
                o.text = text
                o.randomPosition = fRandom?.isChecked ?: false
                val fontIdx = fFontSpinner?.selectedItemPosition ?: 0
                o.font = when (fontIdx) { 2, 3 -> "Times"; 4 -> "Courier"; else -> "Helvetica" }
                o.bold = fontIdx == 1 || fontIdx == 3
                o.color = COLOUR_VALUES.getOrElse(fColourSpinner?.selectedItemPosition ?: 1) { COLOUR_VALUES[1] }
                o.fontSize = fFont?.text?.toString()?.toFloatOrNull() ?: 0f
                o.opacity = (fOpacity?.text?.toString()?.toFloatOrNull() ?: 0.25f).coerceIn(0.05f, 1f)
                single { PdfEngine.watermarkText(it.first, o, it.second) }
            }
            Action.PROTECT -> {
                val p1 = fPw?.text?.toString().orEmpty()
                val p2 = fPw2?.text?.toString().orEmpty()
                if (p1.isEmpty()) return toast(getString(R.string.msg_enter_password))
                if (p1.length < 6) return toast(getString(R.string.pw_too_short))
                if (p1 != p2) return toast(getString(R.string.msg_passwords_mismatch))
                if (weakPassword(p1)) toast(getString(R.string.pw_weak))
                single { PdfEngine.encrypt(it.first, p1, p1, it.second) }
            }
            Action.UNLOCK -> {
                val p = fPw?.text?.toString().orEmpty()
                single { PdfEngine.decrypt(it.first, p, it.second) }
            }
            Action.SIGN -> {
                val name = fSignName?.text?.toString()?.trim().orEmpty()
                if (name.isEmpty()) return toast(getString(R.string.msg_enter_text))
                val params = PdfSigner.SignParams()
                params.name = name
                params.organisation = fSignOrg?.text?.toString()?.trim().orEmpty()
                params.reason = fSignReason?.text?.toString()?.trim().orEmpty()
                params.location = fSignLocation?.text?.toString()?.trim().orEmpty()
                params.contact = fSignContact?.text?.toString()?.trim().orEmpty()
                single { PdfSigner.sign(it.first, it.second, params) }
            }
            Action.VERIFY -> {
                val src = source ?: return toast(getString(R.string.msg_pick_file_first))
                runTask(getString(R.string.msg_processing), onDone = checked@{ list ->
                    if (list == null) return@checked
                    showVerification(list)
                }) { PdfSigner.verify(src) }
            }
            Action.METADATA -> {
                val info = PdfEngine.MetadataInfo()
                info.title = fTitle?.text?.toString()
                info.author = fAuthor?.text?.toString()
                info.subject = fSubject?.text?.toString()
                info.keywords = fKeywords?.text?.toString()
                info.creator = fCreator?.text?.toString()
                info.producer = fProducer?.text?.toString()
                info.creationDate = fCreated?.text?.toString()
                info.modDate = fModified?.text?.toString()
                single { PdfEngine.setMetadata(it.first, info, it.second) }
            }
            Action.PAGENUM -> {
                val fmt = fFormat?.text?.toString()?.ifBlank { "Page {n} of {total}" } ?: "Page {n} of {total}"
                val size = fFont?.text?.toString()?.toFloatOrNull() ?: 10f
                val op = (fPagenumOpacity?.text?.toString()?.toFloatOrNull() ?: 1f).coerceIn(0.05f, 1f)
                val place = fPagenumPlace?.selectedItemPosition ?: 0
                val col = COLOUR_VALUES.getOrElse(fPagenumColour?.selectedItemPosition ?: 1) { 0xFF333333.toInt() }
                single { PdfEngine.addPageNumbers(it.first, fmt, size, col, op, place, it.second) }
            }
            Action.EXTRACT -> {
                val src = source ?: return toast(getString(R.string.msg_pick_file_first))
                if (treeUri == null) { pendingRun = true; pickTree(); return }
                // clamp to the real page count: an input like "1-999999999" must not
                // build an enormous list
                val total = PdfEngine.pageCount(src)
                val pageList = parseRanges(fExtractPages?.text?.toString().orEmpty())
                    .flatMap { r -> (maxOf(1, r[0])..minOf(total, r[1])).toList() }
                    .distinct().sorted()
                multi { dir -> PdfEngine.extractImages(src, dir, pageList.ifEmpty { null }) }
            }
            Action.SPLIT -> {
                val src = source ?: return toast(getString(R.string.msg_pick_file_first))
                val allPages = fSplitAll?.isChecked == true
                val ranges = parseRanges(fRanges?.text?.toString().orEmpty())
                if (!allPages && ranges.isEmpty()) return toast(getString(R.string.msg_invalid_ranges))
                if (treeUri == null) { pendingRun = true; pickTree(); return }
                val base = Files.baseName(sourceName)
                multi { dir ->
                    val use = if (allPages) {
                        val n = PdfEngine.pageCount(src)
                        (1..n).map { intArrayOf(it, it) }
                    } else ranges
                    PdfEngine.splitToFiles(src, use, dir, base)
                }
            }
            else -> { }
        }
    }

    private fun showVerification(list: List<PdfSigner.SignatureInfo>) {
        if (isFinishing || isDestroyed) return
        val v = layoutInflater.inflate(R.layout.dialog_signature_result, null)
        val icon = v.findViewById<android.widget.ImageView>(R.id.statusIcon)
        val title = v.findViewById<android.widget.TextView>(R.id.statusTitle)
        val sub = v.findViewById<android.widget.TextView>(R.id.statusSub)
        val details = v.findViewById<android.widget.LinearLayout>(R.id.details)

        val allValid = list.isNotEmpty() && list.all { it.valid && it.coversWholeDocument }
        val anyValid = list.any { it.valid }

        val accent: Int
        when {
            list.isEmpty() -> {
                accent = getColor(R.color.text_secondary)
                title.text = getString(R.string.verify_unsigned_title)
                sub.text = getString(R.string.verify_unsigned_sub)
                icon.setImageResource(R.drawable.ic_verify)
            }
            allValid -> {
                accent = getColor(R.color.success)
                title.text = getString(R.string.verify_valid_title)
                sub.text = getString(R.string.verify_valid_sub)
                icon.setImageResource(R.drawable.ic_check)
            }
            !anyValid -> {
                accent = getColor(R.color.danger)
                title.text = getString(R.string.verify_invalid_title)
                sub.text = getString(R.string.verify_invalid_sub)
                icon.setImageResource(R.drawable.ic_close)
            }
            else -> {
                accent = getColor(R.color.danger)
                title.text = getString(R.string.verify_partial_title)
                sub.text = getString(R.string.verify_partial_sub)
                icon.setImageResource(R.drawable.ic_verify)
            }
        }
        title.setTextColor(accent)
        icon.setColorFilter(accent)

        list.forEachIndexed { i, s ->
            val whole = s.valid && s.coversWholeDocument
            if (list.size > 1) {
                details.addView(sectionHeader(getString(R.string.title_signature) + " " + (i + 1)))
            }
            addRow(details, getString(R.string.verify_signer), s.signerName.ifEmpty { "\u2014" })
            addRow(details, getString(R.string.verify_date), s.date.ifEmpty { "\u2014" })
            if (s.reason.isNotEmpty()) addRow(details, getString(R.string.verify_reason), s.reason)
            if (s.location.isNotEmpty()) addRow(details, getString(R.string.verify_location), s.location)
            addRow(details, getString(R.string.verify_certificate), s.subject.ifEmpty { "\u2014" })
            val status = when {
                whole -> getString(R.string.msg_sig_valid)
                !s.valid -> getString(R.string.msg_sig_invalid)
                else -> getString(R.string.msg_sig_partial)
            }
            addRow(details, getString(R.string.verify_status), status,
                if (whole) getColor(R.color.success) else getColor(R.color.danger))
            if (whole) {
                addRow(details, getString(R.string.verify_note), getString(R.string.msg_sig_selfsigned))
            } else if (s.error.isNotEmpty()) {
                addRow(details, getString(R.string.verify_detail), s.error, getColor(R.color.danger))
            }
        }

        val dialog = AlertDialog.Builder(this).setView(v).create()
        v.findViewById<android.view.View>(R.id.btnClose).setOnClickListener { dialog.dismiss() }
        dialog.show()
    }

    /**
     * After a repair has been saved, show what was actually done.
     *
     * <p>The file is already saved at this point; this is the receipt - what was wrong,
     * what was rebuilt, and what did not make it across.
     */
    override fun onSaved(file: File) {
        if (tool != Action.REPAIR) return
        repairReport?.let { showRepairReport(it) }
    }

    /** The read-only card shown under the file name before repairing. */
    private fun showDiagnosis(rep: PdfRepair.Report) {
        val parent = binding.params
        parent.addView(sectionHeader(getString(R.string.repair_diagnosis)))
        addRow(parent, getString(R.string.repair_label_pages),
            rep.pagesBefore.toString())
        if (!rep.version.isEmpty()) {
            addRow(parent, "PDF", rep.version)
        }
        val findings = if (rep.findings.isEmpty()) {
            listOf(getString(R.string.repair_nothing_found))
        } else {
            rep.findings
        }
        findings.forEach { line ->
            parent.addView(android.widget.TextView(this).apply {
                text = "\u2022  " + line
                textSize = 13f
                setTextColor(getColor(R.color.text_secondary))
                setPadding(dp(2), dp(3), dp(2), dp(3))
            })
        }
        if (rep.lostPages.isNotEmpty() || rep.blankPages.isNotEmpty()) {
            addRow(parent, getString(R.string.repair_label_lost),
                rep.lostPages.joinToString(", ").ifEmpty { "\u2014" })
        }
    }

    /** The receipt shown once the repaired file has been saved. */
    private fun showRepairReport(rep: PdfRepair.Report) {
        if (isFinishing || isDestroyed) return
        val v = layoutInflater.inflate(R.layout.dialog_signature_result, null)
        val icon = v.findViewById<android.widget.ImageView>(R.id.statusIcon)
        val title = v.findViewById<android.widget.TextView>(R.id.statusTitle)
        val sub = v.findViewById<android.widget.TextView>(R.id.statusSub)
        val details = v.findViewById<android.widget.LinearLayout>(R.id.details)

        val intact = rep.findings.isEmpty() && rep.actions.isEmpty()
        val lost = rep.pagesBefore - rep.pagesAfter
        val accent: Int
        when {
            !rep.verified -> {
                accent = getColor(R.color.danger)
                title.setText(R.string.repair_failed_title)
                sub.text = getString(R.string.repair_not_ok)
                icon.setImageResource(R.drawable.ic_close)
            }
            intact -> {
                accent = getColor(R.color.success)
                title.setText(R.string.repair_intact_title)
                sub.setText(R.string.repair_intact_sub)
                icon.setImageResource(R.drawable.ic_check)
            }
            lost > 0 -> {
                accent = getColor(R.color.danger)
                title.setText(R.string.repair_partial_title)
                sub.text = getString(R.string.repair_recovered, rep.pagesAfter, rep.pagesBefore)
                icon.setImageResource(R.drawable.ic_repair)
            }
            else -> {
                accent = getColor(R.color.success)
                title.setText(R.string.repair_fixed_title)
                sub.text = getString(R.string.repair_all_recovered, rep.pagesAfter)
                icon.setImageResource(R.drawable.ic_check)
            }
        }
        title.setTextColor(accent)
        icon.setColorFilter(accent)

        if (rep.findings.isNotEmpty()) {
            details.addView(sectionHeader(getString(R.string.repair_section_found)))
            rep.findings.forEach { details.addView(bullet(it)) }
        }
        if (rep.actions.isNotEmpty()) {
            details.addView(sectionHeader(getString(R.string.repair_section_done)))
            rep.actions.forEach { details.addView(bullet(it)) }
        }
        addRow(details, getString(R.string.repair_label_pages),
            rep.pagesBefore.toString() + " \u2192 " + rep.pagesAfter)
        if (rep.lostPages.isNotEmpty()) {
            addRow(details, getString(R.string.repair_label_lost),
                rep.lostPages.joinToString(", "), getColor(R.color.danger))
        }
        if (rep.blankPages.isNotEmpty()) {
            addRow(details, getString(R.string.repair_label_blank),
                rep.blankPages.joinToString(", "), getColor(R.color.danger))
        }
        addRow(details, getString(R.string.repair_label_size),
            humanSize(rep.sizeBefore) + " \u2192 " + humanSize(rep.sizeAfter))
        addRow(details, getString(R.string.repair_label_checked),
            if (rep.verified) getString(R.string.repair_ok) else getString(R.string.repair_not_ok),
            if (rep.verified) getColor(R.color.success) else getColor(R.color.danger))

        val dialog = AlertDialog.Builder(this).setView(v).create()
        v.findViewById<android.view.View>(R.id.btnClose).setOnClickListener { dialog.dismiss() }
        dialog.show()
    }

    /** One finding or action line. */
    private fun bullet(text: String): android.widget.TextView =
        android.widget.TextView(this).apply {
            this.text = "\u2022  " + text
            textSize = 13f
            setTextColor(getColor(R.color.text_primary))
            setPadding(0, dp(2), 0, dp(2))
        }

    private fun humanSize(bytes: Long): String {
        if (bytes <= 0) return "\u2014"
        val mb = bytes / 1048576.0
        return if (mb >= 1) String.format(java.util.Locale.US, "%.1f MB", mb)
        else String.format(java.util.Locale.US, "%.0f KB", bytes / 1024.0)
    }

    /** A small grey caption used to separate several signatures. */
    private fun sectionHeader(text: String): android.widget.TextView =
        android.widget.TextView(this).apply {
            this.text = text
            setTextColor(getColor(R.color.text_secondary))
            textSize = 12f
            setPadding(0, dp(14), 0, dp(2))
        }

    /** label / value pair, optionally tinted. */
    private fun addRow(parent: android.widget.LinearLayout, label: String, value: String,
                       valueColour: Int? = null) {
        val row = android.widget.LinearLayout(this).apply {
            orientation = android.widget.LinearLayout.HORIZONTAL
            setPadding(0, dp(6), 0, dp(6))
        }
        val l = android.widget.TextView(this).apply {
            text = label
            setTextColor(getColor(R.color.text_secondary))
            textSize = 13f
            layoutParams = android.widget.LinearLayout.LayoutParams(dp(96), android.view.ViewGroup.LayoutParams.WRAP_CONTENT)
        }
        val r = android.widget.TextView(this).apply {
            text = value
            setTextColor(valueColour ?: getColor(R.color.text_primary))
            textSize = 13f
            layoutParams = android.widget.LinearLayout.LayoutParams(0, android.view.ViewGroup.LayoutParams.WRAP_CONTENT, 1f)
        }
        row.addView(l); row.addView(r)
        parent.addView(row)
    }

    private fun dp(v: Int): Int = (v * resources.displayMetrics.density).toInt()

    private fun single(produce: (Pair<File, File>) -> Unit) {
        val src = source ?: return toast(getString(R.string.msg_pick_file_first))
        runAndSave(Files.suggestName(sourceName, suffixFor(tool))) { out ->
            produce(src to out)
        }
    }

    private fun multi(produce: (File) -> List<File>) {
        val tree = treeUri ?: return
        runTask(getString(R.string.msg_processing), onDone = done@{ n ->
            if (n != null) showSuccess(getString(R.string.msg_saved_to, "$n files"), null)
        }) {
            val dir = Files.newFile(this, "out").apply { if (exists()) delete(); mkdirs() }
            val files = produce(dir)
            val root = DocumentFile.fromTreeUri(this, tree) ?: error("Cannot open the folder")
            var saved = 0
            files.forEach { f ->
                val df = root.createFile(mimeFor(f.name), f.name)
                if (df != null) {
                    contentResolver.openOutputStream(df.uri)?.use { os -> f.inputStream().copyTo(os) }
                    saved++
                }
            }
            saved
        }
    }

    private fun suffixFor(tool: Action) = when (tool) {
        Action.COMPRESS -> "_compressed"
        Action.WATERMARK -> "_watermarked"
        Action.PROTECT -> "_protected"
        Action.UNLOCK -> "_unlocked"
        Action.SIGN -> "_signed"
        Action.METADATA -> "_metadata"
        Action.PAGENUM -> "_numbered"
        Action.REPAIR -> "_repaired"
        else -> "_out"
    }

    private fun mimeFor(name: String) = when {
        name.endsWith(".png", true) -> "image/png"
        name.endsWith(".jpg", true) || name.endsWith(".jpeg", true) -> "image/jpeg"
        else -> "application/pdf"
    }

    private fun parseRanges(s: String): List<IntArray> {
        val out = ArrayList<IntArray>()
        s.split(',').forEach { part ->
            val p = part.trim()
            if (p.isEmpty()) return@forEach
            if (p.contains('-')) {
                val a = p.split('-')
                if (a.size == 2) {
                    val f = a[0].trim().toIntOrNull()
                    val t = a[1].trim().toIntOrNull()
                    if (f != null && t != null && f >= 1 && t >= f) out.add(intArrayOf(f, t))
                }
            } else {
                val v = p.toIntOrNull()
                if (v != null && v >= 1) out.add(intArrayOf(v, v))
            }
        }
        return out
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        if (tool == Action.METADATA) {
            menu.add(0, 1, 0, "Clear all metadata")
        }
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        if (item.itemId == 1 && tool == Action.METADATA) {
            single { PdfEngine.clearMetadata(it.first, it.second) }
            return true
        }
        return super.onOptionsItemSelected(item)
    }

    /** The picture chosen for the watermark, copied where pdfbox can read it. */
    override fun onImagesChosen(uris: List<Uri>) {
        val uri = uris.firstOrNull() ?: return
        runTask(getString(R.string.msg_processing), onDone = done@{ f ->
            if (f == null) return@done
            wmImage = f
            toast(getString(R.string.msg_watermark_image_ready))
        }) {
            Files.copyToCache(this, uri)
        }
    }

}
