import { ConfigApi } from '@backstage/core-plugin-api';
import { RagLlmApi, QueryRequest, QueryResponse, FeedbackRequest } from './types';

export class RagLlmClient implements RagLlmApi {
  private readonly apiUrl: string;

  constructor(configApi: ConfigApi) {
    this.apiUrl = configApi.getString('ragLlm.apiUrl');
  }

  async query(query: string, conversationId?: string): Promise<QueryResponse> {
    const request: QueryRequest = {
      query,
      conversation_id: conversationId,
      metadata: {
        source: 'backstage',
      },
    };

    const response = await fetch(`${this.apiUrl}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Failed to query RAG LLM API: ${response.statusText}`);
    }

    return await response.json();
  }

  async submitFeedback(feedback: FeedbackRequest): Promise<void> {
    const response = await fetch(`${this.apiUrl}/feedback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(feedback),
    });

    if (!response.ok) {
      throw new Error(`Failed to submit feedback: ${response.statusText}`);
    }
  }
}
