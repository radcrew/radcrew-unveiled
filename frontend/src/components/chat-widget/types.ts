export type ChatRole = "user" | "assistant";

export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  /** Follow-up questions offered under an assistant answer. */
  hints?: string[];
}

export const WELCOME_MESSAGE: ChatMessage = {
  id: "welcome",
  role: "assistant",
  content:
    "Hello. I'm the radcrew assistant — ask me anything about our services, process, or expertise.",
};
