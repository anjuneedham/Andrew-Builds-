import re
import unittest

from dashboard import app as dash


class StaticAssetsTest(unittest.TestCase):
    def test_every_asset_the_page_references_is_served(self):
        html = dash.PAGE
        refs = re.findall(r'(?:src|href)="(/[^"]+)"', html)
        self.assertTrue(refs)
        for r in refs:
            self.assertIsNotNone(dash.static_file(r), f"{r} is referenced by index.html but not served")

    def test_stylesheet_is_well_formed_at_the_top(self):
        css = dash.static_file("/css/app.css")[1].decode()
        self.assertEqual(css.count("/*"), css.count("*/"), "unbalanced CSS comment")
        head = css.lstrip()
        end = head.index("*/") + 2 if head.startswith("/*") else 0
        self.assertTrue(head[end:].lstrip().startswith(":root"), "the first rule must be :root; stray text breaks the whole sheet")

    def test_no_leftover_os_pages_or_branding(self):
        html = dash.PAGE
        for bad in ("overview.js", "scout.js", "operator.js", "treasury.js", "plan.js", "Zero", "Z2R", "Matchday"):
            self.assertNotIn(bad, html)
        self.assertIsNone(dash.static_file("/js/overview.js"))

    def test_page_is_not_cached_and_has_security_headers(self):
        self.assertEqual(dash.HEADERS["Cache-Control"], "no-store")
        self.assertIn("script-src 'self'", dash.HEADERS["Content-Security-Policy"])


if __name__ == "__main__":
    unittest.main()
