import { act } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { useAppStore } from "../../src/store/AppStore";
import { useFollows } from "../../src/hooks/useFollows";
import { renderHookWithProviders } from "../testUtils";

describe("useFollows", () => {
  it("adds a company to the store", () => {
    const { result } = renderHookWithProviders(() => ({
      store: useAppStore(),
      follows: useFollows(),
    }));

    act(() => result.current.follows.addCompany("New Co"));
    expect(result.current.store.preferences.followed_companies).toContain("New Co");
  });

  it("ignores blank input", () => {
    const { result } = renderHookWithProviders(() => ({
      store: useAppStore(),
      follows: useFollows(),
    }));

    const before = result.current.store.preferences.followed_investors.length;
    act(() => result.current.follows.addInvestor("   "));
    expect(result.current.store.preferences.followed_investors.length).toBe(before);
  });
});
