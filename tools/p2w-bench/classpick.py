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
    """Documents this history actually moved, counting only the attempts that were measured.

    `x.get("moved") or 0` summed a None - "not measured" - as a zero, so an attempt that never read a
    number was indistinguishable from one that read a number and found nothing moved. 47_margins holds
    moved=[2, 2, 0, None, 1, 0, 1, 0]: five of those eight rows are measurements, three are not, and
    the old sum called it six moved from eight attempts either way.

    A None is skipped, not zeroed. `measured_of()` says how many rows the sum rests on, so a caller
    that wants to know whether an empty total means "nothing moved" or "nothing was read" can ask.
    """
    return sum(int(x["moved"]) for x in history
               if isinstance(x.get("moved"), int) and not isinstance(x.get("moved"), bool))


def measured_of(history):
    """How many rows of a history carry a real moved count - the denominator moved_of() rests on."""
    return sum(1 for x in history
               if isinstance(x.get("moved"), int) and not isinstance(x.get("moved"), bool))


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
    hand = dict(rot.get("exhausted") or {})
    # AND THE LEDGER DERIVES THE REST, WHERE THE NAMES ALREADY AGREE.
    #
    # The docstring above says the two ledgers do not share a namespace, and for 13 of the 23 attempt
    # keys that is true - `content-present-partly-displaced` is not a check name. But 10 of them ARE:
    # 18_displacement (57 attempts), 47_margins (18), 32_stroke_lines (17), 00_page_count (9),
    # 60_text_column_right_edge (5), 04_chars_missing (4). Those need no mapping, and a mapping written
    # by hand for the other 13 would be a guess that switches a real class off for good.
    #
    # So an exact name match with five attempts and at most one document moved is exhausted, derived
    # rather than remembered. A hand-written entry still wins: it is loaded first and never overwritten.
    try:
        from verify_google import all_check_ids
        _ids = set(all_check_ids())
        for _k, _v in (load(ATTEMPTS, {}) or {}).items():
            if _k not in _ids or _k in hand:
                continue
            _h = (_v or {}).get("history") or []
            _mv = sum(int(x.get("moved") or 0) for x in _h if isinstance(x.get("moved"), int))
            # A LIFETIME SUM CANNOT SEE A WALL. 47_margins held 18 attempts that moved 6 documents between
            # them and 8 reverts at the end; the sum said 6 > 1, so the class was never exhausted and the
            # rotation returned to it again and again. What matters is whether the RECENT attempts still move
            # anything - a class that moved 6 last week and nothing since is one where the current approach
            # has stopped working.
            #
            # So the tail decides as well. A class whose last measured attempts moved nothing is spent,
            # whatever the lifetime total says; the lifetime rule stays, because five attempts that never
            # moved anything is the same wall reached faster.
            _tail = [x.get("moved") for x in _h[-5:]]
            _tail_m = [m for m in _tail if isinstance(m, int)]
            # AND THE OUTCOME IS THE SHARPER SIGNAL. 47_margins holds 18 attempts of which 8 are reverted -
            # the last five carry moved [None, 1, 0, 1, 0], so a moved-sum rule reads progress where the
            # ledger records eight straight reversions. A reverted attempt is one that was applied and did
            # not hold; three of them in the recent tail means this approach has been tried and has failed.
            _tail_oc = [x.get("outcome") for x in _h[-5:]]
            _tail_rev = sum(1 for o in _tail_oc if o == "reverted")
            _tail_dead = (len(_tail_m) >= 3 and sum(_tail_m) == 0) or _tail_rev >= 3
            if len(_h) >= 5 and (_mv <= 1 or _tail_dead):
                hand[_k] = ("derived: %d attempt(s), %d moved lifetime, last %d measured moved %d - from ATTEMPTS.json" % (len(_h), _mv, len(_tail_m), sum(_tail_m)))
    except Exception:
        pass
    return hand


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


