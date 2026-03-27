import { InferenceClient } from "@huggingface/inference";

function messageContentToString(content: unknown): string {
  if (typeof content === "string") return content;
  if (Array.isArray(content)) {
    return content
      .map((part) => {
        if (part && typeof part === "object" && "text" in part && typeof (part as { text: unknown }).text === "string") {
          return (part as { text: string }).text;
        }
        return "";
      })
      .join("");
  }
  return "";
}

export async function generateAnswer(model: string, accessToken: string, prompt: string): Promise<string> {
  const client = new InferenceClient(accessToken);
  const out = await client.chatCompletion({
    model,
    messages: [{ role: "user", content: prompt }],
    max_tokens: 1024,
  });
  const text = messageContentToString(out.choices?.[0]?.message?.content).trim();
  return text || "I don't have enough information to answer that right now.";
}
