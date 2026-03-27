import cors from "cors";
import express from "express";
import rateLimit from "express-rate-limit";
import { z } from "zod";
import type { AppConfig } from "./config.js";
import { generateAnswer } from "./chat/huggingface.js";
import { buildChatPrompt } from "./chat/prompt.js";
import { retrieveRelevantChunks } from "./chat/retrieval.js";
import type { ChatResponsePayload, KnowledgeChunk } from "./types.js";

const chatRequestSchema = z.object({
  message: z.string().trim().min(2).max(1500),
  history: z
    .array(
      z.object({
        role: z.enum(["user", "assistant"]),
        content: z.string().trim().min(1).max(2000),
      }),
    )
    .max(12)
    .optional(),
});

export function createServer(config: AppConfig, knowledgeChunks: KnowledgeChunk[]) {
  const app = express();

  app.use(
    cors({
      origin: config.FRONTEND_ORIGIN,
    }),
  );
  app.use(express.json({ limit: "1mb" }));

  app.use(
    rateLimit({
      windowMs: 60_000,
      max: 25,
      standardHeaders: "draft-7",
      legacyHeaders: false,
    }),
  );

  app.get("/health", (_req, res) => {
    res.json({ ok: true, chunks: knowledgeChunks.length });
  });

  app.post("/chat", async (req, res) => {
    const parsed = chatRequestSchema.safeParse(req.body);
    if (!parsed.success) {
      return res.status(400).json({ error: "Invalid request payload." });
    }

    try {
      const { message } = parsed.data;
      const relevantChunks = retrieveRelevantChunks(knowledgeChunks, message, 5);
      const fallbackNeeded = relevantChunks.length === 0 || relevantChunks[0].score < 1.2;

      if (fallbackNeeded) {
        const fallback: ChatResponsePayload = {
          answer:
            "I don't have enough verified context for that yet. Please email hello@radcrew.dev and the team can help directly.",
          confidence: 0.2,
          sources: [],
        };
        return res.json(fallback);
      }

      if (!config.HUGGINGFACE_API_KEY) {
        return res.json({
          answer:
            "The FAQ assistant is not configured yet. Set HUGGINGFACE_API_KEY or HF_TOKEN in backend/.env (see backend/.env.example), then restart the server.",
          confidence: 0,
          sources: [],
        } satisfies ChatResponsePayload);
      }

      const prompt = buildChatPrompt(
        message,
        relevantChunks.map(({ score: _score, ...chunk }) => chunk),
      );
      const answer = await generateAnswer(config.HUGGINGFACE_MODEL, config.HUGGINGFACE_API_KEY, prompt);

      const payload: ChatResponsePayload = {
        answer,
        confidence: Math.min(1, relevantChunks[0].score / 3),
        sources: relevantChunks.map((chunk) => ({
          id: chunk.id,
          title: chunk.title,
          snippet: chunk.text,
          url: chunk.url,
        })),
      };

      return res.json(payload);
    } catch (error) {
      console.error("POST /chat failed:", error);
      return res.status(502).json({
        error:
          "The AI service is temporarily unavailable. Please try again in a moment or email hello@radcrew.dev.",
      });
    }
  });

  return app;
}
