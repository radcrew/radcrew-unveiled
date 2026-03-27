import { getConfig } from "./config.js";
import { loadContentfulDocuments } from "./knowledge/contentful-loader.js";
import { getStaticSiteDocuments } from "./knowledge/site-content.js";
import { createServer } from "./server.js";

async function bootstrap() {
  const config = getConfig();
  const staticDocs = getStaticSiteDocuments();
  const contentfulDocs = await loadContentfulDocuments(config);

  const app = createServer(config, chunks);
  app.listen(config.PORT, () => {
    console.log(`Chatbot backend listening on http://localhost:${config.PORT}`);
    console.log(`Knowledge chunks loaded: ${chunks.length}`);
  });
}

bootstrap().catch((error) => {
  console.error("Failed to start backend:", error);
  process.exit(1);
});
