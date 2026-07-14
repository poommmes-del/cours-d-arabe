import re
import unittest
from pathlib import Path


CSS = (Path(__file__).resolve().parents[1] / "site/assets/app.css").read_text(encoding="utf-8")
INDEX = (Path(__file__).resolve().parents[1] / "site/index.html").read_text(encoding="utf-8")


class SiteTypographyTest(unittest.TestCase):
    def test_beginner_arabic_title_typography_is_scoped(self) -> None:
        match = re.search(
            r"\.course-tile h3,\s*#courseTitle,\s*#moduleTitle\s*\{(?P<body>[^}]*)\}",
            CSS,
        )
        self.assertIsNotNone(match)
        body = match.group("body")
        self.assertIn("font-family: var(--font-ar);", body)
        self.assertIn("font-weight: 400;", body)
        self.assertIn("line-height: 1.55;", body)

    def test_title_typography_stylesheet_is_cache_busted(self) -> None:
        self.assertIn('href="assets/app.css?v=20260713-26px-titles"', INDEX)

    def test_course_tile_titles_are_large_enough(self) -> None:
        match = re.search(r"\.course-tile h3\s*\{(?P<body>[^}]*)\}", CSS)
        self.assertIsNotNone(match)
        self.assertIn("font-size: 26px;", match.group("body"))

    def test_module_tile_titles_are_beginner_friendly(self) -> None:
        match = re.search(r"\.lesson-main strong\s*\{(?P<body>[^}]*)\}", CSS)
        self.assertIsNotNone(match)
        body = match.group("body")
        self.assertIn("font-family: var(--font-ar);", body)
        self.assertIn("font-size: 26px;", body)
        self.assertIn("font-weight: 400;", body)
        self.assertIn("line-height: 1.5;", body)


if __name__ == "__main__":
    unittest.main()
