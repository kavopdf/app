package com.kavopdf.app

import android.graphics.Bitmap
import android.graphics.Color
import android.net.Uri
import android.os.Bundle
import android.view.Menu
import android.view.MenuItem
import android.view.View
import android.widget.ArrayAdapter
import androidx.appcompat.app.AlertDialog
import com.kavopdf.app.databinding.ActivityCreatePdfBinding
import com.kavopdf.app.databinding.DialogSignatureBinding
import com.kavopdf.app.databinding.DialogTextBinding
import com.kavopdf.app.engine.PdfEngine
import com.kavopdf.app.model.Annot
import com.kavopdf.app.ui.AnnotRenderer
import com.kavopdf.app.ui.OverlayView
import com.kavopdf.app.util.Files
import java.io.File
import java.io.FileOutputStream
import kotlin.math.max

/**
 * Create a PDF from scratch: pick a page size and colour, then add text, images,
 * highlights and freehand drawing on any number of pages.
 */
class CreatePdfActivity : PdfActivity() {

    private class PageData(var w: Float, var h: Float, var bg: Int) {
        val items: MutableList<Annot> = mutableListOf()
        fun copyOf(): PageData {
            val p = PageData(w, h, bg)
            items.forEach { p.items.add(it.copy()) }
            return p
        }
    }

    private lateinit var binding: ActivityCreatePdfBinding
    private val pages = mutableListOf<PageData>()
    /** Set when the next picked picture should become a whole page. */
    private var addingImagePage = false
    private val undoStack = ArrayDeque<List<Annot>>()
    private val redoStack = ArrayDeque<List<Annot>>()
    private var current = 0
    private var pendingPoint: Pair<Float, Float>? = null

    private val sizeNames = listOf("A4", "Letter", "Legal")
    private val sizeValues = listOf(floatArrayOf(595f, 842f), floatArrayOf(612f, 792f), floatArrayOf(612f, 1008f))
    private val orientNames = listOf("Portrait", "Landscape")

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityCreatePdfBinding.inflate(layoutInflater)
        setContentView(binding.root)
        setSupportActionBar(binding.toolbar)
        binding.toolbar.setNavigationOnClickListener { finish() }
        binding.overlay.onBeforeChange = { snapshotBefore() }

        binding.overlay.imageView = binding.pageImage
        binding.overlay.onTextAt = { fx, fy -> askText(fx, fy) }
        binding.overlay.onStampAt = { fx, fy ->
            if (binding.overlay.tool == OverlayView.Tool.SIGN) startStamp(fx, fy)
            else startImage(fx, fy)
        }
        binding.overlay.onSelectionChanged = { updateOptions() }
        binding.sizeSpinner.adapter = ArrayAdapter(this, R.layout.item_dropdown, sizeNames)
        binding.orientSpinner.adapter = ArrayAdapter(this, R.layout.item_dropdown, orientNames)
        binding.sizeSpinner.setOnItemSelectedListener(onItem { applyPageSize() })
        binding.orientSpinner.setOnItemSelectedListener(onItem { applyPageSize() })

        binding.toolPan.setOnClickListener { selectTool(OverlayView.Tool.PAN, binding.toolPan) }
        binding.toolPen.setOnClickListener { selectTool(OverlayView.Tool.PEN, binding.toolPen) }
        binding.toolHighlight.setOnClickListener { selectTool(OverlayView.Tool.HIGHLIGHT, binding.toolHighlight) }
        binding.toolText.setOnClickListener { selectTool(OverlayView.Tool.TEXT, binding.toolText) }
        binding.toolImage.setOnClickListener {
            selectTool(OverlayView.Tool.IMAGE, binding.toolImage)
            startImage(0.5f, 0.5f)      // open the picker straight away
        }
        binding.toolMove.setOnClickListener { selectTool(OverlayView.Tool.SELECT, binding.toolMove) }
        binding.toolErase.setOnClickListener { selectTool(OverlayView.Tool.ERASE, binding.toolErase) }
        binding.toolShape.setOnClickListener { selectTool(OverlayView.Tool.SHAPE, binding.toolShape) }
        // long press a tool to see what it does, like Annotate
        val toolNames = listOf(
            binding.toolPan to "Pan",
            binding.toolPen to "Pen",
            binding.toolHighlight to "Highlighter",
            binding.toolCover to "Cover",
            binding.toolSign to "Signature",
            binding.toolText to "Text",
            binding.toolImage to "Image",
            binding.toolMove to "Select",
            binding.toolErase to "Eraser",
            binding.toolShape to "Shape"
        )
        // The tooltip itself is set in the layout with android:tooltipText, because a
        // tooltip assigned at runtime loses the app icon that Annotate's shows.
        binding.toolCover.setOnClickListener { selectTool(OverlayView.Tool.COVER, binding.toolCover) }
        binding.toolSign.setOnClickListener { selectTool(OverlayView.Tool.SIGN, binding.toolSign) }
        // the cover needs somewhere to put the rectangle it draws
        binding.overlay.onCoverRect = { x, y, w, h -> askCover(x, y, w, h) }
        binding.toolShape.setOnLongClickListener { pickShape(); true }
        binding.toolErase.setOnLongClickListener { pickEraser(); true }
        if (android.os.Build.VERSION.SDK_INT >= 26) {
            binding.toolErase.tooltipText = null
            binding.toolShape.tooltipText = null
        }

        binding.swatchBlack.setOnClickListener { selectColour(Color.BLACK, binding.swatchBlack) }
        binding.swatchRed.setOnClickListener { selectColour(getColor(R.color.swatch_red), binding.swatchRed) }
        binding.swatchBlue.setOnClickListener { selectColour(getColor(R.color.swatch_blue), binding.swatchBlue) }
        binding.swatchGreen.setOnClickListener { selectColour(getColor(R.color.swatch_green), binding.swatchGreen) }
        binding.swatchOrange.setOnClickListener { selectColour(getColor(R.color.swatch_orange), binding.swatchOrange) }
        binding.swatchPurple.setOnClickListener { selectColour(getColor(R.color.swatch_purple), binding.swatchPurple) }

        binding.sizeSlider.addOnChangeListener { _, value, fromUser ->
            if (!fromUser) return@addOnChangeListener
            when (binding.overlay.tool) {
                OverlayView.Tool.PEN -> binding.overlay.penWidthPt = value
                OverlayView.Tool.HIGHLIGHT -> binding.overlay.highlightWidthPt = value
                OverlayView.Tool.TEXT -> binding.overlay.textSizePt = value
                OverlayView.Tool.SELECT -> {
                    val i = binding.overlay.selected
                    if (i in binding.overlay.items.indices) {
                        when (val a = binding.overlay.items[i]) {
                            is Annot.Text -> a.sizePt = value
                            else -> { }
                        }
                        binding.overlay.refresh()
                    }
                }
                else -> { }
            }
        }
        binding.opacitySlider.addOnChangeListener { _, value, fromUser ->
            if (fromUser) { binding.overlay.highlightOpacity = value; binding.overlay.refresh() }
        }
        binding.selDelete.setOnClickListener {
            val i = binding.overlay.selected
            if (i in binding.overlay.items.indices) {
                binding.overlay.items.removeAt(i)
                binding.overlay.selectItem(-1)
                binding.overlay.refresh()
            }
        }

        binding.prevPage.setOnClickListener { goTo(current - 1) }
        binding.nextPage.setOnClickListener { goTo(current + 1) }
        binding.addPage.setOnClickListener { addPage(after = current) }
        // long press: add a page of a chosen size instead of copying the current one
        binding.addPage.setOnLongClickListener { choosePageSize(after = current); true }
        binding.delPage.setOnClickListener { deletePage() }

        selectColour(Color.BLACK, binding.swatchBlack)
        selectTool(OverlayView.Tool.PEN, binding.toolPen)

