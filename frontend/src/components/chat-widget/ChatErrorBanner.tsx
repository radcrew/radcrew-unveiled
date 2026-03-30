interface ChatErrorBannerProps {
  message: string;
}

export const ChatErrorBanner = ({ message }: ChatErrorBannerProps) => (
  <p className="shrink-0 border-t border-destructive/30 bg-destructive/5 px-4 py-2 text-center text-xs text-destructive">
    {message}
  </p>
);
