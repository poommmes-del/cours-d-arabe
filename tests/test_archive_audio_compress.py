import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from outils.archive_audio_compress import (
    AudioJob,
    merge_manifest_rows,
    read_manifest,
    write_manifest,
)


def manifest_row(identifier: str, name: str, size: int):
    job = AudioJob(identifier, name, 60.0, 1000, f"https://example.test/{name}")
    return job, Path(f"audios-opus/{identifier}/{name}.opus"), size


class ManifestMergeTest(unittest.TestCase):
    def as_map(self, rows):
        return {(job.identifier, job.name): size for job, _path, size in rows}

    def test_limit_updates_only_processed_keys(self):
        existing = [
            manifest_row("a", "1.mp3", 10),
            manifest_row("a", "2.mp3", 20),
            manifest_row("b", "1.mp3", 30),
        ]
        updates = [manifest_row("a", "1.mp3", 99)]

        merged = merge_manifest_rows(
            existing,
            updates,
            replace_all=False,
            replace_identifiers=set(),
        )

        self.assertEqual(
            {("a", "1.mp3"): 99, ("a", "2.mp3"): 20, ("b", "1.mp3"): 30},
            self.as_map(merged),
        )

    def test_identifier_replaces_only_target_course(self):
        existing = [
            manifest_row("a", "old.mp3", 10),
            manifest_row("a", "stale.mp3", 20),
            manifest_row("b", "1.mp3", 30),
        ]
        updates = [manifest_row("a", "new.mp3", 99)]

        merged = merge_manifest_rows(
            existing,
            updates,
            replace_all=False,
            replace_identifiers={"a"},
        )

        self.assertEqual(
            {("a", "new.mp3"): 99, ("b", "1.mp3"): 30},
            self.as_map(merged),
        )

    def test_full_run_replaces_everything(self):
        merged = merge_manifest_rows(
            [manifest_row("old", "1.mp3", 10)],
            [manifest_row("new", "1.mp3", 20)],
            replace_all=True,
            replace_identifiers=set(),
        )
        self.assertEqual({("new", "1.mp3"): 20}, self.as_map(merged))

    def test_manifest_round_trip_is_sorted(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest.tsv"
            write_manifest(
                path,
                [
                    manifest_row("b", "10.mp3", 10),
                    manifest_row("a", "2.mp3", 20),
                    manifest_row("a", "1.mp3", 30),
                ],
            )

            rows = read_manifest(path)
            self.assertEqual(
                [("a", "1.mp3"), ("a", "2.mp3"), ("b", "10.mp3")],
                [(job.identifier, job.name) for job, _path, _size in rows],
            )
            self.assertEqual([], list(path.parent.glob(f".{path.name}.*.tmp")))

    def test_manifest_sort_is_deterministic_when_natural_keys_tie(self):
        with TemporaryDirectory() as tmp:
            first = Path(tmp) / "first.tsv"
            second = Path(tmp) / "second.tsv"
            rows = [
                manifest_row("a", "1.mp3", 10),
                manifest_row("a", "01.mp3", 20),
            ]

            write_manifest(first, rows)
            write_manifest(second, list(reversed(rows)))

            self.assertEqual(first.read_bytes(), second.read_bytes())


if __name__ == "__main__":
    unittest.main()