        pages.add(PageData(595f, 842f, Color.WHITE))
        goTo(0)
    }

    private fun onItem(action: () -> Unit) = object : android.widget.AdapterView.OnItemSelectedListener {
        override fun onItemSelected(parent: android.widget.AdapterView<*>?, view: View?, position: Int, id: Long) = action()
        override fun onNothingSelected(parent: android.widget.AdapterView<*>?) { }
    }

    private fun applyPageSize() {
        val size = sizeValues[binding.sizeSpinner.selectedItemPosition.coerceIn(0, sizeValues.size - 1)]
        val landscape = binding.orientSpinner.selectedItemPosition == 1
        val w = if (landscape) size[1] else size[0]
        val h = if (landscape) size[0] else size[1]
        pages.forEach { it.w = w; it.h = h }
        goTo(current)
    }

    private fun addPage(after: Int) {
        val ref = pages[after.coerceIn(0, pages.size - 1)]
        pages.add(after + 1, PageData(ref.w, ref.h, ref.bg))
        goTo(after + 1)
    }

    private fun deletePage() {
        if (pages.size <= 1) { toast(getString(R.string.msg_keep_one)); return }
        pages.removeAt(current)
        goTo(current.coerceAtMost(pages.size - 1))
    }

    private fun goTo(index: Int) {
        if (index !in pages.indices) return
        current = index
        val p = pages[index]
        binding.pageLabel.text = "${getString(R.string.create_page)} ${index + 1} / ${pages.size}"
        binding.prevPage.isEnabled = index > 0
        binding.nextPage.isEnabled = index < pages.size - 1
        binding.delPage.isEnabled = pages.size > 1

        val targetW = resources.displayMetrics.widthPixels
        val h = (p.h / p.w * targetW).toInt().coerceAtLeast(1)
        val bmp = Bitmap.createBitmap(targetW, h, Bitmap.Config.ARGB_8888)
        bmp.eraseColor(p.bg)
        binding.pageImage.setImageBitmap(bmp)

        binding.overlay.pageW = p.w
        binding.overlay.pageH = p.h
        binding.overlay.items = p.items
        binding.overlay.selectItem(-1)
        binding.overlay.post { binding.overlay.refresh() }
    }

    private fun selectTool(tool: OverlayView.Tool, button: View) {
        binding.overlay.applyTool(tool)
        listOf(
            binding.toolPan, binding.toolPen, binding.toolHighlight, binding.toolText,
            binding.toolImage, binding.toolMove, binding.toolErase, binding.toolShape, binding.toolCover, binding.toolSign
        ).forEach { it.alpha = 0.4f }
        button.alpha = 1f
        updateOptions()
    }

    private fun selectColour(c: Int, active: View) {
        binding.overlay.color = c
        listOf(
            binding.swatchBlack, binding.swatchRed, binding.swatchBlue,
            binding.swatchGreen, binding.swatchOrange, binding.swatchPurple
        ).forEach { it.alpha = 0.4f }
        active.alpha = 1f
    }

    private fun updateOptions() {
        val t = binding.overlay.tool
        binding.colourRow.visibility = if (t == OverlayView.Tool.PAN || t == OverlayView.Tool.ERASE) View.GONE else View.VISIBLE
        binding.sizeBox.visibility =
            if (t in listOf(OverlayView.Tool.PEN, OverlayView.Tool.HIGHLIGHT, OverlayView.Tool.TEXT, OverlayView.Tool.COVER)) View.VISIBLE else View.GONE
        binding.opacityBox.visibility = if (t == OverlayView.Tool.HIGHLIGHT) View.VISIBLE else View.GONE
        binding.selDelete.visibility =
            if (t == OverlayView.Tool.SELECT && binding.overlay.selected >= 0) View.VISIBLE else View.GONE
        binding.optHint.text = if (t == OverlayView.Tool.SELECT && binding.overlay.selected >= 0)
            getString(R.string.hint_selected_item) else ""
    }

    private fun askText(fx: Float, fy: Float) {
        val dlg = DialogTextBinding.inflate(layoutInflater)

        AlertDialog.Builder(this)
            .setTitle(R.string.tool_text_box)
            .setView(dlg.root)
            .setPositiveButton(R.string.action_add) { _, _ ->
                val text = dlg.textInput.text?.toString()?.trim().orEmpty()
                if (text.isEmpty()) { toast(getString(R.string.msg_enter_text)); return@setPositiveButton }
                binding.overlay.items.add(
                    Annot.Text(fx, fy, binding.overlay.textSizePt, binding.overlay.color, text)
                )
                binding.overlay.refresh()
            }
            .setNegativeButton(R.string.action_cancel, null)
            .show()
    }

    private fun startImage(fx: Float, fy: Float) {
        pendingPoint = fx to fy
        pickAfterEnter { pickImages() }
    }

    override fun onImagesChosen(uris: List<Uri>) {
        if (addingImagePage) {
            addingImagePage = false
            val uri = uris.firstOrNull() ?: return
            val bmp = decodeBounded(uri, 2600)
            if (bmp == null) { toast(getString(R.string.msg_failed, "image")); return }
            // page takes the picture's own proportions, 595pt wide like A4
            val pw = 595f
            val ph = (pw * bmp.height / bmp.width.coerceAtLeast(1)).coerceIn(100f, 5000f)
            val page = PageData(pw, ph, Color.WHITE)
            // one stamp filling the whole page
            page.items.add(Annot.Stamp(0f, 0f, 1f, 1f, bmp))
            val at = (current + 1).coerceIn(0, pages.size)
            pages.add(at, page)
            goTo(at)
            return
        }
        val point = pendingPoint
        if (point == null || uris.isEmpty()) { pendingPoint = null; return }
        val bmp = decodeBounded(uris.first(), 2000)
        pendingPoint = null
        if (bmp == null) { toast(getString(R.string.msg_failed, "image")); return }
        val pw = binding.overlay.pageW
        val ph = binding.overlay.pageH
        val targetWpt = pw * 0.4f
        val targetHpt = targetWpt * bmp.height / bmp.width.coerceAtLeast(1).toFloat()
        var fx = point.first - (targetWpt / pw) / 2f
        var fy = point.second - (targetHpt / ph) / 2f
        fx = fx.coerceIn(0f, max(0f, 1f - targetWpt / pw))
        fy = fy.coerceIn(0f, max(0f, 1f - targetHpt / ph))
        binding.overlay.items.add(Annot.Stamp(fx, fy, targetWpt / pw, targetHpt / ph, bmp))
        binding.overlay.refresh()
    }

    private fun decodeBounded(uri: Uri, maxDim: Int): Bitmap? {
        val bounds = android.graphics.BitmapFactory.Options().apply { inJustDecodeBounds = true }
        try {
            contentResolver.openInputStream(uri)?.use {
                android.graphics.BitmapFactory.decodeStream(it, null, bounds)
            }
        } catch (_: Exception) { return null }
        if (bounds.outWidth <= 0 || bounds.outHeight <= 0) return null
        var sample = 1
        while (max(bounds.outWidth, bounds.outHeight) / (sample * 2) >= maxDim) sample *= 2
        val opts = android.graphics.BitmapFactory.Options().apply { inSampleSize = sample }
        return try {
            contentResolver.openInputStream(uri)?.use {
                android.graphics.BitmapFactory.decodeStream(it, null, opts)
            }
        } catch (_: Exception) { null }
    }

    private fun choosePageColour() {
        val names = arrayOf("White", "Cream", "Light blue", "Light grey", "Dark")
        val colors = intArrayOf(Color.WHITE, 0xFFFFF8E1.toInt(), 0xFFE7F0FF.toInt(), 0xFFF1F3F5.toInt(), 0xFF1B1E24.toInt())
        AlertDialog.Builder(this)
            .setTitle(R.string.create_background)
            .setSingleChoiceItems(names, -1) { d, which ->
                pages[current].bg = colors[which]
                d.dismiss()
                goTo(current)
            }
            .show()
    }

    override fun onConfigurationChanged(newConfig: android.content.res.Configuration) {
        super.onConfigurationChanged(newConfig)
        goTo(current)
    }

    private fun save() {
        val withInk = pages.any { it.items.isNotEmpty() }
        if (!withInk) { toast(getString(R.string.msg_need_selection)); return }
        runAndSave("KavoPDF-created.pdf") { out ->
            val specs = ArrayList<PdfEngine.PageSpec>()
            pages.forEachIndexed { i, p ->
                var raster: File? = null
                if (p.items.isNotEmpty()) {
                    val bmp = AnnotRenderer.rasterize(p.items, p.w, p.h, 2.5f)
                    raster = Files.newFile(this, "page_${i + 1}.png")
                    FileOutputStream(raster).use { bmp.compress(Bitmap.CompressFormat.PNG, 100, it) }
                    bmp.recycle()
                }
                specs.add(PdfEngine.PageSpec(p.w, p.h, p.bg, raster))
            }
            PdfEngine.createPdf(specs, out)
        }
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        menu.add(0, 3, 0, R.string.action_undo)
            .setIcon(R.drawable.ic_undo)
            .setShowAsAction(MenuItem.SHOW_AS_ACTION_ALWAYS)
        menu.add(0, 4, 0, R.string.action_redo)
            .setIcon(R.drawable.ic_redo)
            .setShowAsAction(MenuItem.SHOW_AS_ACTION_ALWAYS)
        menu.add(0, 5, 1, R.string.action_add_page)
        menu.add(0, 1, 2, R.string.create_background)
        menu.add(0, 2, 2, R.string.action_save_as)
            .setShowAsAction(MenuItem.SHOW_AS_ACTION_ALWAYS)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        when (item.itemId) {
            3 -> { undo(); return true }
            4 -> { redo(); return true }
            5 -> { choosePageSize(current); return true }
            1 -> { choosePageColour(); return true }
            2 -> { save(); return true }
        }
        return super.onOptionsItemSelected(item)
    }

    private fun snapshotBefore() {
        undoStack.addLast(binding.overlay.items.map { it.copy() })
        if (undoStack.size > 40) undoStack.removeFirst()
        redoStack.clear()
        updateUndoButtons()
    }

    private fun restore(list: List<Annot>) {
        binding.overlay.items = list.map { it.copy() }.toMutableList()
        binding.overlay.selectItem(-1)
        binding.overlay.refresh()
        updateUndoButtons()
    }

    private fun undo() {
        val prev = undoStack.removeLastOrNull() ?: return
        redoStack.addLast(binding.overlay.items.map { it.copy() })
        restore(prev)
    }

    private fun redo() {
        val next = redoStack.removeLastOrNull() ?: return
        undoStack.addLast(binding.overlay.items.map { it.copy() })
        restore(next)
    }

    private fun updateUndoButtons() {
        invalidateOptionsMenu()
    }
    /** Long press the shape tool: pick from the six shapes. */
    private fun pickShape() {
        androidx.appcompat.app.AlertDialog.Builder(this)
            .setTitle(getString(R.string.tool_shape))
            .setItems(com.kavopdf.app.model.Annot.Shape.NAMES) { _, which ->
                binding.overlay.shapeKind = which
                binding.toolShape.setImageResource(shapeIcon(which))
                selectTool(OverlayView.Tool.SHAPE, binding.toolShape)
                toast(getString(R.string.tool_shape) + ": " + com.kavopdf.app.model.Annot.Shape.NAMES[which])
            }
            .show()
    }

    /** Long press the eraser: whole line, or only the part you touch. */
    private fun pickEraser() {
        androidx.appcompat.app.AlertDialog.Builder(this)
            .setTitle(getString(R.string.tool_erase))
            .setItems(arrayOf("Erase whole line", "Erase part of a line")) { _, which ->
                binding.overlay.eraserWholeStroke = (which == 0)
                selectTool(OverlayView.Tool.ERASE, binding.toolErase)
            }
            .show()
    }

    /** Same cover as Annotate: a white box with the text written on it. */
    private fun askCover(x: Float, y: Float, w: Float, h: Float) {
        val dlg = DialogTextBinding.inflate(layoutInflater)
        val inkNames = arrayOf("Black", "White", "Red", "Blue", "Green", "Orange", "Purple")
        val inkVals = intArrayOf(
            android.graphics.Color.BLACK, android.graphics.Color.WHITE,
            0xFFB91C1C.toInt(), 0xFF1D4ED8.toInt(), 0xFF15803D.toInt(),
            0xFFEA580C.toInt(), 0xFF7C3AED.toInt()
        )
        val inkSpin = android.widget.Spinner(this).apply {
            adapter = android.widget.ArrayAdapter(this@CreatePdfActivity, R.layout.item_dropdown, inkNames)
        }
        (dlg.root as? android.view.ViewGroup)?.addView(
            inkSpin, android.view.ViewGroup.LayoutParams(
                android.view.ViewGroup.LayoutParams.MATCH_PARENT,
                android.view.ViewGroup.LayoutParams.WRAP_CONTENT
            )
        )

        AlertDialog.Builder(this)
            .setTitle(R.string.tool_cover)
            .setView(dlg.root)
            .setNeutralButton(R.string.action_use_saved) { _, _ ->
                val saved = SignatureStore.load(this)
                if (saved == null) { toast(getString(R.string.msg_no_saved_signature)); return@setNeutralButton }
                pendingPoint?.let { placeStamp(saved) }
            }
            .setPositiveButton(R.string.action_apply) { _, _ ->
                val text = dlg.textInput.text?.toString()?.trim().orEmpty()
                if (text.isEmpty()) { toast(getString(R.string.msg_enter_text)); return@setPositiveButton }
                snapshotBefore()
                val box = binding.overlay.color
                binding.overlay.items.add(Annot.Cover(x, y, w, h, box))
                // the text colour is its own choice now - the box colour no longer
                // forces black or white on the writing
                val ink = inkVals.getOrElse(inkSpin.selectedItemPosition) { Color.BLACK }
                val pageH = binding.overlay.pageH
                val size = kotlin.math.max(8f, kotlin.math.min(h * pageH * 0.62f, binding.overlay.textSizePt * 3f))
                binding.overlay.items.add(
                    Annot.Text(x + 0.004f, y + h * 0.78f, size, ink, text)
                )
                binding.overlay.refresh()
            }
            .setNegativeButton(R.string.action_cancel, null)
            .show()
    }


    private fun startStamp(fx: Float, fy: Float) {
        pendingPoint = fx to fy
        when (binding.overlay.tool) {
            OverlayView.Tool.SIGN -> showSignatureDialog()
            OverlayView.Tool.IMAGE -> pickImages()
            else -> { }
        }
    }

    private fun showSignatureDialog() {
        val dlg = DialogSignatureBinding.inflate(layoutInflater)
        var ink = binding.overlay.color
        dlg.pad.setInkColor(ink)
        dlg.inkBlack.setOnClickListener { ink = Color.BLACK; dlg.pad.setInkColor(ink) }
        dlg.inkBlue.setOnClickListener { ink = getColor(R.color.swatch_blue); dlg.pad.setInkColor(ink) }
        dlg.inkRed.setOnClickListener { ink = getColor(R.color.swatch_red); dlg.pad.setInkColor(ink) }
        dlg.clear.setOnClickListener { dlg.pad.clear() }

        val dialog = AlertDialog.Builder(this)
            .setTitle(R.string.tool_signature)
            .setView(dlg.root)
            .setPositiveButton(R.string.action_add, null)
            .setNegativeButton(R.string.action_cancel, null)
            .create()
        dialog.setOnShowListener {
            dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener {
                if (dlg.pad.isEmpty()) { toast(getString(R.string.msg_enter_text)); return@setOnClickListener }
                SignatureStore.save(this, dlg.pad.toBitmap())
                placeStamp(dlg.pad.toBitmap())
                dialog.dismiss()
            }
        }
        dialog.show()
    }

    private fun placeStamp(bmp: Bitmap) {
        val point = pendingPoint ?: return
        val pw = binding.overlay.pageW
        val ph = binding.overlay.pageH
        val targetWpt = pw * 0.35f
        val targetHpt = targetWpt * bmp.height / bmp.width.coerceAtLeast(1).toFloat()
        var fx = point.first - (targetWpt / pw) / 2f
        var fy = point.second - (targetHpt / ph) / 2f
        fx = fx.coerceIn(0f, max(0f, 1f - targetWpt / pw))
        fy = fy.coerceIn(0f, max(0f, 1f - targetHpt / ph))
        snapshotBefore()
        binding.overlay.items.add(Annot.Stamp(fx, fy, targetWpt / pw, targetHpt / ph, bmp))
        binding.overlay.refresh()
    }
    /** The shape tool shows the shape you picked, like Annotate. */
    private fun shapeIcon(kind: Int): Int = when (kind) {
        com.kavopdf.app.model.Annot.Shape.KIND_ELLIPSE -> R.drawable.ic_shape_ellipse
        com.kavopdf.app.model.Annot.Shape.KIND_LINE -> R.drawable.ic_shape_line
        com.kavopdf.app.model.Annot.Shape.KIND_ARROW -> R.drawable.ic_shape_arrow
        com.kavopdf.app.model.Annot.Shape.KIND_TRIANGLE -> R.drawable.ic_shape_triangle
        com.kavopdf.app.model.Annot.Shape.KIND_STAR -> R.drawable.ic_shape_star
        else -> R.drawable.ic_shape
    }

    /** True when white text would read better on this colour. */
    private fun isDark(c: Int): Boolean {
        val r = (c shr 16) and 0xFF
        val g = (c shr 8) and 0xFF
        val b = c and 0xFF
        return (0.299 * r + 0.587 * g + 0.114 * b) < 140
    }

    /** A4, A5, Letter or a custom size, in points (72 per inch). */
    private fun choosePageSize(after: Int) {
        val names = arrayOf(
            "A4  (595 x 842)", "A5  (420 x 595)", "Letter  (612 x 792)", "Custom...",
            getString(R.string.action_page_from_picture),
            getString(R.string.action_lines_vertical),
            getString(R.string.action_lines_horizontal),
            getString(R.string.action_grid_page)
        )
        androidx.appcompat.app.AlertDialog.Builder(this)
            .setTitle(R.string.title_page_size)
            .setItems(names) { _, which ->
                when (which) {
                    0 -> insertSizedPage(after, 595f, 842f)
                    1 -> insertSizedPage(after, 420f, 595f)
                    2 -> insertSizedPage(after, 612f, 792f)
                    3 -> askCustomSize(after)
                    4 -> { addingImagePage = true; pendingPoint = null; pickImages() }
                    5 -> askGuideOptions(Guide.VERTICAL)
                    6 -> askGuideOptions(Guide.HORIZONTAL)
                    else -> askGuideOptions(Guide.GRID)
                }
            }
            .setNegativeButton(R.string.action_cancel, null)
            .show()
    }

    private fun askCustomSize(after: Int) {
        val d = resources.displayMetrics.density
        val box = android.widget.LinearLayout(this).apply {
            orientation = android.widget.LinearLayout.VERTICAL
            setPadding((20 * d).toInt(), (8 * d).toInt(), (20 * d).toInt(), 0)
        }
        fun num(hint: String, value: String): android.widget.EditText {
            val et = android.widget.EditText(this).apply {
                this.hint = hint
                setText(value)
                inputType = android.text.InputType.TYPE_CLASS_NUMBER
                textSize = 15f
                background = getDrawable(R.drawable.bg_field_pill)
                setPadding((16 * d).toInt(), (10 * d).toInt(), (16 * d).toInt(), (10 * d).toInt())
            }
            box.addView(et, android.widget.LinearLayout.LayoutParams(
                android.widget.LinearLayout.LayoutParams.MATCH_PARENT,
                android.widget.LinearLayout.LayoutParams.WRAP_CONTENT
            ).also { it.topMargin = (10 * d).toInt() })
            return et
        }
        val fW = num(getString(R.string.hint_page_width), "595")
        val fH = num(getString(R.string.hint_page_height), "842")
        androidx.appcompat.app.AlertDialog.Builder(this)
            .setTitle(R.string.title_page_size)
            .setView(box)
            .setPositiveButton(R.string.action_apply) { _, _ ->
                val w = (fW.text.toString().toFloatOrNull() ?: 595f).coerceIn(72f, 5000f)
                val h = (fH.text.toString().toFloatOrNull() ?: 842f).coerceIn(72f, 5000f)
                insertSizedPage(after, w, h)
            }
            .setNegativeButton(R.string.action_cancel, null)
            .show()
    }

    private fun insertSizedPage(after: Int, w: Float, h: Float) {
        // same insert position and navigation as addPage, only the size differs
        val at = (after + 1).coerceIn(0, pages.size)
        pages.add(at, PageData(w, h, Color.WHITE))
        goTo(at)
    }

    /**
     * Grid or ruled lines on the current page, as real strokes so they survive the
     * export - anything drawn only on the preview would vanish when the PDF is built.
     */
    private enum class Guide { VERTICAL, HORIZONTAL, GRID }

    /**
     * How many lines, and how far apart. An empty spacing means "spread them evenly
     * across the page", which is what the tool always did; a spacing in millimetres
     * keeps the gap fixed and just stops at the page edge.
     */
    private fun askGuideOptions(guide: Guide) {
        val d = resources.displayMetrics.density
        val box = android.widget.LinearLayout(this).apply {
            orientation = android.widget.LinearLayout.VERTICAL
            val pad = (20 * d).toInt()
            setPadding(pad, (8 * d).toInt(), pad, 0)
        }
        fun field(hint: String, value: String): android.widget.EditText {
            val et = android.widget.EditText(this).apply {
                this.hint = hint
                setText(value)
                textSize = 15f
                inputType = android.text.InputType.TYPE_CLASS_NUMBER or
                        android.text.InputType.TYPE_NUMBER_FLAG_DECIMAL
                background = getDrawable(R.drawable.bg_field_pill)
                val px = (16 * d).toInt()
                setPadding(px, (10 * d).toInt(), px, (10 * d).toInt())
            }
            box.addView(et, android.widget.LinearLayout.LayoutParams(
                android.widget.LinearLayout.LayoutParams.MATCH_PARENT,
                android.widget.LinearLayout.LayoutParams.WRAP_CONTENT
            ).also { it.topMargin = (10 * d).toInt() })
            return et
        }
        val fCount = field(getString(R.string.hint_guide_count), "10")
        val fGap = field(getString(R.string.hint_guide_gap), "")
        val fOpacity = field(getString(R.string.hint_guide_opacity), "")
        androidx.appcompat.app.AlertDialog.Builder(this)
            .setTitle(R.string.title_guide_options)
            .setView(box)
            .setPositiveButton(R.string.action_apply) { _, _ ->
                val count = (fCount.text.toString().toIntOrNull() ?: 10).coerceIn(2, 200)
                val gap = fGap.text.toString().toFloatOrNull()?.coerceIn(0f, 500f) ?: 0f
                // empty keeps the old 55% look
                val alpha = (fOpacity.text.toString().toFloatOrNull() ?: 55f)
                    .coerceIn(5f, 100f) / 100f
                addGuides(count, guide, gap, alpha)
            }
            .setNegativeButton(R.string.action_cancel, null)
            .show()
    }

    private fun addGuides(count: Int, guide: Guide, gapMm: Float = 0f, alpha: Float = 0.55f) {
        val pw = binding.overlay.pageW
        val ph = binding.overlay.pageH
        if (pw <= 0f || ph <= 0f) return
        snapshotBefore()
        val c = 0xFF9AA3B2.toInt()
        val thin = 0.6f
        // guide = true, so no eraser removes them
        fun vline(x: Float) = binding.overlay.items.add(
            Annot.Stroke(
                mutableListOf(android.graphics.PointF(x, 0f), android.graphics.PointF(x, 1f)),
                thin, c, alpha, true
            )
        )
        fun hline(y: Float) = binding.overlay.items.add(
            Annot.Stroke(
                mutableListOf(android.graphics.PointF(0f, y), android.graphics.PointF(1f, y)),
                thin, c, alpha, true
            )
        )
        val gapPt = if (gapMm > 0f) gapMm * 72f / 25.4f else 0f   // mm -> points
        val maxLines = (count - 1).coerceAtLeast(1)
        // step as a fraction of the page: a fixed gap, or count lines spread evenly
        fun draw(stepFrac: Float, add: (Float) -> Unit) {
            var i = 1
            var made = 0
            while (made < maxLines) {
                val f = i * stepFrac
                if (f >= 1f) break
                add(f)
                made++
                i++
            }
        }
        if (guide != Guide.HORIZONTAL) {
            draw(if (gapPt > 0f) gapPt / pw else 1f / count) { vline(it) }
        }
        if (guide != Guide.VERTICAL) {
            draw(if (gapPt > 0f) gapPt / ph else 1f / count) { hline(it) }
        }
        binding.overlay.refresh()
        toast(
            getString(
                when (guide) {
                    Guide.GRID -> R.string.msg_grid_added
                    Guide.VERTICAL -> R.string.msg_lines_vertical_added
                    Guide.HORIZONTAL -> R.string.msg_lines_horizontal_added
                }
            )
        )
    }

}
