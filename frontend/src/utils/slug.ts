/**
 * Turn a company name into a URL slug.
 *
 * Centralizes the `name -> slug` derivation that used to be duplicated inline across
 * StoryCard, BookmarksPage, and DeepDiveModal. Prefer an explicit backend-provided
 * slug (e.g. `Article.company_slug` or `CompanyProfile.slug`) via {@link resolveSlug}
 * when one is available.
 */
export function companySlug(name: string): string {
  return name
    .trim()
    .toLowerCase()
    .replace(/\s+/g, "-");
}

/** Use the backend slug when present, otherwise derive one from the name. */
export function resolveSlug(name: string, backendSlug?: string | null): string {
  return backendSlug?.trim() ? backendSlug : companySlug(name);
}
