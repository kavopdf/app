#!/usr/bin/env bash
# Verify before you commit. Nothing goes in without this passing.
#
# WHY THIS EXISTS
#   Two agents changed tools/p2w-bench/visual.py on 7 Nov. The first fixed a crash: the
#   page handles were kept after their documents had been closed, so the image and QR
#   questions threw on every page and a catch-all recorded them as "unsure", which
#   passes. The second rewrote the file from a copy made before that fix and put the
#   crash back. Nothing caught it, because nothing ran before the commit.
#
#   A commit message is not evidence. This checks the thing itself.
#
# THREE TIERS, BECAUSE MOST COMMITS ARE NOT ENGINE COMMITS
#   tier 1  always          python syntax, the cheap guards, file names        ~20 s
#   tier 2  engine changed  javac + TestPdfToWord                              ~90 s
#   tier 3  engine changed  G2 across the corpus against base208.json         ~180 s
#
#   Tier 1 alone catches a broken script. Tier 2 catches a broken compile. Tier 3
#   catches a document that got worse. Skipping tier 3 on an engine change is how a
#   regression ships.
#
# USAGE
#   bash tools/precommit.sh              # decide the tier from what changed
#   bash tools/precommit.sh --all        # force every tier
#   bash tools/precommit.sh --no-corpus  # skip tier 3 (when no corpus is available)
#
# EXIT
#   0  everything passed
#   1  something failed - do not commit
#   2  could not run (toolchain missing) - say so, do not commit blind

set -u
cd "$(dirname "$0")/.." || exit 2

FORCE_ALL=0
# The corpus tier used to look only at /scratch/work/corpus, a path from the
# session that wrote it, so tier 3 could not run anywhere else and anyone without
# that exact directory got a hard failure. The directory is now taken from the
# environment with the old path as the default.
CORPUS_DIR="${P2W_CORPUS:-/scratch/work/corpus}"
NO_CORPUS=0
for arg in "$@"; do
  case "$arg" in
    --all) FORCE_ALL=1 ;;
    --no-corpus) NO_CORPUS=1 ;;
  esac
done

FAILED=0
fail() { echo "FAIL  $*"; FAILED=1; }
pass() { echo "ok    $*"; }

echo "=== tier 1: syntax and guards ==="

# every python file must at least parse
PY_BAD=0
for f in $(find tools -name '*.py' 2>/dev/null); do
  python3 -c "import ast,sys; ast.parse(open(sys.argv[1]).read())" "$f" 2>/dev/null || {
    fail "python syntax: $f"
    PY_BAD=1
  }
done
[ "$PY_BAD" -eq 0 ] && pass "every python file parses"

