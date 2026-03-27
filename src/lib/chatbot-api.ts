export interface ChatbotSource {
  id: string;
  title: string;
  snippet: string;
  url?: string;
}

export interface ChatbotResponse {
  answer: string;
  confidence: number;
  sources: ChatbotSource[];
}

const baseUrl = (import.meta.env.VITE_CHATBOT_API_BASE_URL ?? "http://localhost:8787").replace(/\/$/, "");

export async function sendChatMessage(message: string): Promise<ChatbotResponse> {
  const response = await fetch(`${baseUrl}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    throw new Error("The chatbot service is currently unavailable.");
  }

  return (await response.json()) as ChatbotResponse;
}
