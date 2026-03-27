export interface ChatSource {
  id: string;
  title: string;
  snippet: string;
  url?: string;
}

export interface ChatResponsePayload {
  answer: string;
  confidence: number;
  sources: ChatSource[];
}

export interface KnowledgeDocument {
  id: string;
  title: string;
  text: string;
  url?: string;
}

export interface KnowledgeChunk {
  id: string;
  title: string;
  text: string;
  tokens: string[];
  url?: string;
}
