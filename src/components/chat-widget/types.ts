import type { ChatbotSource } from "@/lib/chatbot-api";

export type ChatRole = "user" | "assistant";

export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  sources?: ChatbotSource[];
}

export const WELCOME_MESSAGE: ChatMessage = {
  id: "welcome",
  role: "assistant",
  content:
    "Ask about RadCrew's services, how we work, or how to reach us. Answers use this site's content as context.",
};
