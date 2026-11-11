package com.kavopdf.app

import android.content.ClipData
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import com.kavopdf.app.util.CrashGuard

/**
 * What KavoPDF asks when a PDF is shared into it from another app.
 *
 * Reading a document and working on one are two different intentions, and the share sheet
 * cannot tell them apart. This screen asks once: open the reader, or go to the tool list with
 * the file already in hand.
 *
 * It owns no view of its own - it shows a dialog over whatever the user was looking at and
 * finishes immediately.
 *
 * A SHARE TARGET MUST NEVER KILL THE APP. This is the only screen that can be launched by
 * another application, with an intent this app did not build, on a process that was not
 * running a moment ago. Anything that goes wrong here is reported and closed, never thrown:
 * a crash on this screen means the user taps a PDF in their file manager and the app they
 * chose simply disappears.
 */
class ShareChoiceActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // The theme stays the one the manifest declares - Theme.KavoPDF.Transparent, so the
        // dialog floats over the sending app. ThemeUtil.apply() used to run here and replace
        // it with the opaque accent theme, which threw away the translucency this screen
        // exists for. The accent still reaches the dialog: the transparent theme inherits
        // materialAlertDialogTheme from Theme.KavoPDF.
        try {
            ask()
        } catch (t: Throwable) {
            // Never let this screen take the process down. Report it and get out of the way.
            CrashGuard.problem(this, "ShareChoice:Opening", t)
            finish()
        }
    }

    private fun ask() {
        val uri = sharedPdf()
        if (uri == null) {
            finish()
            return
        }

        // androidx AlertDialog, not MaterialAlertDialogBuilder. Every other screen in this
        // app uses this one; this screen was the only place that required the activity theme
        // to carry the Material dialog attributes, which is one more thing that can be wrong
        // on a screen launched by someone else's intent.
        AlertDialog.Builder(this)
            .setTitle(R.string.share_choice_title)
            .setItems(
                arrayOf(
                    getString(R.string.share_choice_read),
                    getString(R.string.share_choice_tools)
                )
            ) { _, which ->
                try {
                    if (which == 0) openReader(uri) else openTools(uri)
                } catch (t: Throwable) {
                    CrashGuard.problem(this, "ShareChoice:Launch", t)
                }
                finish()
            }
            .setOnCancelListener { finish() }
            .show()
    }

    /**
     * The PDF the sharing app handed over.
     *
     * Three places it can be, in the order Android puts it there:
     *
     * 1. `EXTRA_STREAM` - what a share sheet normally sends. Read with the typed accessor on
     *    API 33+, because the untyped one is deprecated and can hand back a class this
     *    process cannot cast.
     * 2. `clipData` - newer senders attach the file here instead, and an intent with a null
     *    `EXTRA_STREAM` is common enough that treating it as "no file" loses the share.
     * 3. `intent.data` - not expected from ACTION_SEND, but it costs one line to accept.
     */
    private fun sharedPdf(): Uri? {
        val intent = intent ?: return null

        val stream: Uri? = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            intent.getParcelableExtra(Intent.EXTRA_STREAM, Uri::class.java)
        } else {
            @Suppress("DEPRECATION")
            runCatching { intent.getParcelableExtra(Intent.EXTRA_STREAM) as? Uri }.getOrNull()
        }
        if (stream != null) return stream

        val fromClip = intent.clipData
            ?.takeIf { it.itemCount > 0 }
            ?.getItemAt(0)
            ?.uri
        if (fromClip != null) return fromClip

        return intent.data
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
        intent.clipData = ClipData.newRawUri("", uri)
        startActivity(intent)
    }
}
