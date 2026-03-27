import {
  InferenceClient,
  InferenceClientInputError,
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

function providersToTry(policy: string): InferenceProviderOrPolicy[] {
  const primary = policy as InferenceProviderOrPolicy;
  if (primary === "auto") return ["auto"];
  return [primary, "auto"];
}

function logHfError(phase: string, provider: string, err: unknown): void {
  if (err instanceof InferenceClientProviderApiError) {
    const body = err.httpResponse?.body;
    console.error(
      `[HF ${phase} provider=${provider}] status=${err.httpResponse?.status} body=${typeof body === "object" ? JSON.stringify(body) : String(body)}`,
    );
  } else if (err instanceof InferenceClientInputError) {
    console.error(`[HF ${phase} provider=${provider}] ${err.message}`);
  }
}

/**
 * Chat completions, then text generation. Retries each with `auto` routing if the configured provider has no mapping for the model.
 */
export async function generateAnswer(
  model: string,
  accessToken: string,
  prompt: string,
  providerPolicy: string = "hf-inference",
): Promise<string> {
  const client = new InferenceClient(accessToken);
  const providers = providersToTry(providerPolicy);

  for (const provider of providers) {
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
      logHfError("chatCompletion", String(provider), err);
    }
  }

  for (const provider of providers) {
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
      logHfError("textGeneration", String(provider), err);
    }
  }

  throw new Error(
    `No inference provider could run model "${model}". Try HUGGINGFACE_PROVIDER=auto, pick another HUGGINGFACE_MODEL, or enable a provider at https://huggingface.co/settings/inference-providers`,
  );
}
