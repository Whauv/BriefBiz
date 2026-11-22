import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { AppShell } from "../../src/components/AppShell";
import { renderWithProviders } from "../testUtils";

function seedAuthenticatedSession(unread: number) {
  window.localStorage.setItem("briefbiz-auth-token", JSON.stringify("token"));
  window.localStorage.setItem(
    "briefbiz-current-user",
    JSON.stringify({
      id: 1,
      email: "founder@example.com",
      name: "Founder",
      preferences: { sectors: [], regions: [], followed_companies: [], followed_investors: [] },
      created_at: "2026-01-01T00:00:00Z",
    }),
  );
  window.localStorage.setItem(
    "briefbiz-notifications",
    JSON.stringify(
      Array.from({ length: unread }, (_, index) => ({
        id: index + 1,
        user_id: 1,
        article_id: index + 1,
        type: "x",
        read: false,
        created_at: "",
      })),
    ),
  );
}

describe("AppShell", () => {
  it("shows the unread badge when authenticated with unread notifications", () => {
    seedAuthenticatedSession(3);
    renderWithProviders(<AppShell>content</AppShell>);
    expect(screen.getByText("3")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /profile and notifications/i })).toBeInTheDocument();
  });

  it("renders the sign-in affordance when unauthenticated", () => {
    renderWithProviders(<AppShell>content</AppShell>);
    expect(screen.getByRole("button", { name: /open sign in/i })).toBeInTheDocument();
  });
});
