# Slack Integration Guide

This guide provides detailed instructions for integrating the RAG-Enabled LLM Framework with Slack.

## Overview

The Slack integration allows users to interact with the RAG-enabled LLM directly from Slack. Features include:

- Direct messaging with the bot
- Mentioning the bot in channels
- Providing feedback on responses
- Searching company knowledge base

## Prerequisites

- A Slack workspace with admin privileges
- The RAG-LLM backend service running and accessible

## Creating a Slack App

### 1. Create a New Slack App

1. Go to [Slack API](https://api.slack.com/apps) and click "Create New App"
2. Choose "From scratch"
3. Enter a name for your app (e.g., "Company AI Assistant")
4. Select your workspace
5. Click "Create App"

### 2. Configure Bot Features

1. In the left sidebar, click on "OAuth & Permissions"
2. Scroll down to "Scopes" and add the following Bot Token Scopes:
   - `app_mentions:read` - Allow the bot to be mentioned
   - `chat:write` - Allow the bot to send messages
   - `im:history` - Allow the bot to view direct message history
   - `im:read` - Allow the bot to read direct messages
   - `im:write` - Allow the bot to send direct messages
   - `reactions:write` - Allow the bot to add reactions

### 3. Enable Socket Mode

1. In the left sidebar, click on "Socket Mode"
2. Toggle "Enable Socket Mode" to On
3. Generate an app-level token with the `connections:write` scope
4. Save the token (it starts with `xapp-`)

### 4. Enable Event Subscriptions

1. In the left sidebar, click on "Event Subscriptions"
2. Toggle "Enable Events" to On
3. Under "Subscribe to bot events", add:
   - `app_mention` - When the bot is mentioned
   - `message.im` - When a message is sent in a direct message

### 5. Install the App to Your Workspace

1. In the left sidebar, click on "Install App"
2. Click "Install to Workspace"
3. Review the permissions and click "Allow"
4. Save the Bot User OAuth Token (it starts with `xoxb-`)

## Configuring the Slack Bot

### 1. Set Environment Variables

Add the following environment variables to your deployment:

```
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
SLACK_SIGNING_SECRET=your-signing-secret
RAG_API_URL=http://your-rag-llm-backend-url:8000
```

For local development, add these to your `.env` file.

### 2. Update Configuration

Update the `config/config.yaml` file with your Slack credentials:

```yaml
slack:
  bot_token: ${SLACK_BOT_TOKEN}
  app_token: ${SLACK_APP_TOKEN}
  signing_secret: ${SLACK_SIGNING_SECRET}
```

## Running the Slack Bot

### Local Development

To run the Slack bot locally:

```bash
cd src/integrations/slack
python slack_bot.py
```

### Production Deployment

For Kubernetes deployment, the Slack bot is included in the main deployment. Ensure the environment variables are set in your Kubernetes secrets.

## Using the Slack Bot

### Direct Messages

Users can send direct messages to the bot to ask questions:

1. Find the bot in your Slack workspace
2. Start a direct message conversation
3. Ask a question

### Mentions in Channels

Users can mention the bot in channels:

1. In any channel where the bot is present, type `@botname`
2. Follow with your question
3. The bot will respond in the channel

### Providing Feedback

After receiving a response, users can provide feedback:

1. Click the 👍 or 👎 button below the response
2. Optionally, add a comment to explain the feedback

## Customizing the Slack Bot

### Bot Personality

To customize the bot's personality, edit the `src/integrations/slack/slack_bot.py` file:

```python
# Customize the bot's responses
GREETING_MESSAGES = [
    "Hello! How can I help you today?",
    "Hi there! What can I assist you with?",
    "Greetings! What would you like to know?"
]

# Customize the bot's error messages
ERROR_MESSAGES = [
    "I'm sorry, I encountered an error. Please try again.",
    "Oops! Something went wrong. Let's try that again."
]
```

### Response Formatting

To customize how responses are formatted in Slack, edit the `_format_response_blocks` method in `slack_bot.py`:

```python
def _format_response_blocks(self, response, query):
    # Customize the response formatting
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Question:*\n{query}\n\n*Answer:*\n{response['response']}"
            }
        }
    ]
    
    # Add your custom formatting here
    
    return blocks
```

## Advanced Features

### Slash Commands

To add slash commands to your bot:

1. In the Slack API dashboard, click on "Slash Commands"
2. Click "Create New Command"
3. Enter the command details:
   - Command: `/ask`
   - Request URL: Your bot's endpoint (for Socket Mode, this can be any valid URL)
   - Short Description: "Ask the AI Assistant a question"
   - Usage Hint: "[your question]"
4. Click "Save"

5. Update your bot code to handle slash commands:

```python
@app.command("/ask")
def handle_ask_command(ack, command, say):
    ack()
    query = command["text"]
    # Process the query and respond
    response = query_rag_api(query, command["user_id"])
    say(blocks=format_response_blocks(response, query))
```

### Interactive Components

To add interactive components like buttons and menus:

1. In the Slack API dashboard, click on "Interactivity & Shortcuts"
2. Toggle "Interactivity" to On
3. Set the Request URL (for Socket Mode, this can be any valid URL)
4. Click "Save Changes"

5. Update your bot code to handle interactive components:

```python
@app.action("action_id")
def handle_action(ack, body, client):
    ack()
    # Process the action
    # Update the message
    client.chat_update(
        channel=body["channel"]["id"],
        ts=body["message"]["ts"],
        blocks=new_blocks
    )
```

## Troubleshooting

### Bot Not Responding

If the bot doesn't respond:

1. Check that the bot is online and the service is running
2. Verify that the bot has been invited to the channel
3. Check the logs for any errors
4. Ensure the bot has the necessary permissions

### Socket Mode Issues

If you're having issues with Socket Mode:

1. Verify that the `SLACK_APP_TOKEN` is correct and has the `connections:write` scope
2. Check that Socket Mode is enabled in the Slack API dashboard
3. Restart the bot service

### Rate Limiting

If you encounter rate limiting issues:

1. Implement exponential backoff for retries
2. Consider upgrading to a paid Slack plan for higher rate limits
3. Optimize your bot to reduce the number of API calls

## Monitoring and Maintenance

### Logging

The bot logs important events and errors. To view the logs:

- For local development: Check the console output
- For Kubernetes: Use `kubectl logs` to view the pod logs

### Health Checks

To ensure the bot is running properly:

1. Implement a health check endpoint in your bot service
2. Set up monitoring to alert on failures
3. Periodically test the bot functionality

### Updates

When updating the bot:

1. Test changes in a development environment first
2. Deploy during low-usage periods
3. Monitor closely after updates for any issues

## Security Considerations

### Token Security

Protect your Slack tokens:

1. Never commit tokens to version control
2. Use environment variables or secrets management
3. Rotate tokens periodically

### User Data

When handling user data:

1. Only store what's necessary
2. Follow your organization's data retention policies
3. Ensure compliance with relevant regulations (GDPR, CCPA, etc.)

## Feedback Collection

The bot automatically collects user feedback through reactions and buttons. This feedback is stored in the database and can be used to improve the system over time.

To view collected feedback, access the admin dashboard at `/admin/feedback` (requires admin authentication).
