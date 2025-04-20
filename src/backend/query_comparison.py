"""
Query comparison module for the RAG-LLM Framework.
This module provides the endpoint for comparing RAG-enhanced and standard LLM responses.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

from src.backend.rag_engine import RAGEngine

logger = logging.getLogger(__name__)

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None

class ComparisonResponse(BaseModel):
    rag_response: str
    standard_response: str
    sources: list
    query: str

@router.post(
    "/query-comparison",
    response_model=ComparisonResponse,
    summary="Compare RAG-enhanced and standard LLM responses",
    description="This endpoint returns both the RAG-enhanced response (with context from the vector database) and the standard LLM response (without additional context) for the same query. This is useful for evaluating the impact of RAG on response quality.",
    response_description="A comparison of RAG-enhanced and standard LLM responses"
)
async def compare_responses(
    query_request: QueryRequest,
    rag_engine: RAGEngine = Depends(lambda: RAGEngine())
) -> Dict[str, Any]:
    """
    Compare RAG-enhanced and standard LLM responses for the same query.
    
    Args:
        query_request: The query request containing the query text and optional parameters
        rag_engine: The RAG engine instance
        
    Returns:
        A dictionary containing both the RAG-enhanced and standard LLM responses
    """
    try:
        rag_result = rag_engine.query(
            query_request.query,
            max_tokens=query_request.max_tokens,
            temperature=query_request.temperature
        )
        
        standard_result = rag_engine.query_llm_directly(
            query_request.query,
            max_tokens=query_request.max_tokens,
            temperature=query_request.temperature
        )
        
        return {
            "rag_response": rag_result["answer"],
            "standard_response": standard_result,
            "sources": rag_result.get("sources", []),
            "query": query_request.query
        }
    except Exception as e:
        logger.error(f"Error comparing responses: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error comparing responses: {str(e)}")
