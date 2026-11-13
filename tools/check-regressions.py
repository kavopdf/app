#!/usr/bin/env python3
"""Fails the build if a commit's additions are not in the tree any more.

WHY THIS EXISTS
  On 13 Nov commit 995290a copied a whole verify_google.py from a clone taken four
  commits earlier, and wrote it over the tree. It was not a patch: it reverted
  2310c3b, 7fe434e and 54928a0 - six fixes, hours old, each verified green when it
  was committed - and prove_checks.py lost five mutations with it. Nothing failed.
  Every guard passed, because every guard reads the tree as it is and the tree was
  internally consistent. It was simply four commits older than it claimed to be.
  b242cfa repaired it. This is the check that would have refused it.

  A commit message is a claim. "three checks were blind to their own subject" is a
  claim. This measures the claim: of the lines a commit added, how many are still
  in the same file at HEAD. A fix whose lines are gone - and which was not itself a
  revert - did not survive, whatever the message says.

WHAT IT DOES
  1. for each of the last N non-merge, non-revert commits, take the lines it added
     to each file, and count how many of those exact lines are still in that file at
     HEAD (multiset match, so a duplicated line is counted once)
  2. flag a file when at least MIN_ADDED lines were added and under MIN_SURVIVAL of
     them survive - and name the commit that removed them, with its rewrite scale,
     because "545 deletions to fix three checks" is a whole-file copy and "35" is a
     later commit that deliberately replaced the line
  3. the reverse direction: a file the tree has and its parent did not, that the
     commit's own diff does not account for; and any file in the tree that no commit
     in history ever added

WHAT IT IS NOT
  It is not a correctness check. A line that survives can still be wrong, and a line
  that is gone can have been superseded on purpose - see tools/regressions-known.txt,
  which is where an explained flag goes, with the reason written down.

USAGE
  python3 tools/check-regressions.py                  # last 40 commits against HEAD
  python3 tools/check-regressions.py --commits 120    # a wider window
  python3 tools/check-regressions.py --at 995290a     # the tree as it was committed
  python3 tools/check-regressions.py --verbose        # every commit's survival, not just flags
  python3 tools/check-regressions.py --worktree       # compare against the files on disk,
                                                      # i.e. before the copy is committed

EXIT
  0  nothing unaccounted for
  1  an addition vanished, or a file appeared without a commit - do not commit
  2  could not run (no git, no history) - say so, do not commit blind
"""
import collections
import os
import re
import subprocess
import sys

# ---- thresholds, and why they are these numbers --------------------------------
# MIN_ADDED = 10: below ten added lines a survival fraction is noise. Two of the last
#   40 commits add 1 and 2 lines ("baseline: claim slot", "start run 13 Nov 11:05") and
#   read 0 % and 50 % because a slot file is overwritten by design. At ten lines the
#   smallest genuine fix in the window (859329c, 8 lines to one file) is still below it
#   and is measured as a whole commit, not per file.
# MIN_SURVIVAL = 0.50: the lowest survival of any commit in the last 40 that is still
#   in the tree on purpose is 78 % (c743aa2's patches README, edited in place since).
#   Everything real sits above 78 %, everything broken sits at 19 % or below. The
#   threshold is in the empty band between them, not at a round number for its own sake.
MIN_ADDED = 10
MIN_SURVIVAL = 0.50

# A commit that rewrote this much of a file did not patch it.
WHOLE_FILE = 0.30

KNOWN = "tools/regressions-known.txt"

REVERT = re.compile(r"^\s*revert\b", re.I)


def git(*args, check=False):
    p = subprocess.run(["git"] + list(args), capture_output=True, text=True)
    if p.returncode != 0 and check:
        raise SystemExit("could not run git %s: %s" % (" ".join(args), p.stderr.strip()))
    return p.stdout


def blob(rev, path):
    """The file at rev, as a Counter of lines, or None if it is not there."""
    p = subprocess.run(["git", "show", "%s:%s" % (rev, path)],
                       capture_output=True, text=True)
    if p.returncode != 0:
        return None
    return collections.Counter(p.stdout.splitlines())


def is_binary(rev, path):
    p = subprocess.run(["git", "show", "%s:%s" % (rev, path)],
                       capture_output=True)
    return b"\0" in p.stdout[:8000]


def diff_lines(rev, path, cache={}):
    """(added, removed) line lists for rev's change to path, against its first parent."""
    key = (rev, path)
    if key not in cache:
        out = git("diff", "--no-color", "-U0", "--no-renames", "--diff-filter=AM",
                  rev + "^", rev, "--", path)
        added, removed = [], []
        for line in out.splitlines():
            if line.startswith("+++") or line.startswith("---"):
                continue
            if line.startswith("+"):
                added.append(line[1:])
            elif line.startswith("-"):
                removed.append(line[1:])
        cache[key] = (added, removed)
    return cache[key]


def filesize(rev, path):
    b = blob(rev, path)
    return sum(b.values()) if b else 0


