# Finding: `gverify.py --collect` could not be called with what `GOOGLEDRIVE_DOWNLOAD_FILE` returns

**Date:** 23 Nov 2026
**File patched:** `gverify.py` (one new pure function `download_source()` + the fetch step in `collect()`)
**Defect recorded by:** the 04:47 fixer run, 23 Nov 2026, verbatim —

> `GOOGLEDRIVE_DOWNLOAD_FILE` does NOT return `downloaded_file_content.s3url` any more — it returns `artifacts[0].workspace_path`, a local path. `gverify.py --collect` expects an s3url, so it cannot be called with what the tool hands back today.

## What the code expected

`gverify.py` reads a download result in exactly one place: the `--collect` path.

```python
def collect(name, url):
    ...
    r = subprocess.run(["curl", "-sL", "--max-time", "120", url, "-o", tmp], ...)
```

`url` came from `argv` (`--collect <name> <url>`, `nargs=2`) and was handed to `curl`
unexamined. The docstring said what it had to be — `gverify.py --collect <name> <s3url>`, step
`d` of the four-step loop — so the contract was: **a fetchable URL string, i.e.
`downloaded_file_content.s3url`**. Nothing in the file read a dict at all, so the key
`downloaded_file_content.s3url` was never touched by name; the dependency was on the *string*
the caller extracted from it, and the extraction lived in the caller (the cron), not here.

No other code path in `gverify.py` reads a download result. `--plan`, `--stage`, `--report`,
`--matrix` and `collect_lo()` all read local files or local JSON; `collect_lo()` renders with
soffice and never downloads. `verify_google.py` does **not** read a download result either — it
takes two local file paths (`src`, `gd`) plus optional `--docx`/`--json`/`--detail`, and contains
no `curl`, `urlopen`, `requests`, `s3url`, `s3key`, `artifacts` or `workspace_path` at all (its only
occurrence of the word "download" is prose at line ~1541 about comments being dropped). **No patch
was needed there**, so `verify_google.py` is untouched.

## What the tool returns now

```json
{"artifacts": [{"workspace_path": "/tmp/....pdf", ...}]}
```

A local filesystem path that is already fetched. Passing it to `curl` produced either a
curl error or — worse — a file named like the path that was not the export, and `--collect`
returned 2/3 and recorded nothing. The cron therefore collected no render at all: the instrument
was not reporting a bad score, it was not reporting.

## The fix

One pure function, `download_source(result)`, does the key-reading that used to be implicit in
the caller's argument:

| input | returns |
|---|---|
| `{"downloaded_file_content": {"s3url": "https://…"}}` | the s3url (old shape, **unchanged**) |
| `{"artifacts": [{"workspace_path": "/tmp/x.pdf"}]}` | `/tmp/x.pdf` (new shape) |
| both present | the `workspace_path` — **new shape preferred**: a local path is already fetched, an s3url is a second download that can fail on its own |
| several artifacts | the one whose `workspace_path` ends in `.pdf`; if none is named `.pdf`, the first entry that has a `workspace_path` |
| a bare string (an s3url or a local path) | itself — the shell still passes one argument, as before |
| a string that parses as a JSON object | treated as the tool result it is, so the cron can paste the whole response |
| top-level `s3url` (flattened wrappers) | that, as a last fallback |
| neither shape | `ValueError` |

`collect()` now calls `download_source(url)` and branches on the result: a value with an
`http://` / `https://` / `s3://` / `gs://` / `file://` scheme goes through the **existing**
`curl` call untouched; anything else is copied locally with `shutil.copyfile` into the same
`<name>.pdf.part` path, so everything downstream — the `%PDF-` magic check, the page-count
refusal, `verify_google.py`, `_write()` and its engine stamp, `collect_lo()` — runs exactly as
before. A `ValueError` from `download_source` prints `cannot collect <name>: …` and returns 2,
the same code a failed download returned.

### Failing loudly

The error names what actually came back, not just what was wanted:

```
GOOGLEDRIVE_DOWNLOAD_FILE result has neither artifacts[].workspace_path nor
downloaded_file_content.s3url (top-level keys: ['bytes', 'download_url'])
```

```
GOOGLEDRIVE_DOWNLOAD_FILE result has neither artifacts[].workspace_path nor
downloaded_file_content.s3url (top-level keys: ['artifacts']; artifacts has 1 entry;
artifacts[0] keys: ['s3key'])
```

It reports the sorted top-level keys, whether `artifacts` is a list (and its length), the sorted
keys of `artifacts[0]` when that is a dict, or its type when it is not, and the type of
`downloaded_file_content` when that key exists but carries no s3url. An empty or non-dict result
gets its own message with the value repr'd.

### What was deliberately not changed

