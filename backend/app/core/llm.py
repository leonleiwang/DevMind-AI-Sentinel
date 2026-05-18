# backend/app/core/llm.py
from langchain_openai import ChatOpenAI
import httpx

from app.core.config import settings


def get_llm():
    """
    返回一个基于 Qwen 兼容接口的 ChatOpenAI 实例。
    """
    return ChatOpenAI(
        model=settings.OPENAI_MODEL_NAME,
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL,
        temperature=0,
        verbose=True,
        http_client=httpx.Client(trust_env=False, timeout=60),
        http_async_client=httpx.AsyncClient(trust_env=False, timeout=60),
    )
