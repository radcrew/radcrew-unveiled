import cors from "cors";
import express from "express";
import rateLimit from "express-rate-limit";
import { z } from "zod";
import type { AppConfig } from "./config.js";
import { generateAnswer } from "./chat/gemini.js";
import { buildChatPrompt } from "./chat/prompt.js";
import { retrieveRelevantChunks } from "./chat/retrieval.js";
import type { ChatResponsePayload, KnowledgeChunk } from "./types.js";

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


  return app;
}
