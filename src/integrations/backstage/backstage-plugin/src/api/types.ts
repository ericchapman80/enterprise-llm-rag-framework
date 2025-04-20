export interface RagLlmApi {
  query(query: string, conversationId?: string): Promise<QueryResponse>;
  submitFeedback(feedback: FeedbackRequest): Promise<void>;
}

export interface QueryRequest {
  query: string;
  conversation_id?: string;
  metadata?: Record<string, any>;
}

export interface QueryResponse {
  response: string;
  sources: Source[];
  conversation_id: string;
}

export interface Source {
  title: string;
  url?: string;
  content?: string;
}

export interface FeedbackRequest {
  conversation_id: string;
  query_id: string;
  rating: number;
  comments?: string;
}
