# backend/app/core/config.py
from typing import Optional, List
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # 核心应用配置
    PROJECT_NAME: str = "DevMind AI Sentinel"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "change-me-to-a-very-long-random-string"
    ENVIRONMENT: str = "development"  # development, staging, production

    # 跨域 (CORS) 配置
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        return v

    # 数据库配置
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "password"
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: str = "3306"
    MYSQL_DATABASE: str = "devmind"

    # 可选：直接指定完整的数据库连接串（优先级最高）
    DATABASE_URL: Optional[str] = None

    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
    
    # Redis 配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # JWT 配置
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 天

    # LLM 配置
    LLM_PROVIDER: str = "openai"  # 或 "azure", "zhipuai" 等
    OPENAI_API_KEY: Optional[str] = None
    # OPENAI_MODEL_NAME: str = "gpt-4o-mini"
    # OPENAI_BASE_URL: Optional[str] = "https://api.openai.com/v1"
    OPENAI_MODEL_NAME: str = "qwen3-max"     
    OPENAI_BASE_URL: Optional[str] = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    # MCP Server 配置 (可后续扩展为动态发现)
    MCP_SERVER_CONFIGS: dict = {
        "prometheus": {
            "url": "http://localhost:9090",
            "enabled": True
        },
        "jira": {
            "url": "https://your-domain.atlassian.net",
            "email": "your-jira-email@example.com",
            "api_token": "your-jira-api-token",
            "project_key": "DEVMIND",
            "enabled": True
        },
        "gitlab": {
            "url": "https://gitlab.com",
            "private_token": "your-gitlab-token",
            # "enabled": False  # 初期先关闭
            "enabled": True
        },
        "confluence": {
            "url": "https://your-domain.atlassian.net/wiki",
            "username": "your-email",
            "api_token": "your-api-token",
            # "enabled": False  # 初期先关闭
            "enabled": True
        },
        "incident": {
            "enabled": True
        }
    }

    # 向量数据库 (Milvus) 配置 - 文档问答用
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    MILVUS_COLLECTION: str = "tech_docs"

    # 使用 pydantic-settings 的环境变量加载方式
    model_config = SettingsConfigDict(
        env_file=".env",         # 从 .env 文件加载（开发时使用）
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    # ---------- Embedding 配置（用于文档问答 RAG）----------
    DASHSCOPE_API_KEY: Optional[str] = None          # ← 新增这一行
    EMBEDDING_MODEL_NAME: str = "text-embedding-v4"
    EMBEDDING_API_KEY: Optional[str] = None           # 如果你不再使用可删除
    EMBEDDING_BASE_URL: Optional[str] = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# 全局单例
settings = Settings()
