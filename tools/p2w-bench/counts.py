"""One rule for every count that is printed beside its own base.

THE SAME DEFECT APPEARED IN FOUR PLACES ON 25 NOV, AND EACH WAS FIXED SEPARATELY.

    cronreport.py   "Google measured 213 of 212"   - RANKING rows as the base, gverify as the count
    health.py       "done 213 of 82"               - the Google count as the base
    report.py       "0 of 212 current"             - a failed read printed as a measurement
    restamp_txt.py  "engine 85b8735f"              - a git abbreviation where a source hash belongs

Every one is a number that does not describe the thing it is printed against. Fixing them one at a time
left the next generator free to make the same mistake, so the rule lives here and callers ask for it.

WHAT THIS DOES NOT DO: it does not decide which base is right. That is a judgement each caller must make
and defend. It only refuses the two shapes that cannot be true - a count larger than its base, and a
count stated when the read that produced it failed.
"""


def checked(count, base, what, allow_over=False):
    """Return (count, base) after refusing a count that cannot be true.

    Raises ValueError rather than returning a clamped number, because a clamped number is a lie that
    looks like a measurement. The caller that gets this exception has a real bug to fix.
    """
    if count is None or base is None:
        raise ValueError("%s: count or base is None - a missing number is not a zero" % what)
    count = int(count)
    base = int(base)
    if count < 0 or base < 0:
        raise ValueError("%s: negative count %d or base %d" % (what, count, base))
    if not allow_over and count > base:
        raise ValueError(
            "%s: %d of %d - the count exceeds its own base. This is the shape that printed "
            "'213 of 212' on 25 Nov; the two numbers come from different populations and one of "
            "them is the wrong base" % (what, count, base))
    return count, base


def pct(count, base, what):
    """Percentage of a checked pair, or 0.0 when the base is zero.

    A ZERO BASE IS NOT A VIOLATION, IT IS AN EMPTY POPULATION. checked() refuses count > base, and with
    base 0 that refuses everything, so this returns early instead. Both halves matter: 0.0 must not be
    printed as though something was measured, and a division by zero must not become a traceback in a
    report generator either.
    """
    if base is None:
        raise ValueError("%s: base is None - a missing number is not a zero" % what)
    base = int(base)
    if base == 0:
        return 0.0
    count, base = checked(count, base, what)
    return 100.0 * count / base


class FailedRead(Exception):
    """Raised instead of returning zero when an instrument could not read at all.

    THE DISTINCTION THAT COST A WEEK. '0 of 212 documents are current' and 'the store could not be read'
    print differently but were both rendered as zero, so a failed read looked like a measurement of
    nothing. Callers must catch this and say the read failed; they must not print a count from it.
    """
