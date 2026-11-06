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

    /**
     * The PDF the sharing app handed over.
     *
     * This screen is registered for ACTION_SEND only (AndroidManifest.xml), so the file is
     * always the EXTRA_STREAM. The ACTION_VIEW filter - where the file would arrive as
     * intent.data - belongs to ViewerActivity, so reading intent.data here would be a branch
     * that can never run.
     */
    private fun sharedPdf(): Uri? {
        val intent = intent ?: return null
        val raw = intent.getParcelableExtra(Intent.EXTRA_STREAM) ?: return null
        return runCatching { Uri.parse(raw.toString()) }.getOrNull()
    }

    private fun openReader(uri: Uri) {
        startActivity(
            Intent(this, ViewerActivity::class.java)
                .setData(uri)
                .addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        )
    }

    /**
     * FLAG_GRANT_READ_URI_PERMISSION grants access to the URI in the intent's data or its
     * ClipData - not to a URI sitting in an extra as a string. The reader path used setData,
     * so it worked; this one used putExtra, so the flag granted nothing, the tool screen got
     * a URI it was not allowed to open, and every tool answered "this file couldn't be read".
     *
     * The URI still travels as a string extra because that is what the tool screens read, but
     * it is also set as ClipData so the permission has something to attach to.
     */
    private fun openTools(uri: Uri) {
        val intent = Intent(this, MainActivity::class.java)
            .putExtra(PdfActivity.EXTRA_SOURCE_URI, uri.toString())
            .addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            .addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP)
        // Set as a property, not chained: Kotlin maps setClipData/getClipData to a property,
        // and the setter returns Unit, so ".setClipData(x).addFlags(y)" does not compile.
        intent.clipData = android.content.ClipData.newRawUri("", uri)
        startActivity(intent)
    }
}
