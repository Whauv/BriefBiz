import { waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { useFeedData } from "../../src/hooks/useBriefBizData";
import { apiClient } from "../../src/utils/api";
import { mockArticles } from "../../src/utils/mockData";
import { renderHookWithProviders } from "../testUtils";

describe("useFeedData", () => {
  it("returns feed items from the API", async () => {
    vi.spyOn(apiClient, "get").mockResolvedValue({ data: { items: [mockArticles[0]] } });

    const { result } = renderHookWithProviders(() => useFeedData());

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toHaveLength(1);
    expect(result.current.data?.[0].id).toBe(mockArticles[0].id);
  });

  it("falls back to mock data when enabled and the request fails", async () => {
    vi.stubEnv("DEV", true);
    vi.stubEnv("VITE_ENABLE_MOCK_FALLBACK", "true");
    vi.spyOn(apiClient, "get").mockRejectedValue(new Error("network down"));

    const { result } = renderHookWithProviders(() => useFeedData());

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockArticles);
  });

  it("errors when the request fails and fallback is disabled", async () => {
    vi.spyOn(apiClient, "get").mockRejectedValue(new Error("network down"));

    const { result } = renderHookWithProviders(() => useFeedData());

    await waitFor(() => expect(result.current.isError).toBe(true));
  });
});
