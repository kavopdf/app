package com.kavopdf.app

import android.net.Uri
import android.os.Bundle
import android.text.InputType
import android.view.View
import android.widget.CheckBox
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView
import com.kavopdf.app.databinding.ActivityFormsBinding
import com.kavopdf.app.engine.PdfEngine
import com.kavopdf.app.util.Files
import java.io.File

/** Lists a PDF's AcroForm fields and fills them in. */
class FormsActivity : PdfActivity() {

    private lateinit var binding: ActivityFormsBinding
    private var source: File? = null
    private var sourceName: String = "form.pdf"

    private val rows = mutableListOf<Row>()
    private var lastHeadingPage = -1

    private class Row(val field: PdfEngine.FormField, val view: View)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityFormsBinding.inflate(layoutInflater)
        setContentView(binding.root)
        setSupportActionBar(binding.toolbar)
        binding.toolbar.setNavigationOnClickListener { finish() }
        binding.btnSave.setOnClickListener { save() }
        pickAfterEnter { pickPdf() }
    }

    override fun onPdfChosen(uri: Uri) {
        sourceName = Files.displayName(this, uri)
        openPdf(uri) { f ->
            runTask(getString(R.string.msg_processing), onDone = loaded@{ fields ->
                if (fields == null) return@loaded
                binding.container.removeAllViews()
                rows.clear()
                if (fields.isEmpty()) {
                    // An XFA form (Adobe LiveCycle - most Indian bank and government
                    // forms) keeps its fields in an XML stream, not as AcroForm
                    // widgets. There is nothing for pdfbox to fill, but the user
                    // still needs a way forward, so send them to Annotate.
                    val xfa = PdfEngine.hasXfa(f)
                    binding.info.text = getString(
                        if (xfa) R.string.msg_xfa_form else R.string.msg_no_form_fields
                    )
                    binding.btnSave.isEnabled = true
                    binding.btnSave.text = getString(R.string.action_fill_in_annotate)
                    binding.btnSave.setOnClickListener {
                        // hand the same file over, so Annotate opens it directly
                        val here = source
                        if (here != null) {
                            startActivity(
                                android.content.Intent(this, AnnotateActivity::class.java)
                                    .putExtra("com.kavopdf.app.EXTRA_PATH", here.absolutePath)
                            )
                        } else {
                            startActivity(android.content.Intent(this, AnnotateActivity::class.java))
                        }
                        finish()
                    }
                    return@loaded
                }
                binding.info.text = getString(R.string.label_pages, PdfEngine.pageCount(f)) +
                        "   •   " + fields.size + " fields"
                val shown = fields.take(MAX_FORM_FIELDS)
                shown.forEach { addRow(it) }
                if (fields.size > shown.size) {
                    binding.info.text = binding.info.text.toString() +
                            "  (showing first ${shown.size} fields)"
                }
                binding.btnSave.isEnabled = true
                // Put the save action back: the no-fields branch above points this same
                // button at Annotate, and that used to stick for the next file.
                binding.btnSave.text = getString(R.string.action_save_as)
                binding.btnSave.setOnClickListener { save() }
                // This slot used to be "Fill from profile". That feature had too many
                // gaps to keep, so the button now clears the whole form instead.
                binding.btnProfile.isEnabled = true
                binding.btnProfile.setText(R.string.action_clear_form)
                binding.btnProfile.setOnClickListener { clearForm() }
                binding.btnProfile.setOnLongClickListener(null)
            }) {
                source = f
                PdfEngine.listFormFields(f)
            }
        }
    }

    private val MAX_FORM_FIELDS = 5000

    /** Field-name words that usually hold a date, and ones that usually hold a number. */
    private val DATE_WORDS = setOf("date", "dob", "birth", "birthdate", "birthday")
    private val NUMBER_WORDS = setOf(
        "phone", "mobile", "amount", "pan", "pin", "pincode", "zip", "postcode"
    )

    private fun addRow(field: PdfEngine.FormField) {
        // A page heading before the first field of each page. A 352-field form is one
        // long list; without this the user cannot tell where page 2 begins.
        if (field.page > 0 && field.page != lastHeadingPage) {
            lastHeadingPage = field.page
            binding.container.addView(TextView(this).apply {
                text = getString(R.string.msg_form_page, field.page)
                setTextColor(getColor(R.color.text_secondary))
                textSize = 12f
                val lp2 = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT
                )
                lp2.topMargin = dp(20)
                layoutParams = lp2
            })
        }
        val label = TextView(this).apply {
            var shown = field.label?.takeIf { it.isNotBlank() } ?: field.name
            // several fields share a name across pages ("Date" four times); the page
            // number is what tells them apart
            if (field.page > 0) shown = "p" + field.page + " · " + shown
            text = if (field.required) shown + " *" else shown
            setTextColor(getColor(R.color.text_primary))
            textSize = 13f
        }
        val lp = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT
        )
        lp.topMargin = dp(16)
        label.layoutParams = lp
        binding.container.addView(label)

        val choices = field.options.orEmpty().filter { it.isNotBlank() }
        val view: View = if (field.type == "checkbox") {
            CheckBox(this).apply {
                // same readable label as every other field - this used to print the raw
                // key ("chk_p1_New") next to the tick box
                text = field.label?.takeIf { it.isNotBlank() } ?: field.name
                textSize = 13f
                isChecked = field.value.equals("on", true) || field.value == "1" || field.value.equals("yes", true)
                // a read-only field belongs to the document, not to the user
                isEnabled = !field.readOnly
                if (field.readOnly) alpha = 0.6f
            }
        } else if (choices.isNotEmpty()) {
            // a dropdown or a radio group: the value has to be one of the options, so
            // a free text box would only let the user type something invalid.
            android.widget.Spinner(this).apply {
                background = getDrawable(R.drawable.bg_field_pill)
                val px = (16 * resources.displayMetrics.density).toInt()
                val py = (8 * resources.displayMetrics.density).toInt()
                setPadding(px, py, px, py)
                layoutParams = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT
                ).also { it.topMargin = (10 * resources.displayMetrics.density).toInt() }
                adapter = android.widget.ArrayAdapter(
                    this@FormsActivity, android.R.layout.simple_spinner_dropdown_item, choices
                )
                val at = choices.indexOfFirst { it == field.value }
                setSelection(if (at >= 0) at else 0)
                isEnabled = !field.readOnly
                if (field.readOnly) alpha = 0.6f
            }
        } else {
            // a plain pill field - see ToolsActivity.addField for why
            // Only the allowed values are worth showing. The raw pdfbox type ("text")
            // means nothing to the person filling the form.
            val opts = if (field.options.isNotEmpty()) field.options.joinToString(", ") else ""
            val et = EditText(this).apply {
                hint = opts
                inputType = InputType.TYPE_CLASS_TEXT
                background = getDrawable(R.drawable.bg_field_pill)
                val px = (16 * resources.displayMetrics.density).toInt()
                val py = (14 * resources.displayMetrics.density).toInt()
                setPadding(px, py, px, py)
                layoutParams = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT
                ).also { it.topMargin = (10 * resources.displayMetrics.density).toInt() }
                setTextColor(getColor(R.color.text_primary))
                setHintTextColor(getColor(R.color.text_secondary))
                textSize = 15f
                maxLines = if (field.multiline) 4 else 1
                if (field.multiline) inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_FLAG_MULTI_LINE
                // a read-only field is part of the document, not something to type in
                isEnabled = !field.readOnly
                if (field.readOnly) alpha = 0.6f
                setText(field.value ?: "")
            }
            et
        }
        binding.container.addView(view)
        rows.add(Row(field, view))
    }

    private fun save() {
        val src = source ?: return toast(getString(R.string.msg_pick_file_first))
        // required fields must not be blank, and a date or a number field must look
        // like one - catching it here beats producing a form the bank rejects
        val problems = mutableListOf<String>()
        val values = HashMap<String, String>()
        rows.forEach { row ->
            // A read-only field belongs to the document. Writing it back could replace
            // data the PDF put there itself, so it is left alone.
            if (row.field.readOnly) return@forEach
            val view = row.view
            val v = when (view) {
                is CheckBox -> if (view.isChecked) "true" else "false"
                is EditText -> view.text.toString()
                is android.widget.Spinner -> view.selectedItem?.toString().orEmpty()
                else -> return@forEach
            }
            // One field can appear on several pages, so the screen shows it more than
            // once. A box left empty must not overwrite the copy the user filled in.
            if (v.isEmpty() && !values[row.field.name].isNullOrEmpty()) return@forEach
            values[row.field.name] = v
        }
        // required first: an empty one is a hard stop
        rows.forEach { row ->
            // a read-only field is never in `values`, so it must not be judged here
            if (!row.field.required || row.field.readOnly) return@forEach
            val v = values[row.field.name].orEmpty().trim()
            val missing = if (row.view is CheckBox) v != "true" else v.isEmpty()
            if (missing) problems.add(row.field.name)
        }
        if (problems.isNotEmpty()) {
            toast(getString(R.string.msg_required_missing, shownName(problems.first())))
            return
        }
        // then format checks - these only warn, because the PDF's own idea of the
        // format may differ from ours
        val warnings = mutableListOf<String>()
        rows.forEach { row ->
            val v = values[row.field.name].orEmpty().trim()
            if (v.isEmpty() || row.view !is EditText) return@forEach
            // Whole words only. Substring matching made "Company" look like a PAN
            // field and "Shipping" like a PIN field, so ordinary text raised a warning.
            val words = row.field.name.lowercase().split(Regex("[^a-z0-9]+")).toSet()
            if (words.any { it in DATE_WORDS }) {
                if (!Regex("^\\d{1,2}[/.-]\\d{1,2}[/.-]\\d{2,4}$").matches(v)) {
                    warnings.add(shownName(row.field.name) + " (date)")
                }
            } else if (words.any { it in NUMBER_WORDS }) {
                if (!Regex("^[A-Za-z0-9 .-]+$").matches(v)) {
                    warnings.add(shownName(row.field.name) + " (number)")
                }
            }
        }
        if (warnings.isNotEmpty()) toast(getString(R.string.msg_check_format, warnings.first()))
        runAndSave(Files.suggestName(sourceName, "_filled")) { out ->
            PdfEngine.fillForm(src, values, out)
        }
    }

    /** What the screen calls a field, so messages never show a raw key like txt_p3_Address. */
    private fun shownName(name: String): String =
        rows.firstOrNull { it.field.name == name }
            ?.field?.label?.takeIf { it.isNotBlank() } ?: name

    private fun dp(v: Int) = (v * resources.displayMetrics.density).toInt()
    /** Empties every field the form is showing, in one tap. */
    private fun clearForm() {
        rows.forEach { row ->
            when (val v = row.view) {
                is CheckBox -> v.isChecked = false
                is EditText -> v.setText("")
                is android.widget.Spinner -> if ((v.adapter?.count ?: 0) > 0) v.setSelection(0)
                else -> { }
            }
        }
        toast(getString(R.string.msg_form_cleared))
    }

}
