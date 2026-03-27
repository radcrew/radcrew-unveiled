import { getConfig } from "./config.js";
import { createServer } from "./server.js";

async function bootstrap() {
  const config = getConfig();

  const app = createServer(config, chunks);
  app.listen(config.PORT, () => {
    console.log(`Chatbot backend listening on http://localhost:${config.PORT}`);
  });
}

bootstrap().catch((error) => {
  console.error("Failed to start backend:", error);
  process.exit(1);
});
