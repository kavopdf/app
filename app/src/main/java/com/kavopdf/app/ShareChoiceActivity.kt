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
        // MERGE the accent into the theme the manifest declares. Do not replace it.
        //
        // ThemeUtil.apply() calls setTheme(), which swaps Theme.KavoPDF.Transparent for the
        // opaque accent theme - and that threw away the two things this screen is:
        // windowIsTranslucent, so the dialog floats over the app the PDF came from, and
        // windowAnimationStyle = @null, so it appears in place instead of sliding in like a
        // full screen. With both gone the screen animated as a plain activity, and it did so
        // differently depending on who launched it, because a share sheet starts it inside
        // the sending task and a file manager's "Open with" starts it in a new one.
        //
        // applyStyle takes only the items the accent theme actually declares - its colours -
        // and leaves every window attribute from Theme.KavoPDF.Transparent untouched.
        theme.applyStyle(ThemeUtil.themeRes(this), true)
        super.onCreate(savedInstanceState)

        val uri = sharedPdf()
        if (uri == null) {
            finish()
            return
        }

        val dialog = MaterialAlertDialogBuilder(this)
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
            .create()
        // MaterialAlertDialogBuilder draws its own window background and ignores the one
        // ThemeOverlay.KavoPDF.Dialog sets, so this dialog came out a shade lighter than
        // every other one in the app. Setting it here puts it back with the rest.
        dialog.window?.setBackgroundDrawableResource(R.drawable.bg_dialog_rounded)
        dialog.show()
    }

    /**
     * The PDF another app handed over.
     *
     * Two ways in, and the file travels differently in each, so both are read here:
     *
     *   ACTION_SEND - a share sheet. The file is in EXTRA_STREAM.
     *   ACTION_VIEW - "Open with" from a file manager or a browser. The file is in intent.data.
     *
     * This screen answers both (AndroidManifest.xml), so a PDF opened from a file manager
     * asks the same question a shared one does instead of landing in the reader with no way
     * back to the tools.
     */
    private fun sharedPdf(): Uri? {
        val intent = intent ?: return null
        if (intent.action == Intent.ACTION_VIEW) {
            intent.data?.let { return it }
        }
        // THE DECLARED TYPE IS THE FIX. getParcelableExtra is generic, and written without
        // an expected type - with the elvis below whose other side is `return null`, i.e.
        // Nothing - Kotlin left T unconstrained and the bytecode cast the result to Void:
        //
        //   java.lang.ClassCastException: android.net.Uri$HierarchicalUri cannot be cast to
        //   java.lang.Void, in ShareChoiceActivity, on every share from another app.
        //
        // `Uri?` forces T = Uri, so the cast is (Uri). Do not drop the annotation.
        val raw: Uri? = intent.getParcelableExtra(Intent.EXTRA_STREAM) ?: return null
        return raw
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
