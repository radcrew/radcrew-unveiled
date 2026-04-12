import { MessageCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import * as styles from "./styles";

interface ChatFloatingButtonProps {
  onOpen: () => void;
}

export const ChatFloatingButton = ({ onOpen }: ChatFloatingButtonProps) => (
  <Button
    type="button"
    className={styles.button}
    aria-label="Open FAQ chat"
    onClick={onOpen}
  >
    <MessageCircle className={styles.icon} strokeWidth={1.75} />
    <span className={styles.placeholder}>Ask RadCrew assistant</span>
  </Button>
);
