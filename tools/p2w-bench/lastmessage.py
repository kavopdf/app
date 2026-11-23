#!/usr/bin/env python3
"""lastmessage.py - store the exact text the run is about to send, so it can be read afterwards.

WHY THIS EXISTS. The cron delivers the fixer's final message to the user's chat and stores nothing.
`cron runs` returns output_summary: null for every run, so the one text the user actually reads exists
only in their chat window. Twice on 18 Nov the only way to see it was for the user to export the cron
page to a PDF and attach it - and the PDF carries the whole prompt too, seven pages of it.

report.py writes LAST-MESSAGE.md from what it printed, but the run then adds the three things only it
knows (the prose headline, the verdict per idea, why the silence happened) - so the file and the
message drift apart by exactly the parts that matter.

This closes that: the run writes its finished message here, commits it, then sends the same text.

    python3 tools/p2w-bench/lastmessage.py --file /tmp/report.md
    python3 tools/p2w-bench/lastmessage.py --check        # is the file there and non-trivial?
"""
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "LAST-MESSAGE.md")
MIN = 400


def out_path(cron):
    """Which state file a report for this cron may write.

    ONE FILE PER CRON, BECAUSE ONE FILE WAS NOT ENOUGH. `OUT` used to be LAST-MESSAGE.md for every
    caller, so a watchdog pass that ran `lastmessage.py --file /tmp/report.md` (its prompt does not
    pass `--for`) wrote a WATCHDOG table into the FIXER's committed message. Measured 20 Nov: the
    fixer's real handoff was replaced by a watchdog report and had to be restored from git by hand;
    a pass that forgot would leave the next fixer run reading someone else's numbers. BLOCKERS.md
    row 2026-11-20 12:11 asked for exactly this - either a watchdog-only path or a refusal.

    The fixer keeps LAST-MESSAGE.md: the fixer's prompt names that file, and it is the message the
    chat actually delivers. Every other cron gets its own file and can no longer reach it.
    """
    c = (cron or "").strip().lower()
    if c in ("", "fix", "fixer"):
        return OUT
    return os.path.join(HERE, "LAST-MESSAGE-%s.md" % c)

# Rows of the Progress table that MUST equal report.py's own value. Everything else in the
# message is the run's to write: the headline, the per-idea verdicts, why the silence
# happened, the subagent durations. These are not.
BACKED_ROWS = (
    "documents improved this run",
    "documents improved, round total",
    "corpus improvement vs 15 nov",
    "regressions",
    "exempt, not measured",
    "fixed to 99%",
    "moved but still open",
    "classes solved",
    "committed",
)

_NUM = re.compile(r"-?\d[\d,]*\.?\d*")


def _numbers(cell):
    """Every number in a table cell, in order, with commas and bold stripped."""
    # Cut at the first backtick: what follows is a file name or a document name, and a
    # commit sha or a document called `300_prescription_rx` is not a number this row is
    # making a claim about.
    c = cell.split("`")[0]
    c = c.replace("**", "").replace("\u2014", " ").replace("\u2192", " ")
    return [n.replace(",", "") for n in _NUM.findall(c)]


def progress_rows(text):
    """{lower-cased label: cell} for the Progress table of a report.

    The table is the one whose rows look like `| label | value |` and which sits under a
    `## Progress` heading. Reading only that table keeps a number in the prose from being
    compared against a number in a table, which would be a false alarm.
    """
    out = {}
    inside = False
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("## "):
            inside = s.lower().startswith("## progress")
            continue
        if not inside or not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 2:
            continue
        label = cells[0].replace("**", "").replace("`", "").strip().lower()
        if not label or set(label) <= set(":- "):
            continue
        out[label] = cells[1]
    return out


def report_py_rows():
    """Run report.py and read its Progress table. None when it cannot be run."""
    try:
        r = subprocess.run([sys.executable, os.path.join(HERE, "report.py")],
                           capture_output=True, text=True, timeout=280)
        if r.returncode != 0 or "## Progress" not in r.stdout:
            return None
        return progress_rows(r.stdout)
    except Exception:
        return None


