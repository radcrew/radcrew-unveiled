import "dotenv/config";
import { z } from "zod";

const envSchema = z.object({
  PORT: z.coerce.number().int().positive().default(8787),
  FRONTEND_ORIGIN: z.string().url().default("http://localhost:8080"),
  HUGGINGFACE_API_KEY: z.string().min(1),
  HUGGINGFACE_MODEL: z.string().default("Qwen/Qwen2.5-1.5B-Instruct"),
  CONTENTFUL_SPACE_ID: z.string().optional(),
  CONTENTFUL_DELIVERY_TOKEN: z.string().optional(),
  CONTENTFUL_ENVIRONMENT: z.string().default("master"),
});

export type AppConfig = z.infer<typeof envSchema>;

function mergedProcessEnv(): NodeJS.ProcessEnv {
  const env = { ...process.env };
  if (!env.HUGGINGFACE_API_KEY && env.HF_TOKEN) {
    env.HUGGINGFACE_API_KEY = env.HF_TOKEN;
  }
  return env;
}

export function getConfig(): AppConfig {
  return envSchema.parse(mergedProcessEnv());
}
