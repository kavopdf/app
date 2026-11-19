# THE APK CRON'S BRIEF

This is the instruction set for the daily APK cron. The cron's prompt is a short wrapper that
points here, because a prompt that duplicates its brief drifts out of step with it - the fixer's
prompt reached 11 000 characters of near-duplicate before that was fixed on 19 Nov.

Repo github.com/kavopdf/app, branch main. Everything below assumes you have already cloned it,
set the commit identity and run `bash tools/install-gate.sh`, as the wrapper tells you.

---

Publish a signed KavoPDF APK. Repo github.com/kavopdf/app, branch main.

This cron runs once a day. For almost all of its runs it does nothing, and that is correct.

STEP 0 - MAY IT SHIP AT ALL?
  git clone https://github.com/kavopdf/app /scratch/work/apk ; cd /scratch/work/apk
  git config user.email "320240581+Onyx-Node@users.noreply.github.com"
  git config user.name "Onyx-Node"
  bash tools/install-gate.sh
      python3 tools/p2w-bench/round.py --apk-status
  Exit 0 means every round is finished and nothing has been published for this corpus.
  Exit 1 means no, and it printed why. Output that line and STOP.

STEP 0b - THE TWO GATES THAT DECIDE, IN THIS ORDER

  GATE A - the authoritative measurement. Run it and read its verdict.
      cp benchmarks/p2w.py benchmarks/gate.py /scratch/work/
      mkdir -p /scratch/output
      python3 /scratch/work/p2w.py --validate
      python3 /scratch/work/gate.py --budget 250
      python3 -c "import json;s=json.load(open('/scratch/output/STATE.json'));print(s['verdict'])"

  Three outcomes, and only one of them may ship:
      'BLOCKED: instrument failed ground-truth validation'  -> STOP. Do not build.
      'REGRESSION: N document(s) worse than baseline'        -> STOP. Report which documents.
      'OK: no regressions against baseline'                  -> continue.

  GATE B - the legacy ratchet, still worth running as a second opinion.
      python3 tools/p2w-bench/ratchet.py --check
  Read the EXIT CODE, because the failures are different things:
      exit 0  -> every mark held
      exit 1  -> a document is below the best score it has ever reached. Do NOT publish.
                 Report which documents and which checks fell, and stop.
      exit 3  -> the gate REFUSED to compare: its stored marks were stamped against a
                 different set of checks than the verifier now reports. That is not a
                 regression and not a pass - it is a gate that cannot speak. Say so, treat
                 Gate B as UNPROVEN, and fall back to Gate A, which is the validated one.
  There is no `--txt` mode any more. The store it read was deleted and the .txt ratchet now
  lives in txt_gate.py; run that instead:
      python3 tools/p2w-bench/txt_gate.py --gate

  GATE B is no longer the primary signal. benchmarks/LAYER-POLICY.md says why: the docx
  checks are advisory because they name a defect but do not size one. That is the
  whole reason and it needs no percentage. GATE A is the validated instrument: 14/14
  against known ground truth, reproducible to the digit across full environment wipes,
  two axes per document, a derived problem name per document, and a ratchet on share@5px.
  If A and B ever disagree, A wins and B is a bug to report.

  ONE THING YOU MUST KNOW ABOUT THE .txt GATE, so you do not misread it. It is txt_gate.py
  now, and its scores are in tools/p2w-bench/txt/RANKING-TXT.csv. The store the old --txt
  mode read was deleted. The reason the .txt ratchet was reset is in
  benchmarks/TXT-RATCHET-RESET.md: t09_page_furniture had a min() cap that made it one-sided,
  so it could only see MISSING page furniture and never DUPLICATED furniture. Read that file
  for the counts rather than trusting a number written here.
  An empty or absent .txt store is NOT the same as the .txt being clean. If the store is
  missing or empty, say so in your output and treat the .txt gate as UNPROVEN, not passed.

