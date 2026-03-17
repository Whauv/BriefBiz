from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy import Select, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article, ArticleVertical
from app.models.company import ArticleCompany, Company
from app.schemas.ingestion import SourceArticle
from app.services.enrichment import source_quality_score
from app.utils.hashing import hash_url
from app.utils.slug import slugify


class ArticleIngestionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def article_exists(self, url_hash: str) -> bool:
        query: Select[tuple[int]] = select(Article.id).where(Article.url_hash == url_hash)
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def create_article(
        self,
        source_article: SourceArticle,
        *,
        vertical: ArticleVertical,
        region: str,
    ) -> Article:
        article = Article(
            title=source_article.title,
            url=str(source_article.url),
            url_hash=hash_url(str(source_article.url)),
            source_name=source_article.source_name,
            source_quality_score=source_quality_score(source_article.source_name),
            published_at=source_article.published_at,
            raw_content=source_article.raw_content,
            vertical=vertical,
            region=region,
            image_url=str(source_article.image_url) if source_article.image_url else None,
        )
        self.session.add(article)
        await self.session.flush()
        return article

    async def upsert_companies(self, article: Article, company_names: Iterable[str]) -> list[Company]:
        companies: list[Company] = []
        seen_names: set[str] = set()
        for company_name in company_names:
            normalized_name = company_name.strip()
            if not normalized_name:
                continue
            dedupe_key = normalized_name.casefold()
            if dedupe_key in seen_names:
                continue
            seen_names.add(dedupe_key)

            query = select(Company).where(Company.name == normalized_name)
            result = await self.session.execute(query)
            company = result.scalar_one_or_none()
            if company is None:
                company = await self._create_company(normalized_name, article.title)
            company.article_count += 1
            company.last_headline = article.title
            association_exists = await self.session.execute(
                select(ArticleCompany).where(
                    ArticleCompany.article_id == article.id,
                    ArticleCompany.company_id == company.id,
                )
            )
            if association_exists.scalar_one_or_none() is None:
                self.session.add(
                    ArticleCompany(
                        article_id=article.id,
                        company_id=company.id,
                    )
                )
            companies.append(company)
        return companies

    async def _create_company(self, name: str, headline: str) -> Company:
        base_slug = slugify(name)
        slug = base_slug
        suffix = 1
        while await self._slug_exists(slug):
            suffix += 1
            slug = f"{base_slug}-{suffix}"

        company = Company(name=name, slug=slug, article_count=0, last_headline=headline)
        self.session.add(company)
        await self.session.flush()
        return company

    async def _slug_exists(self, slug: str) -> bool:
        result = await self.session.execute(select(Company.id).where(Company.slug == slug))
        return result.scalar_one_or_none() is not None

    async def commit(self) -> None:
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise
