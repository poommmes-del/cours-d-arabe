from __future__ import annotations

import csv
import json
import re
import subprocess
import unittest
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "site" / "data" / "catalog.json"
TRANSCRIPT_FIRST_SECTIONS = (
    "الهدف",
    "قبل أن تبدأ",
    "شرح المسألة",
    "القاعدة",
    "لماذا؟",
    "أمثلة متدرجة",
    "تحليل خطوة خطوة",
    "خطأ شائع",
    "تدريب موجه",
    "تدريب مستقل",
    "خلاصة للحفظ",
)
VERIFICATION_STATUSES = ("transcript", "grammar", "arabic", "pedagogy")
ARABIC_DIACRITICS = re.compile(r"[\u064b-\u065f\u0670\u06d6-\u06ed]")
APPLIED_TASKS = re.compile(
    r"(?:^|[\s،؛:؟.!«])"
    r"(?:اعرب|صنف|زن|استخرج|حلل|صحح|انشئ|اختبر|طبق|ميز|اكمل|اذكر\s+مثال(?:ا)?)"
    r"(?=$|[\s،؛:؟.!»])"
)


def resolve_site_href(href: str) -> Path:
    if href.startswith("../"):
        return (ROOT / "site" / href).resolve()
    return (ROOT / href).resolve()


def transcript_first_source_map(course_id: str) -> dict | None:
    path = ROOT / "cours-pedagogiques" / course_id / "source-map.json"
    if not path.exists():
        return None
    source_map = json.loads(path.read_text(encoding="utf-8"))
    modules = source_map.get("modules", [])
    if source_map.get("schema_version") != 2 or not modules:
        return None
    if not all(
        module.get("verification", {}).get(status) == "verified"
        for module in modules
        for status in VERIFICATION_STATUSES
    ):
        return None
    return source_map


def normalize_arabic(text: str) -> str:
    text = ARABIC_DIACRITICS.sub("", text).replace("ـ", "")
    return text.translate(str.maketrans("أإآٱ", "اااا"))


def has_applied_task(question: str) -> bool:
    return APPLIED_TASKS.search(normalize_arabic(question)) is not None


class SiteDataTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = json.loads(CATALOG.read_text(encoding="utf-8"))

    def assert_transcript_first_contract(self, course: dict, source_map: dict) -> None:
        modules = course.get("modules", [])
        expected_modules = [
            (module["id"], module["title"])
            for module in source_map["modules"]
        ]
        actual_modules = [(module.get("id"), module.get("title")) for module in modules]
        self.assertEqual(expected_modules, actual_modules, course["id"])

        for index, module in enumerate(modules):
            headings = [
                match.group(1).strip()
                for match in re.finditer(r"^###\s+(.+?)\s*$", module.get("markdown", ""), re.MULTILINE)
            ]
            final_section = "تشخيص قبلي" if index == 0 else "مراجعة تراكمية"
            self.assertEqual(
                [*TRANSCRIPT_FIRST_SECTIONS, final_section],
                headings,
                f"{course['id']} {module['id']}",
            )
            self.assertEqual(13, 1 + len(headings), f"{course['id']} {module['id']}")
            self.assertGreaterEqual(len(module.get("questions", [])), 8, module["id"])
            self.assertLessEqual(len(module.get("questions", [])), 10, module["id"])

    def test_catalog_totals_match_manifests(self) -> None:
        with (ROOT / "audios-opus" / "manifest.tsv").open(encoding="utf-8") as handle:
            manifest_rows = list(csv.DictReader(handle, delimiter="\t"))
        inventory_count = 0
        for inventory in (ROOT / "archive-items").glob("*/inventory.tsv"):
            with inventory.open(encoding="utf-8") as handle:
                inventory_count += sum(1 for _ in handle) - 1

        self.assertEqual(len(self.catalog["courses"]), self.catalog["course_count"])
        self.assertEqual(len(manifest_rows), self.catalog["lesson_count"])
        self.assertEqual(inventory_count, self.catalog["lesson_count"])

    def test_catalog_has_contiguous_public_course_order(self) -> None:
        expected_ids = [
            "ajroumiya",
            "moutammima",
            "qatr-nada",
            "qawaid-i3raab-sa3di",
            "qawaid-i3raab-zawawi",
            "mawsil-toullab",
            "shoudhour-dhahab",
            "alfiya-nahw",
            "moulakhas-sarfi",
            "nadhm-maqsoud",
            "alfiya-sarf",
            "laamiya-af3al",
            "dourous-balagha",
            "maani-we-bayan",
        ]
        self.assertEqual(expected_ids, [course["id"] for course in self.catalog["courses"]])
        self.assertEqual(list(range(1, 15)), [course["order"] for course in self.catalog["courses"]])

    def test_ajroumiya_is_separate_beginner_course(self) -> None:
        courses = self.catalog["courses"]
        course_ids = [course["id"] for course in courses]
        nahw_ids = [course["id"] for course in courses if course["group"] == "Nahw"]

        self.assertIn("ajroumiya", course_ids)
        self.assertIn("moutammima", course_ids)
        self.assertEqual("ajroumiya", nahw_ids[0])
        self.assertEqual("moutammima", nahw_ids[1])

        ajroumiya = next(course for course in courses if course["id"] == "ajroumiya")
        self.assertEqual(30, ajroumiya["lesson_count"])
        self.assertGreater(len(ajroumiya["resources"]["items"]), 0)

    def test_ajroumiya_modules_keep_source_audio_spans(self) -> None:
        ajroumiya = next(course for course in self.catalog["courses"] if course["id"] == "ajroumiya")

        self.assertEqual(
            {
                "lesson_id": "002-شرح المقدمة الآجرومية للأستاذ محمود الشافعي (2)",
                "start_seconds": 6,
                "end_seconds": 2407,
            },
            ajroumiya["modules"][1]["audio_spans"][0],
        )

    def test_ajroumiya_has_pedagogical_modules_not_transcript_copy(self) -> None:
        ajroumiya = next(course for course in self.catalog["courses"] if course["id"] == "ajroumiya")
        modules = ajroumiya.get("modules", [])
        module_text = "\n\n".join(module.get("markdown", "") for module in modules)

        self.assertGreaterEqual(len(modules), 10)
        self.assertIn("| العلامة | المثال | الكلمة | السبب |", module_text)
        self.assertIn("أمثلة", module_text)
        self.assertIn("تدريب", module_text)
        self.assertNotIn("request_id:", module_text)
        self.assertNotIn("## Segments", module_text)
        self.assertNotEqual(module_text[:500], ajroumiya["lessons"][0]["preview"][:500])

    def test_moutammima_uses_curriculum_modules_like_ajroumiya(self) -> None:
        moutammima = next(course for course in self.catalog["courses"] if course["id"] == "moutammima")
        source_map = transcript_first_source_map("moutammima")

        self.assertIsNotNone(source_map)
        self.assert_transcript_first_contract(moutammima, source_map)

    def test_remaining_courses_use_curriculum_modules_not_audio_chunks(self) -> None:
        required_titles = {
            "qatr-nada": ("مدخل", "الإعراب والبناء", "المرفوعات", "المنصوبات", "المجرورات"),
            "qawaid-i3raab-sa3di": ("مدخل", "الجمل", "العوامل", "التطبيق"),
            "qawaid-i3raab-zawawi": ("مدخل", "الجمل", "العوامل", "التطبيق"),
            "mawsil-toullab": ("مدخل", "الجمل", "العوامل", "الإعراب"),
            "shoudhour-dhahab": ("مدخل", "المرفوعات", "المنصوبات", "التوابع", "الأبواب المتقدمة"),
            "alfiya-nahw": ("مدخل", "الكلام", "المرفوعات", "المنصوبات", "التوابع", "الأبواب المتقدمة"),
            "moulakhas-sarfi": ("مدخل", "الميزان", "الأفعال", "المصادر", "الإعلال"),
            "nadhm-maqsoud": ("مدخل", "الميزان", "الأبواب", "الإعلال", "الزوائد"),
            "alfiya-sarf": ("مدخل", "الأفعال", "المصادر", "الإعلال", "الإبدال"),
            "laamiya-af3al": ("مدخل", "الأبواب", "المجرد", "المزيد", "الإعلال"),
            "dourous-balagha": ("مدخل", "الفصاحة", "المعاني", "البيان", "البديع"),
            "maani-we-bayan": ("مدخل", "المعاني", "البيان", "التطبيق"),
        }
        excluded = {"ajroumiya", "moutammima"}
        for course in self.catalog["courses"]:
            if course["id"] in excluded:
                continue
            source_map = transcript_first_source_map(course["id"])
            if source_map is not None:
                self.assert_transcript_first_contract(course, source_map)
                continue
            modules = course.get("modules", [])
            titles = [module.get("title", "") for module in modules]
            module_text = "\n\n".join(module.get("markdown", "") for module in modules)
            generic_examples = sum(module_text.count(example) for example in ("جَاءَ زَيْدٌ", "رَأَيْتُ زَيْدًا", "مَرَرْتُ بِزَيْدٍ"))

            self.assertGreaterEqual(len(modules), 8, course["id"])
            self.assertFalse(any(re.search(r"الدروس\s+\d+\s*-\s*\d+", title) for title in titles), course["id"])
            self.assertLessEqual(generic_examples, 4, course["id"])
            self.assertIn("تدريب", module_text, course["id"])
            self.assertTrue("| الباب |" in module_text or "| المسألة |" in module_text or "| الصيغة |" in module_text, course["id"])
            for required_title in required_titles[course["id"]]:
                self.assertTrue(any(required_title in title for title in titles), f"{course['id']}: {required_title}")

    def test_all_courses_have_modules_and_questionnaires(self) -> None:
        generic_prompts = {
            "ما موضوع هذه الوحدة؟",
            "ما أهم قاعدة ينبغي حفظها هنا؟",
            "كيف تميز المسألة عند قراءة مثال جديد؟",
            "ما الخطأ الشائع الذي ينبغي تجنبه؟",
            "ما تدريبك العملي بعد هذه الوحدة؟",
        }
        for course in self.catalog["courses"]:
            modules = course.get("modules", [])
            self.assertGreater(len(modules), 0, course["id"])
            for module in modules:
                questions = module.get("questions", [])
                self.assertGreaterEqual(len(questions), 5, f"{course['id']} {module['id']}")
                question_texts = [question.get("question", "") for question in questions]
                self.assertFalse(generic_prompts.intersection(question_texts), f"{course['id']} {module['id']}")
                self.assertTrue(
                    any(has_applied_task(text) for text in question_texts),
                    f"{course['id']} {module['id']}",
                )
                for question in questions:
                    self.assertGreater(len(question.get("question", "")), 10)
                    self.assertGreater(len(question.get("answer", "")), 10)
                self.assertNotIn("request_id:", module.get("markdown", ""))
                self.assertNotIn("## Segments", module.get("markdown", ""))

    def test_site_exposes_course_tab_before_raw_transcription(self) -> None:
        index = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
        js = (ROOT / "site" / "assets" / "app.js").read_text(encoding="utf-8")

        self.assertIn('data-tab="course"', index)
        self.assertIn('id="courseContent"', index)
        self.assertIn('data-tab="quiz"', index)
        self.assertIn('id="quizList"', index)
        self.assertIn("function renderMarkdown", js)
        self.assertIn("function renderQuiz", js)
        self.assertIn("Voir corrigé", js)
        self.assertIn("Corrigé", js)
        self.assertNotIn('"Valider"', js)
        self.assertNotIn('"Validée"', js)

    def test_matn_charh_tab_is_third_after_quiz(self) -> None:
        index = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
        tabs = re.findall(r'class="tab[^"]*"\s+data-tab="([^"]+)"', index)

        self.assertEqual(["course", "quiz", "resources"], tabs[:3])

    def test_layout_uses_course_tiles_without_left_sidebar(self) -> None:
        index = (ROOT / "site" / "index.html").read_text(encoding="utf-8")

        self.assertNotIn('class="sidebar"', index)
        self.assertNotIn('id="courseNav"', index)
        self.assertNotIn('id="homeButton"', index)
        self.assertIn('id="backHomeButton"', index)
        self.assertIn('id="moduleGrid"', index)

    def test_modules_are_openable_tiles_with_persistent_progress(self) -> None:
        js = (ROOT / "site" / "assets" / "app.js").read_text(encoding="utf-8")

        self.assertIn("cours-arabe-progress-v1", js)
        self.assertIn("selectedModuleId", js)
        self.assertIn("function renderModuleTiles", js)
        self.assertIn("function toggleModuleDone", js)
        self.assertIn("localStorage", js)

    def test_home_tiles_are_laid_out_right_to_left(self) -> None:
        css = (ROOT / "site" / "assets" / "app.css").read_text(encoding="utf-8")
        grid_block = re.search(r"\.course-tile-grid\s*\{(?P<body>[^}]+)\}", css)
        tile_block = re.search(r"\.course-tile\s*\{(?P<body>[^}]+)\}", css)

        self.assertIsNotNone(grid_block)
        self.assertIsNotNone(tile_block)
        self.assertIn("direction: rtl;", grid_block.group("body"))
        self.assertIn("direction: ltr;", tile_block.group("body"))

    def test_all_lesson_assets_exist(self) -> None:
        seen_audio_paths = set()
        seen_transcripts = set()
        for course in self.catalog["courses"]:
            self.assertEqual(course["lesson_count"], len(course["lessons"]), course["id"])
            self.assertGreater(len(course["resources"]["items"]), 0, course["id"])
            for lesson in course["lessons"]:
                audio_path = resolve_site_href(lesson["audio_path"])
                transcript_path = resolve_site_href(lesson["transcript_path"])
                self.assertTrue(audio_path.exists(), audio_path)
                self.assertTrue(transcript_path.exists(), transcript_path)
                self.assertGreater(lesson["duration_seconds"], 0, lesson["id"])
                self.assertGreater(lesson["word_count"], 0, lesson["id"])
                self.assertGreater(lesson["segment_count"], 0, lesson["id"])
                if lesson["confidence"] is not None:
                    self.assertGreaterEqual(lesson["confidence"], 0)
                    self.assertLessEqual(lesson["confidence"], 1)
                seen_audio_paths.add(audio_path)
                seen_transcripts.add(transcript_path)

        self.assertEqual(self.catalog["lesson_count"], len(seen_audio_paths))
        self.assertEqual(self.catalog["lesson_count"], len(seen_transcripts))

    def test_resource_local_paths_exist(self) -> None:
        for course in self.catalog["courses"]:
            for item in course["resources"]["items"]:
                for link in item.get("links", []):
                    href = link.get("href")
                    if not href or href.startswith("http"):
                        continue
                    if href.startswith("/home/"):
                        path = Path(href)
                    else:
                        path = resolve_site_href(href)
                    self.assertTrue(path.exists(), f"{course['id']}: {path}")

    def test_resources_can_be_consulted_inside_site(self) -> None:
        viewable_kinds = {"pdf", "html", "md", "txt"}
        for course in self.catalog["courses"]:
            viewer_links = [
                link
                for item in course["resources"]["items"]
                for link in item.get("links", [])
                if link.get("viewer_href")
            ]
            self.assertGreater(len(viewer_links), 0, course["id"])
            for link in viewer_links:
                self.assertIn(link.get("viewer_kind"), viewable_kinds, link)
                self.assertFalse(link["viewer_href"].startswith("/home/"), link)
                self.assertTrue(resolve_site_href(link["viewer_href"]).exists(), link)

    def test_ajroumiya_has_direct_matn_and_charh_readers(self) -> None:
        course = next(course for course in self.catalog["courses"] if course["id"] == "ajroumiya")
        direct_links = []
        for item in course["resources"]["items"]:
            for link in item.get("links", []):
                if link.get("viewer_kind") in {"pdf", "html"}:
                    direct_links.append((item["title"], link))

        matn = [
            link
            for title, link in direct_links
            if "Matn" in title or "متن" in title
        ]
        charh = [
            link
            for title, link in direct_links
            if "Sharh" in title or "شرح" in title
        ]

        self.assertTrue(matn, "Ajroumiya doit avoir un Matn consultable directement")
        self.assertTrue(charh, "Ajroumiya doit avoir un Charh consultable directement")
        self.assertTrue(any(link["viewer_kind"] == "pdf" for link in matn), matn)
        self.assertTrue(any(link["viewer_kind"] == "pdf" for link in charh), charh)

    def test_local_shamela_books_prefer_pdf_viewer(self) -> None:
        for course in self.catalog["courses"]:
            for item in course["resources"]["items"]:
                for link in item.get("links", []):
                    if not link.get("path", "").endswith("/book.md"):
                        continue
                    self.assertEqual(link.get("viewer_kind"), "pdf", f"{course['id']}: {link}")
                    self.assertTrue(link.get("viewer_href", "").endswith("/book.pdf"), link)

    def test_matn_resources_have_real_pdf(self) -> None:
        matn_titles = ("Matn", "متن", "Livre du cours", "Source proche")
        for course in self.catalog["courses"]:
            for item in course["resources"]["items"]:
                if not any(token in item["title"] for token in matn_titles):
                    continue
                pdf_links = [
                    link
                    for link in item.get("links", [])
                    if link.get("kind") == "pdf" and "../livres/pdf/" in link.get("href", "")
                ]
                self.assertTrue(pdf_links, f"{course['id']}: {item['title']}")

    def test_all_book_resources_have_author_and_real_pdf(self) -> None:
        for course in self.catalog["courses"]:
            for item in course["resources"]["items"]:
                self.assertTrue(item.get("author"), f"{course['id']}: {item['title']}")
                pdf_links = [
                    link
                    for link in item.get("links", [])
                    if link.get("kind") == "pdf" and "../livres/pdf/" in link.get("href", "")
                ]
                self.assertTrue(pdf_links, f"{course['id']}: {item['title']}")

    def test_qatr_nada_sharh_resources_have_real_pdf(self) -> None:
        course = next(course for course in self.catalog["courses"] if course["id"] == "qatr-nada")
        sharh_items = [
            item
            for item in course["resources"]["items"]
            if "Sharh" in item["title"] or "شرح" in item["title"]
        ]
        self.assertGreaterEqual(len(sharh_items), 2)
        for item in sharh_items:
            pdf_links = [
                link
                for link in item.get("links", [])
                if link.get("kind") == "pdf" and "../livres/pdf/qatr-nada/sharh/" in link.get("href", "")
            ]
            self.assertTrue(pdf_links, item["title"])

    def test_site_entrypoint_references_existing_assets(self) -> None:
        index = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
        js = (ROOT / "site" / "assets" / "app.js").read_text(encoding="utf-8")
        for href in re.findall(r'href="([^"]+)"', index):
            if href.startswith("http"):
                continue
            self.assertTrue((ROOT / "site" / urlsplit(href).path).exists(), href)
        for src in re.findall(r'src="([^"]+)"', index):
            if src.startswith("http"):
                continue
            self.assertTrue((ROOT / "site" / src).exists(), src)
        self.assertIn('data-tab="transcript"', index)
        self.assertIn('id="homeGrid"', index)
        self.assertIn('id="backHomeButton"', index)
        self.assertIn("function consultableResourceButtons", js)
        self.assertNotIn('id = "bookViewer"', js)
        self.assertIn("Consulter", js)
        self.assertIn('target="_blank"', js)

    def test_app_extracts_transcript_and_segments(self) -> None:
        script = r"""
const fs = require("fs");
const vm = require("vm");

const context = {
  console,
  document: {
    querySelector: () => ({}),
    querySelectorAll: () => [],
    body: {},
    createDocumentFragment: () => ({ append() {} }),
    createElement: () => ({ addEventListener() {}, append() {} }),
  },
  fetch: () => new Promise(() => {}),
  Intl,
  Map,
  RegExp,
  String,
  Number,
};
vm.runInNewContext(fs.readFileSync("site/assets/app.js", "utf8"), context);

const markdown = `# Exemple

## Transcription

نص التجربة

## Segments

[00:01 - 00:03] نص التجربة`;

const transcript = context.extractTranscript(markdown);
const segments = context.extractSegments(markdown);
console.log(JSON.stringify({ transcript, segmentCount: segments.length, firstText: segments[0]?.text }));
"""
        result = subprocess.run(
            ["node", "-e", script],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        parsed = json.loads(result.stdout)
        self.assertEqual("نص التجربة", parsed["transcript"])
        self.assertEqual(1, parsed["segmentCount"])
        self.assertEqual("نص التجربة", parsed["firstText"])

    def test_app_renders_markdown_tables_for_pedagogical_courses(self) -> None:
        script = r"""
const fs = require("fs");
const vm = require("vm");

const context = {
  console,
  document: {
    querySelector: () => ({}),
    querySelectorAll: () => [],
    body: {},
    createDocumentFragment: () => ({ append() {} }),
    createElement: () => ({ addEventListener() {}, append() {} }),
  },
  fetch: () => new Promise(() => {}),
  Intl,
  Map,
  RegExp,
  String,
  Number,
};
vm.runInNewContext(fs.readFileSync("site/assets/app.js", "utf8"), context);

const html = context.renderMarkdown(`مثال:

| العلامة | المثال |
|---|---|
| الضمة | \`جاء زيدٌ\` |

- تدريب سريع`);

console.log(JSON.stringify({
  hasTable: html.includes("<table>"),
  hasCode: html.includes("<code>جَاءَ زَيْدٌ</code>"),
  hasList: html.includes("<li>تدريب سريع</li>")
}));
"""
        result = subprocess.run(
            ["node", "-e", script],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        parsed = json.loads(result.stdout)
        self.assertTrue(parsed["hasTable"])
        self.assertTrue(parsed["hasCode"])
        self.assertTrue(parsed["hasList"])

    def test_beginner_reading_uses_larger_arabic_font_and_harakat(self) -> None:
        css = (ROOT / "site" / "assets" / "app.css").read_text(encoding="utf-8")
        for selector, minimum in ((".markdown-body", 23), (".transcript-text", 22)):
            with self.subTest(selector=selector):
                blocks = re.findall(rf"{re.escape(selector)}\s*\{{(?P<body>[^}}]+)\}}", css)
                self.assertTrue(blocks, f"Aucune règle trouvée pour {selector}")
                sizes = [
                    float(value)
                    for block in blocks
                    for value in re.findall(r"font-size:\s*([0-9]+(?:\.[0-9]+)?)px", block)
                ]
                self.assertTrue(sizes, f"Aucune taille en px trouvée pour {selector}")
                self.assertTrue(
                    all(size >= minimum for size in sizes),
                    f"{selector}: toutes les tailles {sizes} doivent être >= {minimum}px",
                )

        script = r"""
const fs = require("fs");
const vm = require("vm");

const context = {
  console,
  document: {
    querySelector: () => ({}),
    querySelectorAll: () => [],
    body: {},
    createDocumentFragment: () => ({ append() {} }),
    createElement: () => ({ addEventListener() {}, append() {} }),
  },
  fetch: () => new Promise(() => {}),
  Intl,
  Map,
  RegExp,
  String,
  Number,
};
vm.runInNewContext(fs.readFileSync("site/assets/app.js", "utf8"), context);

const html = context.renderMarkdown("الإعراب مثال: `جاء زيدٌ`");
console.log(JSON.stringify({
  hasIrab: html.includes("الْإِعْرَابُ"),
  hasExample: html.includes("جَاءَ زَيْدٌ")
}));
"""
        result = subprocess.run(
            ["node", "-e", script],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        parsed = json.loads(result.stdout)
        self.assertTrue(parsed["hasIrab"])
        self.assertTrue(parsed["hasExample"])


if __name__ == "__main__":
    unittest.main()
