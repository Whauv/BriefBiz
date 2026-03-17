from __future__ import annotations

import re
import unicodedata

NON_WORD_RE = re.compile(r"[^a-z0-9]+")


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    slug = NON_WORD_RE.sub("-", normalized.lower()).strip("-")
    return slug or "company"

