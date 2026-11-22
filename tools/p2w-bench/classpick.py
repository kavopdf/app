#!/usr/bin/env python3
"""Which class this run works on. Rotation, by how many documents each one costs.

    python3 tools/p2w-bench/classpick.py            # the class to take, and why
    python3 tools/p2w-bench/classpick.py --json     # the same, machine-readable
    python3 tools/p2w-bench/classpick.py --status   # where the rotation stands

THE RULE, in the user's words (20 Nov):

    "ek class me jab tak improvement ho raha hai tab tak kaam hota rahe agar kisi class me poore ek
     run me multiple attempt try karne ke baad bhi ek bhi documents improvement nhi ho raha hai toh
     next turn me dusre sabse jyada documents wale class par kaam ho aur yeh silsila rotation based
     chalna chahiye"

So: ranked by documents, biggest first. Stay on a class while it is producing movement. When a whole
run of attempts on it produced nothing, move to the next class in the ranking. When the ranking runs
out, wrap round and start again - a class that failed once is not a class that failed for ever, and the
engine will have changed by the time it comes round.

WHY NOT ALWAYS THE EASIEST. The handoff on 20 Nov said take 25_invisible_text because its LibreOffice
tail is one document and the gate therefore cannot refuse it. That is a good first pick and a bad
policy: if every run takes the easiest class, the hard ones are never touched and the corpus never
finishes. The rotation starts at the biggest and moves on when a class stalls, which reaches the easy
ones early anyway - 25_invisible_text is the seventh biggest - without ever abandoning the hard ones.

WHERE THE EVIDENCE COMES FROM. benchmarks/DEFECT-CLASSES-GOOGLE.md for the ranking (Google's counts,
because Google is the renderer the user opens), and ATTEMPTS.json for what has actually been tried -
`moved` is how many documents an attempt improved, and it is the only honest measure of progress.
"""
import json, os, sys
from datetime import datetime, timezone, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
IST = timezone(timedelta(hours=5, minutes=30))

CLASSES = os.path.join(ROOT, "benchmarks", "DEFECT-CLASSES-GOOGLE.md")
CLASSES_TXT = os.path.join(HERE, "txt", "DEFECT-CLASSES-TXT.md")
ATTEMPTS = os.path.join(HERE, "ATTEMPTS.json")
ROTATION = os.path.join(HERE, "ROTATION.json")
GV = os.path.join(ROOT, "benchmarks", "gverify")

LEVERAGE_RATIO = 3.0
MIN_ATTEMPTS_FOR_A_VERDICT = 2


def now_str():
    return datetime.now(IST).strftime("%Y-%m-%d %H:%M")


def load(path, default):
    try:
        return json.load(open(path, encoding="utf-8"))
    except Exception:
        return default


def save(path, obj):
    tmp = path + ".tmp"
    json.dump(obj, open(tmp, "w", encoding="utf-8"), indent=1)
    os.replace(tmp, path)


def ranking():
    """[(class, google_docs)] biggest first, from the capability table.

    READ THE COLUMN BY ITS HEADER, NEVER BY ITS POSITION.

    This read c[5] because the table had six columns and google was the sixth. On 21 Nov a `status`
    column was added for round.py's open_classes(), the table became seven columns, and c[5] silently
    became `libreoffice` instead of `google`. Nothing crashed. The rotation simply started ranking by
    the renderer nobody opens - 60_text_column_right_edge at 28 instead of 57, 18_displacement at 19
    instead of 125 - and the two largest classes, 32_stroke_lines at 145 and 05_chars_extra at 141,
    fell off the top of the list entirely. A positional read of a table someone else edits is a bug
    waiting for an edit.
    """
    out = []
    if not os.path.exists(CLASSES):
        return out
    col = None
    for line in open(CLASSES, encoding="utf-8"):
        cells = [x.strip() for x in line.strip().strip("|").split("|")]
        if col is None:
            # the header row: find where `google` sits
            if "google" in [c.lower() for c in cells]:
                col = [c.lower() for c in cells].index("google")
            continue
        if not line.startswith("| `") or col >= len(cells):
            continue
        name = cells[0].strip("` ")
        try:
            out.append((name, int(cells[col].strip("*"))))
        except ValueError:
            continue
    return sorted(out, key=lambda x: -x[1])


