package com.kavopdf.app

import android.graphics.pdf.PdfRenderer
import android.net.Uri
import android.os.Bundle
import android.os.ParcelFileDescriptor
import android.view.View
import androidx.lifecycle.lifecycleScope
import com.kavopdf.app.databinding.ActivityLinksBinding
import com.kavopdf.app.engine.PdfEngine
import com.kavopdf.app.ui.PageRenderer
import com.kavopdf.app.util.Files
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File

/**
 * Turns the web / e-mail addresses already written in a PDF into real, clickable
 * link annotations — or lets you draw one yourself.
 *
 * Detection reads the actual glyph positions, so a link covers exactly the text it
 * came from (verified by rendering the result and measuring where the ink is).
 */
class LinksActivity : PdfActivity() {

    private lateinit var binding: ActivityLinksBinding
    private var renderer: PageRenderer? = null
    private var pfd: ParcelFileDescriptor? = null
    private var source: File? = null
    private var sourceName: String = "document.pdf"
    private var pageCount = 0
    private var current = 0
    private val sizes = mutableListOf<FloatArray>()
    private var found: List<PdfEngine.FoundLink> = emptyList()
    private var rectPlaced = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityLinksBinding.inflate(layoutInflater)
        setContentView(binding.root)
        setSupportActionBar(binding.toolbar)
        binding.toolbar.setNavigationOnClickListener { finish() }
        binding.rectPick.imageView = binding.pageImage
        // pointing anywhere on the page should place the link there
        binding.rectPick.moveOnTapOutside = true

