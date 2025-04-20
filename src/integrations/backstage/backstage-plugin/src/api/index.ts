import { createApiRef } from '@backstage/core-plugin-api';
import { RagLlmApi } from './types';

export const ragLlmApiRef = createApiRef<RagLlmApi>({
  id: 'plugin.rag-llm.api',
});

export * from './types';
export * from './RagLlmClient';