def verify(text):
    """Compare the report's Progress rows against report.py. Returns (problems, checked)."""
    mine = progress_rows(text)
    theirs = report_py_rows()
    if theirs is None:
        return None, 0
    problems = []
    checked = 0
    for label in BACKED_ROWS:
        if label not in mine:
            continue
        if label not in theirs:
            problems.append("%-38s in the message but report.py has no such row" % label)
            continue
        a, b = _numbers(mine[label]), _numbers(theirs[label])
        checked += 1
        # The FIRST number is the claim. The rest are compared only when both sides carry
        # the same count, because a row may name a document in backticks on one side and in
        # plain text on the other - `1 - 416_many_tiny_pages` against `1 - 416` is the same
        # claim twice, and refusing it would teach a run to distrust a working check.
        same = (a[:1] == b[:1]) and (len(a) != len(b) or a == b)
        if not same:
            problems.append("%-38s message %s  !=  report.py %s" % (label, a, b))
    for label, cell in mine.items():
        if label in BACKED_ROWS:
            continue
        if label in theirs:
            continue
        # A row nobody backs. It is allowed only if it carries no number.
        if _numbers(cell):
            problems.append("%-38s carries %s and no tool produces this row"
                            % (label, _numbers(cell)))
    return problems, checked


def _report_md():
    """report.py's own markdown, or None."""
    try:
        r = subprocess.run([sys.executable, os.path.join(HERE, "report.py")] + _for_args(),
                           capture_output=True, text=True, timeout=120, cwd=os.path.dirname(HERE))
        return r.stdout if r.returncode == 0 else None
    except Exception:
        return None


def _section(md, title):
    """The body of one `## title` section, up to the next `## `."""
    out, on = [], False
    for line in (md or "").splitlines():
        if line.startswith("## "):
            on = line[3:].strip().lower() == title.lower()
            continue
        if on:
            out.append(line)
    return "\n".join(out).strip()


# THE SECTIONS THAT MUST BE REPORT.PY'S, WORD FOR WORD. These are the ones that carry numbers a run
# has got wrong: the .txt counts, and the clock. The rest of the message is the run's to write - the
# headline, the verdict per idea, why a silence happened - and those are prose, not figures.
COPIED_SECTIONS = ("The txt", "Timing")


def verify_sections(text):
    """Every line of report.py's txt and timing tables must appear in the message unchanged."""
    md = _report_md()
    if md is None:
        return []
    problems = []
    for title in COPIED_SECTIONS:
        want = _section(md, title)
        if not want:
            continue
        # The rows that carry a number. A separator or an empty cell cannot be got wrong.
        for line in want.splitlines():
            line = line.strip()
            if not line or set(line) <= set("|:- "):
                continue
            if not re.search(r"\d", line):
                continue
            if line not in text:
                problems.append("%s: this row from report.py is missing or altered:\n      %s"
                                % (title, line[:110]))
    return problems


def _for_args():
    """The `--for <cron>` pair this invocation was given, or nothing."""
    for i, a in enumerate(sys.argv):
        if a == "--for" and i + 1 < len(sys.argv):
            return ["--for", sys.argv[i + 1]]
    return []


def _report_json():
    """report.py's own numbers, as a dict. None when it cannot be read."""
    import json
    try:
        r = subprocess.run([sys.executable, os.path.join(HERE, "report.py"), "--json"] + _for_args(),
                           capture_output=True, text=True, timeout=120, cwd=os.path.dirname(HERE))
        if r.returncode != 0 or not r.stdout.strip():
            return None
        return json.loads(r.stdout)
    except Exception:
        return None


_HHMM = re.compile(r"(\d{1,2}):(\d{2})")


