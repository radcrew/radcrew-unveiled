import fs from "node:fs/promises";
import path from "node:path";
import type { KnowledgeChunk, KnowledgeDocument } from "../types.js";

const TOKEN_RE = /[a-z0-9]+/gi;

function tokenize(input: string): string[] {
  return (input.toLowerCase().match(TOKEN_RE) ?? []).filter((token) => token.length > 1);
}

function chunkDocument(doc: KnowledgeDocument): KnowledgeChunk[] {
  const sentenceChunks = doc.text
    .split(/(?<=[.?!])\s+/)
    .map((part) => part.trim())
    .filter(Boolean);

  if (sentenceChunks.length <= 2) {
    return [
      {
        id: `${doc.id}:0`,
        title: doc.title,
        text: doc.text,
        tokens: tokenize(doc.text),
        url: doc.url,
      },
    ];
  }

  const chunks: KnowledgeChunk[] = [];
  for (let i = 0; i < sentenceChunks.length; i += 2) {
    const chunkText = sentenceChunks.slice(i, i + 2).join(" ").trim();
    chunks.push({
      id: `${doc.id}:${i / 2}`,
      title: doc.title,
      text: chunkText,
      tokens: tokenize(chunkText),
      url: doc.url,
    });
  }
  return chunks;
}

export function buildKnowledgeChunks(documents: KnowledgeDocument[]): KnowledgeChunk[] {
  return documents.flatMap((doc) => chunkDocument(doc)).filter((chunk) => chunk.tokens.length > 0);
}

export async function persistKnowledgeIndex(chunks: KnowledgeChunk[]): Promise<void> {
  const cacheDir = path.resolve(process.cwd(), ".cache");
  await fs.mkdir(cacheDir, { recursive: true });
  await fs.writeFile(path.join(cacheDir, "knowledge-index.json"), JSON.stringify(chunks, null, 2), "utf8");
}

export function retrieveRelevantChunks(
  chunks: KnowledgeChunk[],
  query: string,
  limit = 5,
): Array<KnowledgeChunk & { score: number }> {
  const queryTokens = new Set(tokenize(query));
  if (queryTokens.size === 0) return [];

  return chunks
    .map((chunk) => {
      const overlap = chunk.tokens.reduce((score, token) => score + (queryTokens.has(token) ? 1 : 0), 0);
      const density = overlap / Math.max(chunk.tokens.length, 1);
      return { ...chunk, score: overlap + density };
    })
    .filter((chunk) => chunk.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, limit);
}
