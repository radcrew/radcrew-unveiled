import { describe, expect, it } from "vitest";
import { buildKnowledgeChunks, retrieveRelevantChunks } from "./retrieval.js";

describe("retrieveRelevantChunks", () => {
  it("returns the most relevant chunks for a query", () => {
    const chunks = buildKnowledgeChunks([
      {
        id: "a",
        title: "Contact",
        text: "Email hello@radcrew.dev and expect a reply in one to two business days.",
      },
      {
        id: "b",
        title: "Services",
        text: "RadCrew builds full-stack apps, Web3 products, and AI systems.",
      },
    ]);

    const result = retrieveRelevantChunks(chunks, "How can I contact you?");
    expect(result.length).toBeGreaterThan(0);
    expect(result[0].title).toBe("Contact");
  });
});