def load_known():
    """Waivers: '<sha>:<path>' or '<sha>' followed by a reason after '#'."""
    if not os.path.exists(KNOWN):
        return set()
    out = set()
    for line in open(KNOWN, encoding="utf-8"):
        line = line.split("#", 1)[0].strip()
        if line:
            out.add(line)
    return out


def main(argv):
    at = "HEAD"
    n = 40
    verbose = False
    worktree = False
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--at" and i + 1 < len(argv):
            at = argv[i + 1]; i += 2
        elif a.startswith("--at="):
            at = a.split("=", 1)[1]; i += 1
        elif a == "--commits" and i + 1 < len(argv):
            n = int(argv[i + 1]); i += 2
        elif a.startswith("--commits="):
            n = int(a.split("=", 1)[1]); i += 1
        elif a == "--verbose":
            verbose = True; i += 1
        elif a == "--worktree":
            worktree = True; i += 1
        else:
            print("unknown argument: %s" % a)
            return 2

    if subprocess.run(["git", "rev-parse", "--git-dir"],
                      capture_output=True).returncode != 0:
        print("FAIL: not a git repository - this check reads history and cannot run here")
        return 2
    # A shallow clone has no history to prove anything against: every file in the tree
    # would read as having no adding commit, which is a wall of FAILs that means one
    # thing. Say the one thing.
    if git("rev-parse", "--is-shallow-repository").strip() == "true":
        print("FAIL: this is a shallow clone - the history is not here, so no commit's "
              "additions can be checked and no file's origin can be proven")
        print("      run: git fetch --unshallow   (or run this where the full history is)")
        return 2
    revs = git("rev-list", "--no-merges", "-n", str(n), at).split()
    if not revs:
        print("FAIL: no commits at %s - nothing to check, so nothing is proven" % at)
        return 2

    # "This reverts commit <sha>" is a recorded intent to undo. Skipping the revert commit
    # itself is not enough: the commit it reverts is the one whose lines are gone, and it
    # would still be flagged. Collect the names it names.
    reverted = set()
    for line in git("log", "--all", "--format=%H%x00%B%x00", at).split("\0"):
        for m in re.finditer(r"This reverts commit ([0-9a-f]{7,40})", line):
            reverted.add(m.group(1))
    reverted = tuple(reverted)

    known = load_known()
    fails = []
    flags = 0
    checked = 0
    skipped_revert = 0
    head_blobs = {}

    def at_blob(path):
        if path not in head_blobs:
            if worktree:
                # The tree as it stands, not as it was committed. This is the mode that
                # catches the mistake before it is history: a whole-file copy sitting in
                # the working tree is compared against the commits that produced the file
                # it overwrote. 995290a was still a working-tree change until it was
                # committed - this is the only mode that would have stopped it landing.
                head_blobs[path] = (collections.Counter(
                    open(path, encoding="utf-8", errors="replace").read().splitlines())
                    if os.path.exists(path) else None)
            else:
                head_blobs[path] = blob(at, path)
        return head_blobs[path]

    for rev in revs:
        short = git("log", "-1", "--format=%h", rev).strip()
        subject = git("log", "-1", "--format=%s", rev).strip()
        body = git("log", "-1", "--format=%b", rev).strip()
        if REVERT.match(subject) or "This reverts commit" in body:
            skipped_revert += 1
            if verbose:
                print("  revert, skipped  %s  %s" % (short, subject[:60]))
            continue
        if reverted and rev.startswith(reverted):
            skipped_revert += 1
            if verbose:
                print("  reverted since, skipped  %s  %s" % (short, subject[:56]))
            continue
        checked += 1

        out = git("diff", "--no-color", "-U0", "--no-renames", "--diff-filter=AM",
                  rev + "^", rev)
        added = collections.defaultdict(list)
        cur = None
        for line in out.splitlines():
            if line.startswith("+++ b/"):
                cur = line[6:]
            elif line.startswith("+++") or line.startswith("---") or line.startswith("diff "):
                continue
            elif line.startswith("+") and cur:
                added[cur].append(line[1:])

        c_add = c_surv = 0
        for path, lines in sorted(added.items()):
            head = at_blob(path)
            if head is None:          # deleted or renamed away since - a separate event
                continue
            if not worktree and is_binary(at, path):
                continue
            want = collections.Counter(lines)
            got = sum(min(c, head[l]) for l, c in want.items())
            c_add += len(lines)
            c_surv += got
            if len(lines) < MIN_ADDED:
                continue
            frac = got / len(lines)
            if frac >= MIN_SURVIVAL:
                continue

            # It vanished. Who removed it, and how much of the file did that commit rewrite?
            gone = []
            for line, c in want.items():
                if head[line] < c:
                    gone.append(line)
            # Which commit took them? Count per line and name the one that accounts for
            # the most: the first commit to touch any single gone line is often an
            # unrelated edit to a comment beside it, and naming that one sends the reader
            # to the wrong place.
            tally = collections.Counter()
            if not worktree:   # an uncommitted change has no commit to blame
                for later in git("rev-list", "--no-merges", "--reverse",
                                 "%s..%s" % (rev, at), "--", path).split():
                    _, removed_l = diff_lines(later, path)
                    n = sum(1 for g in gone if g in removed_l)
                    if n:
                        tally[later] = n
            killer = None
            if worktree and gone:
                killer = ("the working tree - not committed yet", 0, 0, 0.0, len(gone), len(gone))
            elif tally:
                later, n = tally.most_common(1)[0]
                added_l, removed_l = diff_lines(later, path)
                size = filesize(later + "^", path) or 1
                killer = (git("log", "-1", "--format=%h %s", later).strip(),
                          len(added_l), len(removed_l), (len(removed_l) / size),
                          n, len(gone))

            key_file = "%s:%s" % (short, path)
            key_commit = short
            waived = key_file in known or key_commit in known
            flags += 1
            tag = "known" if waived else "FAIL:"
            scale = ""
            if killer:
                scale = (" | %d/%d gone lines removed by %s  (+%d/-%d, %.0f%% of the file)"
                         % (killer[4], killer[5], killer[0][:58], killer[1], killer[2],
                            killer[3] * 100))
                if killer[3] >= WHOLE_FILE:
                    scale += "  WHOLE-FILE REWRITE"
            print("%s %s %s - %.0f%% of %d added lines survive (%d left)%s"
                  % (tag, short, path, frac * 100, len(lines), got, scale))
            if not waived:
                fails.append("%s %s: %.0f%% of its %d added lines are still in %s"
                             % (short, path, frac * 100, len(lines),
                                ("the working tree" if worktree else "%s:%s" % (at, path))))
                if killer:
                    fails.append("        %d of %d gone lines removed by %s (+%d/-%d, "
                                 "%.0f%% of the file)"
                                 % (killer[4], killer[5], killer[0][:60], killer[1],
                                    killer[2], killer[3] * 100))
        if verbose:
            frac = (c_surv / c_add) if c_add else 1.0
            print("  %s  %5.1f%%  %4d/%-5d %s" % (short, frac * 100, c_surv, c_add,
                                                 subject[:58]))

    # ---- the reverse direction -------------------------------------------------
    # (a) a file the tree has and its parent did not, that the commit does not explain.
    #     Every addition should be visible in the diff that made it. When it is not, the
    #     file arrived by something other than a commit - a checkout, a copy, a restore.
    for rev in revs:
        # A root commit has no parent: every file in it is new and no diff can explain
        # any of them. Skipping is not leniency - there is nothing to compare against.
        if len(git("rev-list", "--parents", "-n", "1", rev).split()) < 2:
            continue
        short = git("log", "-1", "--format=%h", rev).strip()
        tree = set(git("ls-tree", "-r", "--name-only", rev).splitlines())
        parent = set(git("ls-tree", "-r", "--name-only", rev + "^").splitlines())
        new = tree - parent
        if not new:
            continue
        claimed = set()
        for line in git("diff", "--no-renames", "--name-status", rev + "^", rev).splitlines():
            parts = line.split("\t")
            if len(parts) >= 2:
                claimed.add(parts[-1])
        for path in sorted(new - claimed):
            flags += 1
            print("FAIL: %s has %s but its parent did not, and the commit does not add it"
                  % (short, path))
            fails.append("%s: %s appears in the tree with no commit accounting for it"
                         % (short, path))

    # (b) a file in the tree that no commit in history ever added.
    added_by = {}
    cur = None
    # --no-renames is load-bearing: with rename detection on, a file that is deleted and
    # re-added reads as a rename and its adding commit is lost. docs/planning/*.md are
    # exactly that (884177f added them, c51b870 re-added them after a revert) and they
    # were reported as having no origin until this flag went in.
    for line in git("log", "--no-merges", "--no-renames", "--diff-filter=A",
                    "--name-only", "--format=C %H", at).splitlines():
        if line.startswith("C "):
            cur = line[2:8]
        elif line.strip() and cur:
            added_by.setdefault(line.strip(), cur)
    for path in sorted(git("ls-tree", "-r", "--name-only", at).splitlines()):
        if path not in added_by:
            flags += 1
            print("FAIL: %s is in %s and no commit in history ever added it" % (path, at))
            fails.append("%s has no adding commit - its origin is not recorded" % path)

    print("")
    print("scanned %d commits at %s (%d reverted, skipped); %d file(s) flagged"
          % (checked, at, skipped_revert, flags))
    if fails:
        for x in fails:
            print("FAIL:", x) if not x.startswith("    ") else print(x)
        print("")
        print("An addition that is not in the tree did not happen. If a later commit")
        print("replaced it on purpose, say so in %s - 'sha:path  # why' - so the next" % KNOWN)
        print("reader does not have to work it out again.")
        return 1
    print("PASS: every commit in the window still has its additions in %s, and every "
          "file in the tree has a commit that added it"
          % ("the working tree" if worktree else at))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
