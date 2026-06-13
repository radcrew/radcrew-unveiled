import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

// Mock the streaming API so no network happens; tests drive onChunk directly.
const streamChatMessage = vi.fn();
vi.mock("@/lib/chatbot-api", () => ({
  streamChatMessage: (...args: unknown[]) => streamChatMessage(...args),
}));

// Render framer-motion elements as plain DOM so AnimatePresence enter/exit and
// motion-only props don't interfere with queries. The Proxy memoizes one
// component per tag so React keeps a stable element type across re-renders
// (otherwise the subtree, including the input, remounts on every render).
vi.mock("framer-motion", () => {
  const FRAMER_PROPS = [
    "initial",
    "animate",
    "exit",
    "transition",
    "whileHover",
    "whileTap",
    "layout",
  ];
  const cache = new Map<string, React.FC<Record<string, unknown>>>();

  return {
    AnimatePresence: ({ children }: { children: React.ReactNode }) => children,
    motion: new Proxy(
      {},
      {
        get: (_t, tag: string) => {
          if (!cache.has(tag)) {
            const Component = ({ children, ...props }: Record<string, unknown>) => {
              const rest: Record<string, unknown> = {};
              for (const [k, v] of Object.entries(props)) {
                if (!FRAMER_PROPS.includes(k)) rest[k] = v;
              }
              const Tag = tag as keyof JSX.IntrinsicElements;
              return <Tag {...rest}>{children as React.ReactNode}</Tag>;
            };
            Component.displayName = `motion.${tag}`;
            cache.set(tag, Component);
          }
          return cache.get(tag);
        },
      },
    ),
  };
});

import { ChatWidget } from "./index";

async function openPanel(
  user: ReturnType<typeof userEvent.setup>,
): Promise<HTMLElement> {
  await user.click(screen.getByRole("button", { name: /ask radcrew/i }));
  const panel = await screen.findByRole("dialog", { name: /radcrew chat/i });
  // Suggestions render as soon as the panel mounts (no user message yet).
  await within(panel).findByRole("button", {
    name: /what does radcrew specialize in/i,
  });
  return panel;
}

function submitButton(panel: HTMLElement): HTMLButtonElement {
  return panel.querySelector('button[type="submit"]') as HTMLButtonElement;
}

beforeEach(() => {
  streamChatMessage.mockReset();
  streamChatMessage.mockResolvedValue(undefined);
});

afterEach(() => {
  vi.useRealTimers();
});

describe("ChatWidget", () => {
  it("opens the panel and shows header + suggestions", async () => {
    const user = userEvent.setup();
    render(<ChatWidget />);
    const panel = await openPanel(user);

    expect(within(panel).getByText(/AI Assistant/i)).toBeInTheDocument();
    expect(
      within(panel).getByRole("button", { name: /how quickly can you start/i }),
    ).toBeInTheDocument();
  });

  it("keeps send disabled until the draft has at least 2 chars", async () => {
    const user = userEvent.setup();
    render(<ChatWidget />);
    const panel = await openPanel(user);

    const send = submitButton(panel);
    const input = within(panel).getByPlaceholderText(/ask anything about radcrew/i);

    expect(send).toBeDisabled();
    await user.type(input, "a");
    expect(send).toBeDisabled();
    await user.type(input, "b");
    expect(send).toBeEnabled();
  });

  it("renders streamed assistant chunks after sending", async () => {
    streamChatMessage.mockImplementation(async (_msg, handlers) => {
      handlers.onChunk("Hello ");
      handlers.onChunk("there.");
    });
    const user = userEvent.setup();
    render(<ChatWidget />);
    const panel = await openPanel(user);

    const input = within(panel).getByPlaceholderText(/ask anything about radcrew/i);
    await user.type(input, "what do you do?");
    await user.click(submitButton(panel));

    expect(within(panel).getByText("what do you do?")).toBeInTheDocument();
    await waitFor(() =>
      expect(within(panel).getByText("Hello there.")).toBeInTheDocument(),
    );
    expect(streamChatMessage).toHaveBeenCalledOnce();
    // History is empty on the first turn (welcome message is filtered out).
    expect(streamChatMessage).toHaveBeenCalledWith(
      "what do you do?",
      expect.objectContaining({ onChunk: expect.any(Function) }),
      [],
    );
  });

  it("shows an error banner on failure", async () => {
    streamChatMessage.mockRejectedValue(new Error("service down"));
    const user = userEvent.setup();
    render(<ChatWidget />);
    const panel = await openPanel(user);

    const input = within(panel).getByPlaceholderText(/ask anything about radcrew/i);
    await user.type(input, "hello");
    await user.click(submitButton(panel));

    await waitFor(() =>
      expect(within(panel).getByText("service down")).toBeInTheDocument(),
    );
  });
});
