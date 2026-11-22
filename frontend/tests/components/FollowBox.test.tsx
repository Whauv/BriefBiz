import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { FollowBox } from "../../src/components/FollowBox";

describe("FollowBox", () => {
  it("renders existing items", () => {
    render(
      <FollowBox
        title="Follow companies"
        value=""
        onChange={() => {}}
        items={["Stripe", "OpenAI"]}
        placeholder="Add a company"
        onSubmit={() => {}}
      />,
    );
    expect(screen.getByText("Stripe")).toBeInTheDocument();
    expect(screen.getByText("OpenAI")).toBeInTheDocument();
  });

  it("calls onChange as the user types", async () => {
    const onChange = vi.fn();
    render(
      <FollowBox
        title="Follow companies"
        value=""
        onChange={onChange}
        items={[]}
        placeholder="Add a company"
        onSubmit={() => {}}
      />,
    );
    await userEvent.type(screen.getByPlaceholderText("Add a company"), "A");
    expect(onChange).toHaveBeenCalledWith("A");
  });

  it("calls onSubmit when Add is clicked", async () => {
    const onSubmit = vi.fn();
    render(
      <FollowBox
        title="Follow companies"
        value="Acme"
        onChange={() => {}}
        items={[]}
        placeholder="Add a company"
        onSubmit={onSubmit}
      />,
    );
    await userEvent.click(screen.getByRole("button", { name: "Add" }));
    expect(onSubmit).toHaveBeenCalledOnce();
  });
});