LEAD_ATTEMPT_BUDGET = 3   # fruitless attempts before a lead stops outranking the rotation
STALE = {}


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
        # A LEAD THAT NOTHING LANDS ON IS NOT A LEAD, IT IS A LOOP.
        #
        # This closed a lead only on "kept" or "partial", so a class whose every attempt was refuted
        # or reverted held an open lead for ever - and _pick returns an open lead before it consults
        # the rotation at all. Measured 23 Nov: 18_displacement held a lead from 06:17, twenty
        # attempts had been spent on it, four documents had moved, and every run still answered
        # "18_displacement holds an open LEAD and nothing outranks it". Behind it sat
        # 04_chars_missing with 65 documents and 25_invisible_text with 48, both at zero attempts.
        #
        # A lead now expires after LEAD_ATTEMPT_BUDGET attempts that landed nothing. It is not
        # forgotten - it is reported as STALE so the next run still sees what was tried and why it
        # failed - but it stops outranking work that has never been attempted.
        # COUNT ATTEMPTS SINCE SOMETHING LAST LANDED, NOT SINCE THE LEAD WAS WRITTEN. A run ends by
        # recording a lead, so the lead is always the newest entry and a counter that stopped at it
        # would read zero for ever. What matters is how many attempts have gone by without a "kept" or
        # "partial" - that is the user's own rule: multiple attempts and not one document improved.
        since_landed = 0
        found = None
        for x in reversed(h):
            o = (x.get("outcome") or "")
            if o in ("kept", "partial"):
                break            # something landed - the class is not stalled
            if o == "lead" and found is None:
                found = x
            since_landed += 1    # an attempt that landed nothing
        if found is not None:
            _r = str(found.get("reason") or "")
            if since_landed < LEAD_ATTEMPT_BUDGET:
                out[cls] = "%s - %s" % (found.get("at") or "?", _r[:120])
            else:
                STALE[cls] = "%s - %s (STALE: %d attempts since it landed nothing)" % (
                    found.get("at") or "?", _r[:90], since_landed)
    return out


def _solo_counts():
    """{check: documents that fail ONLY this check} - the ones a fix can finish outright."""
    import json as _j, glob as _g, os as _o
    out = {}
    try:
        eng = (_j.load(open('/scratch/work/p2w/.stamp', encoding='utf-8')).get('engine') or '')
    except Exception:
        eng = ''
    for f in _g.glob(_o.path.join(HERE, '..', '..', 'benchmarks', 'gverify', '*.json')):
        try:
            v = _j.load(open(f, encoding='utf-8'))
        except Exception:
            continue
        if eng and (v.get('engine') or '') != eng:
            continue
        fl = v.get('failed') or []
        if len(fl) == 1:
            out[fl[0]] = out.get(fl[0], 0) + 1
    return out


SOLO = _solo_counts()


def by_expected_fixes(rows):
    """Order classes by how many documents are likely to be FIXED, not by how many are broken.

    THE RANKING WAS BY DOCUMENT COUNT, AND THAT IS WHY NOTHING GOT FIXED. Measured 23 Nov, the order read
    18_displacement 101 documents first, and that class had taken 20 attempts and moved 4. Behind it sat
    04_chars_missing with 65 documents and 25_invisible_text with 48, both at ZERO attempts - never tried,
    because the biggest class was always first and it never finished. A run that keeps taking the largest
    class spends every attempt where the yield is 0.2 documents per attempt instead of where it is 1.9.

    The user's instruction was "jisme sabse jyada documents fix karna ho" - where the most documents can be
    FIXED - and document count is not that number.

    score = documents x yield, where yield is moved/attempts shrunk toward the corpus's own average by
    attempt count (K=3). The shrinkage stops a class that moved 11 documents in its single attempt from
    taking the top on one observation, and it gives an untried class the corpus's average yield rather than
    a zero: "we have not measured it" is not "it does not work".

    rows: (name, docs, attempts, moved). Returns (name, docs, attempts, moved, score, yield), best first.
    """
    A = sum(r[2] for r in rows)
    M = sum(r[3] for r in rows)
    g = (M / A) if A else 1.0
    K = 3.0
    out = []
    for name, docs, att, moved in rows:
        y = (moved + g * K) / (att + K)
        # A CHECK THAT CANNOT MAKE ANY DOCUMENT CLEAN IS WORTH ZERO DOCUMENTS, WHATEVER ITS SIZE.
        # 34 of the 40 failing checks finish nothing - every document they touch fails something
        # else too. Only six can: 18_displacement 25, 60_text_column_right_edge 6, 47_margins 3,
        # 59_shape_anchor 3, 32_stroke_lines 2, 17_matched_runs 1. The factor is 3, not infinity,
        # so the other 34 stay reachable once the six are done.
        out.append((name, docs, att, moved, docs * y * (3.0 if SOLO.get(name, 0) else 1.0), y))
    return sorted(out, key=lambda x: (-x[4], -x[1]))


