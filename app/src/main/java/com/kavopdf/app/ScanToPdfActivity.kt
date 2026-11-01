package com.kavopdf.app

import com.kavopdf.app.util.AppLog
import com.kavopdf.app.util.Files

import android.Manifest
import android.content.pm.PackageManager
import android.graphics.BitmapFactory
import android.os.Bundle
import android.view.Gravity
import android.widget.FrameLayout
import android.widget.ImageView
import android.widget.LinearLayout
import androidx.activity.result.contract.ActivityResultContracts
import androidx.camera.core.Camera
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageCapture
import androidx.camera.core.ImageCaptureException
import androidx.camera.core.ImageProxy
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.core.content.ContextCompat
import com.kavopdf.app.databinding.ActivityScanToPdfBinding
import com.kavopdf.app.engine.PdfEngine
import java.io.File
import java.util.concurrent.Executors

/**
 * Photograph pages with the camera and turn them into one PDF.
 *
 * Each shot is written straight to a JPEG in the app's own cache, so memory stays
 * flat no matter how many pages are captured, and the existing image-to-PDF path
 * does the assembly.
 */
class ScanToPdfActivity : PdfActivity() {

    private lateinit var binding: ActivityScanToPdfBinding
    private val cameraExecutor = Executors.newSingleThreadExecutor()
    private var provider: ProcessCameraProvider? = null
    private var camera: Camera? = null
    private var capture: ImageCapture? = null
    private var torchOn = false

    private val pages = ArrayList<File>()

    private val askCamera =
        registerForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
            if (granted) startCamera() else toast(getString(R.string.msg_camera_needed))
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityScanToPdfBinding.inflate(layoutInflater)
        setContentView(binding.root)
        binding.toolbar.setNavigationOnClickListener { finish() }
        binding.btnCapture.setOnClickListener { shoot() }
        binding.btnBuild.setOnClickListener { buildPdf() }
        binding.btnTorch.setOnClickListener { toggleTorch() }
        refresh()

        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA)
            == PackageManager.PERMISSION_GRANTED
        ) startCamera() else askCamera.launch(Manifest.permission.CAMERA)
    }

    private fun startCamera() {
        val future = ProcessCameraProvider.getInstance(this)
        future.addListener({
            val p = runCatching { future.get() }.getOrNull() ?: return@addListener
            provider = p
            val preview = Preview.Builder().build().also {
                it.setSurfaceProvider(binding.preview.surfaceProvider)
            }
            val ic = ImageCapture.Builder()
                .setCaptureMode(ImageCapture.CAPTURE_MODE_MINIMIZE_LATENCY)
                .build()
            capture = ic
            runCatching {
                p.unbindAll()
                camera = p.bindToLifecycle(this, CameraSelector.DEFAULT_BACK_CAMERA, preview, ic)
                binding.btnTorch.alpha = if (camera?.cameraInfo?.hasFlashUnit() == true) 0.85f else 0.35f
            }.onFailure { toast(getString(R.string.msg_camera_needed)) }
        }, ContextCompat.getMainExecutor(this))
    }

    private fun shoot() {
        val ic = capture ?: return
        binding.btnCapture.isEnabled = false
        ic.takePicture(cameraExecutor, object : ImageCapture.OnImageCapturedCallback() {
            override fun onCaptureSuccess(image: ImageProxy) {
                val f = File(Files.workDir(this@ScanToPdfActivity), "scan_" + System.currentTimeMillis() + ".jpg")
                val ok = runCatching {
                    val buf = image.planes[0].buffer
                    val bytes = ByteArray(buf.remaining())
                    buf.get(bytes)
                    f.writeBytes(bytes)
                    // make sure it really is a readable image before accepting it
                    val bm = BitmapFactory.decodeFile(f.absolutePath)
                    if (bm == null) { f.delete(); false } else { bm.recycle(); true }
                }.getOrDefault(false)
                image.close()
                runOnUiThread {
                    binding.btnCapture.isEnabled = true
                    if (ok) { pages.add(f); refresh() } else toast(getString(R.string.msg_failed, "capture"))
                }
            }

            override fun onError(e: ImageCaptureException) {
                runOnUiThread {
                    binding.btnCapture.isEnabled = true
                    AppLog.problem(applicationContext, "Capture", e)
                    toast(getString(R.string.msg_could_not_capture))
                }
            }
        })
    }

    private fun refresh() {
        val strip = binding.strip
        strip.removeAllViews()
        binding.countLabel.text =
            if (pages.isEmpty()) getString(R.string.scan_none)
            else getString(R.string.scan_count, pages.size)
        binding.btnBuild.isEnabled = pages.isNotEmpty()

        pages.forEachIndexed { index, file ->
            val cell = FrameLayout(this)
            cell.layoutParams = LinearLayout.LayoutParams(dp(76), dp(98)).also { it.marginEnd = dp(8) }
            val iv = ImageView(this)
            iv.layoutParams = FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT, FrameLayout.LayoutParams.MATCH_PARENT
            )
            iv.scaleType = ImageView.ScaleType.CENTER_CROP
            iv.contentDescription = getString(R.string.scan_count, index + 1)
            runCatching { iv.setImageBitmap(PdfEngine.decodeUpright(file, 400)) }
            cell.addView(iv)

            val del = ImageView(this)
            del.layoutParams = FrameLayout.LayoutParams(dp(26), dp(26), Gravity.TOP or Gravity.END)
            del.setImageResource(R.drawable.ic_close)
            del.setBackgroundColor(0x99000000.toInt())
            del.contentDescription = getString(R.string.action_delete)
            del.setOnClickListener { pages.removeAt(index); refresh() }
            cell.addView(del)
            strip.addView(cell)
        }
    }

    private fun buildPdf() {
        if (pages.isEmpty()) return toast(getString(R.string.scan_none))
        val inputs = ArrayList(pages)
        runAndSave("scan.pdf") { out -> PdfEngine.imagesToPdf(inputs, out) }
    }

    private fun toggleTorch() {
        val cam = camera ?: return
        if (!cam.cameraInfo.hasFlashUnit()) return toast(getString(R.string.qr_no_torch))
        torchOn = !torchOn
        cam.cameraControl.enableTorch(torchOn)
        binding.btnTorch.alpha = if (torchOn) 1f else 0.85f
    }

    override fun onDestroy() {
        super.onDestroy()
        runCatching { cameraExecutor.shutdown() }
        provider = null
        camera = null
        // the shots are only needed until the PDF is written
        pages.forEach { runCatching { it.delete() } }
        pages.clear()
    }

    private fun dp(v: Int): Int = (v * resources.displayMetrics.density).toInt()
}
