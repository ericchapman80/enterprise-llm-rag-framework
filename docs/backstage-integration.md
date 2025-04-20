# Backstage Integration Guide

This guide provides detailed instructions for integrating the RAG-Enabled LLM Framework with Backstage.

## Overview

The Backstage integration consists of a plugin that adds an AI Assistant to your Backstage instance. The plugin provides:

- A chat interface for interacting with the RAG-enabled LLM
- Documentation search capabilities
- Code examples and best practices lookup
- User feedback collection

## Prerequisites

- A running Backstage instance
- Access to modify your Backstage app
- The RAG-LLM backend service running and accessible

## Installation Steps

### 1. Copy the Plugin to Your Backstage App

Copy the `src/integrations/backstage/backstage-plugin` directory to your Backstage plugins directory:

```bash
cp -r rag-llm-framework/src/integrations/backstage/backstage-plugin your-backstage-app/plugins/rag-llm
```

### 2. Add the Plugin to Your Backstage App's Package.json

Edit your Backstage app's `package.json` to include the plugin:

```json
"dependencies": {
  // ... other dependencies
  "@internal/plugin-rag-llm": "link:../plugins/rag-llm"
}
```

### 3. Install Dependencies

```bash
cd your-backstage-app
yarn install
```

### 4. Register the Plugin

Edit your `packages/app/src/App.tsx` file to include the plugin:

```tsx
import { RagLlmPage } from '@internal/plugin-rag-llm';

// Add to the routes
<Route path="/rag-llm" element={<RagLlmPage />} />
```

### 5. Add to Sidebar

Edit your `packages/app/src/components/Root/Root.tsx` file:

```tsx
import ChatIcon from '@material-ui/icons/Chat';

// Add to the sidebar items
<SidebarItem icon={ChatIcon} to="rag-llm" text="AI Assistant" />
```

### 6. Configure the Plugin

Create or update your `app-config.local.yaml` file in your Backstage root:

```yaml
ragLlm:
  apiUrl: http://your-rag-llm-backend-url:8000  # URL to your RAG LLM backend
```

For production, add this configuration to your main `app-config.yaml` or use environment variables.

### 7. Build and Start Backstage

```bash
yarn build
yarn start
```

## Plugin Structure

The plugin consists of the following components:

### Chat Interface

The main chat interface allows users to interact with the RAG-enabled LLM. It includes:

- A chat history display
- A message input field
- Source references for responses
- Feedback buttons

### API Client

The API client handles communication with the RAG-LLM backend service. It includes methods for:

- Sending queries
- Submitting feedback
- Managing conversation history

### Admin Panel

An optional admin panel for administrators to:

- View usage statistics
- Review user feedback
- Configure the LLM settings

## Customization

### Styling

You can customize the appearance of the plugin by modifying the theme in your Backstage app:

```tsx
// In your App.tsx
import { ThemeProvider } from '@material-ui/core/styles';
import { lightTheme } from '@backstage/theme';
import { customTheme } from './themes/custom';

// Merge the custom theme with the Backstage light theme
const theme = {
  ...lightTheme,
  ...customTheme,
};

// Use the theme provider
<ThemeProvider theme={theme}>
  {/* Your app */}
</ThemeProvider>
```

### Configuration Options

The plugin supports the following configuration options in `app-config.yaml`:

```yaml
ragLlm:
  apiUrl: http://your-rag-llm-backend-url:8000
  features:
    adminPanel: true  # Enable/disable the admin panel
    codeExamples: true  # Enable/disable code examples feature
    documentationSearch: true  # Enable/disable documentation search
  ui:
    chatTitle: "AI Assistant"  # Custom title for the chat interface
    chatPlaceholder: "Ask me anything..."  # Custom placeholder for the input field
```

## Troubleshooting

### Plugin Not Appearing

If the plugin doesn't appear in your Backstage instance:

1. Check that the plugin is correctly registered in `App.tsx`
2. Verify that the sidebar item is added in `Root.tsx`
3. Ensure the plugin is built correctly with `yarn build`

### Connection Issues

If the plugin can't connect to the RAG-LLM backend:

1. Verify the `apiUrl` in your configuration
2. Check that the backend service is running
3. Ensure there are no CORS issues (the backend should allow requests from your Backstage domain)

### Build Errors

If you encounter build errors:

1. Check that all dependencies are installed
2. Verify that the plugin is compatible with your Backstage version
3. Look for any TypeScript errors in the plugin code

## Advanced Usage

### Custom Embeddings

To use custom embeddings for your organization's specific terminology:

1. Train a custom embeddings model
2. Update the backend configuration to use your custom model
3. No changes are needed in the Backstage plugin

### Authentication

To add authentication to the plugin:

1. Implement an auth provider in your Backstage app
2. Pass the authentication token to the RAG-LLM API client
3. Update the backend to validate the token

Example:

```tsx
// In your API client
const { token } = useApi(identityApiRef);

// Add token to requests
const headers = {
  Authorization: `Bearer ${token}`,
};
```

## Feedback and Contributions

We welcome feedback and contributions to improve the Backstage integration. Please submit issues and pull requests to the repository.