STEP 0c - READ THE TRUTH BEFORE YOU JUDGE ANYTHING
      benchmarks/PIPELINE.md
      benchmarks/LAYER-POLICY.md
      benchmarks/REALWORLD-FINDINGS.md
  Short. They state what is measured and what is not. Two numbers matter more than any
  others here and BOTH ARE IN THOSE FILES - read them there, do not carry them from memory:
    - the synthetic corpus: median share@5px and how many documents are clean
      (benchmarks/REALWORLD-FINDINGS.md)
    - the real documents: median share@5px, how many are clean, and the worst one
      (the same file - it keeps the two sets apart on purpose)
  Never quote the synthetic number as if it described the product. Quote both.
  Do not cite any figure from the docx checks as a score. They are advisory.

STEP 0d - WHEN SOMETHING FAILS
      cat tools/p2w-bench/RETRY.md
      bash tools/retry.sh --classify "<the error text>"
  transient (rate limit, 429, 5xx, timeout) clears and is worth waiting for.
  permanent (401, 404, 'Resource not accessible', no space) never clears.
  already-done means the state you wanted is the state you have.
  NEVER retry a write without checking whether the first one landed - and this cron
  writes the two things that must never happen twice:
      a release   GET the release by tag first. If the asset is there, it landed.
      a workflow  list the runs for that tag before dispatching again.

STEP 1 - WHAT TO SHIP
  gh api repos/kavopdf/app/tags --jq '.[0].name' for the last tag.
  gh api 'repos/kavopdf/app/commits?per_page=50' for commits since.
  Only app/src ships. If every commit since the last tag touched only tools/,
  benchmarks/ or docs, say so and stop - do not invent a release for changes that are
  not in the APK.

STEP 2 - PRECOMMIT
      bash tools/precommit.sh --no-corpus        must exit 0 before the version bump.

STEP 3 - BUMP AND RELEASE
  versionName +1 and versionCode +1 in app/build.gradle. Commit 'release: <version>'.
  Verify it landed by re-reading the file.
  GITHUB_CREATE_A_RELEASE: tag v<version>, target main, name 'KavoPDF <version>', draft false.
  GITHUB_CREATE_A_WORKFLOW_DISPATCH_EVENT workflow_id 401545091 ref v<version>.
  Poll GITHUB_LIST_WORKFLOW_RUNS_FOR_A_REPOSITORY up to ~25 min. One retry at most.

STEP 4 - VERIFY, THEN MARK IT SHIPPED
  GITHUB_GET_A_RELEASE_BY_TAG_NAME: an .apk asset must exist, several MB not a few KB,
  and NO asset may carry a label. No asset means the workflow skipped publishing because
  KEYSTORE_BASE64 is not visible to it - report that, never upload an unsigned build.
  versionName in build.gradle must equal the tag.
  gh api repos/kavopdf/app/compare/v<version>...main --jq '.ahead_by' must be 0.
  Website download link must point at releases/latest with no pinned version.

  ONLY AFTER the asset is confirmed present and signed:
      python3 tools/p2w-bench/round.py --mark-apk-shipped <version>
  Commit ROUND.json. Without this mark the cron publishes again tomorrow.
  If anything above failed, do NOT mark it.

WHAT DOES NOT WORK - verified

  NOTHING ON THAT LIST ANY MORE. Until 19 Nov every push returned 403 "Permission to
  kavopdf/app.git denied to Onyx-Node", and so did gh api POST .../git/refs and gh release
  delete; the workaround was GITHUB_COMMIT_MULTIPLE_FILES and GITHUB_DELETE_A_RELEASE. The
  cause was never a permission on the repository - the Sarvam GitHub App was not installed on
  the kavopdf organization at all. It was installed on 19 Nov with kavopdf/app selected and
  Contents: Read and write, and verified end to end: clone, commit, push -> 8e8fdd2..199d611.

  So commit and push with git, as the identity set in STEP 0. The MCP tools remain valid and
  are a fine fallback; they are no longer the required path, and a run must not spend itself
  on a workaround for a blocker that is gone.

  TWO THINGS STILL MAKE A PUSH FAIL, AND BOTH LOOK LIKE PERMISSIONS:
    * a commit authored as a private address - "push declined due to email privacy
      restrictions". The identity in STEP 0 is the fix; retrying is not.
    * the pre-commit gate refusing a change that was not measured across the whole corpus.
      There is no override. For a release commit that touches only build.gradle, scope.py will
      say no engine change and the gate passes in a second.

