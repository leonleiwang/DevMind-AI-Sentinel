# backend/app/rag/vectorstore.py
import os, shutil
from langchain_chroma import Chroma
from langchain_core.documents import Document
from app.core.embeddings import get_embeddings

MOCK_DOCUMENTS = [
    {
        "id": "doc-001",
        "title": "订单服务部署手册",
        "content": "订单服务部署在 Kubernetes 集群，使用 Helm Chart 管理。数据库连接池大小为 50，超时时间 30 秒。主要参数包括 database.poolSize: 50, database.timeout: 30s, service.replicas: 3, log.level: info"
    },
    {
        "id": "doc-002",
        "title": "常见故障处理 SOP",
        "content": "当订单服务延迟超过 2 秒时，首先检查数据库连接池是否耗尽，然后检查 Redis 缓存命中率。"
    },
    {
        "id": "doc-003",
        "title": "JWT 认证中间件技术方案",
        "content": "使用 HS256 算法，令牌过期时间 7 天，公钥存储在 ConfigMap 中。"
    },
    {
        "id": "doc-004",
        "title": "订单服务 Helm 部署与维护手册",
        "content": "要升级订单服务的 Helm Chart，请执行以下步骤：1. 确保你拥有最新版的 chart（可从 GitLab 仓库 orders/helm-charts 获取）。2. 使用命令 helm repo update 更新本地 Helm 仓库缓存。3. 执行升级命令：helm upgrade order-service orders/order-service -f values-prod.yaml --version <目标版本>。4. 验证 Pod 是否正常重启并检查日志无异常。注意：升级前请务必备份当前配置和数据库状态。"
    }
]

CHROMA_PERSIST_DIR = os.path.join(os.path.dirname(__file__), "../../chroma_db")

def get_vectorstore():
    embeddings = get_embeddings()

    # 如果已有持久化数据，直接加载
    if os.path.exists(CHROMA_PERSIST_DIR) and os.listdir(CHROMA_PERSIST_DIR):
        return Chroma(
            persist_directory=CHROMA_PERSIST_DIR,
            embedding_function=embeddings,
        )

    # 否则创建并添加文档
    docs = []
    for m in MOCK_DOCUMENTS:
        docs.append(
            Document(
                page_content=f"{m['title']}\n{m['content']}",
                metadata={"id": m["id"], "title": m["title"]}
            )
        )

    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=CHROMA_PERSIST_DIR,
    )
    return vectorstore