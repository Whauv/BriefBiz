import { describe, expect, it } from "vitest";

import { companySlug, resolveSlug } from "../../src/utils/slug";

describe("companySlug", () => {
  it("lowercases and hyphenates", () => {
    expect(companySlug("Acme Corp")).toBe("acme-corp");
  });

  it("trims and collapses whitespace", () => {
    expect(companySlug("  Open  AI  ")).toBe("open-ai");
  });
});

describe("resolveSlug", () => {
  it("prefers the backend slug when present", () => {
    expect(resolveSlug("Acme Corp", "acme-inc")).toBe("acme-inc");
  });

  it("falls back to the derived slug when backend slug is empty", () => {
    expect(resolveSlug("Acme Corp", "")).toBe("acme-corp");
    expect(resolveSlug("Acme Corp", null)).toBe("acme-corp");
    expect(resolveSlug("Acme Corp")).toBe("acme-corp");
  });
});