def verify_facts(text, data):
    """Compare the report's PROSE against report.py - the timing, the corpus size, the .txt, the agents.

    WHY THIS EXISTS. verify() above checks the Progress table and nothing else, and every wrong
    number the 19 Nov run printed lived outside that table:

      * the header said "slot 16:11 -> 17:18 IST - 1h 07m". RUN.json says the slot ended at 17:00
        and lasted 48 minutes. The run wrote the clock it was looking at, not the one it recorded,
        and over-reported its own runtime by nineteen minutes.
      * every sentence about the corpus said "of 212". The corpus is 213; 212 is the intersection of
        the baseline table and the current one, because 416_many_tiny_pages was exempt when the
        baseline was taken. Two different quantities, one word.
      * "29 files in 7 commit(s) from 0b8c821" - it was 25 files in 8 commits, and only three of them
        came after 0b8c821.
      * the .txt was not mentioned at all, and an agent's window was given as "16:22 -> 16:32" with
        nothing behind it.

    A number a run types is a number a run can get wrong. These are the ones it types most.
    """
    if not data:
        return ["report.py --json could not be read - nothing in this message is verified"]
    problems = []
    run = data.get("run") or {}
    co = data.get("corpus") or {}
    tx = data.get("txt") or {}

    # ---- 1. THE HEADER'S CLOCK ------------------------------------------------------------
    head = "\n".join(text.splitlines()[:12])
    # A RUN THAT IS STILL GOING HAS NO END CLOCK, AND report.py SAYS SO.
    #
    # report.py writes "slot 18:00 → running IST · 41 min" while the slot is open, because
    # RUN.json has no ended clock yet - that is the honest header, and it is the only one a
    # live run can write. This check demanded a clock at both ends, so it REFUSED the report
    # report.py had just produced, every time, and no run could commit a report while it was
    # still working. The end is checked only when there is one to check; the start and the
    # duration are checked either way, which is what the 19 Nov over-reporting was about.
    m = re.search(r"slot\s+(\d{1,2}:\d{2})\s*(?:→|->|—)\s*(\d{1,2}:\d{2}|running)\s*IST", head)
    if not m:
        problems.append("header: no 'slot HH:MM -> HH:MM IST' window, so the timing cannot be checked")
    elif run.get("present"):
        if m.group(1) != (run.get("started") or ""):
            problems.append("header: start %s, report.py says %s" % (m.group(1), run.get("started")))
        if m.group(2) != "running" and m.group(2) != (run.get("ended") or ""):
            problems.append("header: end %s, report.py says %s" % (m.group(2), run.get("ended")))
    # the duration, wherever it appears in the first twelve lines
    mins = run.get("minutes")
    if isinstance(mins, int) and mins > 0:
        for hh, mm in _HHMM.findall(head):
            pass
        d = re.search(r"(\d+)\s*h\s*(\d+)\s*m|(\d+)\s*min", head)
        if d:
            claimed = (int(d.group(1)) * 60 + int(d.group(2))) if d.group(1) else int(d.group(3))
            if abs(claimed - mins) > 1:
                problems.append("header: duration %d min, report.py says %d min" % (claimed, mins))

    # ---- 2. THE CORPUS SIZE ---------------------------------------------------------------
    docs = co.get("docs")
    # A ROW COPIED FROM report.py IS NOT A NUMBER THIS RUN TYPED.
    #
    # report.py's own .txt table says "Scored | **213** of 213" - the .txt corpus is 213 - while the
    # .docx corpus this check compares against is 212, because 416_many_tiny_pages is exempt. So the
    # section the validator REQUIRES (verify_sections) was refused by the number check in the same
    # file, and no report could pass. Measured 22 Nov 23:5x: the fixer report was refused for a row
    # it had copied verbatim. Lines that appear in REPORT.md are checked against report.py by
    # verify_sections, character for character; they are skipped here.
    _copied = set()
    _md = _report_md()
    if _md:
        _copied = {l.strip() for l in _md.splitlines()}
    if isinstance(docs, int) and docs > 0:
        # ONLY A NUMBER NEAR THE CORPUS SIZE CAN BE A CLAIM ABOUT THE CORPUS. "5 of 10" is a
        # class's documents and "of 22" is a batch; flagging those teaches a run to ignore the
        # check, which is worse than not having it. A corpus claim is always in the hundreds.
        for n in re.findall(r"of\s+\*{0,2}(\d{2,4})\*{0,2}\b", text):
            v = int(n)
            if not (100 <= v <= 400):
                continue
            _line = text[max(0, text.rfind("\n", 0, text.find("of " + n)) + 1):]
            _line = _line.split("\n", 1)[0].strip()
            if _line in _copied:
                continue
            if v != docs and v != co.get("compared"):
                problems.append("corpus: 'of %s' appears, the corpus is %d (compared: %s)"
                                % (n, docs, co.get("compared")))
                break

    # ---- 3. THE .TXT ----------------------------------------------------------------------
    # ONLY IF THIS CRON'S REPORT IS SUPPOSED TO CARRY IT. The classifier and the APK report do not
    # have a .txt section - report.py's --for does not give them one - so demanding the counts there
    # would refuse every classifier report for a section it was never meant to have.
    cron = "fixer"
    for i, a in enumerate(sys.argv):
        if a == "--for" and i + 1 < len(sys.argv):
            cron = sys.argv[i + 1].strip().lower()
    wants_txt = cron in ("fixer", "baseline")
    if tx.get("available") and wants_txt:
        scored, clean, failing = tx.get("scored"), tx.get("clean"), tx.get("failing")
        if not re.search(r"\.txt|\btxt\b", text, re.I):
            problems.append("txt: the .txt is not mentioned at all (%d scored, %d clean, %d failing)"
                            % (scored, clean, failing))
        else:
            tail = text[text.lower().find(".txt"):] if ".txt" in text.lower() else text
            for want, name in ((clean, "clean"), (failing, "failing")):
                if isinstance(want, int) and str(want) not in text:
                    problems.append("txt: %d %s in report.py, that number is not in the message"
                                    % (want, name))
                    break

    # ---- 4. THE AGENTS' TIMINGS -----------------------------------------------------------
    agents = data.get("subagents")
    rows = agents if isinstance(agents, list) else (agents or {}).get("agents") or []
    for a in rows:
        aid = (a.get("id") or "")[:12]
        if not aid:
            continue
        dep, land = a.get("deployed_at"), a.get("landed_at")
        if dep and dep not in text:
            problems.append("agent %s: deployed_at %s is not in the message" % (aid, dep))
        if land and land not in text:
            problems.append("agent %s: landed_at %s is not in the message" % (aid, land))
        mins = a.get("minutes")
        # A ZERO WAS NEVER CHECKED, so a report could say an agent worked 0 min and pass. Worse,
        # "0 min" was TRUE of the recording and false about the work: deployed_at and landed_at
        # were both written in UTC at the moment the record was written, so 30 of 62 agents had
        # identical stamps and every one reported zero while producing real findings.
        #
        # So a zero must now be explained. Either the message says the duration is not recorded,
        # or it says the agent did nothing - and if it says neither, the report is refused.
        if isinstance(mins, int) and mins == 0:
            if "not recorded" not in text and "0 min" not in text:
                problems.append(
                    "agent %s: recorded 0 min and the message does not say why - write "
                    "\"not recorded\" when the stamps cannot measure it, or say it did nothing" % aid)
        elif isinstance(mins, int) and mins > 0 and str(mins) not in text:
            problems.append("agent %s: worked %d min, that number is not in the message" % (aid, mins))
    return problems


# ---------------------------------------------------------------- gverify and health
#
# THESE TWO CRONS HAD NO VERIFICATION AT ALL. report.py and lastmessage.py covered the baseline, the
# classifier, the fixer and the APK; the gverify and watchdog reports were prose a run wrote by hand,
# and the only thing standing between a number and the message was the run's own care. The two
# reports audited on 20 Nov were accurate - and nothing would have caught them if they had not been.
#
# The check is the same one that makes the others trustworthy: every number in the message must be
# one the tool actually printed. A run cannot type a count it did not measure, because the count it
# typed is compared against the tool's own output character for character.

# ANY LENGTH. This read `\d{1,4}`, so a fabricated 987654 was invisible to the checker - a run could
# type any number of five digits or more and be told "every number is one the tool printed". Found on
# 20 Nov by falsifying the generated reports: three of them carried 987654 and all three passed.
NUM_RE = r"\b\d+\b"


def _tool_numbers(cmds):
    """Every integer any of these tools prints, plus the tool output itself for the record."""
    seen = set()
    text = ""
    for cmd in cmds:
        try:
            r = subprocess.run(cmd, shell=True, cwd=os.path.dirname(os.path.dirname(HERE)),
                               capture_output=True, text=True,
                               timeout=180)
            out = (r.stdout or "") + (r.stderr or "")
        except Exception as e:
            out = ""
            print("warning: %s did not run - %s" % (cmd, e))
        text += out + "\n"
        for m in re.findall(NUM_RE, out):
            seen.add(int(m))
    return seen, text


