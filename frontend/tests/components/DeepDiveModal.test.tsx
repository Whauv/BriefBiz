import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { DeepDiveModal } from "../../src/components/DeepDiveModal";
import { mockArticles } from "../../src/utils/mockData";
import { renderWithProviders } from "../testUtils";

const article = mockArticles[0]; // companies: ["Stripe"], key_players include "Stripe"

describe("DeepDiveModal", () => {
  it("renders nothing when there is no article", () => {
    renderWithProviders(<DeepDiveModal article={null} onClose={() => {}} />);
    expect(screen.queryByText("What Happened")).not.toBeInTheDocument();
  });

  it("renders the article's deep dive", () => {
    renderWithProviders(<DeepDiveModal article={article} onClose={() => {}} />);
    expect(screen.getByRole("heading", { name: article.title })).toBeInTheDocument();
    expect(screen.getByText("What Happened")).toBeInTheDocument();
    expect(screen.getByText("Market Impact")).toBeInTheDocument();
  });

  it("links key players that are known companies to their profile", () => {
    renderWithProviders(<DeepDiveModal article={article} onClose={() => {}} />);
    const link = screen.getByRole("link", { name: "Stripe" });
    expect(link).toHaveAttribute("href", "/companies/stripe");
  });

  it("invokes onClose from the close button", async () => {
    const onClose = vi.fn();
    renderWithProviders(<DeepDiveModal article={article} onClose={onClose} />);
    // The first button is the backdrop; the close (X) button is the one inside the sheet.
    await userEvent.click(screen.getAllByRole("button")[0]);
    expect(onClose).toHaveBeenCalled();
  });
});
