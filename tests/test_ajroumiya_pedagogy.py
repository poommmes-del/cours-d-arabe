import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from outils import build_pedagogical_course as builder
from outils.build_pedagogical_course import (
    ModuleFragment,
    PedagogyValidationError,
    assemble_fragments,
    expected_module_id,
    load_lesson_durations,
    load_fragments,
    validate_source_batch,
    validate_source_map,
    validate_fragment,
    write_course,
)


REQUIRED = [
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
    "تشخيص قبلي",
]


def valid_text(title: str = "منزلة الآجرومية") -> str:
    sections = "\n\n".join(f"### {name}\n\nمحتوى عربي واضح." for name in REQUIRED)
    questions = "\n\n".join(
        f"{index}. سؤال تطبيقي رقم {index}؟\n- الجواب: جواب صحيح مع بيان السبب."
        for index in range(1, 9)
    )
    return f"## {title}\n\n{sections}\n\n### أسئلة التحقق\n\n{questions}\n"


def complete_source_map_fixture(
    root: Path,
    *,
    course_id: str = "ajroumiya",
    module_count: int = 25,
    count_range: tuple[int, int] = (25, 35),
    canonical_available: bool = True,
):
    source_dir = root / "sources"
    source_dir.mkdir()
    (source_dir / "matn.md").write_text("متن", encoding="utf-8")
    (source_dir / "charh.md").write_text("شرح", encoding="utf-8")
    lesson_count = max(30, module_count)
    durations = {f"lesson-{index:03d}": 100.0 for index in range(1, lesson_count + 1)}
    fragments = []
    modules = []
    for index in range(1, module_count + 1):
        title = f"الوحدة {index}"
        fragments.append(
            ModuleFragment(
                order=index,
                path=root / f"{index:02d}.md",
                title=title,
                text=valid_text(title),
                question_count=8,
            )
        )
        modules.append(
            {
                "id": expected_module_id(course_id, index, title),
                "title": title,
                "estimated_study_minutes": 20,
                "audio_spans": [
                    {
                        "lesson_id": f"lesson-{index:03d}",
                        "start_seconds": 0.0,
                        "end_seconds": 50.0,
                        "evidence": "دليل صوتي واضح",
                    }
                ],
                "canonical_refs": ["sources/matn.md"] if canonical_available else [],
                "supporting_refs": ["sources/charh.md"],
                "verification": {
                    "transcript": "verified",
                    "grammar": "verified",
                    "arabic": "verified",
                    "pedagogy": "verified",
                },
            }
        )
    excluded = [
        {
            "lesson_id": f"lesson-{index:03d}",
            "start_seconds": 0.0,
            "end_seconds": 100.0,
            "reason": "مادة إدارية",
        }
        for index in range(module_count + 1, lesson_count + 1)
    ]
    data = {
        "schema_version": 2,
        "course_id": course_id,
        "module_count_range": list(count_range),
        "source_inventory": {"canonical_available": canonical_available},
        "modules": modules,
        "excluded_spans": excluded,
    }
    return data, fragments, durations, root


