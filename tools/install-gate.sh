#!/usr/bin/env bash
# Install the commit gate into this clone. Run once per clone; it is not committed because git
# does not track .git/hooks.
#
# WHY A HOOK AND NOT A DOCUMENT. The rule is: no commit lands, for the .docx or the .txt, unless
# the whole corpus has been measured with the engine as it stands and no document got worse. A rule
# that lives in a markdown file is a rule that gets skipped under time pressure - the 18-19 Nov runs
# kept every one of those rules and still published a report claiming 34 committed files when the
# commit had 20. This puts the rule where the commit actually happens.
#
# The hook runs tools/p2w-bench/regress.py --check and refuses on a non-zero exit. It takes about a
# second: it compares two CSVs and one engine fingerprint, it does not re-measure. Re-measuring is
# the expensive part and is the author's job BEFORE asking to commit.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
HOOK="$ROOT/.git/hooks/pre-commit"

if [ ! -d "$ROOT/.git" ]; then
  echo "not a git clone: $ROOT" >&2
  exit 1
fi

cat > "$HOOK" <<'EOS'
#!/usr/bin/env bash
# THE COMMIT GATE. Installed by tools/install-gate.sh.
#
# No commit may land, for the .docx or the .txt, without a full-corpus regression check.
# There is no override flag. If this fails, the change is not ready.
set -uo pipefail
ROOT="$(git rev-parse --show-toplevel)"
exec python3 "$ROOT/tools/p2w-bench/regress.py" --check
EOS

chmod +x "$HOOK"
echo "installed $HOOK"
echo
echo "testing it against the current tree:"
"$HOOK"
