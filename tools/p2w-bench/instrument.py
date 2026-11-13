#!/usr/bin/env python3
"""
instrument.py - how many checks are there, and which ones. Asked, never assumed.

WHY THIS FILE EXISTS
  A score is a count of passes, and a count means nothing without the set it was
  counted out of. On 13 Nov the p2w bench had three different answers to "how many
  checks": verify_google.py published 57, BASELINE.md said 59 on all 211 rows, and
  RATCHET.json said `out_of: 59` while carrying a `universe` list of 57 ids. Two
  checks had been dropped (02_text_run_count, 56_rtl_runs) and one replaced
  (20_within_10pt -> 20_line_placement), and no store noticed.

  ratchet.py could not notice either, because it compared the store's denominator
  against the store's denominator: `out_of == prev["out_of"]` is true for any
  number that is written twice.

  So the denominator is read from the instrument - `--list-checks` on the verifier
  itself - and from nowhere else. ratchet.py fails when a row disagrees with it;
  record.py stamps the digest on every row it writes, so two rows measured by two
  different instruments can never be added together without the difference being
  visible in the file.

  One function, two callers. The reason it is not duplicated in each of them is
  the reason it exists: two copies of "what is the universe" is the drift again.

  AND THE SAME BLINDNESS ONE LEVEL DEEPER (13 Nov, closed here)
  The id list names the universe. It does not name the QUESTIONS. Five checks
  changed their predicate while keeping their id - 32_stroke_lines, 22_reading_order,
  08_image_count, 18_displacement, 53_embedded_faces - and the id list is byte
  identical before and after every one of them:

      7b6ed92  32   drawing objects -> segments        id-sha 80d616987543 -> 80d616987543
      cc8644e  22   LCS over two extractors -> torn lines
      6692271  08   get_images() -> get_image_info()
      11517dc  18   absorbed 19_worst_dy's tail clause

  A mark taken under the old 22_reading_order was therefore compared, silently,
  against the new one. So the sha a row is stamped with now covers the id AND a
  digest of what the id asks - its body, extracted from the verifier's AST by
  checkbody.py. A redefined check moves the sha, and its marks go stale, exactly as
  a changed set already did. Both digests are kept and both are printed: the id-sha
  is what the older marks were stamped with, and saying which one moved is the
  difference between "a check was added" and "a question was changed".

USAGE
  python3 tools/p2w-bench/instrument.py            # print the live universe
  python3 tools/p2w-bench/instrument.py --txt      # the .txt half (t01..t05)
  python3 tools/p2w-bench/instrument.py --bodies   # id, body sha, id-sha, body-sha
  python3 tools/p2w-bench/instrument.py --diff OLD_verify_google.py
                                                   # which checks were redefined
"""
import hashlib
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import checkbody  # noqa: E402  - what each id ASKS, not just that it exists

# A check id is <number>_<words>, and the words can contain digits: 20_within_10pt,
# 43_within_10pt_x. The old pattern allowed [a-z_]+ only, so BOTH were silently
# dropped and the ratchet guarded neither - including the single largest class in
# the corpus. Measured 13 Nov: re.match on 20_within_10pt returned None while
# 18_median_dy matched. The .txt checks are t01..t05 rather than 01..59, so one
# pattern has to cover both or every .txt check vanishes.
CHECK_RE = re.compile(r"^(?:\d{2}[a-c]?|t\d{2})_[a-z0-9_]+$")

CACHE = {}
BODY_CACHE = {}

# A check id the AST could not find a body for is stamped with this instead of being
# left out. It must never equal a real digest, and it must be visible in the row: an
# id whose body cannot be found is an id whose redefinition cannot be seen.
NO_BODY = "nobody000000"


def tool_file(txt=False):
    return os.path.join(HERE, "verify_txt.py" if txt else "verify_google.py")


def body_map(txt=False):
    """({check id: body sha12}, error) for the verifier in use, read from its source.

    The ids come from the verifier itself (`--list-checks`, see live_universe); the
    bodies come from its AST. Both are needed and neither is derived from the other:
    a check added in a branch the AST walk does not reach would be an id with no
    body, and that is reported as an error rather than quietly stamped.
    """
    if txt in BODY_CACHE:
        return BODY_CACHE[txt]
    path = tool_file(txt)
    try:
        raw = checkbody.bodies_of_file(path)
        m = {k: v[0] for k, v in raw.items()}
        err = ""
    except Exception as e:
        m, err = {}, "%s could not be parsed for check bodies: %s" % (
            os.path.basename(path), e)
    BODY_CACHE[txt] = (m, err)
    return m, err