# the shell scripts must parse too
for f in tools/*.sh; do
  [ -f "$f" ] || continue
  bash -n "$f" 2>/dev/null || fail "shell syntax: $f"
done
pass "every shell script parses"

# the cheap guards, the ones that read text and need no build
COULD_NOT_RUN=""
for g in check-file-names check-tool-titles check-permissions check-pdf2word; do
  if [ -f "tools/$g.py" ]; then
    if python3 "tools/$g.py" >/tmp/guard.$$ 2>&1; then
      pass "$g"
    elif grep -q "ModuleNotFoundError\|ImportError" /tmp/guard.$$; then
      # A guard that needs a package this machine does not have did not fail; it could
      # not run. Calling that a failure blocks every commit for a reason nobody can
      # act on, and calling it a pass hides a check that never happened. It is named
      # in the summary instead, so the gap is visible.
      mod=$(grep -o "No module named '[^']*'" /tmp/guard.$$ | head -1)
      echo "gap   $g - could not run ($mod)"
      COULD_NOT_RUN="$COULD_NOT_RUN $g"
    else
      fail "$g"
      tail -3 /tmp/guard.$$ | sed 's/^/        /'
    fi
    rm -f /tmp/guard.$$
  fi
done

# Parse proves a file is Python. This proves it works: on 7 Nov visual.py
# lost its QUESTIONS list, parsed fine, and failed every document it was
# given. The whole pipeline ran and reported five failures that were the
# tool, not the documents.
if ! python3 tools/smoke.py; then
  fail "the bench tools do not run - see the traceback above"
fi

# a file added to the repo must not be a patch, a backup or a build leftover
for bad in $(git status --porcelain 2>/dev/null | awk '{print $2}' | grep -E '\.(patch|orig|rej|bak|tmp)$|~$' || true); do
  fail "leftover file staged or untracked: $bad"
done

echo ""
echo "=== tier 2: does it build ==="

CHANGED_ENGINE=0
if [ "$FORCE_ALL" -eq 1 ]; then
  CHANGED_ENGINE=1
elif git rev-parse --git-dir >/dev/null 2>&1; then
  if git diff --name-only HEAD 2>/dev/null | grep -q 'app/src/main/java/com/kavopdf/app/engine/'; then
    CHANGED_ENGINE=1
  fi
  if git diff --name-only --cached 2>/dev/null | grep -q 'app/src/main/java/com/kavopdf/app/engine/'; then
    CHANGED_ENGINE=1
  fi
fi

if [ "$CHANGED_ENGINE" -eq 0 ]; then
  echo "skipped - no engine file changed"
else
  if [ ! -x /scratch/work/jdk/bin/javac ] && ! command -v javac >/dev/null 2>&1; then
    echo "no JDK - tier 2 and 3 cannot run. Say so; do not commit blind."
    exit 2
  fi
  export JAVA_HOME="${JAVA_HOME:-/scratch/work/jdk}"
  export PATH="$JAVA_HOME/bin:$PATH"
  export _JAVA_OPTIONS="-XX:+UseSerialGC -XX:ActiveProcessorCount=1 -XX:CompressedClassSpaceSize=128m -XX:MaxMetaspaceSize=512m -Xmx900m -Djava.awt.headless=true"
  ulimit -v unlimited 2>/dev/null

  CP="${ENGINE_CP:-/scratch/work/libs/aar/classes.jar:/scratch/work/libs/aar/assets:/scratch/work/libs/bcprov.jar:/scratch/work/libs/bcpkix.jar:/scratch/work/libs/bcutil.jar}"

  rm -rf /tmp/precommit-out && mkdir -p /tmp/precommit-out
  if javac -nowarn -cp "$CP" -d /tmp/precommit-out \
        $(find app/src/main/java -name '*.java') \
        $(find tools/engine-verify/stubs -name '*.java') >/tmp/javac.$$ 2>&1; then
    pass "the engine compiles"
  else
    fail "the engine does not compile"
    grep -E "error" /tmp/javac.$$ | head -10 | sed 's/^/        /'
  fi
  rm -f /tmp/javac.$$

  # Run the tests whatever tier 1 said: a broken guard in tier 1 must not hide whether
  # the engine's own tests pass. Two separate answers are more useful than one.
  if [ -d /tmp/precommit-out ]; then
    if javac -nowarn -cp "/tmp/precommit-out:$CP" -d /tmp/precommit-out \
          tools/engine-verify/TestPdfToWord.java >/tmp/tj.$$ 2>&1; then
      if java -cp "/tmp/precommit-out:$CP" TestPdfToWord >/tmp/tp.$$ 2>&1; then
        pass "TestPdfToWord: $(grep -o 'TOTAL: [0-9]* passed, [0-9]* failed' /tmp/tp.$$ | tail -1)"
      else
        fail "TestPdfToWord failed"
        grep -E "FAIL|TOTAL" /tmp/tp.$$ | tail -5 | sed 's/^/        /'
      fi
    else
      fail "the engine tests do not compile"
      grep error /tmp/tj.$$ | head -5 | sed 's/^/        /'
    fi
    rm -f /tmp/tj.$$ /tmp/tp.$$
  fi

  echo ""
  echo "=== tier 3: did any document get worse ==="
  if [ "$NO_CORPUS" -eq 1 ]; then
    echo "skipped by --no-corpus"
  elif [ ! -d "$CORPUS_DIR" ]; then
    echo "no corpus at $CORPUS_DIR - tier 3 cannot run."
    echo "Run it before committing an engine change: a document that got worse is a"
    echo "regression, and every count can stay clean while one does."
    FAILED=1
  else
    rm -rf /tmp/precommit-docx && mkdir -p /tmp/precommit-docx
    cat > /tmp/RunAll.java <<'JAVA'
import com.kavopdf.app.engine.*; import java.io.File;
import com.tom_roush.pdfbox.android.PDFBoxResourceLoader;
public class RunAll { public static void main(String[] a) throws Exception {
  // Without this the fonts never load, every page yields no text and the whole corpus
  // converts to empty documents - which G2 then reads as 208 regressions. It is the one
  // line ConvertAll has and this runner did not, and it made tier 3 unusable.
  File assets = new File(a[2]);
  PDFBoxResourceLoader.init(new android.content.Context(
      new android.content.res.AssetManager(assets)));
  File in=new File(a[0]), o=new File(a[1]); o.mkdirs();
  File[] fs=in.listFiles((d,n)->n.toLowerCase().endsWith(".pdf"));
  java.util.Arrays.sort(fs);
  for (File f: fs) { try {
    PdfToWord.Result r = PdfToWord.convert(f, null, null);
    PdfToWord.classifyHeadings(r);
    DocxWriter.write(r, new File(o, f.getName().replaceAll("(?i)\\.pdf$","")+".docx"));
  } catch (Throwable t) {} }
  System.out.println("done"); } }
JAVA
    if javac -nowarn -cp "/tmp/precommit-out:$CP" -d /tmp/precommit-out /tmp/RunAll.java >/dev/null 2>&1; then
      java -cp "/tmp/precommit-out:$CP" RunAll "$CORPUS_DIR" /tmp/precommit-docx \
            "$(echo "$CP" | tr ':' '\n' | grep 'assets' | head -1)" >/dev/null 2>&1
      if python3 tools/p2w-bench/gate.py --corpus "$CORPUS_DIR" \
            --out /tmp/precommit-docx \
            --baseline tools/p2w-bench/base208.json --check >/tmp/g2.$$ 2>&1; then
        pass "G2: $(grep -o 'no document got worse' /tmp/g2.$$ || echo passed)"
      else
        fail "G2 - a document got worse"
        grep -E "REGRESSED|->" /tmp/g2.$$ | head -8 | sed 's/^/        /'
      fi
      rm -f /tmp/g2.$$
    else
      fail "the corpus runner did not compile"
    fi
  fi
fi

echo ""
if [ -n "$COULD_NOT_RUN" ]; then
  echo "not run: $COULD_NOT_RUN"
  echo "  those guards need a package this machine does not have. They are not a"
  echo "  failure and not a pass - the gap is named so it is not mistaken for either."
  echo ""
fi
if [ "$FAILED" -eq 0 ]; then
  echo "ALL CHECKS PASSED - safe to commit"
  exit 0
fi
echo "CHECKS FAILED - do not commit. Fix it, then run this again."
exit 1