def ranking_txt():
    """[(check, documents)] for the .txt half, biggest first.

    Read by header, for the same reason as ranking() above: a status column was added to this table on
    21 Nov and a positional read would have started counting the wrong cell the moment anyone added one
    more.
    """
    out = []
    if not os.path.exists(CLASSES_TXT):
        return out
    col = None
    for line in open(CLASSES_TXT, encoding="utf-8"):
        cells = [x.strip() for x in line.strip().strip("|").split("|")]
        if col is None:
            if "documents" in [c.lower() for c in cells]:
                col = [c.lower() for c in cells].index("documents")
            continue
        if not line.startswith("| `") or col >= len(cells):
            continue
        try:
            out.append((cells[0].strip("` "), int(cells[col].strip("*"))))
        except ValueError:
            continue
    return sorted(out, key=lambda x: -x[1])


def attempts_for(cls, since=None):
    """The attempts recorded on a class, optionally only those at or after `since`."""
    d = load(ATTEMPTS, {})
    rec = d.get(cls) or {}
    h = rec.get("history") or []
    if since:
        h = [x for x in h if (x.get("at") or "") >= since]
    return h


def moved_of(history):
    return sum(int(x.get("moved") or 0) for x in history)


def exhausted():
    """Classes a run has already given up on, with the reason it wrote down.

    THE TWO LEDGERS DO NOT SHARE A NAMESPACE, and that cost the rotation its whole memory. ATTEMPTS.json
    is keyed by the classifier's class names - `content-present-partly-displaced` - while the capability
    table is keyed by the check names Google reports - `32_stroke_lines`. Eighteen attempts sit under the
    first and the rotation cannot see a single one under the second, so it would have started at
    `32_stroke_lines` and spent a nineteenth run on the same wall.

    So a run records the class it exhausted here, in the table's own namespace, with the reason. It is
    evidence, not a rule: nothing is hard-coded, and the entry is written by the run that proved it.
    A class listed here is skipped by the rotation and reached again only after a full cycle - the engine
    will have changed by then.
    """
    rot = load(ROTATION, {})
    return rot.get("exhausted") or {}


def clean_leverage():
    """{check: how much of a CLEAN document it is worth}, biggest first.

    WHY THIS AND NOT "documents affected".

    Ranking by documents affected says 32_stroke_lines is worth 145 documents. Measured 21 Nov, fixing
    it alone takes exactly TWO documents to clean, because those 145 documents each fail several checks
    and losing one failure does not make a document clean.

    The user wants 99% or better, and a document is only at 99% when ALL 42 checks pass. So the question
    is not "how many documents does this check touch" but "how much of a clean document is this check
    holding back". A check that is the ONLY failure on a document is worth 1.0 of that document. A check
    that is one of five failures is worth 0.2 - clearing it moves the document a fifth of the way.

    Measured on the corpus:

        fix 05_chars_extra + 18_displacement + 32_stroke_lines   -> 35 documents become clean (6 -> 41)
        add 59_shape_anchor                                      -> 44 clean
        add 25_invisible_text                                    -> 57 clean

    Those five are one construct family - a floating <w:drawing> per rule, plus the shapes it carries -
    which is why they travel together. One fix, five checks, 51 documents.
    """
    out = {}
    if not os.path.isdir(GV):
        return out
    for f in os.listdir(GV):
        if not f.endswith(".json"):
            continue
        try:
            j = json.load(open(os.path.join(GV, f), encoding="utf-8"))
        except Exception:
            continue
        # A REFUSED DOCUMENT IS WORTH A WHOLE DOCUMENT, AND THIS USED TO SKIP IT.
        #
        # gverify writes page_count_refused when Google reflows the document into a different number of
        # pages, and every other check on it is unknown. This loop skipped those files, so
        # 00_page_count - the class that owns them - scored ZERO clean leverage while sitting on 21
        # documents. Measured 22 Nov: 00_page_count was in the ranking at 21 documents and absent from
        # the leverage table entirely, so the tool could never suggest it and the 21 could never be
        # fixed. The user asked "jo 21 documents hai wo kab fix honge" and the honest answer was "never,
        # because nothing scores them".
        #
        # They are not worthless - they are the opposite. A refused document fails exactly one thing
        # (the page count) and is unmeasured on the rest, so clearing that one check makes the whole
        # document measurable. That is worth 1.0 of a clean document, the maximum any single check can
        # be worth.
        if j.get("status") == "page_count_refused":
            out["00_page_count"] = out.get("00_page_count", 0.0) + 1.0
            continue
        failed = j.get("failed") or []
        if not failed:
            continue
        share = 1.0 / len(failed)
        for c in failed:
            out[c] = out.get(c, 0.0) + share
    return out


