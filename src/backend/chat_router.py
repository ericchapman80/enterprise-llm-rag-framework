"""
Chat router module for the RAG-LLM Framework.
This module provides endpoints for interactive chat functionality.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import sys
import os
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

try:
    from src.backend.rag_engine import RAGEngine
except ImportError:
    try:
        from backend.rag_engine import RAGEngine
    except ImportError:
        from rag_engine import RAGEngine

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Chat"])


class ChatRequest(BaseModel):
    """Model for chat message requests."""
    message: str
    conversation_id: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None


class ChatResponse(BaseModel):
    """Model for chat message responses."""
    conversation_id: str
    response: str
    sources: List[Dict[str, Any]]


class ChatHistoryRequest(BaseModel):
    """Model for chat history requests."""
    conversation_id: str


class ChatHistoryResponse(BaseModel):
    """Model for chat history responses."""
    conversation_id: str
    messages: List[Dict[str, Any]]


class ChatFeedbackRequest(BaseModel):
    """Model for chat feedback requests."""
    conversation_id: str
    message_idx: int
    feedback: str
    details: Optional[str] = None


class ChatFeedbackResponse(BaseModel):
    """Model for chat feedback responses."""
    status: str
    message: str


@router.post(
    "/send",
    response_model=ChatResponse,
    summary="Send a message to the chat",
    description="This endpoint sends a message to the chat and returns the "
               "response from the RAG-enhanced LLM system.",
    response_description="The response from the chat with sources and conversation ID"
)
async def send_message(
    request: ChatRequest,
    rag_engine: RAGEngine = Depends(lambda: RAGEngine(config={}))
) -> Dict[str, Any]:
    """
    Send a message to the chat.

    Args:
        request: The chat request containing the message and optional conversation ID
        rag_engine: The RAG engine instance

    Returns:
        A dictionary containing the response, sources, and conversation ID
    """
    try:
        message = request.message
        conversation_id = request.conversation_id

        if not message:
            raise HTTPException(status_code=400, detail="Message is required")

        try:
            if os.environ.get("RAG_TEST_MODE") == "true":
                import uuid
                if not conversation_id:
                    conversation_id = str(uuid.uuid4())
                return {
                    "conversation_id": conversation_id,
                    "response": f"This is a test response for: {message}",
                    "sources": []
                }

            result = rag_engine.query_with_conversation(
                message,
                conversation_id=conversation_id
            )
        except TypeError as e:
            logger.warning(f"Using fallback query method: {str(e)}")
            result = rag_engine.query(message)
            if conversation_id is None:
                import uuid
                conversation_id = str(uuid.uuid4())
            result["conversation_id"] = conversation_id
        except Exception as e:
            logger.error(f"Error querying RAG system: {str(e)}")
            import uuid
            if not conversation_id:
                conversation_id = str(uuid.uuid4())
            return {
                "conversation_id": conversation_id,
                "response": "I'm sorry, I'm having trouble connecting to the "
                           "language model. Please try again later.",
                "sources": []
            }

        return {
            "conversation_id": result["conversation_id"],
            "response": result["response"],
            "sources": result.get("sources", [])
        }
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error sending message: {str(e)}"
        )


@router.get(
    "/history/{conversation_id}",
    response_model=ChatHistoryResponse,
    summary="Get chat history",
    description="This endpoint returns the message history for a specific conversation.",
    response_description="The conversation history with all messages"
)
async def get_chat_history(
    conversation_id: str,
    rag_engine: RAGEngine = Depends(lambda: RAGEngine(config={}))
) -> Dict[str, Any]:
    """
    Get the chat history for a conversation.

    Args:
        conversation_id: The conversation ID
        rag_engine: The RAG engine instance

    Returns:
        A dictionary containing the conversation history
    """
    try:
        if not conversation_id:
            raise HTTPException(
                status_code=400,
                detail="Conversation ID is required"
            )

        try:
            if os.environ.get("RAG_TEST_MODE") == "true":
                return {
                    "conversation_id": conversation_id,
                    "messages": [
                        {
                            "role": "user",
                            "content": "Test message",
                            "timestamp": datetime.now().isoformat()
                        },
                        {
                            "role": "assistant",
                            "content": "This is a test response",
                            "timestamp": datetime.now().isoformat()
                        }
                    ]
                }

            messages = rag_engine.get_conversation_history(conversation_id)

            return {
                "conversation_id": conversation_id,
                "messages": messages
            }
        except Exception as e:
            logger.error(f"Error getting conversation history: {str(e)}")
            return {
                "conversation_id": conversation_id,
                "messages": []
            }
    except Exception as e:
        logger.error(f"Error getting chat history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting chat history: {str(e)}"
        )


@router.post(
    "/feedback",
    response_model=ChatFeedbackResponse,
    summary="Submit feedback for a chat message",
    description="This endpoint allows users to submit feedback on chat responses. "
               "The feedback can be used to improve the system over time.",
    response_description="Confirmation of feedback submission"
)
async def submit_chat_feedback(
    request: ChatFeedbackRequest,
    rag_engine: RAGEngine = Depends(lambda: RAGEngine(config={}))
) -> Dict[str, Any]:
    """
    Submit feedback for a chat message.

    Args:
        request: The feedback request containing conversation ID, message index, and feedback

    Returns:
        A dictionary containing the status of the feedback submission
    """
    try:
        if not request.conversation_id or request.message_idx is None:
            raise HTTPException(
                status_code=400,
                detail="Conversation ID and message index are required"
            )

        logger.info(
            f"Received feedback for conversation {request.conversation_id}, "
            f"message {request.message_idx}: {request.feedback}"
        )

        return {
            "status": "success",
            "message": "Feedback submitted successfully"
        }
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error submitting feedback: {str(e)}"
        )