def _pick(fmt, rot, dead):
    """The class for this format, and the reason. Same stay/rotate rule for both halves."""
    rank = ranking() if fmt == "docx" else ranking_txt()
    if not rank:
        return None, "no class table for the .%s half" % fmt, rot
    # ORDER BY EXPECTED FIXES, NOT BY SIZE. See by_expected_fixes() for the measurement.
    _rows = []
    # SKIP THE CLASSES A FRESH BLOCKER NAMES, NOT EVERY CLASS. _blocked is empty when nothing is
    # live, so this costs nothing in the normal case.
    _blocked_now = _pending_classes()
    for _n, _d in rank:
        if _n in _blocked_now:
            continue
    for _n, _d in rank:
        _h = attempts_for(_n)
        _rows.append((_n, _d, len(_h), moved_of(_h)))
    rank = [(r[0], r[1]) for r in by_expected_fixes(_rows)]
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


STALE_DAYS = 3   # a blocker older than this is reported, not obeyed


def _pending_classes():
    """Class names named by a FRESH pending item. Those classes are skipped, the rest are not.

    The gate blocked every class while any item was open, so a blocker on t01_word_accuracy stopped
    work on 18_displacement. Measured 25 Nov: 6 kept attempts landed in a day - three times the
    previous best - and the clean count did not move, because the attempts were spread across
    classes that cannot finish a document while the six that can sat behind the gate.

    A blocker names its class in its own text; a ratchet carries it in `who`. Both are read here.
    """
    import subprocess, json as _json, time as _time, re as _re
    try:
        r = subprocess.run([sys.executable, os.path.join(HERE, 'pending.py'), '--json'],
                           capture_output=True, text=True, timeout=90)
        items = (_json.loads(r.stdout).get('pending') or [])
    except Exception:
        return set()
    cut = _time.time() - STALE_DAYS * 86400
    out = set()
    for it in items:
        if it.get('kind') == 'agent':
            continue
        ts = it.get('ts') or 0
        if ts and ts < cut:
            continue          # aged out: reported by pending.py, not obeyed
        who = (it.get('who') or '')
        blob = ' '.join([who, it.get('what') or '', it.get('why') or ''])
        for m in _re.findall(r'\b(\d\d_[a-z_]+|t\d\d_[a-z_]+)\b', blob):
            out.add(m)
        if _re.match(r'^(\d\d|t\d\d)_', who):
            out.add(who)
    return out


def _pending_fresh():
    """How many actionable items were filed in the last STALE_DAYS days.

    The gate is right that nothing new should start while something is unfinishable. It is wrong to
    hold that for ever: the list currently holds 17 items, none newer than 23 November, and it refuses
    every class while they sit there. The six checks that can clean 40 documents have not been worked
    since.

    A blocker filed today is a stop - something just broke. One filed three days ago and not closed by
    any run since is either mis-filed or beyond this pipeline, and gating on it stops the work that
    would have closed the newer ones.
    """
    import subprocess, json as _json, time as _time
    try:
        r = subprocess.run([sys.executable, os.path.join(HERE, 'pending.py'), '--json'],
                           capture_output=True, text=True, timeout=90)
        items = (_json.loads(r.stdout).get('pending') or [])
    except Exception:
        return 0
    cut = _time.time() - STALE_DAYS * 86400
    n = 0
    for it in items:
        if it.get('kind') == 'agent':
            continue          # an agent row carries no date this can read
        ts = it.get('ts') or 0
        if ts and ts >= cut:
            n += 1
        elif not ts:
            n += 1            # no date at all: treat as live rather than silently ageing it out
    return n


def _pending():
    """(actionable, decision_needed, first few actionable) from pending.py.

    ACTIONABLE, NOT TOTAL. pending.py lists 81 items on 23 Nov and 59 of them are blockers whose own
    "can I fix it" column begins with "no" - they need a decision, not a patch. A gate that waited for
    all 81 would never open, which is worse than no gate at all. The 22 the fixer can actually close are
    what must be cleared first: the dead agents, the ratchets, and the blockers that carry a real action.

    Run as a subprocess with --json rather than reimplementing pending.py's rules: pending.py is the single
    authority on what is outstanding, and a second copy of that logic is how two answers to one question
    start.
    """
    import subprocess, json as _json
    try:
        r = subprocess.run([sys.executable, os.path.join(HERE, "pending.py"), "--json"],
                           capture_output=True, text=True, timeout=90)
        d = _json.loads(r.stdout)
        items = d.get("pending") or []
    except Exception:
        return 0, 0, ""
    act, dec = [], 0
    for it in items:
        why = (it.get("why") or "").lower()
        if it.get("kind") == "blocker" and why.startswith("can i fix it: no"):
            dec += 1
        else:
            act.append(it)
    head = " | ".join("%s %s" % (i.get("kind"), i.get("who")) for i in act[:3])
    return len(act), dec, head


