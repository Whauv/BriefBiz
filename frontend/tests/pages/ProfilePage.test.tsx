import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import { ProfilePage } from "../../src/pages/ProfilePage";
import { renderWithProviders } from "../testUtils";

describe("ProfilePage", () => {
  it("shows the join/sign-in panel when unauthenticated", () => {
    renderWithProviders(<ProfilePage />);
    expect(screen.getByRole("heading", { name: "Join BriefBiz" })).toBeInTheDocument();
    // Login is the default mode, so the Register toggle is available.
    expect(screen.getByRole("button", { name: "Register" })).toBeInTheDocument();
  });

  it("reveals the name field when switching to register", async () => {
    renderWithProviders(<ProfilePage />);
    await userEvent.click(screen.getByRole("button", { name: "Register" }));
    expect(screen.getByPlaceholderText("Your name")).toBeInTheDocument();
  });

  it("toggles a sector preference on click", async () => {
    renderWithProviders(<ProfilePage />);
    const healthTech = screen.getByRole("button", { name: "HealthTech" });
    expect(healthTech).not.toHaveClass("text-emerald-100");
    await userEvent.click(healthTech);
    expect(screen.getByRole("button", { name: "HealthTech" })).toHaveClass("text-emerald-100");
  });
});
