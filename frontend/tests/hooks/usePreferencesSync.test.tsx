import { act } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { useAppStore } from "../../src/store/AppStore";
import { usePreferencesSync } from "../../src/hooks/usePreferencesSync";
import { renderHookWithProviders } from "../testUtils";

describe("usePreferencesSync", () => {
  it("toggles a preference on in the store", () => {
    const { result } = renderHookWithProviders(() => ({
      store: useAppStore(),
      prefs: usePreferencesSync(),
    }));

    act(() => result.current.prefs.togglePreference("sectors", "Climate"));
    expect(result.current.store.preferences.sectors).toContain("Climate");
  });

  it("toggles a preference off when already selected", () => {
    const { result } = renderHookWithProviders(() => ({
      store: useAppStore(),
      prefs: usePreferencesSync(),
    }));

    // "FinTech" is in the default preferences.
    act(() => result.current.prefs.togglePreference("sectors", "FinTech"));
    expect(result.current.store.preferences.sectors).not.toContain("FinTech");
  });
});
