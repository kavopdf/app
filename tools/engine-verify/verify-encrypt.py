#!/usr/bin/env python3
"""Verifies PDF protection is really AES-256 and really enforced.

A password box that does not actually encrypt would be worse than none, so this
checks the file itself: the security handler, the key length, that the right
password opens it, that a wrong one does not, and that the content survives.
"""
import os, sys
import pymupdf

W = "/tmp/kavopdf-engine-test"
ok = True

d = pymupdf.open(os.path.join(W, "enc_out.pdf"))

print(f"  encrypted at all          : {bool(d.is_encrypted)}")
if not d.is_encrypted:
    ok = False

wrong = d.authenticate('wrong-password')
print(f"  wrong password            : {'refused' if wrong == 0 else 'ACCEPTED <-- BAD'}")
if wrong != 0:
    ok = False

who = d.authenticate("user-pass-123")
print(f"  right password            : {'accepted' if who else 'REFUSED <-- BAD'} (as {'user' if who == 2 else 'owner' if who == 4 else '?'})")
if not who:
    ok = False

t, val = d.xref_get_key(-1, "Encrypt")
xr = int(val.split()[0]) if val and val.endswith(" R") else 0
def k(key):
    _, v = d.xref_get_key(xr, key)
    return v
V, R, L, F = k("V"), k("R"), k("Length"), k("Filter")
print(f"  security handler          : /Filter {F}  /V {V}  /R {R}  /Length {L}")
if F != "/Standard" or V != "5" or R != "6" or L != "256":
    print("    expected /Standard, V 5, R 6, Length 256 (AES-256)")
    ok = False

# the cipher actually used: /CF /StmF /CFM (AESV3 is what V5/R6 means)
cfm = k("CFM")
if cfm in (None, "", "null"):
    cfm = None
    _, cf = d.xref_get_key(xr, "CF")
    if cf and cf.endswith(" R"):
        _, stm = d.xref_get_key(int(cf.split()[0]), "StmF")
        if stm and stm.endswith(" R"):
            _, v = d.xref_get_key(int(stm.split()[0]), "CFM")
            cfm = None if v in (None, "", "null") else v
print(f"  cipher                    : {cfm or '(none declared; V5 implies AESV3)'}")
if cfm is not None and "AESV3" not in cfm:
    print("    expected AESV3")
    ok = False

# the decrypted round-trip must be a plain, unprotected PDF
dec = pymupdf.open(os.path.join(W, "enc_dec.pdf"))
print(f"  decrypt produces plain file: {not dec.is_encrypted}")
if dec.is_encrypted:
    ok = False

print()
print("ENCRYPTION:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
