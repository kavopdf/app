package com.kavopdf.app

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import com.kavopdf.app.util.ThemeUtil

/**
 * What KavoPDF asks when a PDF is shared into it from another app.
 *
 * Reading a document and working on one are two different intentions, and the share sheet
 * cannot tell them apart. This screen asks once: open the reader, or go to the tool list with
 * the file already in hand.
 *
 * It owns no view of its own - it shows a dialog over whatever the user was looking at and
 * finishes immediately.
 */
class ShareChoiceActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        ThemeUtil.apply(this)
        super.onCreate(savedInstanceState)

        val uri = sharedPdf()
        if (uri == null) {
            finish()
            return
        }

        MaterialAlertDialogBuilder(this)
            .setTitle(R.string.share_choice_title)
            .setItems(
                arrayOf(
                    getString(R.string.share_choice_read),
                    getString(R.string.share_choice_tools)
                )
            ) { _, which ->
                if (which == 0) openReader(uri) else openTools(uri)
                finish()
            }
            .setOnCancelListener { finish() }
            .show()
    }

    /** The PDF the sharing app handed over, from either the share or the open intent. */
    private fun sharedPdf(): Uri? {
        val intent = intent ?: return null
        val raw = when (intent.action) {
            Intent.ACTION_SEND -> intent.getParcelableExtra(Intent.EXTRA_STREAM)
            else -> intent.data
        } ?: return null
        return runCatching { Uri.parse(raw.toString()) }.getOrNull()
    }

    private fun openReader(uri: Uri) {
        startActivity(
            Intent(this, ViewerActivity::class.java)
                .setData(uri)
                .addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        )
    }

    private fun openTools(uri: Uri) {
        startActivity(
            Intent(this, MainActivity::class.java)
                .putExtra(PdfActivity.EXTRA_SOURCE_URI, uri.toString())
                .addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                .addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP)
        )
    }
}
