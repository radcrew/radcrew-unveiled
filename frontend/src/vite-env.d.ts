/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_CONTENTFUL_SPACE_ID?: string;
  readonly VITE_CONTENTFUL_DELIVERY_TOKEN?: string;
  readonly VITE_CONTENTFUL_ENVIRONMENT?: string;
  readonly VITE_CHATBOT_API_BASE_URL?: string;
  /** Web3Forms access key for contact + newsletter on the marketing site */
  readonly VITE_WEB3FORMS_ACCESS_KEY?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
