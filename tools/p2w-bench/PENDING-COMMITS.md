# Everything written but not committed

**EMPTY. THE WRITE PATH IS ALIVE AGAIN.**

From 18 Nov 21:12 to 19 Nov 16:00 `git push` returned 403, `gh api` writes returned 403 "Resource
not accessible by integration", and `GITHUB_COMMIT_MULTIPLE_FILES` was not in any run's tool list.
Everything written in that window piled up here.

The cause was never a permission on the repository. **The Sarvam GitHub App was not installed on
the `kavopdf` organization at all**, so the token could only reach public repositories. Sarvam
support found it, the app was installed on 19 Nov with `kavopdf/app` selected and Contents: Read and
write, and the backlog was landed the same afternoon:

    199d611  measure: four axes the table never had, and a gate that refuses to land a regression
    57a0507  engine: two fixes, each proved on the whole corpus before landing
    d51faf8  briefs: git push works again - say so, and say what actually made it fail
    c8c8ca2  baseline brief: the one operational fact the prompt had and the brief did not
    c88423b  apk: the fourth brief, so all four crons read their instructions from the repo

**If this file ever fills up again, the first thing to check is whether the app is still installed
on the organization** - `gh api /user/installations` returning an empty list is the signature. It is
not a repository permission and no amount of retrying fixes it.

Two things that DO still make a push fail, and both look like permissions: a commit authored as a
private address ("push declined due to email privacy restrictions"), and the pre-commit gate
refusing a change that was not measured across the whole corpus. Neither is fixed by retrying.

---
## The four patches

| # | file | what it carries | engine |
|--:|:--|:--|:--|
| 1 | `TXT-FULL-PARITY.patch` | 24 files: two check fixes, two tooling fixes, the re-stamped `.txt` baseline, and three specifications | **none** |
| 2 | `PATCH-411-ctm-size.patch` | the glyph-size CTM fix for `411_nested_xobject_transforms` | `PdfToWord.java` |
| 3 | `PATCH-t13-table-row-per-line.patch` | one table row is one `.txt` line | `TxtWriter.java` |
| 4 | `SPEC-justified-lines.md` | the `855f443` rebuild, specification only | none — the fixer implements it |

All four apply cleanly to `8e8fdd2`, and 1+2+3 apply together.

## Commit order, and why that order

**1. `TXT-FULL-PARITY.patch` first, alone.**

It carries two fixes to `verify_txt.py` that changed the `.txt` universe, so the baseline in the
same patch is the only baseline that matches it. Split them and one of the two halves is a lie:
a new verifier with an old table, or a new table nobody can reproduce.

Inside it, four separate things that should be **separate commits** even though they arrive in one
patch, so a bisect can find which one moved a number:

    a. verify_txt.py  t13 occurrence match    - the .txt table changes with this
    b. verify_txt.py  t12 empty token         - two documents stop failing
    c. round.py       the missing sh()        - no measurement changes
    d. lastmessage.py the number gate         - no measurement changes
    e. txt/RANKING-TXT.csv + RANKING-TXT-BASELINE.csv   - the re-stamp for (a) and (b)
    f. the three documents: PATCHES-READY.md, SPEC-justified-lines.md,
       FINDINGS/t02-t12-t08-root-causes.md, PENDING-NOW.md, this file

**2. `PATCH-411-ctm-size.patch` on its own**, after a build, `screen.py --docs
411_nested_xobject_transforms`, a full corpus pass and both ratchets. Expected: 411 → 0.00, the
other 212 unchanged, `.txt` byte-identical. **Do not commit it on the strength of this description.**

**3. `PATCH-t13-table-row-per-line.patch` last of the three**, because it changes the shape of every
table in the corpus and must be screened against `t02` and `t08` as well as `t13`. 109 of 213
documents carry the cell-per-line shape.

**4. `SPEC-justified-lines.md` is not a commit** — it is an instruction to the fixer.

## Work that exists only as a description

Four fixes were found, measured and kept by fixer runs whose commits died with their pods. They are
recoverable **as specifications, not as diffs**:

| commit | fix | documents | where the description lives |
|:--|:--|--:|:--|
| `16c5fdf` | 411 glyph size × CTM | 1 | 22:51 run report — **rebuilt as patch 2** |
| `2513a2d` | the same, second derivation | 1 | 00:58 run report |
| `c72c0ca` | the same, third derivation | 1 | 02:59 run report |
| `855f443` | justified lines → `w:jc="distribute"` | 22 | 04:56 run report — **written up as patch 4's spec** |

**Three runs derived the same 411 fix because the first one never landed.** The 22:51 version is
the one to implement: it uses the CTM alone, and the 00:58 version that multiplied by `|Trm|` as
well moved `041122` from 98.65 to 97.81.

## Also uncommitted, and not a patch

* `tools/p2w-bench/txt/RESTAMP-TXT.jsonl` — the 213 per-document records the re-stamp produced.
  **Commit it with the table**: it is the evidence the table was produced by a run, not typed.
* The cron prompt for the fixer was updated live (report must reach Drive on a failed commit;
  timing from files; `BLOCKERS.md` always travels with the report). **Cron prompts are not in the
  repo** — they live on the platform, so that change is already in force and needs no commit.

## How to tell this is done

    git log --oneline origin/main -1        # must not be 8e8fdd2
    python3 tools/p2w-bench/restamp_txt.py --report   # must say 213 scored
    python3 tools/p2w-bench/classify_txt.py --print   # must say 54 failing

If the first line still reads `8e8fdd2`, none of this has landed.
