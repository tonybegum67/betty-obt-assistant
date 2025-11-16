"""
Configuration settings for Betty AI Assistant.

This module centralizes all configuration parameters for the application,
making it easier to manage different environments and deployment scenarios.
"""

import os
from typing import Optional


class AppConfig:
    """Main application configuration class."""
    
    # API Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"
    
    # Claude API Configuration
    ANTHROPIC_API_KEY: Optional[str] = None
    CLAUDE_MODEL: str = "claude-sonnet-4-20250514"

    # Cassidy AI Configuration
    CASSIDY_API_KEY: Optional[str] = os.getenv("CASSIDY_API_KEY")
    CASSIDY_ASSISTANT_ID: str = os.getenv("CASSIDY_ASSISTANT_ID", "cmgjq8s7802e1n70frp8qad4r")

    # AI Provider Selection
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "claude")  # "openai", "claude", "cassidy", or "compare"
    
    # Database Configuration
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "./data/betty_chroma_db")
    
    # Text Processing Configuration - Optimized for consistent context
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))  # Larger chunks for better context
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))  # More overlap for continuity
    MAX_SEARCH_RESULTS: int = int(os.getenv("MAX_SEARCH_RESULTS", "15"))  # Increased for comprehensive project analysis
    
    # Embedding Configuration
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-mpnet-base-v2")
    TOKENIZER_MODEL: str = os.getenv("TOKENIZER_MODEL", "cl100k_base")
    
    # File Processing Configuration
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    SUPPORTED_FILE_TYPES: tuple = (".pdf", ".docx", ".txt", ".csv")
    
    # UI Configuration
    PAGE_TITLE: str = "Betty - Your AI Assistant"
    PAGE_ICON: str = "💁‍♀️"
    
    # Knowledge Base Configuration
    KNOWLEDGE_COLLECTION_NAME: str = "betty_knowledge"
    DEFAULT_KNOWLEDGE_FILES: tuple = (
        "docs/Betty for Molex GPS.docx",
        "docs/Molex Manufacturing BA Reference Architecture.docx"
    )
    
    # RAG Enhancement Configuration - Optimized for consistency
    USE_RERANKING: bool = bool(os.getenv("USE_RERANKING", "False"))  # Disabled for deterministic results
    USE_SEMANTIC_CHUNKING: bool = bool(os.getenv("USE_SEMANTIC_CHUNKING", "False"))  # Simplified chunking
    RERANKER_MODEL: str = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")

    # LLM Generation Parameters - Optimized for factual accuracy
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.2"))  # Low temp for deterministic, factual responses
    TOP_P: float = float(os.getenv("TOP_P", "0.9"))  # High nucleus sampling for natural professional language
    TOP_K: int = int(os.getenv("TOP_K", "40"))  # Moderate vocabulary pool for domain-specific terms
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "4000"))  # Maximum response length

    # Environment Configuration
    DISABLE_TOKENIZER_PARALLELISM: bool = True
    
    @classmethod
    def init_environment(cls):
        """Initialize environment variables and settings."""
        if cls.DISABLE_TOKENIZER_PARALLELISM:
            os.environ["TOKENIZERS_PARALLELISM"] = "false"
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate configuration settings."""
        # Check API key based on selected provider
        if cls.AI_PROVIDER == "claude":
            if not cls.ANTHROPIC_API_KEY:
                return False
        elif cls.AI_PROVIDER == "openai":
            if not cls.OPENAI_API_KEY:
                return False
        else:
            return False  # Invalid provider
        
        if cls.CHUNK_SIZE <= 0 or cls.CHUNK_OVERLAP < 0:
            return False
            
        if cls.CHUNK_OVERLAP >= cls.CHUNK_SIZE:
            return False
            
        return True


class ChatConfig:
    """Configuration for the generic chat interface."""
    
    CHROMA_DB_PATH: str = os.getenv("CHAT_CHROMA_DB_PATH", "./data/chroma_db")
    PAGE_TITLE: str = "GPT-4o RAG Chat App"
    PAGE_ICON: str = "🤖"
    
    # Advanced Settings Defaults
    DEFAULT_CHUNK_SIZE: int = 500
    DEFAULT_OVERLAP: int = 50
    DEFAULT_N_RESULTS: int = 3
    DEFAULT_TEMPERATURE: float = 0.7
    
    # Constraints
    MIN_CHUNK_SIZE: int = 200
    MAX_CHUNK_SIZE: int = 1000
    MAX_OVERLAP: int = 200
    MIN_N_RESULTS: int = 1
    MAX_N_RESULTS: int = 10
    MIN_TEMPERATURE: float = 0.0
    MAX_TEMPERATURE: float = 1.0


# Initialize configuration on import
AppConfig.init_environment()