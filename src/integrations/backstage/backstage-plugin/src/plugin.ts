import {
  createPlugin,
  createRoutableExtension,
} from '@backstage/core-plugin-api';

export const ragLlmPlugin = createPlugin({
  id: 'rag-llm',
  routes: {
    root: '/rag-llm',
  },
});

export const RagLlmPage = ragLlmPlugin.provide(
  createRoutableExtension({
    name: 'RagLlmPage',
    component: () =>
      import('./components/RagLlmPage').then(m => m.RagLlmPage),
    mountPoint: '/rag-llm',
  }),
);
