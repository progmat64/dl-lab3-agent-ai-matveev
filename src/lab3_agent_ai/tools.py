from __future__ import annotations

import time
from typing import Any
from urllib.parse import quote

import requests


def search_wikipedia(query: str, timeout: int = 30) -> str:
    title = query.replace(" ", "_")
    extract = _summary_by_title(title, timeout)
    if extract:
        return extract

    search_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "srlimit": 1,
    }
    try:
        response = requests.get(search_url, params=params, timeout=timeout, headers={"User-Agent": "lab3-agent-ai/1.0"})
        response.raise_for_status()
        results = response.json().get("query", {}).get("search", [])
        if not results:
            return ""
        return _summary_by_title(results[0].get("title", ""), timeout)
    except requests.RequestException:
        return ""


def _summary_by_title(title: str, timeout: int = 30) -> str:
    if not title:
        return ""
    url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + quote(title.replace(" ", "_"))
    try:
        response = requests.get(url, timeout=timeout, headers={"User-Agent": "lab3-agent-ai/1.0"})
        if response.status_code != 200:
            return ""
        data = response.json()
        return data.get("extract", "") or ""
    except requests.RequestException:
        return ""


def search_openalex(query: str, per_page: int = 5, timeout: int = 30) -> list[dict[str, Any]]:
    url = "https://api.openalex.org/works"
    params = {
        "search": query,
        "per-page": per_page,
        "select": "id,display_name,publication_year,abstract_inverted_index,authorships,doi",
    }
    response = requests.get(url, params=params, timeout=timeout, headers={"User-Agent": "lab3-agent-ai/1.0"})
    response.raise_for_status()
    return response.json().get("results", [])


def invert_abstract(inv_idx: dict[str, list[int]] | None) -> str:
    if not inv_idx:
        return ""
    words: list[tuple[int, str]] = []
    for token, positions in inv_idx.items():
        for pos in positions:
            words.append((pos, token))
    words.sort(key=lambda item: item[0])
    return " ".join(token for _, token in words)


def normalize_work(work: dict[str, Any]) -> dict[str, Any]:
    authorships = work.get("authorships") or []
    authors = []
    for item in authorships[:5]:
        author = item.get("author") or {}
        name = author.get("display_name")
        if name:
            authors.append(name)

    return {
        "id": work.get("id", ""),
        "doi": work.get("doi", ""),
        "title": work.get("display_name", ""),
        "year": work.get("publication_year", ""),
        "authors": authors,
        "abstract": invert_abstract(work.get("abstract_inverted_index"))[:1600],
    }


def timed_call(fn, *args, **kwargs):
    start = time.time()
    result = fn(*args, **kwargs)
    return result, time.time() - start
