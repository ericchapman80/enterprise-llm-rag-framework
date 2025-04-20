"""
RAG Engine implementation using LangChain and Ollama.
"""
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, UnstructuredMarkdownLoader
from langchain.schema import Document
from .model_storage import ModelStorage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Conversation:
    """
    Class for managing a conversation with conversation history.
    """
    
    def __init__(self, conversation_id: str):
        """
        Initialize a conversation with the given ID.
        
        Args:
            conversation_id: Unique conversation identifier
        """
        self.conversation_id = conversation_id
        self.messages = []
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
    
    def add_message(self, message: Dict[str, Any]):
        """
        Add a message to the conversation history.
        
        Args:
            message: Message to add with keys 'role', 'content', and optional 'metadata'
        """
        self.messages.append(message)
        self.last_updated = datetime.now()
    
    def get_messages(self) -> List[Dict[str, Any]]:
        """
        Get all messages in the conversation.
        
        Returns:
            List of messages
        """
        return self.messages
    
    def get_context_for_llm(self) -> str:
        """
        Get the conversation history formatted for the LLM.
        
        Returns:
            Formatted conversation history
        """
        context = ""
        for message in self.messages:
            role = message["role"]
            content = message["content"]
            if role == "user":
                context += f"User: {content}\n"
            else:
                context += f"Assistant: {content}\n"
        
        return context

