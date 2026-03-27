import {
  InferenceClient,
  InferenceClientProviderApiError,
  type InferenceProviderOrPolicy,
} from "@huggingface/inference";

function messageContentToString(content: unknown): string {
  if (typeof content === "string") return content;
  if (Array.isArray(content)) {
    return content
      .map((part) => {
        if (!part || typeof part !== "object" || !("text" in part)) {
          return "";
        }
        const text = (part as { text: unknown }).text;
        return typeof text === "string" ? text : "";
      })
      .join("");
  }
  return "";
}

function logHfProviderError(phase: string, err: unknown): void {
  if (err instanceof InferenceClientProviderApiError) {
    const body = err.httpResponse?.body;
    console.error(
      `[HF ${phase}] status=${err.httpResponse?.status} body=${typeof body === "object" ? JSON.stringify(body) : String(body)}`,
    );
  }
}

/**
 * Tries OpenAI-style chat completions first, then text generation (some models / routing only support one path).
 */
export async function generateAnswer(
  model: string,
  accessToken: string,
  prompt: string,
  providerPolicy: string = "hf-inference",
): Promise<string> {
  const provider = providerPolicy as InferenceProviderOrPolicy;
  const client = new InferenceClient(accessToken);

  try {
    const out = await client.chatCompletion({
      model,
      provider,
      messages: [{ role: "user", content: prompt }],
      max_tokens: 512,
    });
    const text = messageContentToString(out.choices?.[0]?.message?.content).trim();
    if (text) return text;
  } catch (err) {
    logHfProviderError("chatCompletion", err);
  }

  try {
    const out = await client.textGeneration({
      model,
      provider,
      inputs: prompt,
      parameters: { max_new_tokens: 512, return_full_text: false },
    });
    const generated =
      typeof out === "object" && out !== null && "generated_text" in out
        ? String((out as { generated_text: string }).generated_text).trim()
        : "";
    if (generated) return generated;
  } catch (err) {
    logHfProviderError("textGeneration", err);
    throw err;
  }

  throw new Error("The model returned an empty response.");
}