def open_leads():
    """{class: reason} for every class holding an unlanded lead, most recent first.

    A LEAD WAS ONLY VISIBLE FROM INSIDE ITS OWN CLASS. `_pick` checked the lead on the class the
    rotation was sitting on, so a lead on a DIFFERENT class was invisible: on 22 Nov 18_displacement
    held an open lead from 06:17 - "15 documents re-measured through Google on HEAD, every one is
    41/42 failing 18_displacement alone" - and the tool still said "staying on 32_stroke_lines".
    The most valuable thing in the pipeline was sitting one class away, unread.

    An open lead is the highest-priority work there is, whatever class holds it. This scans every
    class, so it cannot be missed again.
    """
    out = {}
    if not os.path.exists(ATTEMPTS):
        return out
    try:
        d = json.load(open(ATTEMPTS, encoding="utf-8"))
    except Exception:
        return out
    for cls, v in d.items():
        if not isinstance(v, dict):
            continue
        h = v.get("history") or []
        for x in reversed(h):
            o = (x.get("outcome") or "")
            if o in ("kept", "partial"):
                break            # something landed after the lead - it is closed
            if o == "lead":
                out[cls] = "%s - %s" % (x.get("at") or "?", str(x.get("reason") or "")[:120])
                break
    return out


def _pick(fmt, rot, dead):
    """The class for this format, and the reason. Same stay/rotate rule for both halves."""
    rank = ranking() if fmt == "docx" else ranking_txt()
    if not rank:
        return None, "no class table for the .%s half" % fmt, rot
    names = [n for n, _ in rank]
    docs = dict(rank)
    cur = rot.get("class")
    since = rot.get("since")

    # ANY OPEN LEAD, ON ANY CLASS, OUTRANKS THE ROTATION. See open_leads() for why.
    _leads = open_leads()
    for _lc in names:
        if _lc in _leads:
            return _lc, ("%s holds an open LEAD and nothing outranks it: %s"
                         % (_lc, _leads[_lc])), {"class": _lc, "since": now_str()}

    if cur not in names:
        cur = next((n for n in names if n not in dead), names[0])
        return cur, ("starting the .%s rotation at the biggest: %s, %d documents"
                     % (fmt, cur, docs[cur])), {"class": cur, "since": now_str()}

    h = attempts_for(cur, since)
    moved = moved_of(h)
    n = len(h)

    # A LEAD HOLDS THE CLASS, WHATEVER IT DID TO THE DOCUMENT COUNT.
    #
    # The rotation's verdict was sum(moved), so a run that measured a construct through Google and ran
    # out of slot to implement it - the most valuable thing a run can produce - read as zero progress and
    # started counting towards rotating away. On 21 Nov that was w:tblpPr: measured, exact to 0.5 pt,
    # zero flow cost, and the class that owns 145 documents was about to be abandoned with the answer in
    # hand.
    #
    # A lead is unfinished work, not absent work. Stay until it is implemented or refuted.
    # A LEAD IS OPEN ONLY UNTIL SOMETHING LANDS. This read any(lead) over the whole window, so a lead
    # that had already been implemented - and followed by two `kept` attempts - still held the class for
    # ever. On 22 Nov that meant the rotation stayed on 32_stroke_lines after the run had already taken
    # it from 6 clean to 23.
    #
    # A lead is open when it is the most recent attempt, or when nothing since it was kept or partial.
    _open_lead = False
    for x in reversed(h):
        _o = (x.get("outcome") or "")
        if _o in ("kept", "partial"):
            break            # something landed after the lead - it is closed
        if _o == "lead":
            _open_lead = True
            break
    if _open_lead:
        return cur, ("staying on %s (%d documents, .%s): it holds an open LEAD - a construct measured "
                     "and not yet landed. Finish it before anything else; a measured lead is worth more "
                     "than a fresh attempt on any other class."
                     % (cur, docs[cur], fmt)), rot

    if n >= MIN_ATTEMPTS_FOR_A_VERDICT and moved == 0:
        i = names.index(cur)
        nxt = cur
        for step in range(1, len(names) + 1):
            cand = names[(i + step) % len(names)]
            if cand not in dead:
                nxt = cand
                break
        return nxt, ("%s had %d attempt(s) since %s and moved 0 documents - rotating to the next "
                     "biggest in the .%s half: %s, %d documents"
                     % (cur, n, since, fmt, nxt, docs[nxt])), \
               {"class": nxt, "since": now_str()}

    # LEVERAGE. A small class that is trickling must not hold a large one hostage.
    #
    # Measured 21 Nov: the rotation sat on 47_margins - 26 documents, 13 attempts, 8 moved - while
    # 32_stroke_lines (145 documents) and 05_chars_extra (141) had never been attempted. That is
    # 8 documents for thirteen attempts' work, when one construct on the biggest class is worth 145.
    # The user: "1 din me sirf 1 documents hee improvement ho toh yeh kaam 6 months se zyada lag
    # jaayega" - and they are right: at 1 document a run the corpus never finishes.
    #
    # "Stay while it moves" is a good rule between classes of similar size and a bad one when the
    # class being worked is a fifth of the biggest. So: after MIN_ATTEMPTS on the current class, if
    # the biggest unwon class is LEVERAGE_RATIO times larger, go to the biggest. The trickle resumes
    # once the big one has had its own verdict.
    if n >= MIN_ATTEMPTS_FOR_A_VERDICT:
        big = next((c for c in names if c not in dead), None)
        if (big and big != cur and docs.get(big, 0) >= LEVERAGE_RATIO * max(1, docs.get(cur, 1))):
            return big, ("%s has %d document(s) and %d attempt(s) moved only %d - %s is %d document(s),"
                         " %.1fx larger, and has not had its verdict. Working the biggest first is the"
                         " only way the corpus finishes: one construct there clears many documents at"
                         " once. %s resumes when that one has had its attempts."
                         % (cur, docs.get(cur, 0), n, moved, big, docs[big],
                            docs[big] / max(1.0, docs.get(cur, 1)), cur)), \
                   {"class": big, "since": now_str()}

    if n == 0:
        return cur, ("staying on %s (%d documents, .%s): nothing recorded on it since %s yet"
                     % (cur, docs[cur], fmt, since)), rot

    return cur, ("staying on %s (%d documents, .%s): %d attempt(s) since %s moved %d document(s)"
                 % (cur, docs[cur], fmt, n, since, moved)), rot


