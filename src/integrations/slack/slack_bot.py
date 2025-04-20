"""
Slack bot integration for the RAG-enabled LLM system.
"""
import os
import logging
from typing import Dict, Any, Optional
import json
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SlackBot:
    """
    Slack bot for interacting with the RAG-enabled LLM system.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Slack bot.
        
        Args:
            config: Configuration dictionary with the following keys:
                - slack_bot_token: Slack bot token
                - slack_app_token: Slack app token
                - rag_api_url: URL of the RAG API
        """
        self.config = config
        self.app = App(token=config["slack_bot_token"])
        self.rag_api_url = config["rag_api_url"]
        
        self._register_handlers()
        
    def _register_handlers(self):
        """Register event handlers for Slack events."""
        @self.app.event("message")
        def handle_message(event, say):
            if "channel_type" in event and event["channel_type"] == "im":
                self._process_message(event, say)
        
        @self.app.event("app_mention")
        def handle_mention(event, say):
            self._process_message(event, say)
        
        @self.app.action("submit_feedback")
        def handle_feedback(ack, body, client):
            ack()
            self._process_feedback(body, client)
    
    def _process_message(self, event, say):
        """
        Process a message from Slack.
        
        Args:
            event: Slack event
            say: Function to send a message
        """
        try:
            user_id = event["user"]
            text = event["text"]
            channel_id = event["channel"]
            
            text = text.replace(f"<@{self.app.client.auth_test()['user_id']}>", "").strip()
            
            if not text:
                say("How can I help you?")
                return
            
            response = self._query_rag_api(text, user_id)
            
            blocks = self._format_response_blocks(response, text)
            
            say(blocks=blocks)
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            say(f"Sorry, I encountered an error: {str(e)}")
    
    def _query_rag_api(self, query: str, user_id: str) -> Dict[str, Any]:
        """
        Query the RAG API.
        
        Args:
            query: User query
            user_id: Slack user ID
            
        Returns:
            API response
        """
        try:
            headers = {"Content-Type": "application/json"}
            data = {
                "query": query,
                "metadata": {"user_id": user_id, "source": "slack"}
            }
            
            response = requests.post(
                f"{self.rag_api_url}/query",
                headers=headers,
                json=data
            )
            
            if response.status_code != 200:
                logger.error(f"RAG API error: {response.text}")
                raise Exception(f"RAG API returned status code {response.status_code}")
            
            return response.json()
        except Exception as e:
            logger.error(f"Error querying RAG API: {str(e)}")
            raise
    
    def _format_response_blocks(self, response: Dict[str, Any], query: str) -> list:
        """
        Format the response as Slack blocks.
        
        Args:
            response: RAG API response
            query: Original query
            
        Returns:
            List of Slack blocks
        """
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": response["response"]
                }
            }
        ]
        
        if response.get("sources") and len(response["sources"]) > 0:
            blocks.append({"type": "divider"})
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Sources:*"
                }
            })
            
            for source in response["sources"][:3]:  # Limit to 3 sources
                source_text = source.get("title", "Source")
                source_url = source.get("url", "")
                
                if source_url:
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"• <{source_url}|{source_text}>"
                        }
                    })
                else:
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"• {source_text}"
                        }
                    })
        
        blocks.append({"type": "divider"})
        blocks.append({
            "type": "actions",
            "block_id": f"feedback_{response['conversation_id']}",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "👍 Helpful"
                    },
                    "value": json.dumps({
                        "conversation_id": response["conversation_id"],
                        "query": query,
                        "rating": 1
                    }),
                    "action_id": "submit_feedback"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "👎 Not Helpful"
                    },
                    "value": json.dumps({
                        "conversation_id": response["conversation_id"],
                        "query": query,
                        "rating": 0
                    }),
                    "action_id": "submit_feedback"
                }
            ]
        })
        
        return blocks
    
    def _process_feedback(self, body, client):
        """
        Process feedback from a user.
        
        Args:
            body: Slack action payload
            client: Slack client
        """
        try:
            action = body["actions"][0]
            value = json.loads(action["value"])
            
            conversation_id = value["conversation_id"]
            query = value["query"]
            rating = value["rating"]
            
            self._submit_feedback(conversation_id, query, rating)
            
            feedback_text = "👍 Thanks for your feedback!" if rating == 1 else "👎 Thanks for your feedback!"
            
            client.chat_update(
                channel=body["channel"]["id"],
                ts=body["message"]["ts"],
                blocks=body["message"]["blocks"][:-1] + [{
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": feedback_text
                    }
                }]
            )
            
        except Exception as e:
            logger.error(f"Error processing feedback: {str(e)}")
    
    def _submit_feedback(self, conversation_id: str, query: str, rating: int):
        """
        Submit feedback to the RAG API.
        
        Args:
            conversation_id: Conversation ID
            query: Original query
            rating: Feedback rating (0 or 1)
        """
        try:
            headers = {"Content-Type": "application/json"}
            data = {
                "conversation_id": conversation_id,
                "query_id": query,
                "rating": rating
            }
            
            response = requests.post(
                f"{self.rag_api_url}/feedback",
                headers=headers,
                json=data
            )
            
            if response.status_code != 200:
                logger.error(f"RAG API feedback error: {response.text}")
                raise Exception(f"RAG API returned status code {response.status_code}")
            
        except Exception as e:
            logger.error(f"Error submitting feedback: {str(e)}")
            raise
    
    def start(self):
        """Start the Slack bot."""
        try:
            handler = SocketModeHandler(self.app, self.config["slack_app_token"])
            handler.start()
            logger.info("Slack bot started")
        except Exception as e:
            logger.error(f"Error starting Slack bot: {str(e)}")
            raise

if __name__ == "__main__":
    config = {
        "slack_bot_token": os.environ.get("SLACK_BOT_TOKEN"),
        "slack_app_token": os.environ.get("SLACK_APP_TOKEN"),
        "rag_api_url": os.environ.get("RAG_API_URL", "http://localhost:8000")
    }
    
    bot = SlackBot(config)
    bot.start()
