import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";

import { StatusPill } from "../../src/components/StatusPill";

describe("StatusPill", () => {
  it("renders its children", () => {
    render(<StatusPill tone="bullish">Bullish</StatusPill>);
    expect(screen.getByText("Bullish")).toBeInTheDocument();
  });

  it("applies the tone-specific classes", () => {
    render(<StatusPill tone="risk">Risk</StatusPill>);
    const pill = screen.getByText("Risk");
    expect(pill).toHaveClass("text-amber-100");
    expect(pill).toHaveClass("rounded-full");
  });
});