def verify_tool_numbers(text, cmds, label):
    """Every number in the message must appear in what the tools printed.

    Numbers that legitimately come from elsewhere - a date, a commit sha, the corpus size - are
    allowed by the caller passing them in the tool output, which is why the commands include the
    tools that print those too.
    """
    have, _ = _tool_numbers(cmds)
    if not have:
        return ["%s: no tool output could be read - nothing in this message is verified" % label]
    # A DATE OR A CLOCK IS NOT A MEASUREMENT. "20 Nov 2026" and "05:51" carry numbers no tool prints
    # and no reader mistakes for a count. Everything else must be traceable.
    # A NUMBER INSIDE A CHECK NAME IS NOT A MEASUREMENT. `18_displacement` and `59_shape_anchor`
    # begin with digits; counting those as measurements made a correct table fail on "18" and "59".
    # Strip every check-name token first, escaped or not.
    text = re.sub(r"\b\d{1,3}\\?_[a-z0-9_]+", " ", text)
    text = re.sub(r"\b(19|20)\d{2}\b", " ", text)
    text = re.sub(r"\b\d{1,2}:\d{2}(:\d{2})?\b", " ", text)
    text = re.sub(r"\b\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b", " ", text)
    text = re.sub(r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}\b", " ", text)
    bad = []
    for m in re.finditer(r"(?<![\w.])(\d+)(?![\w.])", text):
        n = int(m.group(1))
        if n not in have:
            ctx = text[max(0, m.start() - 45):m.end() + 45].replace("\n", " ")
            bad.append("%s: %d is not in the %s output - ...%s..." % (label, n, label, ctx))
    return bad


# A REPORT IS NOT A TRANSCRIPT OF ITS OWN INSTRUCTIONS.
#
# The 20 Nov gverify report pasted its whole prompt into the message. The numbers were right and the
# layout was destroyed: the prompt rendered as one enormous dark code block that ran across two pages,
# inline code spans came out as empty white rectangles, and the report itself did not begin until the
# bottom of page three. The user's words: "layout bohot zyada toota hai".
#
# Nothing in the prompt belongs in the report. A run that has to paste its instructions to explain
# itself has not understood what it did.
PROMPT_MARKERS = (
    "You measure every document through BOTH renderers",
    "READ THIS FIRST, ALL OF IT",
    "STEP 0 - WHOSE STAGE IS IT",
    "FIVE THINGS THAT COST A RUN",
    "git clone github.com",
    "bash tools/install-gate.sh",
    "COORDINATION.md",
    "THE ONE STEP THAT IS NOT AUTOMATIC",
)


def verify_not_a_transcript(text):
    """Refuse a report that has pasted the prompt into itself."""
    bad = [m for m in PROMPT_MARKERS if m in text]
    if not bad:
        return []
    return ["the report contains its own instructions (%d marker(s), first: %r). The prompt is not the"
            " report - delete it and keep only what the run measured." % (len(bad), bad[0])]


# A CHECK NAME IS AN IDENTIFIER, NOT PROSE. MARKDOWN EATS ITS UNDERSCORES.
#
# The 20 Nov report printed its whole table as `32strokelines`, `05charsextra`, `18displacement`.
# Every underscore had been read as italic markup and swallowed, so the names in the report were not
# the names in the tool - and a reader could not match a row to a check. The table itself was gone too:
# not one line began with a pipe, so what should have been four columns was loose text.
#
# So: every check name the tool prints must appear INTACT if it appears at all. A stripped name is a
# wrong name, and it is checkable exactly.
def verify_versions_intact(text, cmds):
    """A VERSION IS ONE TOKEN, NOT THREE INTEGERS. 9.99.99 must not pass because 9 and 99 exist.

    Found by falsification on 20 Nov: the APK report claimed versionName 9.99.99 and the check said
    "every number is one the tool printed", because it had split the version into 9, 99 and 99 and all
    three appear somewhere in the tag list. A version is the one number where the whole string is the
    fact.
    """
    _, out = _tool_numbers(cmds)
    bad = []
    # A VERSION AT THE END OF A SENTENCE IS STILL A VERSION. `9.99.99.` did not match because the
    # lookahead rejected the full stop - so the one fabricated version this check exists to catch was
    # the one shape it missed. The lookahead now rejects only a further digit or a word character.
    # A MEASUREMENT WITH A UNIT IS NOT A VERSION. `1.6 h`, `3.9 h` and `12.5 %` matched the version
    # shape and made a correct watchdog report fail - the check refused a report for stating the age
    # of a stage. Only a bare dotted token counts.
    UNIT = r"\s*(?:h|hr|hrs|min|mins|s|sec|pt|px|%|MB|KB|GB|d|day|days)\b"
    # ANY LENGTH, SAME AS THE INTEGER SCAN. This required 1-2 digits before the dot, so a fabricated
    # version 987654.1 matched neither this check (wrong shape) nor the integer scan (the lookarounds
    # reject a dotted token) and passed as "every number is one the tool printed".
    for m in re.finditer(r"(?<![\w.])\d+(?:\.\d+)+(?!\w|\.\d)", text):
        v = m.group(0)
        if re.match(UNIT, text[m.end():m.end() + 8], re.I):
            continue
        if v in out:
            continue
        bad.append("%r is not in the tool output - a version is one token, and this one was not"
                   " printed by any tool. Copy it from git tag or app/build.gradle." % v)
    return bad


