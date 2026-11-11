#!/usr/bin/env bash
#
# retry.sh - run a command, and decide from the error whether retrying can help.
#
# WHY THIS EXISTS
#   "Wait and retry" is right for half of all failures and wrong for the other
#   half. A 429 clears by itself; a 401 never does, and three retries against a
#   missing permission cost two minutes and end in the same place. Worse, a blind
#   retry of a WRITE can publish the same release twice - the second attempt
#   succeeds because the first one already did.
#
#   So the error is classified before anything is retried:
#
#     transient   a rate limit, a 5xx, a timeout, a dropped connection.
#                 These clear. Back off and try again.
#     permanent   bad credentials, a missing permission, a 404, a full disk.
#                 These do not clear. Stop at once and say what it was.
#     unknown     neither pattern matched. One retry, then stop - a command that
#                 fails twice for an unknown reason is not about to succeed.
#
#   There is a hard ceiling on waiting: bash stops at 300 seconds in this
#   environment and nothing survives it, so the backoff is 5 + 15 + 45 seconds.
#   Anything longer is the next scheduled run's job, and that run is free.
#
# USAGE
#   bash tools/retry.sh -- git clone https://github.com/kavopdf/app /tmp/x
#   bash tools/retry.sh --tries 4 -- gh release download corpus-v1 --repo kavopdf/app
#   bash tools/retry.sh --classify "API rate limit exceeded for 1.2.3.4"
#       prints: transient        (exit 0)
#
#   exit 0   the command succeeded
#   exit N   the command's own exit code, after the last attempt

set -u

TRIES=3
QUIET=0
CLASSIFY_ONLY=""
HAS_CLASSIFY=0

while [ $# -gt 0 ]; do
  case "$1" in
    --tries) TRIES="${2:-3}"; shift 2 ;;
    --quiet) QUIET=1; shift ;;
    --classify) CLASSIFY_ONLY="${2:-}"; HAS_CLASSIFY=1; shift 2 ;;
    --) shift; break ;;
    *) break ;;
  esac
done

# ---------------------------------------------------------------------------
# The patterns. Order matters: a rate limit is checked first, because GitHub
# answers a rate limit with 403 and a missing permission with 403, and only the
# body tells them apart.
# ---------------------------------------------------------------------------
TRANSIENT='rate limit|ratelimit|secondary rate|abuse detection|userRateLimitExceeded|rateLimitExceeded|quota exceeded|too many requests|resource_exhausted|\b429\b|\b502\b|\b503\b|\b504\b|connection reset|connection refused|connection aborted|timed out|timeout|temporarily unavailable|try again later|service unavailable'

PERMANENT='bad credentials|resource not accessible|not accessible by integration|no space left|permission denied|does not exist|unauthenticated|invalid token|expired token|\b401\b|\b404\b|Not Found'

# The third outcome is not a failure at all: the thing the command was trying to
# create is already there. Retrying a clone into a directory that exists fails the
# same way every time, and stopping the cron over it would be wrong - the state it
# wanted is exactly the state it has.
ALREADY='destination path already exists|already exists and is not an empty directory'

classify() {
  local text="$1"
  if printf '%s' "$text" | grep -qiE "$ALREADY"; then
    printf 'already-done\n'; return
  fi
  if printf '%s' "$text" | grep -qiE "$TRANSIENT"; then
    printf 'transient\n'; return
  fi
  if printf '%s' "$text" | grep -qiE "$PERMANENT"; then
    printf 'permanent\n'; return
  fi
  # A bare 403 with no rate-limit wording is a permission problem.
  if printf '%s' "$text" | grep -qE '(^|[^0-9])403([^0-9]|$)'; then
    printf 'permanent\n'; return
  fi
  printf 'unknown\n'
}

if [ "$HAS_CLASSIFY" -eq 1 ]; then
  classify "$CLASSIFY_ONLY"
  exit 0
fi

if [ $# -eq 0 ]; then
  echo "retry: no command given" >&2
  echo "usage: bash tools/retry.sh [--tries N] -- <command...>" >&2
  exit 2
fi

say() { [ "$QUIET" -eq 1 ] || printf '%s\n' "$*" >&2; }

i=0
rc=1
while [ "$i" -lt "$TRIES" ]; do
  i=$((i + 1))
  OUT=$(mktemp)
  "$@" >"$OUT" 2>&1
  rc=$?
  cat "$OUT"

  if [ "$rc" -eq 0 ]; then
    rm -f "$OUT"
    say "retry: ok on attempt $i of $TRIES"
    exit 0
  fi

  TEXT=$(cat "$OUT")
  rm -f "$OUT"
  CLS=$(classify "$TEXT")

  case "$CLS" in
    already-done)
      say "retry: the target already exists - treating as done"
      exit 0
      ;;
    permanent)
      say "retry: PERMANENT failure (exit $rc) - retrying cannot fix this."
      say "retry: stopped after $i attempt(s). Read tools/p2w-bench/RETRY.md."
      exit "$rc"
      ;;
    unknown)
      if [ "$i" -ge 2 ]; then
        say "retry: failed twice for a reason this script does not recognise - stopping."
        say "retry: read the output above, then tools/p2w-bench/RETRY.md."
        exit "$rc"
      fi
      ;;
    transient)
      ;;
  esac

  if [ "$i" -lt "$TRIES" ]; then
    case "$i" in
      1) D=5 ;;
      2) D=15 ;;
      *) D=45 ;;
    esac
    say "retry: $CLS failure (exit $rc), waiting ${D}s then attempt $((i + 1)) of $TRIES"
    sleep "$D"
  fi
done

say "retry: gave up after $TRIES attempts (last exit $rc)."
say "retry: leave the item out, record it in INCIDENTS.md, and let the next scheduled run try again."
exit "$rc"
