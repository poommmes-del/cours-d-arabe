#!/usr/bin/env python3
"""Create and verify durable baselines for transcript-first course waves."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "cours-pedagogiques" / "course-build-config.json"
DEFAULT_STATE_DIR = ROOT / ".superpowers" / "sdd" / "all-courses"
DEFAULT_BASELINE = DEFAULT_STATE_DIR / "baseline.json"
DEFAULT_PROGRESS = DEFAULT_STATE_DIR / "progress.md"
PROTECTED_DATA_ORDER = ("manifest", "audio_metadata", "transcriptions", "pdf", "shamela")


@dataclass(frozen=True)
class CourseBuildConfig:
    identifier: str
    order: int
    wave: int
    lesson_count: int
    module_count_range: tuple[int, int]


def _positive_integer(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{label} must be a positive integer")
    return value


def load_config(path: Path) -> list[CourseBuildConfig]:
    """Load validated course build configuration in public order."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("config schema_version must be 1")
    raw_courses = data.get("courses")
    if not isinstance(raw_courses, list) or not raw_courses:
        raise ValueError("config courses must be a non-empty list")

    configs: list[CourseBuildConfig] = []
    identifiers: set[str] = set()
    orders: set[int] = set()
    for raw in raw_courses:
        if not isinstance(raw, dict):
            raise ValueError("each course config must be an object")
        identifier = raw.get("identifier")
        if not isinstance(identifier, str) or not identifier.strip():
            raise ValueError("identifier must be a non-empty string")
        if identifier in identifiers:
            raise ValueError(f"duplicate identifier: {identifier}")
        order = _positive_integer(raw.get("order"), f"{identifier} order")
        if order in orders:
            raise ValueError(f"duplicate order: {order}")
        wave = _positive_integer(raw.get("wave"), f"{identifier} wave")
        lesson_count = _positive_integer(raw.get("lesson_count"), f"{identifier} lesson_count")
        raw_range = raw.get("module_count_range")
        if not isinstance(raw_range, list) or len(raw_range) != 2:
            raise ValueError(f"{identifier} module_count_range must contain two integers")
        minimum = _positive_integer(raw_range[0], f"{identifier} module_count_range minimum")
        maximum = _positive_integer(raw_range[1], f"{identifier} module_count_range maximum")
        if maximum < minimum:
            raise ValueError(f"{identifier} module_count_range maximum must be >= minimum")

        identifiers.add(identifier)
        orders.add(order)
        configs.append(CourseBuildConfig(identifier, order, wave, lesson_count, (minimum, maximum)))

    configs.sort(key=lambda item: item.order)
    expected_orders = list(range(1, len(configs) + 1))
    if [item.order for item in configs] != expected_orders:
        raise ValueError(f"orders must be contiguous 1-{len(configs)}")
    return configs


