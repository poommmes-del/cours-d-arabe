import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from outils.manage_course_waves import capture_baseline, load_config, verify_wave


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "cours-pedagogiques" / "course-build-config.json"
MANAGER = ROOT / "outils" / "manage_course_waves.py"

EXPECTED = [
    ("moutammima", 1, 1, 59, (30, 55)),
    ("qatr-nada", 2, 1, 69, (30, 55)),
    ("qawaid-i3raab-sa3di", 3, 1, 44, (30, 55)),
    ("qawaid-i3raab-zawawi", 4, 2, 37, (25, 40)),
    ("mawsil-toullab", 5, 2, 48, (30, 55)),
    ("shoudhour-dhahab", 6, 2, 76, (30, 55)),
    ("alfiya-nahw", 7, 3, 163, (70, 110)),
    ("moulakhas-sarfi", 8, 3, 43, (30, 55)),
    ("nadhm-maqsoud", 9, 3, 60, (30, 55)),
    ("alfiya-sarf", 10, 4, 32, (25, 40)),
    ("laamiya-af3al", 11, 4, 41, (30, 55)),
    ("dourous-balagha", 12, 4, 60, (30, 55)),
    ("maani-we-bayan", 13, 5, 30, (25, 40)),
]


class CourseBuildConfigTest(unittest.TestCase):
    def test_config_has_exact_public_order_waves_counts_and_ranges(self) -> None:
        configs = load_config(CONFIG)

        actual = [
            (item.identifier, item.order, item.wave, item.lesson_count, item.module_count_range)
            for item in configs
        ]
        self.assertEqual(EXPECTED, actual)
        self.assertEqual(
            [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13]],
            [[item.order for item in configs if item.wave == wave] for wave in range(1, 6)],
        )

    def test_config_rejects_duplicate_order(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "config.json"
            data = {
                "schema_version": 1,
                "courses": [
                    {
                        "identifier": "one",
                        "order": 1,
                        "wave": 1,
                        "lesson_count": 10,
                        "module_count_range": [25, 40],
                    },
                    {
                        "identifier": "two",
                        "order": 1,
                        "wave": 1,
                        "lesson_count": 10,
                        "module_count_range": [25, 40],
                    },
                ]
            }
            path.write_text(json.dumps(data), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "duplicate order: 1"):
                load_config(path)


class WaveBaselineTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        config_target = self.root / "cours-pedagogiques" / "course-build-config.json"
        config_target.parent.mkdir(parents=True)
        config_target.write_bytes(CONFIG.read_bytes())

        for relative, content in (
            ("audios-opus/manifest.tsv", "identifier\tfilename\n"),
            ("audios-opus/ajroumiya/001.opus", "audio"),
            ("archive-items/ajroumiya/transcriptions-deepgram/001.md", "transcript"),
            ("livres/pdf/ajroumiya/matn.pdf", "pdf"),
            ("livres/shamela/ajroumiya/book.md", "shamela"),
        ):
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

        courses = [{"id": "ajroumiya", "modules": [{"id": "ajroumiya-01"}]}]
        courses.extend(
            {"id": identifier, "modules": [{"id": f"{identifier}-old"}]}
            for identifier, *_ in EXPECTED
        )
        catalog = self.root / "site" / "data" / "catalog.json"
        catalog.parent.mkdir(parents=True)
        catalog.write_text(json.dumps({"courses": courses}), encoding="utf-8")
        self.baseline = self.root / ".superpowers" / "sdd" / "all-courses" / "baseline.json"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _rewrite_course(self, identifier: str, marker: str) -> None:
        catalog_path = self.root / "site" / "data" / "catalog.json"
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        course = next(item for item in catalog["courses"] if item["id"] == identifier)
        course["marker"] = marker
        catalog_path.write_text(json.dumps(catalog), encoding="utf-8")

    def test_capture_baseline_is_deterministic(self) -> None:
        active = ["moutammima", "qatr-nada", "qawaid-i3raab-sa3di"]
        capture_baseline(self.root, active, self.baseline)
        first = self.baseline.read_bytes()
        capture_baseline(self.root, active, self.baseline)

        self.assertEqual(first, self.baseline.read_bytes())
        data = json.loads(first)
        self.assertEqual(active, data["active_course_ids"])
        self.assertEqual("sha256", data["algorithm"])
        self.assertNotIn("moutammima", data["course_objects"])
        self.assertIn("qawaid-i3raab-zawawi", data["course_objects"])
        self.assertIn("ajroumiya", data["course_objects"])

    def test_verify_wave_ignores_active_course_object_drift(self) -> None:
        active = ["moutammima", "qatr-nada", "qawaid-i3raab-sa3di"]
        capture_baseline(self.root, active, self.baseline)
        self._rewrite_course("moutammima", "new wave content")

        self.assertEqual([], verify_wave(self.root, 1, self.baseline))

    def test_verify_wave_detects_drift_outside_active_wave_in_stable_order(self) -> None:
        active = ["moutammima", "qatr-nada", "qawaid-i3raab-sa3di"]
        capture_baseline(self.root, active, self.baseline)
        self._rewrite_course("qawaid-i3raab-zawawi", "forbidden")
        self._rewrite_course("ajroumiya", "forbidden")

        self.assertEqual(
            [
                "course object drift: ajroumiya",
                "course object drift: qawaid-i3raab-zawawi",
            ],
            verify_wave(self.root, 1, self.baseline),
        )

    def test_verify_wave_detects_protected_file_drift(self) -> None:
        active = ["moutammima", "qatr-nada", "qawaid-i3raab-sa3di"]
        capture_baseline(self.root, active, self.baseline)
        (self.root / "livres/shamela/ajroumiya/book.md").write_text("changed", encoding="utf-8")
        (self.root / "audios-opus/manifest.tsv").write_text("changed", encoding="utf-8")

        self.assertEqual(
            [
                "protected data drift: manifest",
                "protected data drift: shamela",
            ],
            verify_wave(self.root, 1, self.baseline),
        )

    def test_verify_wave_detects_audio_content_drift_with_same_size_and_mtime(self) -> None:
        active = ["moutammima", "qatr-nada", "qawaid-i3raab-sa3di"]
        audio = self.root / "audios-opus" / "ajroumiya" / "001.opus"
        capture_baseline(self.root, active, self.baseline)
        original_stat = audio.stat()

        audio.write_bytes(b"XXXXX")
        os.utime(audio, ns=(original_stat.st_atime_ns, original_stat.st_mtime_ns))

        self.assertEqual(
            ["protected data drift: audio_metadata"],
            verify_wave(self.root, 1, self.baseline),
        )


class WaveManagerCliTest(unittest.TestCase):
    setUp = WaveBaselineTest.setUp
    tearDown = WaveBaselineTest.tearDown

    def _run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(MANAGER), "--root", str(self.root), *arguments],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_cli_init_status_and_verify_wave_success(self) -> None:
        baseline = self.root / "state" / "wave-1.json"
        progress = self.root / "state" / "progress.md"

        initialized = self._run_cli(
            "--baseline", str(baseline), "--progress", str(progress), "--init"
        )
        status = self._run_cli("--progress", str(progress), "--status")
        verified = self._run_cli("--baseline", str(baseline), "--verify-wave", "1")

        self.assertEqual(0, initialized.returncode, initialized.stderr)
        self.assertIn("initialized baseline=", initialized.stdout)
        self.assertTrue(baseline.is_file())
        self.assertTrue(progress.is_file())
        self.assertEqual(0, status.returncode, status.stderr)
        self.assertIn("# Progression transcript-first des cours", status.stdout)
        self.assertIn("## Vague 5 - pending", status.stdout)
        self.assertEqual(0, verified.returncode, verified.stderr)
        self.assertEqual("wave 1 verified\n", verified.stdout)

    def test_cli_verify_wave_failure_returns_one_and_prints_drift(self) -> None:
        baseline = self.root / "state" / "wave-1.json"
        progress = self.root / "state" / "progress.md"
        initialized = self._run_cli(
            "--baseline", str(baseline), "--progress", str(progress), "--init"
        )
        self.assertEqual(0, initialized.returncode, initialized.stderr)
        (self.root / "audios-opus" / "manifest.tsv").write_text("changed", encoding="utf-8")

        verified = self._run_cli("--baseline", str(baseline), "--verify-wave", "1")

        self.assertEqual(1, verified.returncode)
        self.assertEqual("protected data drift: manifest\n", verified.stdout)
        self.assertEqual("", verified.stderr)


if __name__ == "__main__":
    unittest.main()
