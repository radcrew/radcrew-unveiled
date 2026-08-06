import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { Marquee } from "./Marquee";
import { Reveal } from "./Reveal";
import { SplitText } from "./SplitText";

/**
 * framer-motion initialises its reduced-motion listener once per process, so
 * toggling `matchMedia` between tests does not take effect. Stubbing the hook
 * keeps the real motion components while making the branch deterministic.
 */
const reduced = vi.hoisted(() => ({ value: false }));

vi.mock("framer-motion", async (importOriginal) => ({
  ...(await importOriginal<typeof import("framer-motion")>()),
  useReducedMotion: () => reduced.value,
}));

afterEach(() => {
  reduced.value = false;
});

describe("Reveal", () => {
  it("renders its children", () => {
    render(<Reveal>content</Reveal>);
    expect(screen.getByText("content")).toBeInTheDocument();
  });

  it("still renders its children under reduced motion", () => {
    reduced.value = true;
    render(<Reveal>content</Reveal>);
    expect(screen.getByText("content")).toBeInTheDocument();
  });
});

describe("SplitText", () => {
  it("exposes the full headline to assistive tech even while split into words", () => {
    render(<SplitText text="We build what is next" />);
    // The per-word spans are aria-hidden; this match comes from the sr-only copy.
    expect(screen.getByText("We build what is next")).toBeInTheDocument();
    expect(screen.getByText("build")).toBeInTheDocument();
  });

  it("renders one plain string under reduced motion", () => {
    reduced.value = true;
    render(<SplitText text="We build what is next" />);
    expect(screen.getByText("We build what is next")).toBeInTheDocument();
    expect(screen.queryByText("build")).not.toBeInTheDocument();
  });
});

describe("Marquee", () => {
  it("duplicates its children so the loop has no seam", () => {
    render(
      <Marquee>
        <span>Northwind</span>
      </Marquee>,
    );
    expect(screen.getAllByText("Northwind")).toHaveLength(2);
  });

  it("renders a single scrollable copy under reduced motion", () => {
    reduced.value = true;
    render(
      <Marquee>
        <span>Northwind</span>
      </Marquee>,
    );
    expect(screen.getAllByText("Northwind")).toHaveLength(1);
  });
});
