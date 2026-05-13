# DevMind AI Sentinel – 基于多智能体协作的智能运维平台 | AI-powered Operations and Maintenance Platform Based on Multi-Agent Collaboration

> **一句话概述**：面向云原生微服务环境的智能 Agent 运维助手，以自然语言交互、基于 LangChain + LangGraph 的多 Agent 协作和 MCP 标准协议，将故障定位时间从 20 分钟缩短至 3 分钟。

![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.11-blue)
![Vue](https://img.shields.io/badge/vue-3.x-green)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-orange)
![LangChain](https://img.shields.io/badge/LangChain-0.3+-blue)
![MCP](https://img.shields.io/badge/MCP-Protocol-purple)
![AI Agent](https://img.shields.io/badge/AI_Agent-Multi_Agent-blueviolet)
![RAG](https://img.shields.io/badge/RAG-vector_search-green)
![FastAPI](https://img.shields.io/badge/fastapi-0.100+-green)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red)
![Redis](https://img.shields.io/badge/redis-7-red)             
![Docker](https://img.shields.io/badge/docker-compose-2496ED?logo=docker)
![SSE](https://img.shields.io/badge/SSE-Streaming-yellowgreen)
![Chroma](https://img.shields.io/badge/Chroma-vector_db-orange)
![SQLite](https://img.shields.io/badge/SQLite-3-blue)


## 🧠 核心能力

- **故障排查 Agent**：自动查询 Prometheus 指标、告警，并与 Jira 工单联动，输出诊断结论和处理建议  
- **代码审查 Agent**：检测 MR 变更内容，识别安全漏洞、逻辑缺陷，自动发表行级评论  
- **文档问答 Agent**：基于 RAG 技术搜索 Confluence 知识库，回答部署、故障 SOP、技术方案等问题  
- **监控大盘**：实时展示 CPU、内存、请求延迟等核心指标，自动刷新  


## 👤 作者

**王磊（Leon Wang）**<br>
"AI Agent & LLM Application Engineer focused on Agentic and multi-agent Systems, RAG, modern AI Infrastructure, Machine Learning, AI-native products with LLMs and Fullstack AI Products."<br>
<br>
求职 - AI Agent 应用开发 | LLM 大模型开发 | AI Infra | 全栈工程师<br>
AI Agent Engineer | LLM Application Engineer | AI Infrastructure Engineer | Fullstack Developer<br>
<br>
📍 Based in Nanjing / Shanghai / Hangzhou / Suzhou, China<br>
📍 Open to opportunities across Sydney / Melbourne / Brisbane / Adelaide, Australia & Auckland, New Zealand (Work visa holder)<br>
<br>
Email: leonleiwang@outlook.com<br>
GitHub: https://github.com/leonleiwang


---

## 🏗️ 系统设计图（Architecture）

![System Architecture](docs/architecture.png)

---

## 🏗️ 技术架构（文本版）

```
┌─────────────┐     ┌─────────────┐     ┌───────────────────────┐
│   Vue3      │     │  FastAPI    │     │     Agent 核心层       │
│   前端      │◄───►│   后端      │◄───►│ ├ Supervisor          │
│ (SSE 流式)  │     │ (JWT 鉴权)  │     │ ├ FaultDiagnosis      │
└─────────────┘     └─────────────┘     │ ├ CodeReview          │
                                        │ └ DocQA (RAG)         │
                                        └────────┬──────────────┘
                                                 │ MCP 协议
                                  ┌──────────────▼──────────────┐
                                  │        MCP 管理器            │
                                  │ ├ Prometheus Server          │
                                  │ ├ Jira Server                │
                                  │ ├ GitLab Server              │
                                  │ └ Confluence Server          │
                                  └──────────────────────────────┘
```

## ⚙️ 技术栈

- **前端**：Vue3 + TypeScript + Pinia + Element Plus + ECharts
- **后端**：FastAPI + SQLAlchemy + SQLite/MySQL + Redis
- **AI 引擎**：LangChain + LangGraph + 通义千问 (Qwen) + DashScope Embeddings
- **工具协议**：MCP (Model Context Protocol)，所有外部系统统一封装为 MCP Server
- **向量检索**：Chroma 向量数据库 +  DashScopeEmbeddings 适配实现 RAG 语义搜索，极大提升了文档问答的专业度

## 📂 项目结构

```
DevMind AI Sentinel/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── agent/           # Supervisor / Fault / CodeReview / DocQA 智能体
│   │   ├── mcp/             # MCP 管理器及工具服务器
│   │   ├── api/             # 路由接口
│   │   ├── core/            # 配置、安全、LLM 工厂、Embedding 工厂
│   │   ├── models/          # 数据库模型
│   │   ├── schemas/         # Pydantic 请求/响应模型
│   │   └── rag/             # 向量存储与检索 (Chroma)
│   ├── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                # Vue3 前端
│   ├── src/
│   │   ├── api/             # axios 封装、SSE 流式连接
│   │   ├── components/      # 通用组件
│   │   ├── views/           # 页面
│   │   ├── router/          # 路由守卫
│   │   └── store/           # Pinia 状态管理
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml       # 一键启动
└── README.md
```

## 🚀 快速开始

### 1. 环境准备

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (可选)
- 通义千问 API Key (https://dashscope.aliyun.com)

### 2. 本地开发

**后端**
```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # 填写 OPENAI_API_KEY 和 DASHSCOPE_API_KEY
uvicorn main:app --reload
```

**前端**
```bash
cd frontend
npm install
npm run dev
```
浏览器访问 http://localhost:5173

### 3. Docker 一键部署

```bash
docker-compose up -d --build
```
访问 http://localhost:5173

## 🧪 效果展示

| 功能                           | 截图      |
|--------------------------------|-----------|
| 故障排查 Agent 多工具联动      | ![故障排查](docs/screenshots/fault_diagnosis.png) |
| 代码审查 Agent 自动评论        | ![代码审查](docs/screenshots/code_review.png) |
| 文档问答 Agent 语义检索        | ![文档问答](docs/screenshots/doc_qa.png) |
| 监控大盘实时刷新               | <img src="docs/screenshots/dashboard-1.png" width="45%" /> <img src="docs/screenshots/dashboard-2.png" width="45%" /> |

## 🎯 项目亮点

- 前沿技术栈：LangChain、LangGraph 多 Agent 编排、MCP 协议统一工具接口、RAG 向量检索、SSE 流式输出。
- 工业级工程能力：前后端分离、JWT 认证、Docker 部署、异步任务、打字机流式体验。
- 真实业务场景：覆盖 SRE 故障排查、DevOps 代码审查、文档助手、监控大盘，完整运维闭环。
- 模型适配：自定义 DashScopeEmbeddings 适配国产大模型，体现实际落地的工程化思维。

## 🔭 已知权衡与未来规划

### 架构决策与当前限制

| 设计模块 | 当前实现 | 后续计划 |
|----------|----------|----------|
| `services/` 业务逻辑层 | 未独立建层，逻辑直接写在路由或 Agent 中 | 抽取 `user_service`、`chat_service` 等，进一步解耦 |
| 异步任务队列（Celery） | 未引入，所有 Agent 调用同步完成 | 引入 Celery / Redis Queue 处理长耗时 Agent 任务 |
| 数据库迁移 (Alembic) | 使用 `Base.metadata.create_all` 自动建表 | 添加 Alembic 管理 schema 版本，支持无缝升级 |
| WebSocket 推送 | 监控大盘使用轮询，对话为 SSE 单向流 | 引入 WebSocket 实现前端实时通知与状态同步 |
| 向量数据库 | 使用 Chroma（轻量本地库）替代最初计划的 Milvus | 数据量增大后可切换至 Milvus / Qdrant 等分布式方案 |
| Agent 管理界面 (`agents.py`) | 未实现，Agent 配置硬编码 | 提供 Web UI 界面动态管理 Agent 配置与启停 |
| 代码审查差异展示 | 纯文本展示代码变更 | 集成 `diff2html` 或 Monaco Editor 实现可视化差异对比 |
| 监控图表组件 (`MonitoringChart.vue`) | 直接在页面内使用 ECharts 配置 | 封装为独立可复用组件，支持更多图表类型与主题切换 |

### 未来功能规划

- **多语言支持**：前端国际化，支持中英文切换  
- **多租户隔离**：按团队/项目隔离 Agent 会话与监控数据  
- **告警规则引擎**：用户可自定义 Prometheus 告警阈值与通知策略  
- **Agent 编排拖拽界面**：提供低代码画布，灵活组合多个 Agent 的工作流  
- **CI/CD 集成**：将代码审查 Agent 接入 GitHub/GitLab CI，自动评论 MR  
- **日志与链路追踪**：集成 ELK / Jaeger，增强故障诊断的上下文信息  
- **移动端适配**：提供移动端 PWA 版本，方便运维人员随身处理告警  

我会持续迭代，欢迎 Star ⭐ & Watch 关注项目进展！


## 📄 License

MIT

