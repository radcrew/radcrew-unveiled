import { MessageCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import * as styles from "./styles";

interface ChatFloatingButtonProps {
  onOpen: () => void;
  /** Distance from viewport bottom; on home page derived from footer height to vertically center in the footer band. */
  fixedBottomPx?: number;
}

export const ChatFloatingButton = ({
  onOpen,
  fixedBottomPx = 24,
}: ChatFloatingButtonProps) => (
  <Button
    type="button"
    className={styles.buttonFixed}
    style={{ bottom: fixedBottomPx }}
    aria-label="Open FAQ chat"
    onClick={onOpen}
  >
    <MessageCircle className={styles.icon} strokeWidth={1.75} />
    <span className={styles.placeholder}>Ask RadCrew assistant about projects, team, or contact...</span>
  </Button>
);
