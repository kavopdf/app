#!/usr/bin/env python3
"""test_gverify_download_shape.py - the two shapes GOOGLEDRIVE_DOWNLOAD_FILE has returned.

The 04:47 fixer run on 23 Nov 2026 recorded the defect verbatim:

    "GOOGLEDRIVE_DOWNLOAD_FILE does NOT return downloaded_file_content.s3url any more -
     it returns artifacts[0].workspace_path, a local path. gverify.py --collect expects
     an s3url, so it cannot be called with what the tool hands back today."

These four tests are that claim, and the fix, made executable. They exercise
gverify.download_source() with a FAKE tool result - no network, no Drive, no real file.

    python3 test_gverify_download_shape.py
"""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gverify import download_source  # noqa: E402


class OldShape(unittest.TestCase):
    """The shape the code was written against, and which must keep working."""

    def test_s3url_from_downloaded_file_content(self):
        result = {"downloaded_file_content": {"s3url": "https://files.example/x.pdf?sig=abc"},
                  "file_id": "1AbC"}
        self.assertEqual(download_source(result),
                         "https://files.example/x.pdf?sig=abc")

    def test_s3url_passed_as_a_bare_string_still_works(self):
        # The shell has always handed --collect a bare url; nothing about that may change.
        self.assertEqual(download_source("https://files.example/x.pdf?sig=abc"),
                         "https://files.example/x.pdf?sig=abc")


class NewShape(unittest.TestCase):
    """What the tool hands back today."""

    def test_workspace_path_from_artifacts(self):
        result = {"artifacts": [{"workspace_path": "/tmp/x.pdf"}]}
        self.assertEqual(download_source(result), "/tmp/x.pdf")

    def test_new_shape_wins_when_both_are_present(self):
        # A local path is already fetched; an s3url is a second download that can fail.
        result = {"artifacts": [{"workspace_path": "/tmp/x.pdf"}],
                  "downloaded_file_content": {"s3url": "https://files.example/x.pdf"}}
        self.assertEqual(download_source(result), "/tmp/x.pdf")

    def test_picks_the_pdf_out_of_several_artifacts(self):
        result = {"artifacts": [
            {"workspace_path": "/tmp/x.json", "mime_type": "application/json"},
            {"workspace_path": "/tmp/x.pdf", "mime_type": "application/pdf"},
            {"workspace_path": "/tmp/x.png", "mime_type": "image/png"},
        ]}
        self.assertEqual(download_source(result), "/tmp/x.pdf")

    def test_single_unnamed_artifact_is_taken_as_is(self):
        result = {"artifacts": [{"workspace_path": "/tmp/download-7f3e"}]}
        self.assertEqual(download_source(result), "/tmp/download-7f3e")

    def test_whole_tool_result_pasted_as_json(self):
        # The cron may pass the response straight through as one argv element.
        blob = json.dumps({"artifacts": [{"workspace_path": "/tmp/x.pdf"}]})
        self.assertEqual(download_source(blob), "/tmp/x.pdf")


class FailsLoudly(unittest.TestCase):
    """A shape nobody has seen yet must name itself, not raise a bare KeyError."""

    def test_empty_dict_names_what_came_back(self):
        with self.assertRaises(ValueError) as cm:
            download_source({})
        self.assertIn("no usable result", str(cm.exception))

    def test_unknown_shape_prints_returned_keys(self):
        result = {"download_url": "https://files.example/x.pdf", "bytes": 12}
        with self.assertRaises(ValueError) as cm:
            download_source(result)
        msg = str(cm.exception)
        # The next run must not have to guess: top-level keys, and artifacts[0] if present.
        self.assertIn("download_url", msg)
        self.assertIn("bytes", msg)
        self.assertIn("workspace_path", msg)          # names the shape it wanted
        self.assertIn("s3url", msg)

    def test_artifacts_without_workspace_path_prints_artifacts_0_keys(self):
        result = {"artifacts": [{"s3key": "abc/x.pdf", "url": "https://files.example/x"}]}
        with self.assertRaises(ValueError) as cm:
            download_source(result)
        msg = str(cm.exception)
        self.assertIn("artifacts[0] keys", msg)
        self.assertIn("s3key", msg)
        self.assertIn("url", msg)

    def test_artifacts_not_a_list_is_reported(self):
        with self.assertRaises(ValueError) as cm:
            download_source({"artifacts": {"workspace_path": "/tmp/x.pdf"}})
        self.assertIn("not a list", str(cm.exception))

    def test_downloaded_file_content_present_but_without_s3url(self):
        with self.assertRaises(ValueError) as cm:
            download_source({"downloaded_file_content": {"bytes": 12}})
        self.assertIn("downloaded_file_content is dict", str(cm.exception))


if __name__ == "__main__":
    unittest.main(verbosity=2)
