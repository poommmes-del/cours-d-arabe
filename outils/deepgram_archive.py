#!/usr/bin/env python3
"""Transcrire des items Archive.org avec Deepgram.

Le script utilise l'API REST pre-recorded: Deepgram lit directement l'URL
Archive.org du MP3. La cle API reste dans l'environnement ou stdin.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ARCHIVE_METADATA = "https://archive.org/metadata/{identifier}"
ARCHIVE_DOWNLOAD = "https://archive.org/download/{identifier}/{name}"
DEEPGRAM_LISTEN = "https://api.deepgram.com/v1/listen"
DEFAULT_KEYTERMS = [
    "الآجرومية",
    "المتممة",
    "النحو",
    "الإعراب",
    "الفاعل",
    "المفعول",
    "المبتدأ",
    "الخبر",
    "باب الاشتغال",
    "باب التنازع",
    "باب التعجب",
]


@dataclass(frozen=True)
class AudioFile:
    name: str
    length_seconds: float
    size_bytes: int


def natural_key(value: str) -> list[int | str]:
    parts = re.split(r"(\d+)", value)
    return [int(part) if part.isdigit() else part for part in parts]


def fmt_time(seconds: float) -> str:
    total = int(round(seconds))
    hours, rem = divmod(total, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def original_mp3s(metadata: dict[str, Any]) -> list[AudioFile]:
    files = []
    for item in metadata.get("files", []):
        name = str(item.get("name", ""))
        if item.get("source") != "original" or not name.lower().endswith(".mp3"):
            continue
        files.append(
            AudioFile(
                name=name,
                length_seconds=float(item.get("length") or 0),
                size_bytes=int(item.get("size") or 0),
            )
        )
    return sorted(files, key=lambda item: natural_key(item.name))


def archive_download_url(identifier: str, filename: str) -> str:
    return ARCHIVE_DOWNLOAD.format(
        identifier=urllib.parse.quote(identifier, safe=""),
        name=urllib.parse.quote(filename, safe=""),
    )


def fetch_json(url: str, timeout: int = 120) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": "cours-arabe-deepgram/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_archive_metadata(identifier: str) -> dict[str, Any]:
    return fetch_json(ARCHIVE_METADATA.format(identifier=urllib.parse.quote(identifier, safe="")))


def read_api_key(args: argparse.Namespace) -> str:
    if args.api_key_stdin:
        return sys.stdin.readline().strip()
    key = os.environ.get("DEEPGRAM_API_KEY", "").strip()
    if not key:
        raise SystemExit("DEEPGRAM_API_KEY manquant; utilise env ou --api-key-stdin")
    return key


def transcribe_deepgram(
    api_key: str,
    audio_url: str,
    model: str,
    language: str,
    keyterms: list[str],
    timeout: int,
    retries: int,
) -> dict[str, Any]:
    params = [
        ("model", model),
        ("language", language),
        ("smart_format", "true"),
        ("punctuate", "true"),
        ("paragraphs", "true"),
        ("utterances", "true"),
    ]
    for term in keyterms:
        params.append(("keyterm", term))
    url = f"{DEEPGRAM_LISTEN}?{urllib.parse.urlencode(params)}"
    body = json.dumps({"url": audio_url}).encode("utf-8")
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json",
    }

    for attempt in range(1, retries + 1):
        request = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", "replace")
            if exc.code in {401, 403}:
                raise RuntimeError(f"Deepgram auth refusee: HTTP {exc.code}") from exc
            if exc.code not in {408, 409, 425, 429, 500, 502, 503, 504} or attempt == retries:
                raise RuntimeError(f"Deepgram HTTP {exc.code}: {raw[:500]}") from exc
            delay = retry_delay(exc.headers.get("Retry-After"), attempt)
            print(f"retry HTTP {exc.code}: attente {delay}s", flush=True)
            time.sleep(delay)
        except urllib.error.URLError as exc:
            if attempt == retries:
                raise RuntimeError(f"Deepgram erreur reseau: {exc}") from exc
            delay = retry_delay(None, attempt)
            print(f"retry reseau: attente {delay}s", flush=True)
            time.sleep(delay)
    raise RuntimeError("transcription impossible")


def retry_delay(retry_after: str | None, attempt: int) -> int:
    if retry_after:
        try:
            return max(5, int(float(retry_after)) + 2)
        except ValueError:
            pass
    return min(300, 10 * attempt)


def deepgram_markdown(audio_name: str, response: dict[str, Any]) -> str:
    metadata = response.get("metadata", {})
    alternative = (
        response.get("results", {})
        .get("channels", [{}])[0]
        .get("alternatives", [{}])[0]
    )
    transcript = alternative.get("transcript", "").strip()
    confidence = alternative.get("confidence")
    lines = [
        f"# {audio_name}",
        "",
        f"- request_id: `{metadata.get('request_id', '')}`",
        f"- duration: `{metadata.get('duration', '')}`",
        f"- confidence: `{confidence}`",
        "",
        "## Transcription",
        "",
        transcript,
        "",
    ]

    utterances = response.get("results", {}).get("utterances") or []
    if utterances:
        lines.extend(["## Segments", ""])
        for utterance in utterances:
            start = fmt_time(float(utterance.get("start") or 0))
            end = fmt_time(float(utterance.get("end") or 0))
            text = str(utterance.get("transcript") or "").strip()
            if text:
                lines.append(f"[{start} - {end}] {text}")
        lines.append("")
    return "\n".join(lines)


def write_inventory(identifier: str, metadata: dict[str, Any], out_dir: Path) -> list[AudioFile]:
    audios = original_mp3s(metadata)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    lines = ["name\tlength_seconds\tsize_bytes\turl"]
    for audio in audios:
        lines.append(
            "\t".join(
                [
                    audio.name,
                    str(audio.length_seconds),
                    str(audio.size_bytes),
                    archive_download_url(identifier, audio.name),
                ]
            )
        )
    (out_dir / "inventory.tsv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return audios


def command_inventory(args: argparse.Namespace) -> None:
    metadata = fetch_archive_metadata(args.identifier)
    item_dir = args.out_dir / args.identifier
    audios = write_inventory(args.identifier, metadata, item_dir)
    total_hours = sum(audio.length_seconds for audio in audios) / 3600
    print(f"identifier={args.identifier}")
    print(f"title={metadata.get('metadata', {}).get('title', '')}")
    print(f"mp3={len(audios)}")
    print(f"hours={total_hours:.2f}")
    print(f"inventory={item_dir / 'inventory.tsv'}")


def command_transcribe(args: argparse.Namespace) -> None:
    api_key = read_api_key(args)
    item_dir = args.out_dir / args.identifier
    metadata_path = item_dir / "metadata.json"
    metadata = (
        json.loads(metadata_path.read_text(encoding="utf-8"))
        if metadata_path.exists()
        else fetch_archive_metadata(args.identifier)
    )
    audios = write_inventory(args.identifier, metadata, item_dir)
    trans_dir = item_dir / "transcriptions-deepgram"
    trans_dir.mkdir(parents=True, exist_ok=True)
    keyterms = DEFAULT_KEYTERMS + args.keyterm
    selected = audios[args.offset :]
    if args.limit:
        selected = selected[: args.limit]

    for index, audio in enumerate(selected, start=args.offset + 1):
        stem = Path(audio.name).stem
        out_json = trans_dir / f"{int(index):03d}-{stem}.json"
        out_md = trans_dir / f"{int(index):03d}-{stem}.md"
        if out_json.exists() and out_md.exists() and not args.force:
            print(f"skip {audio.name}", flush=True)
            continue
        audio_url = archive_download_url(args.identifier, audio.name)
        print(f"transcribe {index}/{len(audios)} {audio.name} {audio.length_seconds/60:.1f} min", flush=True)
        response = transcribe_deepgram(
            api_key=api_key,
            audio_url=audio_url,
            model=args.model,
            language=args.language,
            keyterms=keyterms,
            timeout=args.timeout,
            retries=args.retries,
        )
        out_json.write_text(json.dumps(response, ensure_ascii=False, indent=2), encoding="utf-8")
        out_md.write_text(deepgram_markdown(audio.name, response), encoding="utf-8")
        print(f"done {audio.name} -> {out_md}", flush=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    inventory = subparsers.add_parser("inventory")
    inventory.add_argument("identifier")
    inventory.add_argument("--out-dir", type=Path, default=Path("archive-items"))
    inventory.set_defaults(func=command_inventory)

    transcribe = subparsers.add_parser("transcribe")
    transcribe.add_argument("identifier")
    transcribe.add_argument("--out-dir", type=Path, default=Path("archive-items"))
    transcribe.add_argument("--model", default="nova-3")
    transcribe.add_argument("--language", default="ar")
    transcribe.add_argument("--keyterm", action="append", default=[])
    transcribe.add_argument("--limit", type=int)
    transcribe.add_argument("--offset", type=int, default=0)
    transcribe.add_argument("--timeout", type=int, default=1800)
    transcribe.add_argument("--retries", type=int, default=5)
    transcribe.add_argument("--force", action="store_true")
    transcribe.add_argument("--api-key-stdin", action="store_true")
    transcribe.set_defaults(func=command_transcribe)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