def decide():
    """Return (class, why, new_state). Alternates the two halves, run about.

    THE .TXT HALF WAS NEVER REACHED. The brief has said since the beginning to alternate - one run on the
    largest .docx class, the next on the largest .txt check - and no run ever did, because the picker only
    ever read the Google table. Measured 20 Nov: ATTEMPTS.json held ten classes and not one of them was a
    .txt check, while 46 documents still failed a .txt check. A rule in a brief is not a mechanism.

    So the alternation is here, where a run cannot skip it: the state carries which half is next, and each
    call flips it. A .docx run is followed by a .txt run, whatever the sizes are - a pipeline that only
    fixes the format with more failures never finishes the other one.
    """
    rot = load(ROTATION, {})
    dead = rot.get("exhausted") or {}
    fmt = rot.get("next") or "docx"
    if fmt not in ("docx", "txt"):
        fmt = "docx"

    sub = rot.get(fmt) or {}
    cls, why, newsub = _pick(fmt, sub, dead)
    other = "txt" if fmt == "docx" else "docx"

    state = dict(rot)
    state[fmt] = newsub if isinstance(newsub, dict) and newsub.get("class") else sub
    state["next"] = other
    state["exhausted"] = dead
    if cls:
        state[fmt] = {"class": cls, "since": (newsub or {}).get("since") or now_str()}
        why = why + " | next run: the .%s half" % other
    return cls, why, state