RATE LIMITS
  5000 core calls an hour. A 403 mentioning rate limit is temporary: wait for the reset
  and retry, up to three attempts. 'Resource not accessible by integration' is a
  permission problem and permanent for this run.

OUTPUT IS A HEADLINE PLUS A SMALL TABLE
    **<version> live - signed - all 3 rounds done - gate A clean - gate B held**
    | | |
    |---|---|
    | Version | <version> |
    | Tag matches | yes |
    | APK | <size> MB - signed |
    | Shipped | <n> commits - 0 left |
    | Gate A (p2w) | OK - <n> regressions - synthetic median <n.nn%> |
    | Gate B (legacy ratchet) | held / UNPROVEN - <why> |
    | Real-world | <median> - <worst> - <which document> |

RULES
  Read benchmarks/LAYER-POLICY.md before you judge any score.
  Never publish an unsigned APK. Never force-push. Never rewrite history.
  Never delete an older release. Never pass a label to an asset upload.
  Never mark it shipped unless the signed asset is confirmed present.
  Never estimate a number. Every number comes from STATE.json, RANKING.csv or a gate.
  Never cite the withdrawn 66% figure. It is retracted in benchmarks/LAYER-POLICY.md.

---

## YOUR REPORT COMES FROM report.py, NOT FROM YOU

**Never type a number. Generate the report and send it.**

    python3 tools/p2w-bench/report.py --for apk > /tmp/report.md
    python3 tools/p2w-bench/lastmessage.py --for apk --file /tmp/report.md

Then send exactly what `/tmp/report.md` now holds, plus at most a short prose paragraph saying what
this run concluded that the tables cannot show. `lastmessage.py` refuses a message whose numbers do
not match `report.py`, and it prints every one that is wrong - exit 3.

**Why this is not optional.** Four reports in a row carried numbers that were not true, and each one
cost a manual audit to find: a header clock that said 1h 07m for a 48-minute run; "of 212" for a
213-document corpus; a `.txt` section that was never written; an agent window with nothing behind
it; "29 files in 7 commits" where there were 25 in 8. Every one was a number somebody typed. The
generator cannot type a wrong number because it does not type at all.

**What is checked:** every Progress row; the header's `slot HH:MM -> HH:MM IST` and its duration
against RUN.json; any number in the corpus range against 213 / 212; the `.txt` clean and failing
counts; every deployed agent's `deployed_at`, `landed_at` and `minutes`; and every line carrying a
digit in report.py's own `The txt` and `Timing` tables, which must appear in your message unchanged.

If it refuses, do not reword the sentence - copy the number from `report.py --json`.

## WHOSE STAGE IS IT — read this before anything else

    python3 tools/p2w-bench/stage.py

It prints which of `measure-google` / `classify` / `fix` / `ship` the evidence says we are in, and what
the next action is. It is computed from the results on disk, never from a label, and `--set` refuses
when the evidence disagrees.

**If it is not your stage, say so in one line and stop.** That is not a wasted slot - it is the five
crons agreeing with each other instead of five runs each deciding for itself. `COORDINATION.md` has the
whole division of work and the settled decisions; read it once.

**Nothing changes without a measurement before and after.** The engine is not rewritten. One construct,
one measurement, one commit - kept only if nothing gets worse.


### This does NOT replace your claim step

Two state machines exist and they answer different questions:

    round.py --claim-<yours>   YOUR SLOT. Whoever holds it works. This is the one that gates you.
    stage.py                   THE MEASUREMENT PIPELINE - informational, for the gverify cron.

**They will disagree while the Google measurement is incomplete, and that is correct.** If `stage.py`
says `measure-google` but your claim succeeds, work - the measurement is another cron's job and is not
your blocker. Never stop because `stage.py` disagrees with your claim; only your claim decides.