def universe_sha(ids, txt=False):
    """The name a row is stamped with: the ids AND the digest of what each one asks.

    Empty for an empty set, which is what a row that knows only its denominator
    carries - it has no set, so it can have no name either.
    """
    ids = sorted(ids)
    if not ids:
        return ""
    m, _err = body_map(txt)
    return hashlib.sha1(
        "\n".join("%s:%s" % (i, m.get(i, NO_BODY)) for i in ids).encode()
    ).hexdigest()[:12]


def live_universe(txt=False):
    """(sorted ids, sha12, error) for the verifier in use, asked right now.

    Discovery, not a hard-coded list: adding or dropping a check must move this
    number by itself, without anyone remembering to edit a store. The sha is what
    a row is stamped with, so two rows can be told apart without carrying 57
    strings each.
    """
    if txt in CACHE:
        return CACHE[txt]
    tool = "verify_txt.py" if txt else "verify_google.py"
    ids, err = [], ""
    try:
        out = subprocess.check_output(
            [sys.executable, os.path.join(HERE, tool), "--list-checks"],
            stderr=subprocess.DEVNULL, timeout=120, text=True)
        ids = sorted({l.strip() for l in out.splitlines()
                      if l.strip() and CHECK_RE.match(l.strip())})
        if not ids:
            err = "%s --list-checks printed no check ids" % tool
    except Exception as e:
        err = "%s --list-checks failed: %s" % (tool, e)
    if ids and not err:
        m, berr = body_map(txt)
        missing = [i for i in ids if i not in m]
        if berr:
            err = berr
        elif missing:
            # An id the AST cannot see a body for is an id this instrument cannot
            # prove is the same question. Saying so is the whole point of the file.
            err = ("%d check id(s) have no body in %s: %s"
                   % (len(missing), os.path.basename(tool_file(txt)),
                      ", ".join(missing[:6])))
    sha = universe_sha(ids, txt)
    CACHE[txt] = (ids, sha, err)
    return ids, sha, err


def digest(ids):
    """The OLD name for a set of check ids: the list only, no bodies.

    Kept, not deleted, because it is what every mark written before 13 Nov carries
    and a reader comparing an old stamp to a new one has to be able to compute it.
    Nothing stamps with it any more: two verifiers that differ only in what a check
    ASKS have the same digest(), which is the blind spot this file now closes. Use
    universe_sha() for anything written from here on.
    """
    ids = sorted(ids)
    return hashlib.sha1("\n".join(ids).encode()).hexdigest()[:12] if ids else ""


def redefined(old_path, txt=False):
    """(redefined ids, added, dropped) between a saved verifier and the live one."""
    old = checkbody.bodies_of_file(old_path)
    new, _err = body_map(txt)
    return (sorted(k for k in old if k in new and old[k][0] != new[k]),
            sorted(set(new) - set(old)), sorted(set(old) - set(new)))


def stamp_of(size):
    """The short universe stamp a store row carries: u57."""
    return "u%d" % size


def parse_stamp(s):
    """The size a stamp names, or None when the row carries no stamp."""
    m = re.match(r"^u(\d+)$", (s or "").strip())
    return int(m.group(1)) if m else None


def main(argv):
    txt = "--txt" in argv
    if "--diff" in argv:
        old = argv[argv.index("--diff") + 1]
        ids, sha, err = live_universe(txt)
        if not ids:
            print("instrument: %s" % err)
            return 2
        was, added, dropped = redefined(old, txt)
        oldm = checkbody.bodies_of_file(old)
        print("redefined (same id, different question): %d" % len(was))
        for k in was:
            print("  %-30s %s -> %s" % (k, oldm[k][0], body_map(txt)[0][k]))
        if added:
            print("added  : %s" % ", ".join(added))
        if dropped:
            print("dropped: %s" % ", ".join(dropped))
        print("id-sha   %s -> %s  %s"
              % (digest(oldm), digest(ids),
                 "SAME - the id list cannot see this" if digest(oldm) == digest(ids)
                 else "changed - the id list sees this one"))
        print("body-sha %s -> %s" % (universe_sha(oldm, txt), sha))
        return 0
    ids, sha, err = live_universe(txt)
    if not ids:
        print("instrument: %s" % err)
        return 2
    if "--bodies" in argv:
        m, berr = body_map(txt)
        for i in ids:
            print("%-32s %s" % (i, m.get(i, NO_BODY)))
        print("")
        print("%d checks; id-sha %s; body-sha %s%s"
              % (len(ids), digest(ids), sha, "" if not (err or berr) else
                 "  ERROR: " + (err or berr)), file=sys.stderr)
        return 0 if not err else 1
    for i in ids:
        print(i)
    print("")
    print("%s --list-checks = %d checks (id-sha %s, body-sha %s)"
          % ("verify_txt.py" if txt else "verify_google.py", len(ids),
             digest(ids), sha), file=sys.stderr)
    if err:
        print("instrument: %s" % err, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
