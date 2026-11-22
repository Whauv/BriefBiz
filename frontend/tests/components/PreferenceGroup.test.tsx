import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { PreferenceGroup } from "../../src/components/PreferenceGroup";

describe("PreferenceGroup", () => {
  it("renders all options and the title", () => {
    render(<PreferenceGroup title="Sectors" options={["AI", "Climate"]} selected={[]} onToggle={() => {}} />);
    expect(screen.getByText("Sectors")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "AI" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Climate" })).toBeInTheDocument();
  });

  it("fires onToggle with the clicked option", async () => {
    const onToggle = vi.fn();
    render(<PreferenceGroup title="Sectors" options={["AI"]} selected={[]} onToggle={onToggle} />);
    await userEvent.click(screen.getByRole("button", { name: "AI" }));
    expect(onToggle).toHaveBeenCalledWith("AI");
  });

  it("highlights selected options", () => {
    render(<PreferenceGroup title="Sectors" options={["AI"]} selected={["AI"]} onToggle={() => {}} />);
    expect(screen.getByRole("button", { name: "AI" })).toHaveClass("text-emerald-100");
  });
});
