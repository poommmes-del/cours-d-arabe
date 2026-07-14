#!/usr/bin/env python3
"""Telecharger des livres depuis shamela.ws en texte local."""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup


BASE = "https://shamela.ws"


@dataclass(frozen=True)
class BookSpec:
    slug: str
    book_id: int
    label: str
    role: str


def fetch_text(url: str, timeout: int = 60, retries: int = 4) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "cours-arabe-shamela/1.0"})
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read().decode("utf-8", "replace")
        except urllib.error.HTTPError:
            if attempt == retries:
                raise
            time.sleep(2 * attempt)
        except urllib.error.URLError:
            if attempt == retries:
                raise
            time.sleep(2 * attempt)
    raise RuntimeError(f"telechargement impossible: {url}")


def fetch_json(url: str, timeout: int = 60) -> dict[str, Any]:
    return json.loads(fetch_text(url, timeout=timeout))


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.select("a.btn_tag, span.anchor"):
        tag.decompose()
    text = soup.get_text("\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())


def extract_index(html: str) -> tuple[str, str, list[int]]:
    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.select_one("h1 a.book_title, h1 a.text-primary")
    title = title_tag.get_text(" ", strip=True) if title_tag else ""
    nass = soup.select_one(".nass")
    meta = html_to_text(str(nass)) if nass else ""
    page_ids = []
    for link in soup.select(".betaka-index a[href*='/book/'], .s-nav a[href*='/book/']"):
        match = re.search(r"/book/\d+/(\d+)", link.get("href", ""))
        if match:
            page_ids.append(int(match.group(1)))
    return title, meta, sorted(set(page_ids))


def page_content(book_id: int, page_id: int) -> dict[str, Any]:
    return fetch_json(f"{BASE}/ajax/pageContent/{book_id}/{page_id}")


def download_book(spec: BookSpec, out_root: Path, delay: float = 0.15) -> None:
    out_dir = out_root / spec.slug / spec.role / f"{spec.book_id}"
    out_dir.mkdir(parents=True, exist_ok=True)
    index_html = fetch_text(f"{BASE}/book/{spec.book_id}")
    title, meta, page_ids = extract_index(index_html)
    (out_dir / "index.html").write_text(index_html, encoding="utf-8")
    (out_dir / "metadata.txt").write_text(meta + "\n", encoding="utf-8")
    if not page_ids:
        # Fallback: one-page books or unusual index. Try page 1.
        page_ids = [1]

    pages = []
    seen = set()
    next_ids = list(page_ids)
    while next_ids:
        page_id = next_ids.pop(0)
        if page_id in seen:
            continue
        seen.add(page_id)
        data = page_content(spec.book_id, page_id)
        pages.append(data)
        next_id = data.get("nextId")
        if next_id and int(next_id) not in seen and int(next_id) not in next_ids:
            next_ids.append(int(next_id))
        time.sleep(delay)

    pages.sort(key=lambda item: int(item.get("pageId") or 0))
    (out_dir / "pages.json").write_text(json.dumps(pages, ensure_ascii=False, indent=2), encoding="utf-8")
    html_parts = []
    text_parts = [f"# {title or spec.label}", "", f"- Shamela ID: {spec.book_id}", f"- Role: {spec.role}", ""]
    for page in pages:
        page_num = page.get("pageNum", "")
        page_title = page.get("title") or ""
        heading = f"## ص{page_num}" + (f" - {page_title}" if page_title else "")
        html = page.get("nass") or ""
        html_parts.append(f"<h2>{heading}</h2>\n{html}")
        text_parts.extend([heading, "", html_to_text(html), ""])

    (out_dir / "book.html").write_text("\n".join(html_parts), encoding="utf-8")
    (out_dir / "book.md").write_text("\n".join(text_parts), encoding="utf-8")
    (out_dir / "book.txt").write_text("\n".join(text_parts), encoding="utf-8")
    print(f"{spec.slug}/{spec.role}/{spec.book_id}: pages={len(pages)} title={title or spec.label}")


def parse_spec(raw: str) -> BookSpec:
    slug, role, book_id, label = raw.split(":", 3)
    return BookSpec(slug=slug, role=role, book_id=int(book_id), label=label)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", nargs="+", help="slug:role:book_id:label")
    parser.add_argument("--out-root", type=Path, default=Path("livres/shamela"))
    parser.add_argument("--delay", type=float, default=0.15)
    args = parser.parse_args()
    for raw in args.spec:
        download_book(parse_spec(raw), args.out_root, delay=args.delay)


if __name__ == "__main__":
    main()