class FragmentValidationTest(unittest.TestCase):
    def test_valid_fragment_parses_eight_questions(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "01-منزلة-الآجرومية.md"
            path.write_text(valid_text(), encoding="utf-8")
            fragment = validate_fragment(path, 1)
            self.assertEqual(1, fragment.order)
            self.assertEqual("منزلة الآجرومية", fragment.title)
            self.assertEqual(8, fragment.question_count)

    def test_fragment_rejects_missing_section(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "01-منزلة-الآجرومية.md"
            path.write_text(valid_text().replace("### لماذا؟", "### تفسير"), encoding="utf-8")
            with self.assertRaisesRegex(PedagogyValidationError, "لماذا؟"):
                validate_fragment(path, 1)

    def test_fragment_rejects_five_questions(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "01-منزلة-الآجرومية.md"
            text = valid_text()
            text = text[: text.index("6. سؤال تطبيقي")]
            path.write_text(text, encoding="utf-8")
            with self.assertRaisesRegex(PedagogyValidationError, "8 إلى 10"):
                validate_fragment(path, 1)

    def test_fragment_rejects_empty_section(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "01-منزلة-الآجرومية.md"
            text = valid_text().replace("### القاعدة\n\nمحتوى عربي واضح.", "### القاعدة\n")
            path.write_text(text, encoding="utf-8")
            with self.assertRaisesRegex(PedagogyValidationError, "section vide القاعدة"):
                validate_fragment(path, 1)

    def test_fragments_assemble_in_numeric_order(self):
        with TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / "02-الوحدة-الثانية.md").write_text(valid_text("الوحدة الثانية").replace("تشخيص قبلي", "مراجعة تراكمية"), encoding="utf-8")
            (directory / "01-الوحدة-الأولى.md").write_text(valid_text("الوحدة الأولى"), encoding="utf-8")
            result = assemble_fragments(load_fragments(directory), enforce_count=False)
            self.assertLess(result.index("الوحدة الأولى"), result.index("الوحدة الثانية"))

    def test_fragment_discovery_reads_order_100(self):
        with TemporaryDirectory() as tmp:
            directory = Path(tmp)
            path = directory / "100-الوحدة-100.md"
            path.write_text(
                valid_text("الوحدة 100").replace("تشخيص قبلي", "مراجعة تراكمية"),
                encoding="utf-8",
            )
            self.assertEqual([(100, path)], builder.discover_fragment_files(directory))

    def test_complete_custom_range_loads_through_order_110(self):
        with TemporaryDirectory() as tmp:
            directory = Path(tmp)
            for index in range(1, 111):
                title = f"الوحدة {index}"
                text = valid_text(title)
                if index > 1:
                    text = text.replace("تشخيص قبلي", "مراجعة تراكمية")
                (directory / f"{index:02d}-الوحدة-{index}.md").write_text(
                    text,
                    encoding="utf-8",
                )

            fragments = load_fragments(directory)
            self.assertEqual(110, len(fragments))
            self.assertEqual(100, fragments[99].order)
            self.assertEqual(110, fragments[-1].order)
            assembled = assemble_fragments(fragments, count_range=(70, 110))
            self.assertIn("## الوحدة 100", assembled)


class ProvenanceValidationTest(unittest.TestCase):
    def test_module_count_range_returns_configured_bounds(self):
        self.assertEqual((30, 55), builder.module_count_range({"module_count_range": [30, 55]}))

    def test_batch_accepts_matching_non_ajroumiya_identifier(self):
        durations = {"lesson-001": 100.0}
        batch = {
            "course_id": "moutammima",
            "lessons": [
                {
                    "lesson_id": "lesson-001",
                    "spans": [
                        {
                            "start_seconds": 0,
                            "end_seconds": 50,
                            "kind": "teaching",
                            "topic_ar": "مقدمة",
                            "claims": ["قاعدة"],
                            "examples": [],
                            "uncertainties": [],
                        }
                    ],
                }
            ],
        }
        validate_source_batch(batch, durations, ["lesson-001"], "moutammima")

    def test_batch_accepts_uncertain_fragment_kind(self):
        durations = {"lesson-001": 100.0}
        batch = {
            "course_id": "alfiya-sarf",
            "lessons": [
                {
                    "lesson_id": "lesson-001",
                    "spans": [
                        {
                            "start_seconds": 0,
                            "end_seconds": 5,
                            "kind": "uncertain_fragment",
                            "topic_ar": "",
                            "claims": [],
                            "examples": [],
                            "uncertainties": ["مقطع غير مكتمل"],
                        }
                    ],
                }
            ],
        }
        validate_source_batch(batch, durations, ["lesson-001"], "alfiya-sarf")

    def test_batch_rejects_mismatched_identifier(self):
        durations = {"lesson-001": 100.0}
        batch = {
            "course_id": "ajroumiya",
            "lessons": [
                {
                    "lesson_id": "lesson-001",
                    "spans": [
                        {
                            "start_seconds": 0,
                            "end_seconds": 50,
                            "kind": "teaching",
                            "topic_ar": "مقدمة",
                            "claims": ["قاعدة"],
                            "examples": [],
                            "uncertainties": [],
                        }
                    ],
                }
            ],
        }
        with self.assertRaisesRegex(PedagogyValidationError, "moutammima"):
            validate_source_batch(batch, durations, ["lesson-001"], "moutammima")

    def test_batch_requires_every_lesson_in_range_once(self):
        durations = {"lesson-001": 100.0, "lesson-002": 120.0}
        batch = {
            "course_id": "ajroumiya",
            "range": [1, 2],
            "lessons": [
                {
                    "lesson_id": "lesson-001",
                    "spans": [
                        {
                            "start_seconds": 0,
                            "end_seconds": 50,
                            "kind": "teaching",
                            "topic_ar": "مقدمة",
                            "claims": ["المتن للمبتدئ"],
                            "examples": [],
                            "uncertainties": [],
                        }
                    ],
                }
            ],
        }
        with self.assertRaisesRegex(PedagogyValidationError, "lesson-002"):
            validate_source_batch(batch, durations, ["lesson-001", "lesson-002"], "ajroumiya")

    def test_source_map_accepts_custom_module_count_range(self):
        with TemporaryDirectory() as tmp:
            data, fragments, durations, root = complete_source_map_fixture(
                Path(tmp),
                course_id="moutammima",
                module_count=40,
                count_range=(30, 55),
            )
            validate_source_map(data, fragments, durations, root, True, True, "moutammima")

    def test_source_map_rejects_fragments_below_configured_range(self):
        with TemporaryDirectory() as tmp:
            data, fragments, durations, root = complete_source_map_fixture(
                Path(tmp),
                course_id="moutammima",
                module_count=29,
                count_range=(30, 55),
            )
            with self.assertRaises(PedagogyValidationError) as caught:
                validate_source_map(data, fragments, durations, root, True, True, "moutammima")
            self.assertIn("modules attendu 30 à 55", str(caught.exception))
            self.assertIn("fragments attendu 30 à 55", str(caught.exception))

    def test_source_map_rejects_mismatched_identifier(self):
        with TemporaryDirectory() as tmp:
            data, fragments, durations, root = complete_source_map_fixture(Path(tmp))
            with self.assertRaisesRegex(PedagogyValidationError, "moutammima"):
                validate_source_map(data, fragments, durations, root, True, True, "moutammima")

    def test_empty_canonical_refs_allowed_when_inventory_declares_absence(self):
        with TemporaryDirectory() as tmp:
            data, fragments, durations, root = complete_source_map_fixture(
                Path(tmp), canonical_available=False
            )
            validate_source_map(data, fragments, durations, root, True, True, "ajroumiya")

    def test_empty_canonical_refs_rejected_when_inventory_declares_source(self):
        with TemporaryDirectory() as tmp:
            data, fragments, durations, root = complete_source_map_fixture(Path(tmp))
            data["modules"][0]["canonical_refs"] = []
            with self.assertRaisesRegex(PedagogyValidationError, "canonical_refs absent"):
                validate_source_map(data, fragments, durations, root, True, True, "ajroumiya")

    def test_source_map_rejects_span_beyond_audio(self):
        with TemporaryDirectory() as tmp:
            data, fragments, durations, root = complete_source_map_fixture(Path(tmp))
            data["modules"][0]["audio_spans"][0]["end_seconds"] = 101.0
            durations["lesson-001"] = 100.0
            with self.assertRaisesRegex(PedagogyValidationError, "hors durée"):
                validate_source_map(data, fragments, durations, root, True, True, "ajroumiya")

    def test_source_map_rejects_pending_final_status(self):
        with TemporaryDirectory() as tmp:
            data, fragments, durations, root = complete_source_map_fixture(Path(tmp))
            data["modules"][0]["verification"]["pedagogy"] = "pending"
            with self.assertRaisesRegex(PedagogyValidationError, "pending"):
                validate_source_map(data, fragments, durations, root, True, True, "ajroumiya")

    def test_source_map_rejects_study_duration_outside_contract(self):
        with TemporaryDirectory() as tmp:
            data, fragments, durations, root = complete_source_map_fixture(Path(tmp))
            data["modules"][0]["estimated_study_minutes"] = 30
            with self.assertRaisesRegex(PedagogyValidationError, "15 à 25"):
                validate_source_map(data, fragments, durations, root, True, True, "ajroumiya")

    def test_write_course_preserves_first_backup(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            directory = root / "cours-pedagogiques" / "ajroumiya"
            directory.mkdir(parents=True)
            (directory / "cours.md").write_text("ancienne version\n", encoding="utf-8")
            write_course(root, "ajroumiya", "nouvelle version\n")
            write_course(root, "ajroumiya", "troisième version\n")
            self.assertEqual(
                "ancienne version\n",
                (directory / "cours.before-transcript-first.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                "troisième version\n",
                (directory / "cours.md").read_text(encoding="utf-8"),
            )


class AjroumiyaFinalContractTest(unittest.TestCase):
    def test_public_course_has_transcript_first_contract(self):
        from outils.generate_site_data import load_pedagogical_modules

        modules = load_pedagogical_modules("ajroumiya")
        self.assertGreaterEqual(len(modules), 25)
        self.assertLessEqual(len(modules), 35)
        self.assertEqual(len(modules), len({module["id"] for module in modules}))
        for module in modules:
            self.assertGreaterEqual(len(module["questions"]), 8, module["title"])
            self.assertLessEqual(len(module["questions"]), 10, module["title"])
            for heading in (
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
            ):
                self.assertIn(heading, module["markdown"], (module["title"], heading))