def verify_names_intact(text, cmds):
    _, out = _tool_numbers(cmds)
    names = sorted({n for n in re.findall(r"\b[a-z0-9]+(?:_[a-z0-9]+)+\b", out)})
    bad = []
    for n in names:
        if n in text:
            continue
        flat = n.replace("_", "")
        if flat and flat in text:
            bad.append("%r appears as %r - the underscores were eaten by markdown italic. Escape them"
                       " (32\\_stroke\\_lines) or the name is not the name." % (n, flat))
    return bad


def _gen(cron):
    return "python3 tools/p2w-bench/cronreport.py --numbers --for %s" % cron


_CMDS = {
    "gverify": [_gen("gverify"), "python3 tools/p2w-bench/gverify.py --report",
                "python3 tools/p2w-bench/stage.py --json",
                "python3 tools/p2w-bench/gverify.py --matrix"],
    # health.py --json and progress.py --json were listed here too, and the watchdog generator already
    # calls both - so the verifier ran health.py twice and timed out at 180 s (exit 124). The generator
    # is the authority for what its own report can contain; the tools behind it do not need repeating.
    "health": [_gen("watchdog"), "python3 tools/p2w-bench/round.py --phase"],
    # THE APK CRON'S NUMBERS ARE NOT THE FIXER'S. `--for apk` used to fall through to report.py's
    # full Progress+Timing check, which demanded a fixer slot window and tool beats - so a correct
    # APK report was refused for not having them, and the run had no way to comply. Its real sources
    # are the tag, the build config and the round state.
    "apk": [_gen("apk"), "git describe --tags --abbrev=0 2>/dev/null || true",
            "git tag --sort=-creatordate | head -20",
            "grep -oE 'versionName *\"[^\"]+\"' app/build.gradle 2>/dev/null || true",
            "grep -oE 'versionCode *[0-9]+' app/build.gradle 2>/dev/null || true",
            "python3 tools/p2w-bench/round.py --phase"],
    "baseline":   [_gen("baseline"), "python3 tools/p2w-bench/round.py --phase"],
    "classifier": [_gen("classifier"), "python3 tools/p2w-bench/round.py --phase"],
}


def verify_for(cron, text):
    """Dispatch the per-cron verification. Returns a list of problems."""
    cmds = _CMDS.get(cron)
    if not cmds:
        return []
    return verify_tool_numbers(text, cmds, cron)


