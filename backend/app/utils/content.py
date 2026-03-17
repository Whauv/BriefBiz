from __future__ import annotations

import re
from html import unescape

TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")


def strip_html(value: str | None) -> str | None:
    if not value:
        return None
    text = TAG_RE.sub(" ", unescape(value))
    return WHITESPACE_RE.sub(" ", text).strip()


def truncate_text(value: str | None, limit: int = 12000) -> str | None:
    if not value:
        return None
    return value[:limit].strip()

