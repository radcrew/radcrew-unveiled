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
// The stand-ins forward refs because the real motion components do; keeping the
// mock faithful means a component that starts using a ref does not silently get
// a dropped one here.
vi.mock("framer-motion", async () => {
  const { forwardRef } = await import("react");
  const FRAMER_PROPS = [
    "initial",
    "animate",
    "exit",
    "transition",
    "whileHover",
    "whileTap",
    "layout",
  ];
  const cache = new Map<string, React.ElementType>();

  return {
    AnimatePresence: ({ children }: { children: React.ReactNode }) => children,
    motion: new Proxy(
      {},
      {
        get: (_t, tag: string) => {
          if (!cache.has(tag)) {
            const Component = forwardRef<HTMLElement, Record<string, unknown>>(
              ({ children, ...props }, ref) => {
                const rest: Record<string, unknown> = {};
                for (const [k, v] of Object.entries(props)) {
                  if (!FRAMER_PROPS.includes(k)) rest[k] = v;
                }
                const Tag = tag as keyof JSX.IntrinsicElements;
                return (
                  <Tag ref={ref} {...rest}>
                    {children as React.ReactNode}
                  </Tag>
                );
              },
            );
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

/**
 * Queries by accessible name rather than placeholder text, because the
 * placeholder becomes the armed hint once an answer carries one.
 */
function chatInput(panel: HTMLElement): HTMLInputElement {
  return within(panel).getByRole("textbox", {
    name: /ask radcrew a question/i,
  }) as HTMLInputElement;
}

/** Answers `msg`, attaching hints only when `hints` is non-empty. */
function answerWith(hints: string[]) {
  streamChatMessage.mockImplementation(async (msg, handlers) => {
    handlers.onChunk(`answer to ${msg}`);
    if (hints.length > 0) handlers.onHints?.(hints);
  });
}

const HINTS = ["Do you work with Rust?", "How fast do you reply?"];

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

  it("offers follow-up hints under the answer and sends the one clicked", async () => {
    streamChatMessage.mockImplementation(async (_msg, handlers) => {
      handlers.onChunk("We build software.");
      handlers.onHints?.(["Do you work with Rust?", "How fast do you reply?"]);
    });
    const user = userEvent.setup();
    render(<ChatWidget />);
    const panel = await openPanel(user);

    const input = within(panel).getByPlaceholderText(/ask anything about radcrew/i);
    await user.type(input, "what do you do?");
    await user.click(submitButton(panel));

    const hint = await within(panel).findByRole("button", { name: /do you work with rust/i });
    await user.click(hint);

    expect(streamChatMessage).toHaveBeenLastCalledWith(
      "Do you work with Rust?",
      expect.objectContaining({ onHints: expect.any(Function) }),
      expect.any(Array),
    );
  });

  it("keeps hints only under the newest answer", async () => {
    streamChatMessage.mockImplementation(async (msg, handlers) => {
      handlers.onChunk(`answer to ${msg}`);
      if (msg === "first question") handlers.onHints?.(["Do you work with Rust?"]);
    });
    const user = userEvent.setup();
    render(<ChatWidget />);
    const panel = await openPanel(user);

    const input = within(panel).getByPlaceholderText(/ask anything about radcrew/i);
    await user.type(input, "first question");
    await user.click(submitButton(panel));
    await within(panel).findByRole("button", { name: /do you work with rust/i });

    await user.type(input, "second question");
    await user.click(submitButton(panel));

    await waitFor(() =>
      expect(within(panel).getByText("answer to second question")).toBeInTheDocument(),
    );
    expect(
      within(panel).queryByRole("button", { name: /do you work with rust/i }),
    ).not.toBeInTheDocument();
  });

  it("arms the top hint on the input after an answer that carried hints", async () => {
    answerWith(HINTS);
    const user = userEvent.setup();
    render(<ChatWidget />);
    const panel = await openPanel(user);

    await user.type(chatInput(panel), "what do you do?");
    await user.click(submitButton(panel));

    await waitFor(() => expect(chatInput(panel)).toHaveAttribute("placeholder", HINTS[0]));
    expect(within(panel).getByText("Tab")).toBeInTheDocument();
  });

  it("truncates an armed hint too long for the input", async () => {
    const long = "What does a typical engagement timeline look like for you?";
    answerWith([long]);
    const user = userEvent.setup();
    render(<ChatWidget />);
    const panel = await openPanel(user);

    await user.type(chatInput(panel), "what do you do?");
    await user.click(submitButton(panel));

    await waitFor(() =>
      expect(chatInput(panel)).toHaveAttribute("placeholder", `${long.slice(0, 37)}…`),
    );
  });

  it("sends the armed hint when tab is pressed in the empty input", async () => {
    const followUp = "What is your stack?";
    streamChatMessage.mockImplementation(async (msg, handlers) => {
      handlers.onChunk(`answer to ${msg}`);
      handlers.onHints?.(msg === HINTS[0] ? [followUp] : HINTS);
    });
    const user = userEvent.setup();
    render(<ChatWidget />);
    const panel = await openPanel(user);

    await user.type(chatInput(panel), "what do you do?");
    await user.click(submitButton(panel));
    await waitFor(() => expect(chatInput(panel)).toHaveAttribute("placeholder", HINTS[0]));

    await user.click(chatInput(panel));
    await user.tab();

    expect(streamChatMessage).toHaveBeenLastCalledWith(
      HINTS[0],
      expect.objectContaining({ onHints: expect.any(Function) }),
      expect.any(Array),
    );
    // The armed hint follows the newest answer rather than sticking.
    await waitFor(() => expect(chatInput(panel)).toHaveAttribute("placeholder", followUp));
  });

  it("leaves tab alone once the draft has text", async () => {
    answerWith(HINTS);
    const user = userEvent.setup();
    render(<ChatWidget />);
    const panel = await openPanel(user);

    await user.type(chatInput(panel), "what do you do?");
    await user.click(submitButton(panel));
    await waitFor(() => expect(chatInput(panel)).toHaveAttribute("placeholder", HINTS[0]));

    await user.type(chatInput(panel), "my own question");
    await user.tab();

    expect(streamChatMessage).toHaveBeenCalledOnce();
    expect(chatInput(panel)).not.toHaveFocus();
  });

  it("leaves shift+tab alone so focus can still move backwards", async () => {
    answerWith(HINTS);
    const user = userEvent.setup();
    render(<ChatWidget />);
    const panel = await openPanel(user);

    await user.type(chatInput(panel), "what do you do?");
    await user.click(submitButton(panel));
    await waitFor(() => expect(chatInput(panel)).toHaveAttribute("placeholder", HINTS[0]));

    await user.click(chatInput(panel));
    await user.keyboard("{Shift>}{Tab}{/Shift}");

    expect(streamChatMessage).toHaveBeenCalledOnce();
  });

  it("arms nothing when the answer carried no hints", async () => {
    answerWith([]);
    const user = userEvent.setup();
    render(<ChatWidget />);
    const panel = await openPanel(user);

    await user.type(chatInput(panel), "what do you do?");
    await user.click(submitButton(panel));
    await waitFor(() =>
      expect(within(panel).getByText("answer to what do you do?")).toBeInTheDocument(),
    );

    expect(chatInput(panel)).toHaveAttribute("placeholder", "Ask anything about radcrew…");
    expect(within(panel).queryByText("Tab")).not.toBeInTheDocument();
  });

  it("arms nothing while the answer is still streaming", async () => {
    let release = () => {};
    streamChatMessage.mockImplementation(async (_msg, handlers) => {
      handlers.onChunk("partial answer");
      await new Promise<void>((resolve) => {
        release = resolve;
      });
      handlers.onHints?.(HINTS);
    });
    const user = userEvent.setup();
    render(<ChatWidget />);
    const panel = await openPanel(user);

    await user.type(chatInput(panel), "what do you do?");
    await user.click(submitButton(panel));
    await waitFor(() =>
      expect(within(panel).getByText("partial answer")).toBeInTheDocument(),
    );

    expect(chatInput(panel)).toHaveAttribute("placeholder", "Ask anything about radcrew…");
    expect(within(panel).queryByText("Tab")).not.toBeInTheDocument();

    release();
    await waitFor(() => expect(chatInput(panel)).toHaveAttribute("placeholder", HINTS[0]));
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

  it("stays open when clicking inside the panel, closes when clicking outside", async () => {
    const user = userEvent.setup();
    render(
      <>
        <div data-testid="outside">outside</div>
        <ChatWidget />
      </>,
    );
    const panel = await openPanel(user);

    // Hit-testing uses a data attribute rather than a ref, because a ref on the
    // AnimatePresence child makes framer-motion trip React 18's `ref` warning.
    await user.click(within(panel).getByPlaceholderText(/ask anything about radcrew/i));
    expect(screen.getByRole("dialog", { name: /radcrew chat/i })).toBeInTheDocument();

    await user.click(screen.getByTestId("outside"));
    await waitFor(() =>
      expect(screen.queryByRole("dialog", { name: /radcrew chat/i })).not.toBeInTheDocument(),
    );
  });
});
