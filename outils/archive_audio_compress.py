#!/usr/bin/env python3
"""Telecharger et compresser les audios Archive.org.

Par defaut, le script produit du Ogg Opus mono 24 kb/s. Pour la voix,
Opus compresse mieux que AAC/M4A a qualite comparable.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AudioJob:
    identifier: str
    name: str
    length_seconds: float
    size_bytes: int
    url: str


@dataclass(frozen=True)
class EncodeConfig:
    codec: str
    bitrate: str
    sample_rate: int
    channels: int
    retries: int
    force: bool


def natural_key(value: str) -> list[int | str]:
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", value)]


def safe_stem(name: str) -> str:
    stem = Path(name).stem.strip()
    stem = stem.replace("/", "_").replace("\\", "_")
    return stem or "audio"


def read_inventory(path: Path) -> list[AudioJob]:
    identifier = path.parent.name
    jobs: list[AudioJob] = []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            jobs.append(
                AudioJob(
                    identifier=identifier,
                    name=row["name"],
                    length_seconds=float(row["length_seconds"] or 0),
                    size_bytes=int(row["size_bytes"] or 0),
                    url=row["url"],
                )
            )
    return sorted(jobs, key=lambda job: natural_key(job.name))


def collect_jobs(inventory_root: Path, identifiers: list[str]) -> list[AudioJob]:
    if identifiers:
        inventory_paths = [inventory_root / item / "inventory.tsv" for item in identifiers]
    else:
        inventory_paths = sorted(inventory_root.glob("*/inventory.tsv"))

    jobs: list[AudioJob] = []
    for path in inventory_paths:
        if not path.exists():
            raise SystemExit(f"inventaire absent: {path}")
        jobs.extend(read_inventory(path))
    return jobs


def output_path(out_dir: Path, job: AudioJob, codec: str) -> Path:
    suffix = ".m4a" if codec == "aac" else ".opus"
    return out_dir / job.identifier / f"{safe_stem(job.name)}{suffix}"


def ffprobe(path: Path) -> dict:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a:0",
            "-show_entries",
            "format=duration,size:stream=codec_name,channels,sample_rate,bit_rate",
            "-of",
            "json",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def valid_output(path: Path, expected_seconds: float, codec: str) -> bool:
    if not path.exists() or path.stat().st_size < 1024:
        return False
    try:
        data = ffprobe(path)
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return False
    streams = data.get("streams") or []
    if not streams:
        return False
    codec_name = streams[0].get("codec_name")
    if codec == "opus" and codec_name != "opus":
        return False
    if codec == "aac" and codec_name != "aac":
        return False
    duration = float((data.get("format") or {}).get("duration") or 0)
    if expected_seconds > 0 and duration < expected_seconds * 0.96:
        return False
    return True


def ffmpeg_command(job: AudioJob, tmp_path: Path, config: EncodeConfig) -> list[str]:
    base = [
        "ffmpeg",
        "-hide_banner",
        "-nostdin",
        "-loglevel",
        "error",
        "-y",
        "-i",
        job.url,
        "-map",
        "0:a:0",
        "-vn",
        "-sn",
        "-dn",
        "-ac",
        str(config.channels),
        "-ar",
        str(config.sample_rate),
    ]
    if config.codec == "aac":
        return base + ["-c:a", "aac", "-b:a", config.bitrate, "-movflags", "+faststart", str(tmp_path)]
    return base + [
        "-c:a",
        "libopus",
        "-b:a",
        config.bitrate,
        "-vbr",
        "on",
        "-compression_level",
        "10",
        "-application",
        "voip",
        str(tmp_path),
    ]


def encode_one(job: AudioJob, out_dir: Path, config: EncodeConfig) -> tuple[str, Path, int]:
    final_path = output_path(out_dir, job, config.codec)
    if not config.force and valid_output(final_path, job.length_seconds, config.codec):
        return "skip", final_path, final_path.stat().st_size

    final_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = final_path.with_name(f".{final_path.stem}.part{final_path.suffix}")
    for attempt in range(1, config.retries + 1):
        if tmp_path.exists():
            tmp_path.unlink()
        cmd = ffmpeg_command(job, tmp_path, config)
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0 and valid_output(tmp_path, job.length_seconds, config.codec):
            os.replace(tmp_path, final_path)
            return "done", final_path, final_path.stat().st_size
        if attempt == config.retries:
            error = (result.stderr or "").strip().splitlines()[-3:]
            raise RuntimeError(f"{job.identifier}/{job.name}: ffmpeg failed: {' | '.join(error)}")
        time.sleep(min(120, 10 * attempt))
    raise RuntimeError(f"{job.identifier}/{job.name}: impossible")


ManifestRow = tuple[AudioJob, Path, int]
MANIFEST_FIELDS = [
    "identifier",
    "name",
    "length_seconds",
    "source_size_bytes",
    "compressed_size_bytes",
    "path",
]


def read_manifest(manifest: Path) -> list[ManifestRow]:
    if not manifest.exists():
        return []
    rows: list[ManifestRow] = []
    with manifest.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            job = AudioJob(
                identifier=row["identifier"],
                name=row["name"],
                length_seconds=float(row["length_seconds"]),
                size_bytes=int(row["source_size_bytes"]),
                url="",
            )
            rows.append((job, Path(row["path"]), int(row["compressed_size_bytes"])))
    return rows


def merge_manifest_rows(
    existing: list[ManifestRow],
    updates: list[ManifestRow],
    *,
    replace_all: bool,
    replace_identifiers: set[str],
) -> list[ManifestRow]:
    merged: dict[tuple[str, str], ManifestRow] = {}
    if not replace_all:
        for row in existing:
            job, _path, _size = row
            if job.identifier not in replace_identifiers:
                merged[(job.identifier, job.name)] = row
    for row in updates:
        job, _path, _size = row
        merged[(job.identifier, job.name)] = row
    return list(merged.values())


def write_manifest(manifest: Path, rows: list[ManifestRow]) -> None:
    manifest.parent.mkdir(parents=True, exist_ok=True)
    temporary = manifest.with_name(f".{manifest.name}.{os.getpid()}.tmp")
    try:
        with temporary.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter="\t")
            writer.writerow(MANIFEST_FIELDS)
            for job, path, size in sorted(
                rows,
                key=lambda row: (row[0].identifier, natural_key(row[0].name), row[0].name),
            ):
                writer.writerow(
                    [
                        job.identifier,
                        job.name,
                        job.length_seconds,
                        job.size_bytes,
                        size,
                        path,
                    ]
                )
        os.replace(temporary, manifest)
    finally:
        if temporary.exists():
            temporary.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory-root", type=Path, default=Path("archive-items"))
    parser.add_argument("--out-dir", type=Path, default=Path("audios-opus"))
    parser.add_argument("--identifier", action="append", default=[])
    parser.add_argument("--codec", choices=["opus", "aac"], default="opus")
    parser.add_argument("--bitrate", default="24k")
    parser.add_argument("--sample-rate", type=int, default=24000)
    parser.add_argument("--channels", type=int, default=1)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--retries", type=int, default=4)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    jobs = collect_jobs(args.inventory_root, args.identifier)
    if args.limit is not None:
        jobs = jobs[: args.limit]
    config = EncodeConfig(
        codec=args.codec,
        bitrate=args.bitrate,
        sample_rate=args.sample_rate,
        channels=args.channels,
        retries=args.retries,
        force=args.force,
    )

    total_seconds = sum(job.length_seconds for job in jobs)
    source_size = sum(job.size_bytes for job in jobs)
    print(
        f"jobs={len(jobs)} hours={total_seconds/3600:.2f} "
        f"source_gb={source_size/1024/1024/1024:.2f} codec={args.codec} bitrate={args.bitrate}",
        flush=True,
    )

    rows: list[tuple[AudioJob, Path, int]] = []
    completed = 0
    skipped = 0
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(encode_one, job, args.out_dir, config): job for job in jobs}
        for future in as_completed(futures):
            job = futures[future]
            status, path, size = future.result()
            rows.append((job, path, size))
            completed += status == "done"
            skipped += status == "skip"
            print(f"{status} {completed + skipped}/{len(jobs)} {job.identifier}/{job.name} -> {path}", flush=True)

    manifest = args.out_dir / "manifest.tsv"
    existing_rows = read_manifest(manifest)
    replace_all = not args.identifier and args.limit is None
    replace_identifiers = set(args.identifier) if args.identifier and args.limit is None else set()
    manifest_rows = merge_manifest_rows(
        existing_rows,
        rows,
        replace_all=replace_all,
        replace_identifiers=replace_identifiers,
    )
    write_manifest(manifest, manifest_rows)
    compressed_size = sum(size for _, _, size in rows)
    print(f"manifest={manifest}", flush=True)
    print(f"compressed_gb={compressed_size/1024/1024/1024:.2f}", flush=True)


if __name__ == "__main__":
    main()