def main(argv):
    if "--leverage" in argv:
        # WHAT EACH CHECK IS WORTH IN CLEAN DOCUMENTS.
        #
        # "Documents affected" is the metric the table ranks by, and it is the wrong one: fixing
        # 32_stroke_lines alone takes exactly TWO documents to clean, because those 145 documents each
        # fail several checks and losing one failure does not make a document clean.
        #
        # This prints what a fix is actually worth, and then shows which checks travel together - because
        # checks that always co-occur are one construct and one fix clears all of them.
        lv = clean_leverage()
        if not lv:
            print("no gverify results - cannot compute leverage", file=sys.stderr)
            return 3
        print("  %-30s %s" % ("check", "worth, in CLEAN documents"))
        print("  " + "-" * 52)
        for c, v in sorted(lv.items(), key=lambda x: -x[1]):
            print("  %-30s %.1f" % (c, v))
        # the shapes: which sets of checks a document fails, most common first
        from collections import Counter
        sets = Counter()
        for f in os.listdir(GV):
            if not f.endswith(".json"):
                continue
            try:
                j = json.load(open(os.path.join(GV, f), encoding="utf-8"))
            except Exception:
                continue
            if j.get("status") == "page_count_refused":
                continue
            fs = frozenset(j.get("failed") or [])
            if fs:
                sets[fs] += 1
        if sets:
            print()
            print("  the shapes - a set of checks one document fails, most common first:")
            print("  %5s  %s" % ("docs", "checks"))
            print("  " + "-" * 52)
            for st, n in sets.most_common(8):
                print("  %5d  %s" % (n, ", ".join(sorted(st))[:60]))
            print()
            print("  Checks that always travel together are ONE CONSTRUCT. One fix clears all of them;")
            print("  fixing one of five has done a fifth of the work.")
        return 0

    # IT ADVISES. IT DOES NOT DECIDE.
    #
    # The user, 21 Nov: "agar ham rotation wala kaam hee khatam kar de aur poora decision fixer ko hee de de
    # ... mujhe lagta hai rotation ki wajah se bohot saare leads choot gye honge".
    #
    # They were right, and the record says so. The rotation ranked by the LibreOffice column for two days
    # and dropped the 145-document class off the list. It sat on a 3-document class for 19 attempts. It
    # parked the two largest classes on the strength of one approach. And on 21 Nov it was about to walk
    # away from a measured lead worth 36.3 clean documents because sum(moved) said zero.
    #
    # What it was good for is one thing: remembering. That memory is not the rotation - it is
    # ATTEMPTS.json, FINDINGS/, HYPOTHESES.md and the class tables, and every one of them is read by the
    # run anyway.
    #
    # So this prints the evidence and a suggestion, and the run decides. There is no rule that the run must
    # take the suggestion, and there is no penalty for not taking it - only the requirement that whatever
    # it takes, it says why in the report.
    cls, why, state = decide()
    if "--exhaust" in argv:
        # the run records the class it gave up on, and why. Never silently.
        i = argv.index("--exhaust") + 1
        if i >= len(argv):
            print("--exhaust needs a class name", file=sys.stderr)
            return 2
        name = argv[i].strip()
        why = " ".join(argv[i + 1:]).strip() or "no reason recorded"
        rot = load(ROTATION, {})
        dead = rot.get("exhausted") or {}
        dead[name] = "%s - %s" % (now_str(), why)
        rot["exhausted"] = dead
        save(ROTATION, rot)
        print("recorded as exhausted: %s" % name)
        print("  reason: %s" % why)
        return 0
    if "--status" in argv:
        rot = load(ROTATION, {})
        rank = ranking()
        print("rotation")
        print("  current : %s" % (rot.get("class") or "-"))
        print("  since   : %s" % (rot.get("since") or "-"))
        print("  ranking :")
        dead = rot.get("exhausted") or {}
        if dead:
            print("  exhausted:")
            for k, v in dead.items():
                print("    %s  (%s)" % (k, v))
            print("  ranking :")
        for i, (n, c) in enumerate(rank[:12]):
            mark = "  <- now" if n == rot.get("class") else ("  [exhausted]" if n in dead else "")
            h = attempts_for(n)
            print("    %2d. %-30s %4d docs  %2d attempt(s), moved %d%s"
                  % (i + 1, n, c, len(h), moved_of(h), mark))
        return 0
    if "--json" in argv:
        print(json.dumps({"class": cls, "why": why, "state": state}, indent=1))
        return 0
    if cls is None:
        print("refused: %s" % why, file=sys.stderr)
        return 3
    # THE EXHAUSTED MAP MUST SURVIVE THE POINTER WRITE. This wrote `state` alone, so every call that
    # moved the rotation silently erased the record of which classes were exhausted - and the very next
    # call put the rotation straight back on 32_stroke_lines, the class 18 attempts had already failed on.
    # Found by watching it happen: after marking two classes dead it still picked the first.
    merged = dict(load(ROTATION, {}))
    merged.update(state)
    merged["exhausted"] = (load(ROTATION, {}).get("exhausted")
                           or state.get("exhausted") or {})
    save(ROTATION, merged)
    print("suggest : %s" % cls)
    print("because : %s" % why)
    print("")
    print("  THAT IS A SUGGESTION, NOT AN ORDER. You decide, on this evidence plus what you have read")
    print("  in FINDINGS/ and HYPOTHESES.md. Take it, or take something else and say why. What you may")
    print("  not do is take something without a reason - the report has to carry the reason.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
