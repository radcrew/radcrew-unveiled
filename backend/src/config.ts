import "dotenv/config";
import { z } from "zod";

const envSchema = z.object({
  PORT: z.coerce.number().int().positive().default(8787),
  FRONTEND_ORIGIN: z.string().url().default("http://localhost:8080"),
  GEMINI_API_KEY: z.string().min(1),
  GEMINI_MODEL: z.string().default("gemini-1.5-flash"),
  CONTENTFUL_SPACE_ID: z.string().optional(),
  CONTENTFUL_DELIVERY_TOKEN: z.string().optional(),
  CONTENTFUL_ENVIRONMENT: z.string().default("master"),
});

export type AppConfig = z.infer<typeof envSchema>;

export function getConfig(): AppConfig {
  return envSchema.parse(process.env);
}