def main(argv):
    if "--check" in argv:
        _c = ""
        if "--for" in argv:
            _i = argv.index("--for") + 1
            if _i < len(argv):
                _c = argv[_i]
        _chk = out_path(_c)
        if not os.path.exists(_chk):
            print("MISSING - write the report to %s before you commit" % _chk)
            return 1
        n = len(open(_chk, encoding="utf-8").read().strip())
        if n < MIN:
            print("TOO SHORT - %d characters. That is not a report." % n)
            return 1
        print("ok - %d characters" % n)
        return 0
    if "--file" in argv:
        i = argv.index("--file") + 1
        if i >= len(argv):
            print("--file needs a path")
            return 2
        text = open(argv[i], encoding="utf-8").read()
    else:
        text = sys.stdin.read()
    if len(text.strip()) < MIN:
        print("refused: %d characters is not a report" % len(text.strip()))
        return 2
    # BOTH CHECKS RUN, AND EVERY PROBLEM IS PRINTED. The row check used to return before the fact
    # check ran, so a report with a wrong table row was rejected without ever telling the run that
    # its header clock was wrong too - and the run fixed the row and shipped the clock.
    _for = ""
    if "--for" in argv:
        _i = argv.index("--for") + 1
        if _i < len(argv):
            _for = argv[_i].strip().lower()
    # A GENERATED REPORT SAYS WHICH CRON IT IS. `--for` is still the explicit way, but every report
    # cronreport.py prints starts with its own title, so a run that forgets the flag - or whose prompt
    # predates it - is still checked against the right sources instead of falling through to report.py's
    # fixer check and being refused for not having a slot window.
    if not _for:
        _title = text.lstrip().split("\n", 1)[0].lower()
        for _key, _pat in (("baseline", "baseline - run report"),
                           ("classifier", "classifier - run report"),
                           ("gverify", "google verify - run report"),
                           ("health", "watchdog - run report"),
                           ("apk", "apk - run report")):
            if _pat in _title:
                _for = _key
                break
    if _for in ("gverify", "health", "apk", "baseline", "classifier"):
        _cmds = _CMDS.get(_for, [])
        _p = (verify_not_a_transcript(text)
              + verify_names_intact(text, _cmds)
              # A DECIMAL SCORE IS NOT A VERSION. 39.7, 3.71 and 39.73 are share@5 means and the
              # version check refused a correct baseline report for them. Only the APK cron has a
              # version that is a fact worth checking whole.
              + (verify_versions_intact(text, _cmds) if _for == "apk" else [])
              + verify_for(_for, text))
        if _p:
            print("REFUSED - %d number(s) in this %s report are not in the tool output:" % (len(_p), _for))
            for x in _p[:12]:
                print("  " + x)
            print("A number a run types is a number a run can get wrong. Re-run the tool and copy")
            print("what it prints, or delete the sentence that needs the number.")
            return 3
        print("ok - every number in this %s report is one the tool printed" % _for)
        # A REPORT THAT PASSES MUST STILL BE WRITTEN. This branch returned before the write below, so
        # every per-cron report that passed the number check was checked and then thrown away - the
        # stored LAST-MESSAGE-health.md stayed at whatever an older, unverified pass had left there.
        # Measured 22 Nov 15:09: the file still held the 12:16 IST pass while this run's checked report
        # sat in /tmp. BLOCKERS.md recorded it at 00:22 and it survived three passes; a check that
        # discards the artefact it approved is not a check.
        if "--dry-run" in argv:
            print("dry run - nothing written")
            return 0
        _dest = out_path(_for)
        open(_dest, "w", encoding="utf-8").write(text)
        print("wrote %s - %d characters" % (_dest, len(text.strip())))
        return 0

    problems, checked = verify(text)
    data = _report_json()
    facts = verify_facts(text, data) + verify_sections(text)
    if problems is None:
        print("WARNING: report.py could not be run, so no number in this message was checked "
              "against it. Say so in the report.")
        problems = []
    bad = list(problems or []) + list(facts or [])
    if bad:
        print("REFUSED - %d number(s) in this message do not match report.py. "
              "Copy them from `report.py --json`; do not retype them." % len(bad))
        for p in bad:
            print("  " + p)
        return 3
    print("numbers: %d Progress row(s) match report.py" % checked)
    print("facts: header clock, corpus size, .txt and agent timings all match report.py")
    # --dry-run CHECKS WITHOUT WRITING. Without it, testing the checker against a known-bad report
    # overwrote the report being tested - which happened twice while building this, and each time
    # the file had to be restored from git before the next attempt meant anything.
    if "--dry-run" in argv:
        print("dry run - nothing written")
        return 0
    _dest = out_path(_for)
    open(_dest, "w", encoding="utf-8").write(text)
    print("wrote %s - %d characters" % (_dest, len(text.strip())))
    if _dest != OUT:
        print("LAST-MESSAGE.md is the fixer's and was not touched by this %s report" % (_for or "?"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