def _file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_hash(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _tree_files(directory: Path, predicate: Any = None) -> list[Path]:
    if not directory.exists():
        return []
    files = [path for path in directory.rglob("*") if path.is_file()]
    if predicate is not None:
        files = [path for path in files if predicate(path)]
    return sorted(files, key=lambda path: path.as_posix())


def _content_tree_record(root: Path, files: Iterable[Path]) -> dict[str, Any]:
    entries = [
        {
            "path": path.relative_to(root).as_posix(),
            "size": path.stat().st_size,
            "sha256": _file_hash(path),
        }
        for path in files
    ]
    return {"file_count": len(entries), "sha256": _canonical_hash(entries)}


def _audio_metadata_record(root: Path) -> dict[str, Any]:
    files = _tree_files(root / "audios-opus", lambda path: path.name != "manifest.tsv")
    entries = [
        {
            "path": path.relative_to(root).as_posix(),
            "size": path.stat().st_size,
            "sha256": _file_hash(path),
        }
        for path in files
    ]
    return {"file_count": len(entries), "sha256": _canonical_hash(entries)}


def _protected_data(root: Path) -> dict[str, dict[str, Any]]:
    manifest = root / "audios-opus" / "manifest.tsv"
    if not manifest.is_file():
        raise FileNotFoundError(f"missing protected manifest: {manifest}")
    transcription_files = _tree_files(
        root / "archive-items",
        lambda path: any("transcription" in part for part in path.parts),
    )
    return {
        "manifest": {"file_count": 1, "sha256": _file_hash(manifest)},
        "audio_metadata": _audio_metadata_record(root),
        "transcriptions": _content_tree_record(root, transcription_files),
        "pdf": _content_tree_record(root, _tree_files(root / "livres" / "pdf")),
        "shamela": _content_tree_record(root, _tree_files(root / "livres" / "shamela")),
    }


def _catalog_courses(root: Path) -> dict[str, dict[str, Any]]:
    catalog_path = root / "site" / "data" / "catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    courses = catalog.get("courses") if isinstance(catalog, dict) else None
    if not isinstance(courses, list):
        raise ValueError("catalog courses must be a list")
    result: dict[str, dict[str, Any]] = {}
    for course in courses:
        identifier = course.get("id") if isinstance(course, dict) else None
        if not isinstance(identifier, str) or identifier in result:
            raise ValueError("catalog course identifiers must be unique strings")
        result[identifier] = course
    return result


def capture_baseline(root: Path, identifiers: list[str], output: Path) -> None:
    """Capture protected data and public course objects outside active identifiers."""
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("active course identifiers must be unique")
    active = set(identifiers)
    courses = _catalog_courses(root)
    missing = sorted(active - courses.keys())
    if missing:
        raise ValueError(f"active courses missing from catalog: {', '.join(missing)}")
    baseline = {
        "schema_version": 1,
        "algorithm": "sha256",
        "active_course_ids": identifiers,
        "protected_data": _protected_data(root),
        "course_objects": {
            identifier: _canonical_hash(course)
            for identifier, course in sorted(courses.items())
            if identifier not in active
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(baseline, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def verify_wave(root: Path, wave: int, baseline: Path) -> list[str]:
    """Return deterministic errors for protected-data or outside-wave drift."""
    configs = load_config(root / "cours-pedagogiques" / "course-build-config.json")
    active = [item.identifier for item in configs if item.wave == wave]
    if not active:
        return [f"unknown wave: {wave}"]
    saved = json.loads(baseline.read_text(encoding="utf-8"))
    errors: list[str] = []
    saved_active = saved.get("active_course_ids")
    if saved_active != active:
        errors.append(
            f"baseline active wave mismatch: expected {','.join(active)}, got {','.join(saved_active or [])}"
        )

    current_protected = _protected_data(root)
    saved_protected = saved.get("protected_data", {})
    for label in PROTECTED_DATA_ORDER:
        if current_protected.get(label) != saved_protected.get(label):
            errors.append(f"protected data drift: {label}")

    current_courses = _catalog_courses(root)
    saved_courses = saved.get("course_objects", {})
    active_set = set(active)
    protected_ids = (set(current_courses) | set(saved_courses)) - active_set
    for identifier in sorted(protected_ids):
        course = current_courses.get(identifier)
        current_hash = _canonical_hash(course) if course is not None else None
        if current_hash != saved_courses.get(identifier):
            errors.append(f"course object drift: {identifier}")
    return errors


def _source_batch_labels(lesson_count: int) -> list[str]:
    return [
        f"{start:03d}-{min(start + 14, lesson_count):03d}"
        for start in range(1, lesson_count + 1, 15)
    ]


def render_initial_progress(configs: list[CourseBuildConfig]) -> str:
    lines = [
        "# Progression transcript-first des cours",
        "",
        "## Fondation - complete",
        "",
        "- [x] Builder schema v2 generalise et valide.",
        "- [x] Configuration, baselines, verification de vague et test UI generique.",
        "",
    ]
    for wave in sorted({item.wave for item in configs}):
        lines.extend((f"## Vague {wave} - pending", ""))
        for item in (entry for entry in configs if entry.wave == wave):
            minimum, maximum = item.module_count_range
            batches = ", ".join(f"`{label}` pending" for label in _source_batch_labels(item.lesson_count))
            lines.extend(
                (
                    f"### {item.order}. `{item.identifier}` - pending",
                    "",
                    f"- Lecons: {item.lesson_count}; modules autorises: {minimum}-{maximum}.",
                    "- [ ] Inventaire et baseline du cours.",
                    f"- [ ] Lots sources (15 max): {batches}.",
                    "- [ ] Architecture et source-map sans statut pending.",
                    "- [ ] Lots de redaction (10 modules max), bornes fixees par architecture.",
                    "- [ ] Validation finale, audit et rapport.",
                    "",
                )
            )
    return "\n".join(lines)


def initialize(root: Path, config_path: Path, baseline: Path, progress: Path) -> None:
    configs = load_config(config_path)
    active = [item.identifier for item in configs if item.wave == 1]
    if not baseline.exists():
        capture_baseline(root, active, baseline)
    if not progress.exists():
        progress.parent.mkdir(parents=True, exist_ok=True)
        progress.write_text(render_initial_progress(configs), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--init", action="store_true", help="initialize baseline and durable ledger")
    actions.add_argument("--status", action="store_true", help="print durable ledger")
    actions.add_argument("--verify-wave", type=int, metavar="N", help="verify protected data for wave N")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--progress", type=Path)
    args = parser.parse_args()
    config = args.config or args.root / "cours-pedagogiques" / "course-build-config.json"
    baseline = args.baseline or args.root / ".superpowers" / "sdd" / "all-courses" / "baseline.json"
    progress = args.progress or args.root / ".superpowers" / "sdd" / "all-courses" / "progress.md"

    if args.init:
        initialize(args.root, config, baseline, progress)
        print(f"initialized baseline={baseline} progress={progress}")
        return 0
    if args.status:
        print(progress.read_text(encoding="utf-8"), end="")
        return 0

    errors = verify_wave(args.root, args.verify_wave, baseline)
    if errors:
        for error in errors:
            print(error)
        return 1
    print(f"wave {args.verify_wave} verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
