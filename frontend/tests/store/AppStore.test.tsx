import { act } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { useAppStore } from "../../src/store/AppStore";
import type { AuthUser } from "../../src/types";
import { renderHookWithProviders } from "../testUtils";

const user: AuthUser = {
  id: 1,
  email: "founder@example.com",
  name: "Founder",
  preferences: {
    sectors: ["AI"],
    regions: ["US"],
    followed_companies: ["Acme"],
    followed_investors: [],
  },
  created_at: "2026-01-01T00:00:00Z",
};

describe("AppStore", () => {
  it("starts unauthenticated", () => {
    const { result } = renderHookWithProviders(() => useAppStore());
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.currentUser).toBeNull();
  });

  it("toggles bookmarks on and off", () => {
    const { result } = renderHookWithProviders(() => useAppStore());
    act(() => result.current.toggleBookmark(999));
    expect(result.current.bookmarks).toContain(999);
    act(() => result.current.toggleBookmark(999));
    expect(result.current.bookmarks).not.toContain(999);
  });

  it("merges preference updates", () => {
    const { result } = renderHookWithProviders(() => useAppStore());
    act(() => result.current.updatePreferences({ sectors: ["Climate"] }));
    expect(result.current.preferences.sectors).toEqual(["Climate"]);
  });

  it("dedupes followed companies", () => {
    const { result } = renderHookWithProviders(() => useAppStore());
    act(() => result.current.followCompany("Dedupe Inc"));
    act(() => result.current.followCompany("Dedupe Inc"));
    const count = result.current.preferences.followed_companies.filter((c) => c === "Dedupe Inc").length;
    expect(count).toBe(1);
  });

  it("marks all notifications read", () => {
    const { result } = renderHookWithProviders(() => useAppStore());
    act(() => result.current.setNotifications([
      { id: 1, user_id: 1, article_id: 1, type: "x", read: false, created_at: "" },
      { id: 2, user_id: 1, article_id: 2, type: "x", read: false, created_at: "" },
    ]));
    act(() => result.current.markNotificationsRead());
    expect(result.current.notifications.every((n) => n.read)).toBe(true);
  });

  it("sets and clears a session", () => {
    const { result } = renderHookWithProviders(() => useAppStore());
    act(() => result.current.setSession("token-123", user));
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.currentUser?.email).toBe("founder@example.com");
    expect(result.current.preferences.followed_companies).toEqual(["Acme"]);

    act(() => result.current.clearSession());
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.currentUser).toBeNull();
  });
});