        // Nothing in this screen's set-up is allowed to take the app down: if a
        // piece of wiring ever fails the screen still opens and stays usable.
        runCatching {
        binding.btnChoose.setOnClickListener { pickPdf() }
        binding.prevPage.setOnClickListener { goTo(current - 1) }
        binding.nextPage.setOnClickListener { goTo(current + 1) }
        binding.btnRun.setOnClickListener { run() }
        binding.btnPlace.setOnClickListener { togglePlacement() }
        binding.modeAuto.setOnClickListener { selectMode(false) }
        binding.modeManual.setOnClickListener { selectMode(true) }
        binding.kindIcon.setOnClickListener { selectKind(false) }
        // long press the icon button: use a picture as the clickable link
        // Picture links used to be reachable only by long-pressing "Link icon", which
        // nobody could find. It now has its own button.
        binding.kindPicture.setOnClickListener { pickImages() }
        binding.kindIcon.setOnLongClickListener { pickImages(); true }
        binding.kindText.setOnClickListener { selectKind(true) }
        selectMode(false)
        selectKind(false)
        binding.fontSpinner.adapter = android.widget.ArrayAdapter(
            this, R.layout.item_dropdown, PdfEngine.LINK_FONTS
        )
        buildColourRow()
        }
        // straight to the picker, exactly like the other tools
        pickAfterEnter { pickPdf() }
    }

    private companion object {
        const val DARK_ON_LIGHT = 0xFF10131A.toInt()
        const val LIGHT_ON_DARK = 0xFFFFFFFF.toInt()
    }

    private var manualMode = false
    private var textKind = false
    /** Set when the user picked a picture to use as a clickable link. */
    private var imgLinkFile: java.io.File? = null
    private var pendingImgUrl: String? = null
    private var pendingImgOpacity = 1f
    private var pendingImgShape = 0

    private fun selectMode(manual: Boolean) {
        manualMode = manual
        paint(binding.modeAuto, !manual)
        paint(binding.modeManual, manual)
        runCatching { applyMode(manual) }
    }

    private fun selectKind(text: Boolean) {
        textKind = text
        paint(binding.kindIcon, !text)
        paint(binding.kindText, text)
        runCatching { applyKind() }
    }

    /**
     * The chosen one is filled with the theme colour, the other is outlined - and
     * both keep the same pill shape, which a MaterialButtonToggleGroup would not do
     * (it squares off the corners where the two buttons meet).
     */
    private fun paint(button: com.google.android.material.button.MaterialButton, selected: Boolean) {
        val primary = attrColor(androidx.appcompat.R.attr.colorPrimary)
        // pick a readable label colour for the filled state from the fill itself
        val onPrimary = if (androidx.core.graphics.ColorUtils.calculateLuminance(primary) > 0.5)
            DARK_ON_LIGHT else LIGHT_ON_DARK
        runCatching {
            button.backgroundTintList = android.content.res.ColorStateList.valueOf(
                if (selected) primary else getColor(R.color.field_bg)
            )
            button.strokeColor = android.content.res.ColorStateList.valueOf(
                if (selected) primary else getColor(R.color.divider)
            )
            // the same stroke on both states keeps the two buttons exactly the same
            // size; only the colour changes
            button.strokeWidth = dp(1)
            button.setTextColor(if (selected) onPrimary else getColor(R.color.text_primary))
        }
    }

    private fun attrColor(attr: Int): Int {
        val tv = android.util.TypedValue()
        theme.resolveAttribute(attr, tv, true)
        return if (tv.resourceId != 0) getColor(tv.resourceId) else tv.data
    }

    /** Full-screen placement: hide the controls so the page fills the screen. */
    private var placing = false

    private fun togglePlacement() {
        if (!manualMode) selectMode(true)
        placing = !placing
        val chrome = if (placing) android.view.View.GONE else android.view.View.VISIBLE
        binding.info.visibility = chrome
        binding.kindRow.visibility = chrome
        binding.textInput.visibility = chrome
        binding.fontRow.visibility = chrome
        binding.opacityRow.visibility = chrome
        binding.colourRow.visibility = chrome
        binding.urlInput.visibility = chrome
        binding.applyAll.visibility = chrome
        binding.btnRun.visibility = chrome
        binding.btnPlace.text = if (placing) getString(R.string.links_done)
        else getString(R.string.links_fullscreen)
        if (!placing) applyKind()
        val pic = imgLinkFile
        val url = pendingImgUrl
        if (!placing && pic != null && url != null) {
            // cropRect() returns [x, y, w, h] as fractions of the page
            val r = binding.rectPick.cropRect()
            imgLinkFile = null
            pendingImgUrl = null
            applyImageLink(pic, url, r[0], r[1], r[2], r[3], pendingImgOpacity, pendingImgShape)
        }
    }

    /** Icon vs custom text for the manual link. */
    private fun applyKind() {
        val text = textKind
        binding.textInput.visibility = if (text) android.view.View.VISIBLE else android.view.View.GONE
        binding.fontRow.visibility = if (text) android.view.View.VISIBLE else android.view.View.GONE
        if (manualMode) {
            binding.info.text = if (text) getString(R.string.links_manual_text_hint)
            else getString(R.string.links_manual_hint)
        }
    }

    // ---- icon colour -------------------------------------------------------

    private val iconColours = intArrayOf(
        0xFF149E8C.toInt(), 0xFF1D4ED8.toInt(), 0xFFB91C1C.toInt(),
        0xFF111827.toInt(), 0xFFF59E0B.toInt()
    )
    private var chosenColour = iconColours[0]
    private val swatches = ArrayList<android.widget.ImageView>()

    private fun buildColourRow() {
        binding.colourRow.removeAllViews()
        swatches.clear()
        iconColours.forEach { c ->
            val v = android.widget.ImageView(this)
            val size = dp(30)
            val lp = android.widget.LinearLayout.LayoutParams(size, size)
            lp.rightMargin = dp(10)
            v.layoutParams = lp
            v.setImageDrawable(swatch(c))
            v.setOnClickListener { chosenColour = c; updateSwatches() }
            binding.colourRow.addView(v)
            swatches.add(v)
        }
        updateSwatches()
    }

    private fun updateSwatches() {
        swatches.forEachIndexed { i, v ->
            val on = iconColours[i] == chosenColour
            v.background = android.graphics.drawable.GradientDrawable().apply {
                shape = android.graphics.drawable.GradientDrawable.OVAL
                setColor(iconColours[i])
                // the chosen one gets a thick light ring so there is no doubt
                setStroke(dp(if (on) 4 else 1), getColor(if (on) R.color.text_primary else R.color.divider))
            }
            v.scaleX = if (on) 1.18f else 1f
            v.scaleY = if (on) 1.18f else 1f
        }
    }

    private fun swatch(c: Int) = android.graphics.drawable.GradientDrawable().apply {
        shape = android.graphics.drawable.GradientDrawable.OVAL
        setColor(c)
    }

    /** A small rounded button with a white link glyph, in the chosen colour. */
    private fun makeIcon(colour: Int, size: Int = 256): android.graphics.Bitmap {
        val bmp = android.graphics.Bitmap.createBitmap(size, size, android.graphics.Bitmap.Config.ARGB_8888)
        val c = android.graphics.Canvas(bmp)
        val p = android.graphics.Paint(android.graphics.Paint.ANTI_ALIAS_FLAG)
        p.color = colour
        val pad = size * 0.06f
        c.drawRoundRect(
            android.graphics.RectF(pad, pad, size - pad, size - pad),
            size * 0.26f, size * 0.26f, p
        )
        val d = androidx.appcompat.content.res.AppCompatResources.getDrawable(this, R.drawable.ic_link)
        d?.let {
            it.setTint(android.graphics.Color.WHITE)
            val in0 = (size * 0.24f).toInt()
            val in1 = (size * 0.76f).toInt()
            it.setBounds(in0, in0, in1, in1)
            it.draw(c)
        }
        return bmp
    }

    override fun onPdfChosen(uri: Uri) {
        sourceName = Files.displayName(this, uri)
        openPdf(uri) { f ->
            binding.fileName.text = sourceName
            runTask(getString(R.string.msg_processing), onDone = opened@{ res ->
                if (res == null) return@opened
                pageCount = res.first
                found = res.second
                binding.btnRun.isEnabled = true
                showFound()
                if (manualMode) goTo(0)
            }) {
                source = f
                sizes.clear()
                // sizes come from the renderer below, so the file is opened once
                val d = ParcelFileDescriptor.open(f, ParcelFileDescriptor.MODE_READ_ONLY)
                try { pfd?.close() } catch (_: Exception) { }
                pfd = d
                val r = PdfRenderer(d)
                renderer = PageRenderer(r)
                sizes.addAll(PageRenderer.displaySizes(r))
                r.pageCount to PdfEngine.findLinks(f)
            }
        }
    }

    private fun copyToClipboard(text: String) {
        val cm = getSystemService(android.content.Context.CLIPBOARD_SERVICE) as android.content.ClipboardManager
        cm.setPrimaryClip(android.content.ClipData.newPlainText("link", text))
        toast(getString(R.string.msg_copied))
    }

    private fun showFound() {
        binding.info.text = if (found.isEmpty()) getString(R.string.links_none)
        else getString(R.string.links_found, found.size)
        binding.linkList.removeAllViews()
        found.take(200).forEach { l ->
            // one compact line: page, address, and a copy button right there
            val row = android.widget.LinearLayout(this).apply {
                orientation = android.widget.LinearLayout.HORIZONTAL
                gravity = android.view.Gravity.CENTER_VERTICAL
                setPadding(dp(4), dp(2), dp(4), dp(2))
            }
            val label = android.widget.TextView(this).apply {
                text = "Page ${l.page}  \u2022  ${l.url}"
                setTextColor(getColor(R.color.text_primary))
                textSize = 13f
                maxLines = 1
                ellipsize = android.text.TextUtils.TruncateAt.MIDDLE
                layoutParams = android.widget.LinearLayout.LayoutParams(0, -2, 1f)
            }
            val copy = android.widget.ImageButton(this).apply {
                setImageResource(R.drawable.ic_copy)
                imageTintList = android.content.res.ColorStateList.valueOf(getColor(R.color.text_secondary))
                background = null
                contentDescription = getString(R.string.action_copy)
                val side = dp(34)
                layoutParams = android.widget.LinearLayout.LayoutParams(side, side)
                setPadding(dp(7), dp(7), dp(7), dp(7))
                setOnClickListener { copyToClipboard(l.url) }
            }
            row.addView(label); row.addView(copy)
            binding.linkList.addView(row)
        }
    }

    private fun applyMode(manual: Boolean) {
        binding.manualWrap.visibility = if (manual) View.VISIBLE else View.GONE
        binding.listWrap.visibility = if (manual) View.GONE else View.VISIBLE
        binding.info.text = if (manual) {
            if (textKind) getString(R.string.links_manual_text_hint)
            else getString(R.string.links_manual_hint)
        } else {
            if (found.isEmpty()) getString(R.string.links_none)
            else getString(R.string.links_found, found.size)
        }
        if (!manual && placing) togglePlacement()
        binding.kindRow.visibility = if (manual) android.view.View.VISIBLE else android.view.View.GONE
        if (manual) applyKind() else {
            binding.textInput.visibility = android.view.View.GONE
            binding.fontRow.visibility = android.view.View.GONE
            binding.opacityRow.visibility = android.view.View.GONE
        }
        binding.colourRow.visibility = if (manual) android.view.View.VISIBLE else android.view.View.GONE
        binding.opacityRow.visibility = if (manual) android.view.View.VISIBLE else android.view.View.GONE
        if (manual && pageCount > 0) goTo(current)
    }

    private fun goTo(index: Int) {
        if (index < 0 || index >= pageCount) return
        current = index
        binding.pageLabel.text = "${index + 1} / $pageCount"
        binding.prevPage.isEnabled = index > 0
        binding.nextPage.isEnabled = index < pageCount - 1
        // a small, icon-sized selection the first time; keep it afterwards so the
        // same spot can be reused on other pages
        if (!rectPlaced) {
            binding.rectPick.resetTo(0.10f, 0.10f, 0.20f, 0.175f)
            rectPlaced = true
        }
        val r = renderer ?: return
        val targetW = (resources.displayMetrics.widthPixels * 1.7f).toInt().coerceAtMost(2400)
        lifecycleScope.launch {
            val bmp = withContext(Dispatchers.IO) {
                r.renderOrRetry(index, targetW)
            }
            if (bmp == null) {
                com.kavopdf.app.util.AppLog.problem(
                    this@LinksActivity, "Page render failed",
                    IllegalStateException("page ${index + 1}")
                )
            }
            if (bmp != null && current == index) {
                binding.pageImage.setImageBitmap(bmp)
                binding.rectPick.post { binding.rectPick.invalidate() }
            }
        }
    }

    private fun run() {
        val src = source ?: return toast(getString(R.string.msg_pick_file_first))
        if (manualMode) {
            val url = binding.urlInput.text?.toString().orEmpty().trim()
            if (PdfEngine.normaliseUrl(url) == null) return toast(getString(R.string.msg_invalid_link))
            val size = sizes.getOrNull(current) ?: floatArrayOf(595f, 842f)
            val opacity = ((binding.opacityInput.text?.toString()?.toFloatOrNull() ?: 100f) / 100f)
                .coerceIn(0.05f, 1f)
            val rect = binding.rectPick.cropRect()
            val x = rect[0] * size[0]
            val y = rect[1] * size[1]
            val w = rect[2] * size[0]
            val h = rect[3] * size[1]
            if (w < 6f || h < 6f) return toast(getString(R.string.msg_area_too_small))
            if (textKind) {
                val body = binding.textInput.text?.toString().orEmpty().trim()
                if (body.isEmpty()) return toast(getString(R.string.msg_enter_link_text))
                val size = binding.sizeInput.text?.toString()?.toFloatOrNull() ?: 18f
                val fonts = PdfEngine.LINK_FONTS
                val font = fonts[binding.fontSpinner.selectedItemPosition.coerceIn(0, fonts.size - 1)]
                val all = binding.applyAll.isChecked
                runAndSave(Files.suggestName(sourceName, "_links")) { out ->
                    if (all) {
                        PdfEngine.addTextLinkAllPages(src, x, y, size, body, font,
                            chosenColour, url, opacity, out)
                    } else {
                        PdfEngine.addTextLink(src, current + 1, x, y, size, body, font,
                            chosenColour, url, opacity, out)
                    }
                }
                return
            }
            val side = minOf(w, h)
            val icon = Files.newFile(this, "link_icon.png")
            java.io.FileOutputStream(icon).use {
                makeIcon(chosenColour).compress(android.graphics.Bitmap.CompressFormat.PNG, 100, it)
            }
            val all = binding.applyAll.isChecked
            runAndSave(Files.suggestName(sourceName, "_links")) { out ->
                if (all) {
                    PdfEngine.addLinkIconAllPages(src, x, y, side, icon, url, opacity, out)
                } else {
                    PdfEngine.addLinkIcon(src, current + 1, x, y, side, icon, url, opacity, out)
                }
            }
            return
        }
        if (found.isEmpty()) return toast(getString(R.string.links_none))
        val n = found.size
        runAndSave(Files.suggestName(sourceName, "_links")) { out ->
            PdfEngine.addLinks(src, found, out)
            n
        }
    }

    private fun dp(v: Int) = (v * resources.displayMetrics.density).toInt()

    override fun onConfigurationChanged(newConfig: android.content.res.Configuration) {
        super.onConfigurationChanged(newConfig)
        if (manualMode) goTo(current)
    }

    override fun onDestroy() {
        super.onDestroy()
        renderer?.close()
        try { pfd?.close() } catch (_: Exception) { }
    }
    /** The picture chosen for an image link, copied where pdfbox can read it. */
    override fun onImagesChosen(uris: List<Uri>) {
        val uri = uris.firstOrNull() ?: return
        runTask(getString(R.string.msg_processing), onDone = done@{ f ->
            if (f == null) return@done
            imgLinkFile = f
            askImageLink(f)
        }) {
            Files.copyToCache(this, uri)
        }
    }

    /** URL, size and opacity for the picture link. */
    private fun askImageLink(pic: java.io.File) {
        val box = android.widget.LinearLayout(this).apply {
            orientation = android.widget.LinearLayout.VERTICAL
            val pad = (20 * resources.displayMetrics.density).toInt()
            setPadding(pad, (8 * resources.displayMetrics.density).toInt(), pad, 0)
        }
        fun field(hint: String, value: String): android.widget.EditText {
            val et = android.widget.EditText(this).apply {
                this.hint = hint
                setText(value)
                textSize = 15f
                background = getDrawable(R.drawable.bg_field_pill)
                val px = (16 * resources.displayMetrics.density).toInt()
                setPadding(px, (10 * resources.displayMetrics.density).toInt(), px, (10 * resources.displayMetrics.density).toInt())
            }
            box.addView(et, android.widget.LinearLayout.LayoutParams(
                android.widget.LinearLayout.LayoutParams.MATCH_PARENT,
                android.widget.LinearLayout.LayoutParams.WRAP_CONTENT
            ).also { it.topMargin = (10 * resources.displayMetrics.density).toInt() })
            return et
        }
        val fUrl = field(getString(R.string.hint_link_url), "")
        // Sizing behaves exactly like the picture watermark: Automatic keeps the
        // picture's own shape, Manual lets width and height be set separately. Both
        // size fields start empty, and empty means "the picture's own size".
        val sizingNames = arrayOf("Automatic (keeps shape)", "Manual (width and height)")
        val sizingSpin = android.widget.Spinner(this).apply {
            adapter = android.widget.ArrayAdapter(this@LinksActivity, R.layout.item_dropdown, sizingNames)
        }
        box.addView(sizingSpin, android.widget.LinearLayout.LayoutParams(
            android.widget.LinearLayout.LayoutParams.MATCH_PARENT,
            android.widget.LinearLayout.LayoutParams.WRAP_CONTENT
        ).also { it.topMargin = (10 * resources.displayMetrics.density).toInt() })

        val fWidth = field(getString(R.string.hint_image_width), "")
        val fHeight = field(getString(R.string.hint_image_height), "")
        fHeight.isEnabled = false            // Automatic until the user picks Manual
        // Same reason as the watermark: say why the field is greyed out, or it just looks broken.
        val autoNote = android.widget.TextView(this).apply {
            text = getString(R.string.note_auto_height)
            textSize = 12f
            setTextColor(getColor(R.color.text_secondary))
            val d = resources.displayMetrics.density
            setPadding((4 * d).toInt(), (6 * d).toInt(), (4 * d).toInt(), 0)
        }
        box.addView(autoNote, android.widget.LinearLayout.LayoutParams(
            android.widget.LinearLayout.LayoutParams.MATCH_PARENT,
            android.widget.LinearLayout.LayoutParams.WRAP_CONTENT
        ))
        sizingSpin.onItemSelectedListener = object : android.widget.AdapterView.OnItemSelectedListener {
            override fun onItemSelected(p0: android.widget.AdapterView<*>?, v: android.view.View?, pos: Int, id: Long) {
                fHeight.isEnabled = pos != 0
                autoNote.visibility = if (pos == 0) android.view.View.VISIBLE else android.view.View.GONE
                if (pos == 0) fHeight.setText("")
            }
            override fun onNothingSelected(p0: android.widget.AdapterView<*>?) { }
        }
        val fOpacity = field(getString(R.string.hint_opacity), "")
        val shapeNames = arrayOf("Rectangle", "Rounded", "Circle")
        val shapeSpin = android.widget.Spinner(this).apply {
            adapter = android.widget.ArrayAdapter(this@LinksActivity, R.layout.item_dropdown, shapeNames)
        }
        box.addView(shapeSpin, android.widget.LinearLayout.LayoutParams(
            android.widget.LinearLayout.LayoutParams.MATCH_PARENT,
            android.widget.LinearLayout.LayoutParams.WRAP_CONTENT
        ).also { it.topMargin = (10 * resources.displayMetrics.density).toInt() })

        androidx.appcompat.app.AlertDialog.Builder(this)
            .setTitle(R.string.action_image_link)
            .setView(box)
            .setPositiveButton(R.string.action_apply) { _, _ ->
                val url = fUrl.text.toString().trim()
                if (url.isEmpty()) { toast(getString(R.string.msg_enter_url)); return@setPositiveButton }
                val op = (fOpacity.text.toString().toIntOrNull() ?: 100).coerceIn(5, 100) / 100f
                // An empty width or height means "the picture's own size".
                val nat = runCatching {
                    PdfEngine.imageNaturalFraction(source!!, current + 1, pic)
                }.getOrNull() ?: floatArrayOf(0.25f, 0.25f)
                val wPct = fWidth.text.toString().trim().toIntOrNull()
                val hPct = fHeight.text.toString().trim().toIntOrNull()
                val w = if (wPct != null) wPct.coerceIn(1, 100) / 100f
                        else nat[0].coerceIn(0.01f, 1f)
                val automatic = sizingSpin.selectedItemPosition == 0
                val h = when {
                    // Automatic: height follows the width, so the shape is never distorted
                    automatic -> w * nat[1] / nat[0].coerceAtLeast(0.0001f)
                    hPct != null -> hPct.coerceIn(1, 100) / 100f
                    else -> nat[1].coerceIn(0.01f, 1f)
                }
                // same flow as a text or icon link: drag the box where you want it
                imgLinkFile = pic
                pendingImgUrl = url
                pendingImgOpacity = op
                pendingImgShape = shapeSpin.selectedItemPosition
                if (!manualMode) selectMode(true)
                if (!placing) togglePlacement()
                binding.rectPick.resetTo((1f - w) / 2f, (1f - h) / 2f, w, h)
                binding.rectPick.post { binding.rectPick.invalidate() }
                toast(getString(R.string.msg_drag_then_done))
            }
            .setNegativeButton(R.string.action_cancel, null)
            .show()
    }

    private fun applyImageLink(pic: java.io.File, url: String,
                               xd: Float, yd: Float, w: Float, h: Float, opacity: Float,
                               shape: Int = 0) {
        val src = source ?: return toast(getString(R.string.msg_pick_file_first))
        val page = current + 1
        runAndSave(Files.suggestName(sourceName, "_linked")) { out ->
            PdfEngine.addImageLink(src, page, shaped(pic, shape), xd, yd, w, h, opacity, url, out)
        }
    }

    /**
     * The engine draws a rectangle, so the shape is applied to the picture itself: a
     * square canvas with the image clipped to a circle or rounded corners. That file
     * is what gets embedded, so the link rectangle matches the picture exactly.
     */
    private fun shaped(pic: java.io.File, shape: Int): java.io.File {
        if (shape == 0) return pic
        val src = android.graphics.BitmapFactory.decodeFile(pic.absolutePath) ?: return pic
        val side = minOf(src.width, src.height).coerceAtLeast(1)
        val outBmp = android.graphics.Bitmap.createBitmap(side, side, android.graphics.Bitmap.Config.ARGB_8888)
        val c = android.graphics.Canvas(outBmp)
        val paint = android.graphics.Paint(android.graphics.Paint.ANTI_ALIAS_FLAG)
        val path = android.graphics.Path()
        if (shape == 2) {
            path.addCircle(side / 2f, side / 2f, side / 2f, android.graphics.Path.Direction.CW)
        } else {
            val r = side * 0.18f
            path.addRoundRect(0f, 0f, side.toFloat(), side.toFloat(), r, r, android.graphics.Path.Direction.CW)
        }
        c.clipPath(path)
        c.drawBitmap(src, (side - src.width) / 2f, (side - src.height) / 2f, paint)
        val f = java.io.File(cacheDir, "link_shape_" + System.currentTimeMillis() + ".png")
        java.io.FileOutputStream(f).use { outBmp.compress(android.graphics.Bitmap.CompressFormat.PNG, 100, it) }
        return f
    }

}
