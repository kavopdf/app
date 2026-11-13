#!/usr/bin/env python3
"""
test_bodysha.py - the instrument's name covers what each check ASKS.

The bug this proves closed: `universe_sha` was a digest of the ID LIST. Five checks
changed their predicate while keeping their id, so the digest was unchanged and a
mark taken under the old question was compared against the new one.

  1. a redefined check moves the body sha and NOT the id sha
  2. a comment-only edit moves neither (prose is not a question)
  3. a docstring-only edit moves neither
  4. an added check moves both
  5. record.py stamps the body sha, and the stamp it writes equals the live one
  6. ratchet.py compares a mark taken by the same instrument
  7. ... calls a mark stale when one check is redefined under it
  8. ... names the redefined check rather than only saying the stamp moved
  9. ... does NOT compare that mark (a stale mark is not a pass and not a fail)
 10. ... and compares again once the documents are re-measured under the new one
 11. instrument.py --diff reports the redefinition the id list cannot see

USAGE
  python3 tools/p2w-bench/test_bodysha.py
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import checkbody  # noqa: E402
import instrument  # noqa: E402

COPIES = ("ratchet.py", "instrument.py", "checkbody.py", "verify_google.py",
          "unmeasured.py", "record.py", "trace.py", "gate.py", "exempt.py")

results = []


def check(name, ok, why=""):
    results.append((name, ok, why))
    print("%s %-64s %s" % ("ok  " if ok else "FAIL", name, why))


def live_src():
    return open(os.path.join(HERE, "verify_google.py"), encoding="utf-8").read()


# ---- 1-4: what moves a body sha ------------------------------------------------
SRC = live_src()
BASE_BODIES = checkbody.bodies(SRC)
BASE_IDS = checkbody.id_sha(BASE_BODIES)
BASE_SHA = checkbody.universe_sha(BASE_BODIES)

# 08_image_count's predicate, changed without touching its id.
OLD_08 = 'checks["08_image_count"] = (s_imgs, g_imgs, g_imgs >= s_imgs)'
NEW_08 = 'checks["08_image_count"] = (s_imgs, g_imgs, g_imgs >= s_imgs - 1)'
assert OLD_08 in SRC, "the fixture line moved - update test_bodysha.py"
REDEF = SRC.replace(OLD_08, NEW_08)
rb = checkbody.bodies(REDEF)
redef, added, dropped = checkbody.moved(SRC, REDEF)
check("a redefined check moves its body sha",
      rb["08_image_count"][0] != BASE_BODIES["08_image_count"][0],
      "%s -> %s" % (BASE_BODIES["08_image_count"][0], rb["08_image_count"][0]))
check("... and leaves the ID LIST digest untouched - the old blind spot",
      checkbody.id_sha(rb) == BASE_IDS,
      "id-sha %s both sides" % BASE_IDS)
check("... and names exactly the check that moved", redef == ["08_image_count"],
      str(redef))
check("... and the whole-instrument name moves too",
      checkbody.universe_sha(rb) != BASE_SHA,
      "%s -> %s" % (BASE_SHA, checkbody.universe_sha(rb)))

# Prose is not a question: comments and docstrings must not invalidate a mark.
NOISY = SRC.replace(
    "def compare(src_path, gd_path, docx_path=None):",
    'def compare(src_path, gd_path, docx_path=None):\n    """A docstring nobody had before."""')
NOISY = NOISY.replace("    s_imgs = ", "    # a comment about images\n    s_imgs = ", 1)
NOISY = NOISY.replace("\n\n", "\n\n\n")            # blank lines and re-spacing
nb = checkbody.bodies(NOISY)
check("a comment, a docstring and blank lines move NO body sha",
      checkbody.universe_sha(nb) == BASE_SHA,
      "%d of %d bodies differ" % (sum(1 for k in nb if nb[k][0] != BASE_BODIES[k][0]),
                                  len(nb)))
check("... so the edit is not mistaken for a redefinition",
      checkbody.moved(SRC, NOISY)[0] == [], str(checkbody.moved(SRC, NOISY)[0]))

# An added check is a real change, and the id digest sees it - both must move.
PLUS = SRC.replace(
    OLD_08, OLD_08 + '\n    checks["61_probe_only"] = (0, 0, True)')
pb = checkbody.bodies(PLUS)
check("an ADDED check moves the id sha (the old guard's own case)",
      checkbody.id_sha(pb) != BASE_IDS, "%s -> %s" % (BASE_IDS, checkbody.id_sha(pb)))
check("... and the body sha", checkbody.universe_sha(pb) != BASE_SHA,
      checkbody.universe_sha(pb))
check("... and is reported as added, not as redefined",
      checkbody.moved(SRC, PLUS) == ([], ["61_probe_only"], []),
      str(checkbody.moved(SRC, PLUS)))

# A change inside a HELPER the check calls is the check's body too: 32_stroke_lines
# moved because _doc_rules changed, not because its own line did.
HELPER = SRC.replace("            if ov <= 0 or ov < overlap * L",
                     "            if ov <= 0 or ov < overlap * L * 0.9", 1)
check("a change to a helper a check calls moves that check's body",
      checkbody.bodies(HELPER)["32_stroke_lines"][0]
      != BASE_BODIES["32_stroke_lines"][0],
      "_rules_lost's overlap test -> 32_stroke_lines")
check("... and does not move a check that never calls it",
      checkbody.bodies(HELPER)["08_image_count"][0]
      == BASE_BODIES["08_image_count"][0],
      "08_image_count unchanged")

# The instrument's public name is the body one, and it agrees with checkbody.
ids, sha, err = instrument.live_universe(False)
check("instrument.live_universe returns the body sha", sha == BASE_SHA and not err,
      "sha %s err %r" % (sha, err))
check("instrument.universe_sha(ids) == the live stamp",
      instrument.universe_sha(ids) == sha, sha)
check("instrument.digest(ids) is still the id-list sha, kept for old marks",
      instrument.digest(ids) == BASE_IDS, instrument.digest(ids))
check("the AST finds a body for every id --list-checks prints",
      sorted(checkbody.bodies(SRC)) == ids,
      "%d ids, %d bodies" % (len(ids), len(checkbody.bodies(SRC))))


# ---- 5-10: ratchet behaviour in a sandbox --------------------------------------
def sandbox():
    d = tempfile.mkdtemp(prefix="bodysha-")
    p = os.path.join(d, "tools/p2w-bench")
    os.makedirs(p)
    for f in COPIES:
        src = os.path.join(HERE, f)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(p, f))
    return d, p


def write_store(p, docs, ids, sha, bodies, failed_one=None):
    """A store in which every doc was measured by the instrument named by `sha`."""
    rows, marks, table = [], {}, []
    for i, doc in enumerate(docs):
        failed = [failed_one] if (failed_one and i == 0) else []
        score = len(ids) - len(failed)
        rows.append({"doc": doc, "engine": "e1", "round": 1, "score": score,
                     "total": len(ids), "failed": failed, "universe": ids,
                     "universe_n": len(ids), "universe_sha": sha,
                     "universe_source": "values", "values": {}})
        marks[doc] = {"best": score, "out_of": len(ids), "failed": failed,
                      "universe": ids, "universe_n": len(ids), "universe_sha": sha,
                      "id_sha": checkbody.id_sha(ids),
                      "check_bodies": dict(bodies)}
        table.append("| %s | %d/%d | PASS | %s | e1 | 13 Nov | u%d |"
                     % (doc, score, len(ids), ", ".join(failed), len(ids)))
    open(os.path.join(p, "RESULTS.jsonl"), "w").write(
        "".join(json.dumps(r) + "\n" for r in rows))
    json.dump(marks, open(os.path.join(p, "RATCHET.json"), "w"), indent=2)
    open(os.path.join(p, "BASELINE.md"), "w").write(
        "# baseline\n\n| document | score | verdict | failed checks | engine | "
        "measured | universe |\n|---|---|---|---|---|---|---|\n" + "\n".join(table) + "\n")


def run(p, script, *args):
    r = subprocess.run([sys.executable, os.path.join(p, script)] + list(args),
                       cwd=os.path.dirname(os.path.dirname(p)),
                       capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


DOCS = ["doc_alpha", "doc_beta", "doc_gamma"]
bodies = {k: v[0] for k, v in BASE_BODIES.items()}
d, p = sandbox()
write_store(p, DOCS, ids, BASE_SHA, bodies)
rc, out = run(p, "ratchet.py")
check("a mark taken by the live instrument is COMPARED",
      "compared against a mark   : 3" in out and rc == 0,
      "exit %d" % rc)

# Now the same verifier with one check redefined and its id kept. This is 22_reading_order
# on cc8644e, reproduced in one line.
src_path = os.path.join(p, "verify_google.py")
open(src_path, "w").write(REDEF)
rc2, out2 = run(p, "ratchet.py")
check("a mark under a REDEFINED check is stale (same ids, new question)",
      "STALE marks" in out2 and "redefined" in out2.lower(),
      "exit %d" % rc2)
check("... and the redefined check is NAMED, not just counted",
      "08_image_count" in out2, "named in the report")
check("... and it is NOT compared (a stale mark is neither pass nor fail)",
      "compared against a mark   : 0" in out2 and rc2 != 0, "exit %d" % rc2)
check("... and the id list alone would have seen nothing",
      checkbody.id_sha(checkbody.bodies(REDEF)) == BASE_IDS,
      "id-sha unchanged on both sides of the redefinition")

# The cure: re-measure under the new instrument. The gate must go back to comparing.
new_bodies = {k: v[0] for k, v in checkbody.bodies(REDEF).items()}
write_store(p, DOCS, ids, checkbody.universe_sha(checkbody.bodies(REDEF)), new_bodies)
rc3, out3 = run(p, "ratchet.py")
check("re-measured under the new question, the gate compares again",
      "compared against a mark   : 3" in out3 and rc3 == 0, "exit %d" % rc3)
check("... so a redefinition costs a re-measure, not a blocked gate",
      "STALE marks" not in out3, "")

# 11: the diff report, over the same pair.
old_path = os.path.join(p, "OLD_verify_google.py")
open(old_path, "w").write(SRC)
rc4, out4 = run(p, "instrument.py", "--diff", old_path)
check("instrument.py --diff names the redefinition",
      "redefined" in out4 and "08_image_count" in out4, "exit %d" % rc4)
check("... and says the id list cannot see it",
      "SAME" in out4, "")

shutil.rmtree(d, ignore_errors=True)

print("")
bad = [n for n, ok, _ in results if not ok]
print("%d checks, %d passed, %d failed" % (len(results), len(results) - len(bad),
                                           len(bad)))
sys.exit(1 if bad else 0)
