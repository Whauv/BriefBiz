import { afterEach, describe, expect, it, vi } from "vitest";

import { AUTH_TOKEN_KEY, isMockFallbackEnabled } from "../../src/utils/query";

describe("query utils", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it("exposes a stable auth token storage key", () => {
    expect(AUTH_TOKEN_KEY).toBe("briefbiz-auth-token");
  });

  it("enables the mock fallback only when the flag is set in dev", () => {
    vi.stubEnv("DEV", true);
    vi.stubEnv("VITE_ENABLE_MOCK_FALLBACK", "true");
    expect(isMockFallbackEnabled()).toBe(true);
  });

  it("stays disabled when the flag is absent", () => {
    vi.stubEnv("DEV", true);
    vi.stubEnv("VITE_ENABLE_MOCK_FALLBACK", "");
    expect(isMockFallbackEnabled()).toBe(false);
  });
});
