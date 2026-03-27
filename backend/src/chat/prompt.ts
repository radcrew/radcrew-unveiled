import type { KnowledgeChunk } from "../types.js";

export function buildChatPrompt(question: string, contextChunks: KnowledgeChunk[]): string {
  const context = contextChunks
    .map((chunk, index) => `Source ${index + 1} (${chunk.title}): ${chunk.text}`)
    .join("\n");

  return [
    "You are RadCrew's website assistant.",
    "Answer only using the provided sources.",
    "If the sources are insufficient, say you do not have enough information and suggest emailing hello@radcrew.dev.",
    "Keep answers concise, helpful, and accurate.",
    "",
    "Context sources:",
    context || "No context found.",
    "",
    `Question: ${question}`,
    "",
    "Respond in plain text.",
  ].join("\n");
}
