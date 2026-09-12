import json
import unittest
from pathlib import Path

from diffintent.core import analyze_diff, filter_files
from diffintent.cli import main

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = (ROOT / "examples" / "sample.diff").read_text(encoding="utf-8")


class ParseAnalyzeTests(unittest.TestCase):
    def test_sample_summary(self):
        analysis = analyze_diff(SAMPLE)
        self.assertGreaterEqual(analysis.totals["files"], 5)
        self.assertIn("code", analysis.summary)
        self.assertIn("tests", analysis.summary)
        self.assertIn("docs", analysis.summary)
        self.assertIn("deps", analysis.summary)
        self.assertIn("ci", analysis.summary)
        self.assertIn("config", analysis.summary)

    def test_filter_only_tests(self):
        analysis = filter_files(analyze_diff(SAMPLE), ["tests"])
        self.assertTrue(all(f.category == "tests" for f in analysis.files))
        self.assertEqual(analysis.totals["files"], 1)

    def test_cli_json(self, cap=None):
        import io
        import contextlib

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = main([str(ROOT / "examples" / "sample.diff"), "--json"])
        self.assertEqual(code, 0)
        data = json.loads(buf.getvalue())
        self.assertIn("summary", data)
        self.assertIn("files", data)


if __name__ == "__main__":
    unittest.main()
