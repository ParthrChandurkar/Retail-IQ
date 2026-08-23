import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { Button, ErrorState, Input, Label } from "../../components/ui";
import { formatCurrency } from "../../lib/utils";

describe("accessible UI primitives", () => {
  it("supports labeled keyboard input and button activation", async () => {
    const click = vi.fn();
    const user = userEvent.setup();
    render(
      <>
        <Label htmlFor="region">Region</Label>
        <Input id="region" />
        <Button onClick={click}>Apply</Button>
      </>,
    );

    await user.tab();
    expect(screen.getByLabelText("Region")).toHaveFocus();
    await user.keyboard("West");
    await user.tab();
    expect(screen.getByRole("button", { name: "Apply" })).toHaveFocus();
    await user.keyboard("{Enter}");
    expect(click).toHaveBeenCalledOnce();
  });

  it("announces API errors", () => {
    render(<ErrorState error={new Error("service unavailable")} />);
    expect(screen.getByRole("alert")).toHaveTextContent("service unavailable");
  });

  it("uses Indian digit grouping for large rupee values", () => {
    expect(formatCurrency(250844101.42)).toBe("₹25,08,44,101.42");
  });
});
