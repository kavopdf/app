package com.kavopdf.app

import android.graphics.Bitmap
import android.graphics.pdf.PdfRenderer
import android.net.Uri
import android.os.Bundle
import android.os.ParcelFileDescriptor
import androidx.lifecycle.lifecycleScope
import com.kavopdf.app.databinding.ActivityCropBinding
import com.kavopdf.app.engine.PdfEngine
import com.kavopdf.app.ui.PageRenderer
import com.kavopdf.app.util.Files
import java.io.File
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

/** Crop a page's margins and save the result in place. */
class CropActivity : PdfActivity() {

    private lateinit var binding: ActivityCropBinding
    private var renderer: PageRenderer? = null
    private var pfd: ParcelFileDescriptor? = null
    private var source: File? = null
    private var sourceName: String = "document.pdf"
    private var pageCount = 0
    private var current = 0
    private val sizes = mutableListOf<FloatArray>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityCropBinding.inflate(layoutInflater)
        setContentView(binding.root)
        setSupportActionBar(binding.toolbar)
        binding.toolbar.setNavigationOnClickListener { finish() }
        binding.cropView.imageView = binding.pageImage

        binding.prevPage.setOnClickListener { goTo(current - 1) }
        binding.nextPage.setOnClickListener { goTo(current + 1) }
        binding.btnReset.setOnClickListener {
            binding.cropView.reset()
            binding.cropView.invalidate()
        }
        binding.btnSave.setOnClickListener { save() }

        pickAfterEnter { pickPdf() }
    }

    override fun onPdfChosen(uri: Uri) {
        sourceName = Files.displayName(this, uri)
        openPdf(uri) { f ->
            runTask(getString(R.string.msg_processing), onDone = opened@{ count ->
                if (count == null || count == 0) return@opened
                pageCount = count
                goTo(0)
            }) {
                source = f
                sizes.clear()
                // sizes come from the renderer below, so the file is opened once
                val d = ParcelFileDescriptor.open(f, ParcelFileDescriptor.MODE_READ_ONLY)
                pfd = d
                val r = PdfRenderer(d)
                renderer = PageRenderer(r)
                sizes.addAll(PageRenderer.displaySizes(r))
                r.pageCount
            }
        }
    }

    private fun goTo(index: Int) {
        if (index < 0 || index >= pageCount) return
        current = index
        binding.pageLabel.text = "${getString(R.string.create_page)} ${index + 1} / $pageCount"
        binding.prevPage.isEnabled = index > 0
        binding.nextPage.isEnabled = index < pageCount - 1
        binding.cropView.reset()
        val r = renderer ?: return
        val targetW = (resources.displayMetrics.widthPixels * 1.6f).toInt().coerceAtMost(2200)
        lifecycleScope.launch {
            val bmp = withContext(Dispatchers.IO) {
                runCatching { r.render(index, targetW) }.getOrNull()
            }
            if (bmp != null && current == index) {
                binding.pageImage.setImageBitmap(bmp)
                binding.cropView.post { binding.cropView.invalidate() }
            }
        }
    }

    private fun save() {
        val src = source ?: return toast(getString(R.string.msg_pick_file_first))
        val size = sizes.getOrNull(current) ?: floatArrayOf(595f, 842f)
        val rect = binding.cropView.cropRect()
        val dx = rect[0] * size[0]
        val dy = rect[1] * size[1]
        val dw = rect[2] * size[0]
        val dh = rect[3] * size[1]
        if (dw < 12f || dh < 12f) return toast(getString(R.string.msg_crop_too_small))
        val all = binding.allPages.isChecked
        runAndSave(Files.suggestName(sourceName, "_cropped")) { out ->
            PdfEngine.cropPages(src, current + 1, dx, dy, dw, dh, all, out)
        }
    }

    override fun onConfigurationChanged(newConfig: android.content.res.Configuration) {
        super.onConfigurationChanged(newConfig)
        goTo(current)
    }

    override fun onDestroy() {
        super.onDestroy()
        renderer?.close()
        try { pfd?.close() } catch (_: Exception) { }
    }
}
