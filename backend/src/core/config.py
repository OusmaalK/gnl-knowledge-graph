# backend/src/core/config.py

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional

class Settings(BaseSettings):
    """
    Configuration de l'application
    """
    
    # Environnement
    ENV: str = Field("dev", env="ENV")
    DEBUG: bool = Field(True, env="DEBUG")
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    
    # Neo4j
    NEO4J_URI=neo4j://6f8b0c72.databases.neo4j.io:7687
    NEO4J_USER: str = Field("neo4j", env="NEO4J_USER")
    NEO4J_PASSWORD: str = Field("", env="NEO4J_PASSWORD")
    
    # Redis
    REDIS_HOST: str = Field("localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(6379, env="REDIS_PORT")
    REDIS_PASSWORD: Optional[str] = Field(None, env="REDIS_PASSWORD")
    
    # Qdrant
    QDRANT_HOST: str = Field("localhost", env="QDRANT_HOST")
    QDRANT_PORT: int = Field(6333, env="QDRANT_PORT")
    QDRANT_API_KEY: Optional[str] = Field(None, env="QDRANT_API_KEY")
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = Field("localhost:9092", env="KAFKA_BOOTSTRAP_SERVERS")
    KAFKA_GROUP_ID: str = Field("gnl-group", env="KAFKA_GROUP_ID")
    
    # API
    API_HOST: str = Field("0.0.0.0", env="API_HOST")
    API_PORT: int = Field(8000, env="API_PORT")
    API_SECRET_KEY: str = Field("change_me", env="API_SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, env="API_ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        ["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
        env="CORS_ORIGINS"
    )
    
    # JWT
    JWT_SECRET: str = Field("change_me", env="JWT_SECRET")
    
    # ============================================================
    # ✅ AJOUTER CES LIGNES POUR LE LLM
    # ============================================================
    LLM_PROVIDER: str = Field("openai", env="LLM_PROVIDER")  # openai, gemini, ollama
    LLM_MODEL: str = Field("gpt-3.5-turbo", env="LLM_MODEL")
    LLM_API_KEY: str = Field("", env="LLM_API_KEY")
    LLM_API_URL: str = Field("http://localhost:11434", env="LLM_API_URL")
    LLM_EMBEDDING_MODEL: str = Field("BGE-M3", env="LLM_EMBEDDING_MODEL")
    
    # Storage
    S3_ENDPOINT: str = Field("localhost:9000", env="S3_ENDPOINT")
    S3_ACCESS_KEY: str = Field("minioadmin", env="S3_ACCESS_KEY")
    S3_SECRET_KEY: str = Field("minioadmin", env="S3_SECRET_KEY")
    S3_BUCKET_RAW: str = Field("gnl-raw", env="S3_BUCKET_RAW")
    S3_BUCKET_PROCESSED: str = Field("gnl-processed", env="S3_BUCKET_PROCESSED")
    
    # Security
    ENCRYPTION_KEY: str = Field("change_me", env="ENCRYPTION_KEY")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # ✅ AJOUTER CETTE LIGNE pour ignorer les champs supplémentaires

# Instance unique
settings = Settings()
