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

USAGE
  python3 tools/p2w-bench/instrument.py            # print the live universe
  python3 tools/p2w-bench/instrument.py --txt      # the .txt half (t01..t05)
"""
import hashlib
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# A check id is <number>_<words>, and the words can contain digits: 20_within_10pt,
# 43_within_10pt_x. The old pattern allowed [a-z_]+ only, so BOTH were silently
# dropped and the ratchet guarded neither - including the single largest class in
# the corpus. Measured 13 Nov: re.match on 20_within_10pt returned None while
# 18_median_dy matched. The .txt checks are t01..t05 rather than 01..59, so one
# pattern has to cover both or every .txt check vanishes.
CHECK_RE = re.compile(r"^(?:\d{2}[a-c]?|t\d{2})_[a-z0-9_]+$")

CACHE = {}


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
    sha = digest(ids)
    CACHE[txt] = (ids, sha, err)
    return ids, sha, err


def digest(ids):
    """A short, stable name for a set of check ids. Empty for an empty set."""
    ids = sorted(ids)
    return hashlib.sha1("\n".join(ids).encode()).hexdigest()[:12] if ids else ""


def stamp_of(size):
    """The short universe stamp a store row carries: u57."""
    return "u%d" % size


def parse_stamp(s):
    """The size a stamp names, or None when the row carries no stamp."""
    m = re.match(r"^u(\d+)$", (s or "").strip())
    return int(m.group(1)) if m else None


def main(argv):
    txt = "--txt" in argv
    ids, sha, err = live_universe(txt)
    if not ids:
        print("instrument: %s" % err)
        return 2
    for i in ids:
        print(i)
    print("")
    print("%s --list-checks = %d checks (sha %s)"
          % ("verify_txt.py" if txt else "verify_google.py", len(ids), sha),
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