No branch, flag or fallback was removed. `--plan`, `--stage`, `--lo`, `--matrix`, `--report`,
the `_RES_REPO`/`_RES_WORK` selection, `_done()`'s engine-stamp logic, `_write()`, the
page-count refusal and the `collect_lo()` pair-measurement are byte-identical. The `curl`
invocation itself is unchanged apart from reading `target` instead of `url`. No new dependency
(`json` and `shutil` were already available; `shutil` is imported locally in `stage()` already).

## The test

`test_gverify_download_shape.py`, 12 tests, all against a fake tool result — no network, no Drive,
no real file. It imports `download_source` directly and covers the four required cases plus the
preference rule, the multi-artifact rule, the JSON-string form and four failure messages.

```
$ python3 test_gverify_download_shape.py
test_artifacts_not_a_list_is_reported (__main__.FailsLoudly.test_artifacts_not_a_list_is_reported) ... ok
test_artifacts_without_workspace_path_prints_artifacts_0_keys (__main__.FailsLoudly.test_artifacts_without_workspace_path_prints_artifacts_0_keys) ... ok
test_downloaded_file_content_present_but_without_s3url (__main__.FailsLoudly.test_downloaded_file_content_present_but_without_s3url) ... ok
test_empty_dict_names_what_came_back (__main__.FailsLoudly.test_empty_dict_names_what_came_back) ... ok
test_unknown_shape_prints_returned_keys (__main__.FailsLoudly.test_unknown_shape_prints_returned_keys) ... ok
test_new_shape_wins_when_both_are_present (__main__.NewShape.test_new_shape_wins_when_both_are_present) ... ok
test_picks_the_pdf_out_of_several_artifacts (__main__.NewShape.test_picks_the_pdf_out_of_several_artifacts) ... ok
test_single_unnamed_artifact_is_taken_as_is (__main__.NewShape.test_single_unnamed_artifact_is_taken_as_is) ... ok
test_whole_tool_result_pasted_as_json (__main__.NewShape.test_whole_tool_result_pasted_as_json) ... ok
test_workspace_path_from_artifacts (__main__.NewShape.test_workspace_path_from_artifacts) ... ok
test_s3url_from_downloaded_file_content (__main__.OldShape.test_s3url_from_downloaded_file_content) ... ok
test_s3url_passed_as_a_bare_string_still_works (__main__.OldShape.test_s3url_passed_as_a_bare_string_still_works) ... ok

----------------------------------------------------------------------
Ran 12 tests in 0.007s

OK
```

Mapping to the required assertions: **(a)** `test_s3url_from_downloaded_file_content`;
**(b)** `test_workspace_path_from_artifacts`; **(c)** `test_picks_the_pdf_out_of_several_artifacts`;
**(d)** `test_unknown_shape_prints_returned_keys` (plus `test_empty_dict_names_what_came_back`).

Also checked: `gverify.py` parses, `python3 gverify.py --help` exits clean, and the CLI's other
subcommands are untouched. `--collect` itself was not run end-to-end, because that needs
`/scratch/work/p2w/corpus`, the `.docx` corpus and PyMuPDF; the fetch branch was verified by
`_is_url()` and by the 12 tests above.

## What would prove the fix wrong

1. **A third response shape.** If `GOOGLEDRIVE_DOWNLOAD_FILE` starts returning something else —
   `{"file": {"path": …}}`, a bare list, `{"artifacts": [{"local_path": …}]}`, a presigned url
   under a new key — `download_source()` raises rather than silently mis-fetching. That is the
   designed outcome, and the raised message will print the new keys, but the cron still collects
   nothing until the branch is added. Any future `ValueError` from this function in a cron log
   **is** this finding recurring in a new shape, and should be treated as a defect, not a
   transient error.
2. **An artifact list with more than one `.pdf`.** The function takes the first `.pdf`. If the
   export ever returns, say, the export plus the source, the wrong PDF could be scored — and it
   would look like a layout failure. A guard would be to check `mime_type == "application/pdf"`
   or to require the artifact name to match `<name>.pdf`; neither is implemented, because the
   observed shape carries one artifact.
3. **A `workspace_path` that is not a real file, or that points outside the sandbox.** The copy
   fails with `cannot read the local artifact …` and returns 2 — loud, but only at collect time.
   If the path is real but stale (an artifact from a previous run), the page-count check would
   refuse it and record `page_count_refused`, which would be a *false* refusal. Nothing in the
   response identifies which file it is, so this cannot be detected from the shape alone.
4. **A path containing a scheme-like prefix** (`http://…` inside a filename) would be sent to
   `curl`. Contrived, but it is the one way the branch choice can be fooled.
5. **The real proof it works is a cron run that records a Google score.** If the next scheduled
   run still writes no `gverify/*.json` with an engine stamp, the fix has not helped and the
   remaining break is downstream of `download_source()`.
