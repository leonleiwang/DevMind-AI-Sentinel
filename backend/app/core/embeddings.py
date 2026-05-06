# backend/app/core/embeddings.py
from langchain_community.embeddings import DashScopeEmbeddings
from app.core.config import settings

def get_embeddings():
    # 使用 DashScope 原生 Embedding 封装，自动从环境变量 DASHSCOPE_API_KEY 读取密钥
    return DashScopeEmbeddings(model=settings.EMBEDDING_MODEL_NAME)