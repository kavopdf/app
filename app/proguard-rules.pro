# KavoPDF ProGuard / R8 rules.
#
# Minification is currently OFF, so none of this affects the shipped APK. It is written
# now so that switching minifyEnabled to true later is a one-line change rather than a
# debugging session. Every library the app reflects into is kept whole.

# ---- pdfbox / fontbox / bouncycastle (PDF engine) ----
-keep class com.tom_roush.pdfbox.** { *; }
-keep class com.tom_roush.fontbox.** { *; }
-keep class com.tom_roush.harmony.** { *; }
-keep class org.bouncycastle.** { *; }
-dontwarn com.tom_roush.**
-dontwarn org.bouncycastle.**
-dontwarn javax.**
-dontwarn java.awt.**
-dontwarn org.apache.**

# ---- ML Kit (text recognition + barcode) ----
-keep class com.google.mlkit.** { *; }
-keep class com.google.android.gms.internal.mlkit_vision_text_common.** { *; }
-keep class com.google.android.gms.internal.mlkit_vision_barcode.** { *; }
-dontwarn com.google.mlkit.**
-keep class com.google.android.gms.common.internal.** { *; }

# ---- CameraX ----
-keep class androidx.camera.** { *; }
-dontwarn androidx.camera.**

# ---- Kotlin coroutines ----
-keepnames class kotlinx.coroutines.internal.MainDispatcherFactory { *; }
-keepnames class kotlinx.coroutines.CoroutineExceptionHandler { *; }
-dontwarn kotlinx.coroutines.**

# ---- AndroidX / Material ----
-keep class androidx.appcompat.** { *; }
-keep class com.google.android.material.** { *; }
-dontwarn androidx.**

# ---- the app's own data classes (parcel / reflection) ----
-keep class com.kavopdf.app.engine.** { *; }
-keep class com.kavopdf.app.util.** { *; }

# Keep annotations and line numbers so a crash report still makes sense.
-keepattributes *Annotation*, Signature, InnerClasses, EnclosingMethod, SourceFile, LineNumberTable
-renamesourcefileattribute SourceFile
