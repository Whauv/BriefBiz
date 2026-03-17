from __future__ import annotations

from app.models.article import ArticleVertical
from app.schemas.ingestion import ArticleClassification, CompanyExtractionResult
from app.services.openai_client import OpenAIStructuredService


class ArticleClassifierService:
    def __init__(self) -> None:
        self.openai = OpenAIStructuredService()

    async def classify_article(self, title: str, raw_content: str | None) -> ArticleClassification:
        prompt = f"""
Classify the following business or startup article.

Return JSON with:
- vertical: one of funding, founder_stories, layoffs, regulatory, emerging_markets, general
- region: the primary geographic region mentioned, or "Global" if broad

Title: {title}
Content: {raw_content or ""}
""".strip()
        try:
            return await self.openai.complete_json(prompt=prompt, response_model=ArticleClassification)
        except Exception:
            return self._fallback_classification(title=title, raw_content=raw_content)

    async def extract_companies(self, title: str, raw_content: str | None) -> CompanyExtractionResult:
        prompt = f"""
Extract the important company names mentioned in this business/startup article.
Return JSON with a `companies` array of company names only. Exclude people, funds, and generic terms.

Title: {title}
Content: {raw_content or ""}
""".strip()
        try:
            companies = await self.openai.complete_list(prompt=prompt)
        except Exception:
            companies = []
        return CompanyExtractionResult(companies=companies)

    def _fallback_classification(self, *, title: str, raw_content: str | None) -> ArticleClassification:
        haystack = f"{title} {raw_content or ''}".lower()
        if any(token in haystack for token in ("funding", "series a", "series b", "raised", "seed round")):
            vertical = ArticleVertical.FUNDING
        elif any(token in haystack for token in ("layoff", "job cut", "restructuring")):
            vertical = ArticleVertical.LAYOFFS
        elif any(token in haystack for token in ("regulator", "regulation", "antitrust", "compliance")):
            vertical = ArticleVertical.REGULATORY
        elif any(token in haystack for token in ("founder", "ceo", "startup story", "entrepreneur")):
            vertical = ArticleVertical.FOUNDER_STORIES
        elif any(token in haystack for token in ("india", "africa", "latam", "southeast asia", "emerging market")):
            vertical = ArticleVertical.EMERGING_MARKETS
        else:
            vertical = ArticleVertical.GENERAL

        region = "Global"
        for candidate in ("US", "Europe", "India", "Southeast Asia", "Africa", "LatAm"):
            if candidate.lower() in haystack:
                region = candidate
                break

        return ArticleClassification(vertical=vertical, region=region)
