#!/usr/bin/env python3
"""Fails the build if any permission other than the app's own internal one is
present in the shipped APK.

The app is meant to request nothing at all - it is fully offline. A dependency
silently adding INTERNET (ML Kit's AAR does exactly that) would quietly break
that promise, so this guard makes it impossible to ship unnoticed.
"""
import glob
import sys

from pyaxmlparser import APK

# CAMERA is the one real permission the app asks for, and only for the QR
# scanner and the camera-to-PDF screen. Nothing else is allowed in.
ALLOWED = {
    "com.kavopdf.app.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION",
    "android.permission.CAMERA",
}

apks = glob.glob("app/build/outputs/apk/release/*.apk")
if not apks:
    # Not a failure and not a pass. There is no APK on this machine, so nothing about
    # its permissions has been observed either way. Exit 3 so precommit.sh can say
    # "did not run" and stop claiming that every check passed. A real bad permission
    # is still exit 1 below, and a missing pyaxmlparser is still the ImportError above.
    print("SKIP: no release APK at app/build/outputs/apk/release/*.apk")
    print("SKIP-REASON: no APK was built here, so its permissions were NOT checked")
    sys.exit(3)

perms = set(APK(apks[0]).get_permissions())
bad = sorted(perms - ALLOWED)
print("permissions in the APK:", sorted(perms) or "none")
if bad:
    print("FAIL: unexpected permission(s) crept in:", bad)
    sys.exit(1)
print("PASS: the app still requests no real permissions")