def decide():
    """Return (class, why, new_state). Alternates the two halves, run about.

    PENDING OUTRANKS THE ROTATION, AND IT IS ENFORCED HERE BECAUSE A RULE IN A BRIEF IS NOT A MECHANISM.
    The brief has said "nothing new starts while anything is unfinished" since the beginning, and the 23
    Nov ledger shows 81 items outstanding while runs kept taking classes: 72 blockers, 5 ratchets and 4
    agents that died 550-700 minutes ago without a finding. The user asked for the pending list to be
    cleared before any new class. The same argument as the alternation below: it belongs here, where a run
    cannot skip it.

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

    # PENDING OUTRANKS EVERYTHING. The brief has said "nothing new starts while anything is unfinished"
    # since the beginning and runs kept taking classes anyway: the 23 Nov ledger shows 81 items
    # outstanding - 72 blockers, 5 ratchets, 4 agents that died 550-700 minutes ago without a finding -
    # while every run went to a class. The user asked for the list to be cleared first. A rule in a brief
    # is not a mechanism, which is the same sentence this file already carries about the alternation.
    # AN OLD BLOCKER IS A RECORD, A NEW ONE IS A STOP. The gate was introduced because runs kept
    # taking classes with 81 items outstanding, and it worked - too well. It now holds 17 items,
    # none newer than 23 November, and it refuses every class while they sit there. The six checks
    # that can clean 40 documents have not been worked since.
    #
    # The distinction that matters is not "pending or not" but "is this still live". A blocker
    # filed today is a stop: something just broke. A blocker filed three days ago and not closed by
    # any of the runs since is either mis-filed or beyond this pipeline, and gating on it stops the
    # work that would have closed the newer ones.
    #
    # So the gate counts only items from the last STALE_DAYS days. Older ones are still printed by
    # pending.py and still in BLOCKERS.md - they are reported, not obeyed.
    _np, _nd, _nw = _pending()
    # A BLOCKER ON ONE CLASS DOES NOT STOP ANOTHER. Measured 25 Nov: 6 kept attempts landed in a
    # day, three times the previous best, and the clean count did not move - the attempts were
    # spread across classes that cannot finish a document while the six that can sat behind a gate
    # held by blockers on five classes they had nothing to do with.
    #
    # So the gate now removes the blocked CLASSES from the ranking and picks among the rest. If every
    # class is blocked, the refusal below still fires and says so.
    _np, _nd, _nw = _pending()
    _blocked = _pending_classes()
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
        # THE GATE MUST REACH THIS PATH TOO. decide() refuses a class while pending work is open, but
        # --leverage is a separate branch that never calls decide(), so a run that reads the leverage
        # table sees a ranked list and picks from it without ever being told the gate is shut. The 04:52
        # run did exactly that: classpick exited 3 with "PENDING FIRST: 18 item(s)" on the plain path,
        # and the run went to 18_displacement anyway because it had read --leverage instead.
        _np, _nd, _nw = _pending()
        if _np > 0:
            print("refused: PENDING FIRST: %d item(s) you can close - take them in the order "
                  "pending.py gives before any new class. (%d more need a decision and do not block "
                  "you.) %s" % (_np, _nd, _nw))
            print("")
            print("The leverage table below is what each check is WORTH, not permission to take one.")
            print("")
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
        return 3 if _np > 0 else 0   # same exit code the plain path uses when the gate is shut

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
        # THE DISPLAY MUST SHOW THE ORDER THE PICKER ACTUALLY USES. It printed ranking(), which is by
        # document count, while _pick had already been changed to order by expected fixes - so a run
        # reading this status would see 18_displacement at number 1 and go there by hand, which is
        # exactly the loop the reordering exists to break.
        _r0 = ranking()
        _rows0 = [(n, d, len(attempts_for(n)), moved_of(attempts_for(n))) for n, d in _r0]
        rank = [(r[0], r[1]) for r in by_expected_fixes(_rows0)] if _rows0 else _r0
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
