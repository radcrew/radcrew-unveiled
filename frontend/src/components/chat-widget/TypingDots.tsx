/** Bouncing dots shown after sending, until the first token of the answer arrives. */
export const TypingDots = () => (
  <span className="flex items-center gap-1 py-0.5">
    {[0, 150, 300].map((delayMs) => (
      <span
        key={delayMs}
        className="h-1.5 w-1.5 animate-bounce rounded-full bg-current"
        style={{ animationDelay: `${delayMs}ms` }}
      />
    ))}
  </span>
);
