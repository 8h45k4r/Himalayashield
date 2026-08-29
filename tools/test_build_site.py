"""Gate 3 tests for the site build — including the failure path.

Zero-install: python3 -m unittest discover -s tools
No network: live mode is exercised through a fixture.
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_site  # noqa: E402

FIXTURE = {
    "features": [
        {"properties": {"mag": 4.4, "time": 1787690000000,
                        "place": "Nepal-Xizang border region <b>xss</b>"},
         "geometry": {"coordinates": [85.4, 28.3, 10.0]}},
        {"properties": {"mag": 3.1, "time": 1787000000000, "place": "western Nepal"},
         "geometry": {"coordinates": [82.1, 29.0, 33.0]}},
        {"properties": {"mag": None, "time": 1787000001000, "place": "dropped"},
         "geometry": {"coordinates": [82.1, 29.0, None]}},
    ]
}


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.out = Path(self.tmp.name) / "_site"
        self.fixture = Path(self.tmp.name) / "fixture.json"
        self.fixture.write_text(json.dumps(FIXTURE), "utf-8")
        os.environ["SOURCE_DATE_EPOCH"] = "1788220800"  # 2026-08-31 UTC, fixed

    def tearDown(self):
        os.environ.pop("SOURCE_DATE_EPOCH", None)
        self.tmp.cleanup()

    def read_index(self):
        return (self.out / "index.html").read_text("utf-8")

    def test_live_build_from_fixture(self):
        rc = build_site.main(["--out", str(self.out), "--input", str(self.fixture)])
        self.assertEqual(rc, 0)
        page = self.read_index()
        self.assertIn("workbench, not a warning system", page)
        self.assertIn("● FEED LIVE", page)
        self.assertIn("<svg", page)
        self.assertIn("M4.4", page)                     # direct label on the max
        self.assertIn("26 Aug collapse", page)          # reference annotation
        self.assertIn("⊘ OFFLINE", page)                # corridor board is honest
        self.assertIn("✱ UNVERIFIED", page)
        self.assertIn("Tsho Rolpa", page)               # lake watch board renders
        self.assertIn("Imja", page)

    def test_upstream_html_is_escaped(self):
        build_site.main(["--out", str(self.out), "--input", str(self.fixture)])
        page = self.read_index()
        self.assertNotIn("<b>xss</b>", page)
        self.assertIn("&lt;b&gt;xss&lt;/b&gt;", page)

    def test_offline_build_is_loud_not_blank(self):
        rc = build_site.main(["--out", str(self.out), "--force-offline"])
        self.assertEqual(rc, 0)
        page = self.read_index()
        self.assertIn("⊘ FEED OFFLINE", page)
        self.assertIn("could not be reached", page)
        self.assertNotIn("<svg", page)                  # no charts without data
        self.assertIn("workbench, not a warning system", page)

    def test_console_is_built(self):
        build_site.main(["--out", str(self.out), "--input", str(self.fixture)])
        console = (self.out / "console" / "index.html").read_text("utf-8")
        self.assertIn("operations console", console)
        self.assertIn("workbench, not a warning system", console)
        self.assertIn("feed-chip", console)
        self.assertIn("operations console v0 (ADR 0005)", console)  # JS inlined
        self.assertIn("<noscript>", console)
        self.assertIn("Tsho Rolpa", console)                        # boards baked
        self.assertNotRegex(console, r'<script[^>]+src=')           # no external JS

    def test_api_endpoints(self):
        build_site.main(["--out", str(self.out), "--input", str(self.fixture)])
        for name in ("meta.json", "events.json", "corridors.json", "lakes.json"):
            payload = json.loads((self.out / "api" / name).read_text("utf-8"))
            self.assertIn("workbench, not a warning system",
                          payload["disclaimer"])
            self.assertIn("generated", payload)
        meta = json.loads((self.out / "api" / "meta.json").read_text("utf-8"))
        self.assertEqual(meta["feed"], "live")
        self.assertEqual(meta["events_in_window"], 2)
        ev = json.loads((self.out / "api" / "events.json").read_text("utf-8"))
        self.assertEqual(ev["events"][-1]["mag"], 4.4)

    def test_api_offline_is_marked(self):
        build_site.main(["--out", str(self.out), "--force-offline"])
        meta = json.loads((self.out / "api" / "meta.json").read_text("utf-8"))
        self.assertEqual(meta["feed"], "offline")
        feed = (self.out / "feed.xml").read_text("utf-8")
        self.assertIn("FEED OFFLINE at build time", feed)
        self.assertNotIn("<entry>", feed)

    def test_atom_feed_is_valid_xml(self):
        import xml.etree.ElementTree as ET
        build_site.main(["--out", str(self.out), "--input", str(self.fixture)])
        root = ET.fromstring((self.out / "feed.xml").read_text("utf-8"))
        ns = "{http://www.w3.org/2005/Atom}"
        entries = root.findall(ns + "entry")
        self.assertEqual(len(entries), 2)
        self.assertIn("M4.4", entries[0].find(ns + "title").text)

    def test_event_record_page(self):
        build_site.main(["--out", str(self.out), "--input", str(self.fixture)])
        page = (self.out / "events" / "2026-08-26-rasuwa" /
                "index.html").read_text("utf-8")
        self.assertIn("Rasuwa", page)
        self.assertIn("✱ UNVERIFIED", page)
        self.assertIn("∅ NULL — not guessed", page)
        self.assertIn("workbench, not a warning system", page)
        self.assertIn("custodian", page)

    def test_404_page(self):
        build_site.main(["--out", str(self.out), "--force-offline"])
        page = (self.out / "404.html").read_text("utf-8")
        self.assertIn("not watched", page)
        self.assertIn("⊘ OFFLINE", page)

    def test_budget_and_headers(self):
        build_site.main(["--out", str(self.out), "--input", str(self.fixture)])
        self.assertLessEqual((self.out / "index.html").stat().st_size,
                             build_site.BUDGET_BYTES)
        self.assertIn("Content-Security-Policy",
                      (self.out / "_headers").read_text("utf-8"))

    def test_deterministic(self):
        build_site.main(["--out", str(self.out), "--input", str(self.fixture)])
        first = self.read_index()
        build_site.main(["--out", str(self.out), "--input", str(self.fixture)])
        self.assertEqual(first, self.read_index())

    def test_bad_fixture_falls_back_to_offline(self):
        bad = Path(self.tmp.name) / "bad.json"
        bad.write_text("{not json", "utf-8")
        rc = build_site.main(["--out", str(self.out), "--input", str(bad)])
        self.assertEqual(rc, 0)
        self.assertIn("⊘ FEED OFFLINE", self.read_index())


if __name__ == "__main__":
    unittest.main()
