package com.kavopdf.app

import android.Manifest
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Bundle
import android.view.View
import androidx.activity.result.contract.ActivityResultContracts
import androidx.camera.core.Camera
import androidx.camera.core.CameraSelector
import androidx.camera.core.ExperimentalGetImage
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.ImageProxy
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.core.content.ContextCompat
import com.google.mlkit.vision.barcode.common.Barcode
import com.google.mlkit.vision.barcode.BarcodeScanner
import com.google.mlkit.vision.barcode.BarcodeScannerOptions
import com.google.mlkit.vision.barcode.BarcodeScanning
import com.google.mlkit.vision.common.InputImage
import com.kavopdf.app.databinding.ActivityQrScanBinding
import java.util.concurrent.Executors

/**
 * Reads any barcode or QR code the camera can see.
 *
 * The model is bundled with the app, so this works with no network at all. All
 * formats are enabled, and the same code is not reported twice in a row.
 */
class QrScanActivity : PdfActivity() {

    private lateinit var binding: ActivityQrScanBinding
    private val cameraExecutor = Executors.newSingleThreadExecutor()
    private var provider: ProcessCameraProvider? = null
    private var camera: Camera? = null
    private var scanner: BarcodeScanner? = null
    private var lastValue: String? = null
    private var lastAt = 0L
    private var paused = false
    private var torchOn = false

    private val askCamera =
        registerForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
            if (granted) startCamera() else toast(getString(R.string.msg_camera_needed))
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityQrScanBinding.inflate(layoutInflater)
        setContentView(binding.root)
        binding.toolbar.setNavigationOnClickListener { finish() }

        scanner = BarcodeScanning.getClient(
            BarcodeScannerOptions.Builder().setBarcodeFormats(Barcode.FORMAT_ALL_FORMATS).build()
        )

        binding.btnTorch.setOnClickListener { toggleTorch() }
        binding.btnGallery.setOnClickListener { pickImageLauncher.launch("image/*") }
        binding.btnAgain.setOnClickListener { resume() }
        binding.btnCopy.setOnClickListener {
            val v = lastValue ?: return@setOnClickListener
            (getSystemService(CLIPBOARD_SERVICE) as ClipboardManager)
                .setPrimaryClip(ClipData.newPlainText("KavoPDF", v))
            toast(getString(R.string.qr_copied))
        }
        binding.btnOpen.setOnClickListener { openDetected() }
        binding.btnShare.setOnClickListener {
            val v = lastValue ?: return@setOnClickListener
            val i = Intent(Intent.ACTION_SEND).apply { type = "text/plain"; putExtra(Intent.EXTRA_TEXT, v) }
            runCatching { startActivity(Intent.createChooser(i, null)) }
        }

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
            val analysis = ImageAnalysis.Builder()
                .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                .build()
            analysis.setAnalyzer(cameraExecutor) { proxy -> analyse(proxy) }
            runCatching {
                p.unbindAll()
                camera = p.bindToLifecycle(this, CameraSelector.DEFAULT_BACK_CAMERA, preview, analysis)
                binding.btnTorch.alpha = if (camera?.cameraInfo?.hasFlashUnit() == true) 0.85f else 0.35f
            }.onFailure { toast(getString(R.string.msg_camera_needed)) }
        }, ContextCompat.getMainExecutor(this))
    }

    /** Scan a code from a picture the user already has. */
    private val pickImageLauncher =
        registerForActivityResult(androidx.activity.result.contract.ActivityResultContracts.GetContent()) { uri ->
            if (uri == null) return@registerForActivityResult
            val bmp = runCatching {
                contentResolver.openInputStream(uri)?.use {
                    android.graphics.BitmapFactory.decodeStream(it)
                }
            }.getOrNull()
            if (bmp == null) {
                toast(getString(R.string.msg_failed, "image"))
                return@registerForActivityResult
            }
            val sc = scanner
            if (sc == null) {
                toast(getString(R.string.msg_failed, "scanner"))
                return@registerForActivityResult
            }
            sc.process(InputImage.fromBitmap(bmp, 0))
                .addOnSuccessListener { codes ->
                    val first = codes.firstOrNull()
                    if (first != null) onFound(first) else toast(getString(R.string.qr_none_found))
                }
                .addOnFailureListener { toast(getString(R.string.msg_failed, "scan")) }
        }

    @OptIn(ExperimentalGetImage::class)
    private fun analyse(proxy: ImageProxy) {
        val media = proxy.image
        val sc = scanner
        if (media == null || sc == null || paused) {
            proxy.close()
            return
        }
        val image = InputImage.fromMediaImage(media, proxy.imageInfo.rotationDegrees)
        sc.process(image)
            .addOnSuccessListener { codes -> codes.firstOrNull()?.let { onFound(it) } }
            .addOnCompleteListener { proxy.close() }
    }

    private fun onFound(code: Barcode) {
        val value = code.rawValue ?: return
        val now = System.currentTimeMillis()
        if (value == lastValue && now - lastAt < 2500) return
        lastValue = value
        lastAt = now
        paused = true
        com.kavopdf.app.util.AppLog.record(
            this, "QR scanned", describe(code.format)
        )
        runOnUiThread {
            binding.resultType.text = describe(code.format)
            binding.resultValue.text = value
            binding.resultCard.visibility = View.VISIBLE
            binding.reticle.visibility = View.INVISIBLE
        }
    }

    private fun describe(format: Int): String = when (format) {
        Barcode.FORMAT_QR_CODE -> "QR code"
        Barcode.FORMAT_CODE_128 -> "Code 128"
        Barcode.FORMAT_CODE_39 -> "Code 39"
        Barcode.FORMAT_CODE_93 -> "Code 93"
        Barcode.FORMAT_CODABAR -> "Codabar"
        Barcode.FORMAT_DATA_MATRIX -> "Data Matrix"
        Barcode.FORMAT_EAN_13 -> "EAN-13"
        Barcode.FORMAT_EAN_8 -> "EAN-8"
        Barcode.FORMAT_ITF -> "ITF"
        Barcode.FORMAT_UPC_A -> "UPC-A"
        Barcode.FORMAT_UPC_E -> "UPC-E"
        Barcode.FORMAT_PDF417 -> "PDF417"
        Barcode.FORMAT_AZTEC -> "Aztec"
        else -> "Barcode"
    }

    /** If the code is a link, open it; otherwise copy it. */
    private fun openDetected() {
        val v = lastValue ?: return
        val url = if (v.startsWith("http://") || v.startsWith("https://")) v
        else if (v.startsWith("www.")) "https://$v" else null
        if (url == null) {
            toast(getString(R.string.qr_not_a_link))
            return
        }
        runCatching { startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url))) }
            .onFailure { toast(getString(R.string.msg_failed, "no browser")) }
    }

    private fun resume() {
        lastValue = null
        paused = false
        binding.resultCard.visibility = View.GONE
        binding.reticle.visibility = View.VISIBLE
    }

    private fun toggleTorch() {
        val cam = camera ?: return
        if (!cam.cameraInfo.hasFlashUnit()) {
            toast(getString(R.string.qr_no_torch))
            return
        }
        torchOn = !torchOn
        cam.cameraControl.enableTorch(torchOn)
        binding.btnTorch.alpha = if (torchOn) 1f else 0.85f
    }

    override fun onDestroy() {
        super.onDestroy()
        runCatching { scanner?.close() }
        runCatching { cameraExecutor.shutdown() }
        provider = null
        camera = null
    }
}
