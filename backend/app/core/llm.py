# backend/app/core/llm.py
from langchain_openai import ChatOpenAI
from app.core.config import settings

def get_llm():
    """
    返回一个基于 Qwen 兼容接口的 ChatOpenAI 实例。
    """
    return ChatOpenAI(
        model=settings.OPENAI_MODEL_NAME,
        openai_api_key=settings.OPENAI_API_KEY,
        openai_api_base=settings.OPENAI_BASE_URL,
        temperature=0,
        verbose=True,
    )