package com.kavopdf.app

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.app.AppCompatDelegate
import androidx.recyclerview.widget.GridLayoutManager
import com.kavopdf.app.databinding.ActivityMainBinding
import com.kavopdf.app.databinding.DialogThemeBinding
import com.kavopdf.app.model.Action
import com.kavopdf.app.model.ToolItem
import com.kavopdf.app.ui.HomeRow
import com.kavopdf.app.ui.ToolAdapter
import com.kavopdf.app.util.ThemeUtil
import com.kavopdf.app.util.useHighestRefreshRate

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        ThemeUtil.apply(this)
        super.onCreate(savedInstanceState)
        useHighestRefreshRate()
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        // read from the build, so every release shows its own version
        findViewById<android.widget.TextView>(R.id.tvVersion)?.text =
            "v" + com.kavopdf.app.BuildConfig.VERSION_NAME

        val rows = buildRows()
        val adapter = ToolAdapter(rows, {
            binding.recycler.scrollState != androidx.recyclerview.widget.RecyclerView.SCROLL_STATE_IDLE
        }) { dispatch(it) }
        val lm = GridLayoutManager(this, 2)
        lm.spanSizeLookup = object : GridLayoutManager.SpanSizeLookup() {
            override fun getSpanSize(position: Int) =
                if (rows[position] is HomeRow.Header) 2 else 1
        }
        binding.recycler.layoutManager = lm
        binding.recycler.adapter = adapter
        binding.recycler.setHasFixedSize(true)
        binding.recycler.itemAnimator?.apply {
            addDuration = 160L
            removeDuration = 160L
            moveDuration = 160L
            changeDuration = 160L
        }

        binding.btnTheme.setOnClickListener { chooseTheme() }
    }

    private fun chooseTheme() {
        val v = DialogThemeBinding.inflate(layoutInflater)
        when (KavoPdfApp.themePref(this)) {
            1 -> v.modeLight.isChecked = true
            2 -> v.modeDark.isChecked = true
            else -> v.modeSystem.isChecked = true
        }
        v.modeGroup.setOnCheckedChangeListener { _, id ->
            val mode = when (id) {
                R.id.modeLight -> 1
                R.id.modeDark -> 2
                else -> 0
            }
            KavoPdfApp.setThemePref(this, mode)
            AppCompatDelegate.setDefaultNightMode(
                when (mode) {
                    1 -> AppCompatDelegate.MODE_NIGHT_NO
                    2 -> AppCompatDelegate.MODE_NIGHT_YES
                    else -> AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM
                }
            )
        }

        val accents = listOf(
            v.accentIndigo, v.accentTeal, v.accentViolet, v.accentGreen, v.accentCrimson, v.accentAmber
        )
        val currentAccent = KavoPdfApp.accentPref(this)
        accents.forEachIndexed { i, b ->
            b.alpha = if (i == currentAccent) 1f else 0.45f
            b.setOnClickListener {
                KavoPdfApp.setAccentPref(this, i)
                recreate()
            }
        }

        AlertDialog.Builder(this)
            .setTitle(R.string.action_theme)
            .setView(v.root)
            .setPositiveButton(R.string.action_close, null)
            .show()
    }

    private fun dispatch(action: Action) {
        val intent = when (action) {
            Action.VIEW -> Intent(this, ViewerActivity::class.java)
            Action.ANNOTATE -> Intent(this, AnnotateActivity::class.java)
            Action.FORMS -> Intent(this, FormsActivity::class.java)
            Action.PAGES -> Intent(this, PagesActivity::class.java)
            Action.MERGE -> Intent(this, MergeActivity::class.java)
            Action.IMAGES_PDF -> Intent(this, ImagesToPdfActivity::class.java)
            Action.CREATE_PDF -> Intent(this, CreatePdfActivity::class.java)
            Action.CROP -> Intent(this, CropActivity::class.java)
            Action.OCR -> Intent(this, OcrActivity::class.java)
            Action.LINKS -> Intent(this, LinksActivity::class.java)
            Action.IMAGE_OCR -> Intent(this, ImageOcrActivity::class.java)
            Action.REDACT -> Intent(this, RedactActivity::class.java)
            Action.BOOKMARKS -> Intent(this, BookmarksActivity::class.java)
            Action.QR_SCAN -> Intent(this, QrScanActivity::class.java)
            Action.SCAN_PDF -> Intent(this, ScanToPdfActivity::class.java)
            Action.LOG -> Intent(this, LogActivity::class.java)
            else -> Intent(this, ToolsActivity::class.java)
                .putExtra(ToolsActivity.EXTRA_TOOL, action.name)
        }
        try {
            startActivity(intent)
        } catch (t: Throwable) {
            android.widget.Toast.makeText(this, t.message ?: "Could not open", android.widget.Toast.LENGTH_LONG).show()
        }
    }

    private fun buildRows(): List<HomeRow> = buildList {
        add(HomeRow.Header(R.string.section_create))
        add(HomeRow.Tool(ToolItem(R.string.tool_create_pdf, R.string.tool_create_pdf_desc, R.drawable.ic_add, Action.CREATE_PDF)))
        add(HomeRow.Tool(ToolItem(R.string.tool_images_pdf, R.string.tool_images_pdf_desc, R.drawable.ic_image_pdf, Action.IMAGES_PDF)))
        add(HomeRow.Tool(ToolItem(R.string.tool_qr, R.string.tool_qr_desc, R.drawable.ic_qr, Action.QR_SCAN)))
        add(HomeRow.Tool(ToolItem(R.string.tool_scan_pdf, R.string.tool_scan_pdf_desc, R.drawable.ic_scan, Action.SCAN_PDF)))

        add(HomeRow.Header(R.string.section_edit))
        add(HomeRow.Tool(ToolItem(R.string.tool_view, R.string.tool_view_desc, R.drawable.ic_view, Action.VIEW)))
        add(HomeRow.Tool(ToolItem(R.string.tool_annotate, R.string.tool_annotate_desc, R.drawable.ic_annotate, Action.ANNOTATE)))
        add(HomeRow.Tool(ToolItem(R.string.tool_forms, R.string.tool_forms_desc, R.drawable.ic_forms, Action.FORMS)))
        add(HomeRow.Tool(ToolItem(R.string.tool_crop, R.string.tool_crop_desc, R.drawable.ic_crop, Action.CROP)))

        add(HomeRow.Header(R.string.section_organize))
        add(HomeRow.Tool(ToolItem(R.string.tool_pages, R.string.tool_pages_desc, R.drawable.ic_pages, Action.PAGES)))
        add(HomeRow.Tool(ToolItem(R.string.tool_links, R.string.tool_links_desc, R.drawable.ic_link, Action.LINKS)))
        add(HomeRow.Tool(ToolItem(R.string.tool_merge, R.string.tool_merge_desc, R.drawable.ic_merge, Action.MERGE)))
        add(HomeRow.Tool(ToolItem(R.string.tool_split, R.string.tool_split_desc, R.drawable.ic_split, Action.SPLIT)))
        add(HomeRow.Tool(ToolItem(R.string.tool_bookmarks, R.string.tool_bookmarks_desc, R.drawable.ic_bookmark, Action.BOOKMARKS)))
        add(HomeRow.Tool(ToolItem(R.string.tool_pagenum, R.string.tool_pagenum_desc, R.drawable.ic_pagenum, Action.PAGENUM)))

        add(HomeRow.Header(R.string.section_security))
        add(HomeRow.Tool(ToolItem(R.string.tool_sign, R.string.tool_sign_desc, R.drawable.ic_sign, Action.SIGN)))
        add(HomeRow.Tool(ToolItem(R.string.tool_verify, R.string.tool_verify_desc, R.drawable.ic_verify, Action.VERIFY)))
        add(HomeRow.Tool(ToolItem(R.string.tool_protect, R.string.tool_protect_desc, R.drawable.ic_lock, Action.PROTECT)))
        add(HomeRow.Tool(ToolItem(R.string.tool_unlock, R.string.tool_unlock_desc, R.drawable.ic_unlock, Action.UNLOCK)))
        add(HomeRow.Tool(ToolItem(R.string.tool_watermark, R.string.tool_watermark_desc, R.drawable.ic_watermark, Action.WATERMARK)))
        add(HomeRow.Tool(ToolItem(R.string.tool_redact, R.string.tool_redact_desc, R.drawable.ic_redact, Action.REDACT)))

        add(HomeRow.Header(R.string.section_output))
        add(HomeRow.Tool(ToolItem(R.string.tool_compress, R.string.tool_compress_desc, R.drawable.ic_compress, Action.COMPRESS)))
        add(HomeRow.Tool(ToolItem(R.string.tool_metadata, R.string.tool_metadata_desc, R.drawable.ic_metadata, Action.METADATA)))
        add(HomeRow.Tool(ToolItem(R.string.tool_extract, R.string.tool_extract_desc, R.drawable.ic_extract, Action.EXTRACT)))
        add(HomeRow.Tool(ToolItem(R.string.tool_ocr, R.string.tool_ocr_desc, R.drawable.ic_ocr, Action.OCR)))
        add(HomeRow.Tool(ToolItem(R.string.tool_image_ocr, R.string.tool_image_ocr_desc, R.drawable.ic_image_pdf, Action.IMAGE_OCR)))
        add(HomeRow.Tool(ToolItem(R.string.tool_log, R.string.tool_log_desc, R.drawable.ic_log, Action.LOG)))
    }
}
