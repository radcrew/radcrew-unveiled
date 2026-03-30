import { MessageCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface ChatFloatingButtonProps {
  onOpen: () => void;
}

export const ChatFloatingButton = ({ onOpen }: ChatFloatingButtonProps) => (
  <Button
    type="button"
    size="icon"
    className={cn(
      "fixed bottom-6 right-6 z-40 h-14 w-14 rounded-full shadow-lg",
      "bg-accent text-accent-foreground hover:bg-accent/90",
    )}
    aria-label="Open FAQ chat"
    onClick={onOpen}
  >
    <MessageCircle className="h-6 w-6" strokeWidth={1.75} />
  </Button>
);