class RAGEngine:
    """
    Retrieval Augmented Generation Engine using LangChain and Ollama.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the RAG Engine with configuration.
        
        Args:
            config: Configuration dictionary with the following keys:
                - model_name: Name of the Ollama model to use
                - ollama_base_url: Base URL for Ollama API
                - embeddings_model: HuggingFace embeddings model to use
                - vector_db_path: Path to store the vector database
                - storage: Model storage configuration (optional)
        """
        self.config = config
        self.llm = None
        self.embeddings = None
        self.vector_store = None
        self.qa_chain = None
        self.model_storage = None
        self.conversations = {}
        
        if "storage" in self.config:
            self.model_storage = ModelStorage(self.config)
            logger.info("Initialized model storage with type: " + 
                       self.model_storage.storage_type)
        
        self._initialize_llm()
        self._initialize_embeddings()
        self._initialize_vector_store()
        self._initialize_qa_chain()
        
    def _initialize_llm(self):
        """Initialize the LLM using Ollama."""
        try:
            model_name = self.config.get("model_name", "llama2")
            base_url = self.config.get("ollama_base_url", "http://localhost:11434")
            
            if self.model_storage and self.model_storage.storage_type == "cloud":
                model_path = self.model_storage.get_model_path(model_name)
                logger.info(f"Using model from cloud storage: {model_path}")
                
                self.llm = Ollama(
                    model=model_name,
                    base_url=base_url,
                )
            else:
                self.llm = Ollama(
                    model=model_name,
                    base_url=base_url,
                )
            
            logger.info(f"Initialized LLM with model: {model_name}")
        except Exception as e:
            logger.error(f"Error initializing LLM: {str(e)}")
            raise
    
    def _initialize_embeddings(self):
        """Initialize the embeddings model."""
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name=self.config.get("embeddings_model", "all-MiniLM-L6-v2")
            )
            logger.info(f"Initialized embeddings with model: {self.config.get('embeddings_model', 'all-MiniLM-L6-v2')}")
        except Exception as e:
            logger.error(f"Error initializing embeddings: {str(e)}")
            raise
    
    def _initialize_vector_store(self):
        """Initialize or load the vector store."""
        vector_db_path = self.config.get("vector_db_path", "./chroma_db")
        try:
            self.vector_store = Chroma(
                persist_directory=vector_db_path,
                embedding_function=self.embeddings
            )
            logger.info(f"Loaded vector store from {vector_db_path}")
        except Exception as e:
            logger.warning(f"Could not load vector store, creating new one: {str(e)}")
            self.vector_store = Chroma(
                persist_directory=vector_db_path,
                embedding_function=self.embeddings
            )
            self.vector_store.persist()
    
    def _initialize_qa_chain(self):
        """Initialize the QA chain."""
        try:
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vector_store.as_retriever(),
                return_source_documents=True
            )
            logger.info("Initialized QA chain")
        except Exception as e:
            logger.error(f"Error initializing QA chain: {str(e)}")
            raise
    
    def add_documents(self, documents: List[Document]):
        """
        Add documents to the vector store.
        
        Args:
            documents: List of LangChain Document objects
        """
        try:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            splits = text_splitter.split_documents(documents)
            
            self.vector_store.add_documents(splits)
            self.vector_store.persist()
            logger.info(f"Added {len(splits)} document chunks to vector store")
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise
    
    def query(self, query_text: str, use_rag: bool = True, max_tokens: Optional[int] = None, temperature: Optional[float] = None) -> Dict[str, Any]:
        """
        Query the RAG system.
        
        Args:
            query_text: The query text
            use_rag: Whether to use RAG context or just the LLM
            max_tokens: Optional maximum number of tokens for the response
            temperature: Optional temperature parameter for the LLM
            
        Returns:
            Dictionary containing the response and source documents
        """
        try:
            llm_kwargs = {}
            if max_tokens is not None:
                llm_kwargs['max_tokens'] = max_tokens
            if temperature is not None:
                llm_kwargs['temperature'] = temperature
            
            if use_rag:
                if llm_kwargs:
                    temp_llm = Ollama(
                        model=self.llm.model_name,
                        base_url=self.llm.base_url,
                        **llm_kwargs
                    )
                    qa_chain = RetrievalQA.from_chain_type(
                        llm=temp_llm,
                        chain_type="stuff",
                        retriever=self.vector_store.as_retriever(),
                        return_source_documents=True
                    )
                    result = qa_chain({"query": query_text})
                else:
                    result = self.qa_chain({"query": query_text})
                
                sources = []
                if "source_documents" in result:
                    for doc in result["source_documents"]:
                        source_info = {
                            "content": doc.page_content,
                            "metadata": doc.metadata
                        }
                        sources.append(source_info)
                
                return {
                    "response": result["result"],
                    "sources": sources
                }
            else:
                if llm_kwargs:
                    temp_llm = Ollama(
                        model=self.llm.model_name,
                        base_url=self.llm.base_url,
                        **llm_kwargs
                    )
                    response = temp_llm.invoke(query_text)
                else:
                    response = self.llm.invoke(query_text)
                return {
                    "response": response,
                    "sources": []
                }
        except Exception as e:
            logger.error(f"Error querying RAG system: {str(e)}")
            raise
            
    def list_documents(self) -> List[Document]:
        """
        List all documents in the vector store.
        
        Returns:
            List of Document objects
        """
        try:
            collection = self.vector_store._collection
            documents = []
            
            results = collection.get()
            
            if results and "documents" in results and "metadatas" in results:
                for i, doc_content in enumerate(results["documents"]):
                    metadata = results["metadatas"][i] if i < len(results["metadatas"]) else {}
                    documents.append(Document(page_content=doc_content, metadata=metadata))
            
            logger.info(f"Retrieved {len(documents)} documents from vector store")
            return documents
        except Exception as e:
            logger.error(f"Error listing documents: {str(e)}")
            raise
            
    def flush_vector_store(self) -> bool:
        """
        Flush all documents from the vector store.
        
        Returns:
            True if successful
        """
        try:
            collection = self.vector_store._collection
            
            collection.delete()
            
            self._initialize_vector_store()
            
            logger.info("Flushed all documents from vector store")
            return True
        except Exception as e:
            logger.error(f"Error flushing vector store: {str(e)}")
            raise

    def create_conversation(self) -> str:
        """
        Create a new conversation.
        
        Returns:
            Conversation ID
        """
        conversation_id = str(uuid.uuid4())
        self.conversations[conversation_id] = Conversation(conversation_id)
        return conversation_id
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Get a conversation by ID.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Conversation object or None if not found
        """
        return self.conversations.get(conversation_id)
    
    def add_message_to_conversation(self, conversation_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a message to a conversation.
        
        Args:
            conversation_id: Conversation ID
            role: Message role ('user' or 'assistant')
            content: Message content
            metadata: Optional message metadata
            
        Returns:
            True if successful, False otherwise
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return False
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }
        
        if metadata:
            message["metadata"] = metadata
        
        conversation.add_message(message)
        return True
    
    def query_with_conversation(self, query_text: str, conversation_id: Optional[str] = None, 
                              max_tokens: Optional[int] = None, temperature: Optional[float] = None) -> Dict[str, Any]:
        """
        Query the RAG system with conversation history.
        
        Args:
            query_text: The query text
            conversation_id: Optional conversation ID for context
            max_tokens: Optional max tokens for the LLM
            temperature: Optional temperature for the LLM
            
        Returns:
            Dictionary containing the response, source documents, and conversation ID
        """
        new_conversation = False
        if not conversation_id:
            conversation_id = self.create_conversation()
            new_conversation = True
        
        conversation = self.get_conversation(conversation_id)
        if not conversation and not new_conversation:
            conversation_id = self.create_conversation()
            conversation = self.get_conversation(conversation_id)
        
        self.add_message_to_conversation(conversation_id, "user", query_text)
        
        context = ""
        if not new_conversation:
            context = conversation.get_context_for_llm()
        
        augmented_query = query_text
        if context:
            augmented_query = f"Conversation history:\n{context}\n\nCurrent query: {query_text}"
        
        result = self.query(augmented_query)
        
        self.add_message_to_conversation(
            conversation_id, 
            "assistant", 
            result["response"], 
            {"sources": result.get("sources", [])}
        )
        
        result["conversation_id"] = conversation_id
        
        return result
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Get the history of a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            List of messages in the conversation or empty list if not found
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return []
        
        return conversation.get_messages()
    
    def cleanup_old_conversations(self, max_age_hours: int = 24):
        """
        Remove conversations older than the specified age.
        
        Args:
            max_age_hours: Maximum age in hours
        """
        now = datetime.now()
        to_remove = []
        
        for conversation_id, conversation in self.conversations.items():
            age = now - conversation.last_updated
            if age.total_seconds() > max_age_hours * 3600:
                to_remove.append(conversation_id)
        
        for conversation_id in to_remove:
            del self.conversations[conversation_id]
        
        logger.info(f"Cleaned up {len(to_remove)} old conversations")
