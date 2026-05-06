from fastapi import APIRouter
from app.api.v1 import auth, mcp_test, conversations
from app.api.v1 import code_review
from app.api.v1 import doc_qa
from app.api.v1 import monitoring


api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(mcp_test.router, prefix="/mcp", tags=["mcp-test"])
api_router.include_router(conversations.router, prefix="/chat", tags=["chat"])
api_router.include_router(code_review.router, prefix="/code-review", tags=["code-review"])
api_router.include_router(doc_qa.router, prefix="/doc-qa", tags=["doc-qa"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])