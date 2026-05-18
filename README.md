# DevMind AI Sentinel – 基于多智能体协作的智能运维平台 | AI-powered Operations and Maintenance Platform Based on Multi-Agent Collaboration

> **一句话概述**：面向云原生微服务环境的智能 Agent 运维助手，通过自然语言交互、多 Agent 协作与 MCP 工具调用，辅助完成故障分析、指标查询、日志定位与运维排查流程。

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


## 🎯 项目背景与设计思路 Why This Project

传统云原生与微服务环境中，故障定位往往依赖人工排查日志、监控指标、告警信息与工单系统，排查路径长、系统复杂度高，尤其在多服务依赖场景下容易出现定位效率低与经验依赖严重的问题。

随着 LLM 与 AI Agent 的发展，自然语言交互与工具调用能力开始具备处理复杂运维任务的潜力。相比传统告警平台，AI Agent 能够结合监控指标、日志、告警与知识库，对故障进行辅助分析、推理与协同排查。

基于这一思考，DevMind AI Sentinel 尝试构建一个面向云原生微服务环境的多智能体智能运维平台，通过自然语言交互、多 Agent 协作与 MCP 工具调用，辅助完成故障分析、指标查询、日志定位与问题排查流程。

项目不仅关注故障分析能力，也探索了 Agent workflow、可观测性、工具治理与多 Agent 协作在复杂运维场景中的工程化实践路径，以验证 AI Application 在智能运维中的可行性与落地价值。

最后，如果要问这是不是想替代LangSmith / Langfuse，答：“不是的，我不是在替代 LangSmith，我是在验证 AI Agent 如何参与真实运维流程。” 实际上在这个项目的设想中，DevMind AI 负责业务运维 Agent 层，而 LangSmith / Langfuse 这类工具负责 tracing、evaluation 和 observability，两者结合，而不是互相替代。


## 🧠 核心能力 Core Competencies

- **多 Agent 智能运维协作**：通过 Supervisor Agent 统一调度 Fault Diagnosis、Code Review、DocQA 等 Worker Agent，实现故障排查、代码审查与知识问答协同执行，支持复杂运维任务分解与执行。

- **自然语言驱动运维交互**：支持通过自然语言描述问题，由系统自动完成指标查询、日志分析、告警解释与问题定位，降低复杂系统排查门槛。

- **Incident Timeline / Root Cause Analysis**：新增事故时间线与根因分析 Agent，模拟聚合 CI/CD、Prometheus、数据库日志与事件管理记录，输出面向 SRE 的 RCA 结论、证据链与修复建议。

- **RAG 运维知识增强**：基于 Confluence 文档与运维知识库构建语义检索能力，通过向量检索增强部署 SOP、故障排查流程与技术方案问答准确性。

- **MCP 工具调用与系统集成**：通过 MCP 协议统一接入 Prometheus、Jira、GitLab、Confluence 等系统，实现指标查询、工单联动与工具调用标准化。

- **模糊输入澄清机制**：在 Supervisor / Fault Agent Prompt 中加入 0.7 置信度阈值的工程化规则，低把握时优先反问服务名、时间范围或告警对象，避免 Agent 基于模糊输入过度猜测。

- **实时可观测性与运维大盘**：通过 SSE 流式输出 Agent 执行过程，并结合 Dashboard 实时展示 CPU、内存、延迟与事件状态，增强系统透明度与可调试性。


---

## 🏗️ 系统设计图 Architecture

![System Architecture](docs/architecture.png)

---

## 🏗️ 技术架构 Technical Architecture

```
┌─────────────┐     ┌─────────────┐     ┌───────────────────────┐
│   Vue3      │     │  FastAPI    │     │     Agent 核心层       │
│   前端      │◄───►│   后端      │◄───►│ ├ Supervisor          │
│ (SSE 流式)  │     │ (JWT 鉴权)  │     │ ├ FaultDiagnosis      │
└─────────────┘     └─────────────┘     │ ├ IncidentAnalysis    │
                                        │ ├ CodeReview          │
                                        │ └ DocQA (RAG)         │
                                        └────────┬──────────────┘
                                                 │ MCP 协议
                                  ┌──────────────▼──────────────┐
                                  │        MCP 管理器            │
                                  │ ├ Prometheus Server          │
                                  │ ├ Jira Server                │
                                  │ ├ GitLab Server              │
                                  │ ├ Confluence Server          │
                                  │ └ Incident Server            │
                                  └──────────────────────────────┘
```

- **前端**：Vue3 + TypeScript + Pinia + Element Plus + ECharts
- **后端**：FastAPI + SQLAlchemy + SQLite/MySQL + Redis
- **AI 引擎**：LangChain + LangGraph + 通义千问 (Qwen) + DashScope Embeddings
- **工具协议**：MCP (Model Context Protocol)，所有外部系统统一封装为 MCP Server
- **向量检索**：Chroma 向量数据库 +  DashScopeEmbeddings 适配实现 RAG 语义搜索，极大提升了文档问答的专业度


## 📂 项目结构 Project Structure

```
DevMind AI Sentinel/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── agent/           # Supervisor / Fault / Incident / CodeReview / DocQA 智能体
│   │   ├── mcp/             # MCP 管理器及工具服务器
│   │   ├── api/             # 路由接口
│   │   ├── core/            # 配置、安全、LLM 工厂、Embedding 工厂
│   │   ├── models/          # 数据库模型
│   │   ├── schemas/         # Pydantic 请求/响应模型
│   │   └── rag/             # 向量存储与检索 (Chroma)
│   ├── main.py
│   ├── Dockerfile
│   ├── .env.example
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
├── Makefile                 # 常用开发命令
├── .dockerignore            # Docker 构建忽略规则
├── .env.example             # Docker Compose 环境变量示例
└── README.md
```


## 🚀 快速开始 Quick Start

### 1. 环境准备 Environmental preparation

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (可选)
- 通义千问 API Key (https://dashscope.aliyun.com)

### 2. 本地开发 Local development

**后端**
```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # 填写 OPENAI_API_KEY 和 DASHSCOPE_API_KEY
uvicorn main:app --reload
```
浏览器访问 http://127.0.0.1:8000/docs

**前端**
```bash
cd frontend
npm install
npm run dev
```
浏览器访问 http://127.0.0.1:5173/

### 3. 一键部署 Docker

```bash
cp .env.example .env        # Docker Compose 会读取根目录 .env
docker-compose up -d --build
```
访问 http://127.0.0.1:5173/


## 🧪 效果展示 Pages Demonstration

| 功能                           | 截图      |
|--------------------------------|-----------|
| 故障排查 Agent 多工具联动      | ![故障排查](docs/screenshots/fault_diagnosis.mp4) |
| Incident RCA 事故时间线分析    | ![事件时间线+根本原因分析](docs/screenshots/Incident_Timeline_and_Root_Cause_Analysis.mp4) |
| 代码审查 Agent 自动评论        | ![代码审查](docs/screenshots/code_review.mp4) |
| 文档问答 Agent 语义检索        | ![文档问答](docs/screenshots/doc_qa.mp4) |
| 监控大盘实时刷新               | ![实时监控](docs/screenshots/dashboard.mp4) |


## ✅ 当前完成度 Current Completion Status

| 模块 | 状态 |
|------|------|
| JWT 登录鉴权 | 已实现 |
| 多 Agent 架构 | 已实现 Supervisor + Worker Agent |
| Fault Diagnosis Agent | 已实现 |
| Incident Analysis Agent（Timeline / RCA） | 已实现 |
| Code Review Agent | 已实现 |
| DocQA Agent（RAG） | 已实现 |
| MCP 工具协议 | 已实现 |
| Prometheus 指标查询 | 已实现 |
| Incident Timeline 模拟工具 | 已实现 |
| Jira 工单联动 | 已实现 |
| GitLab MR 分析 | 已实现 |
| Confluence 文档检索 | 已实现 |
| Chroma 向量检索 | 已实现 |
| SSE 流式输出 | 已实现 |
| Dashboard 运维大盘 | 已实现 |
| Docker Compose 部署 | 已实现 |
| Makefile / .dockerignore / .env.example | 已补齐 |
| DashScope Embeddings 适配 | 已实现 |
| 多模型 API 接入 | 已实现基础封装 |


## 🎯 项目亮点 Project Highlights

- 前沿技术栈：LangChain、LangGraph 多 Agent 编排、MCP 协议统一工具接口、RAG 向量检索、SSE 流式输出。
- 工业级工程能力：前后端分离、JWT 认证、Docker 部署、异步任务、打字机流式体验。
- 真实业务场景：覆盖 SRE 故障排查、Incident RCA、DevOps 代码审查、文档助手、监控大盘，完整运维闭环。
- 面向生产落地的问题处理：加入模糊输入澄清与 0.7 置信度阈值策略，体现 Agent 鲁棒性设计。
- 模型适配：自定义 DashScopeEmbeddings 适配国产大模型，体现实际落地的工程化思维。


## 🧩 挑战与解决方案 Challenges and Solutions

### 1. 多系统运维工具的统一接入

**Challenge**

智能运维场景往往涉及 Prometheus、Jira、GitLab、Confluence 等多个系统，接口风格与数据结构差异较大，直接耦合会导致 Agent 难以扩展与维护。

**Solution**

通过 MCP（Model Context Protocol）统一封装外部系统，将监控、工单、代码仓库与知识库能力抽象为标准化 MCP Server，实现工具发现、调用与扩展解耦。

---

### 2. 复杂运维任务的多 Agent 协作

**Challenge**

故障排查、代码审查与知识问答属于不同任务域，单 Agent 难以稳定处理复杂运维场景。

**Solution**

采用 Supervisor + Worker Agent 架构，将 Fault Diagnosis、Code Review 与 DocQA 拆分为独立 Agent，由 Supervisor Agent 负责任务路由与调度，提升系统可扩展性与职责隔离能力。

---

### 3. 运维知识库的检索准确性

**Challenge**

传统关键词搜索难以准确匹配部署 SOP、故障经验与技术文档，容易出现召回不稳定与上下文缺失问题。

**Solution**

基于 DashScope Embeddings 与 Chroma 构建向量检索层，引入 RAG 检索增强机制，通过语义搜索提升运维知识问答准确性。

---

### 4. Agent 执行过程缺乏可观测性

**Challenge**

Agent workflow 在复杂工具调用场景下容易出现“黑盒化”，不利于调试与问题定位。

**Solution**

通过 SSE 流式输出 Agent 执行过程，并结合 Dashboard 展示指标、事件流与任务状态，增强系统透明度与可调试性。

---

### 5. 模糊自然语言输入容易导致 Agent 误判

**Challenge**

真实运维对话中，用户常会说“系统有点慢”“帮我看一下”这类上下文不足的问题。单纯语义检索只能找到相似文档，不能可靠判断用户真正想排查哪个服务、哪个时间段或哪类告警。

**Solution**

在 Supervisor 与故障排查 Prompt 中加入轻量级不确定性处理：当意图把握低于 0.7 或缺少关键上下文时，Agent 优先向用户反问服务名、时间范围和告警对象；当输入模糊但明显属于运维故障时，路由到 Fault Agent 由其继续澄清。该方案不引入复杂置信度模型，但能体现查询改写、意图澄清和多轮对话的工程意识。


## 🚀 开发时间线 Development Timeline

### 2025
开始从传统软件开发逐步转向 AI Agent 与 LLM Application 方向，调研多 Agent、RAG、Tool Calling 与智能运维场景的结合方式。

### Q3 2025
完成多 Agent 运维系统方向探索与技术验证，持续进行 LangChain、LangGraph、MCP、RAG 与 SSE 流式交互等技术实践。

### Q4 2025
完成 DevMind AI Sentinel 第一版原型，实现 Fault Diagnosis、Code Review、DocQA 与 Dashboard 等核心功能。

### Q4 2025
持续优化多 Agent 协作、MCP 工具抽象、RAG 检索与系统可观测性，逐步形成 AI-native 运维平台的工程化架构雏形。

### Q2 2026
新增 Incident Timeline / RCA 模块，并加入模糊输入澄清策略，前端大优化，提升工程完整度。


## 🔭 已知权衡与未来规划 Known Trade-offs and Future Planning

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
| Kubernetes Agent | 当前未接入真实 K8s 集群，只使用模拟 Prometheus / Incident 数据 | 若有真实集群与权限边界，再接入 Kubernetes API；当前阶段避免 Scope 爆炸 |
| 置信度评估 | 使用 Prompt 自评与 0.7 阈值做澄清决策，未做复杂概率校准 | 后续可引入自一致性、多样化改写或评测集校准 |

### 未来功能规划

- **多语言支持**：前端国际化，支持中英文切换
- **多租户隔离**：按团队/项目隔离 Agent 会话与监控数据
- **告警规则引擎**：用户可自定义 Prometheus 告警阈值与通知策略
- **Alert Noise Reduction**：对同源告警、级联告警和重复告警做聚类降噪，减少值班干扰
- **Agent 编排拖拽界面**：提供低代码画布，灵活组合多个 Agent 的工作流
- **CI/CD 集成**：将代码审查 Agent 接入 GitHub/GitLab CI，自动评论 MR
- **日志与链路追踪**：集成 ELK / Jaeger，增强故障诊断的上下文信息
- **移动端适配**：提供移动端 PWA 版本，方便运维人员随身处理告警

我会持续迭代，欢迎 Star ⭐ & Watch 关注项目进展！


## 👤 作者 Author

**王磊（Leon Wang）**<br>
"AI Agent & LLM Application Engineer focused on Agentic and multi-agent Systems, RAG, modern AI Infrastructure, Machine Learning, AI-native products with LLMs and Fullstack AI Products."<br>
<br>
求职 - AI Agent 应用开发 | LLM 大模型应用开发 | 全栈工程师 | AI 全栈产品开发<br>
AI Agent Engineer | LLM Application Engineer | Fullstack Developer | Fullstack AI Products<br>
<br>
📍 Based in Nanjing / Shanghai / Hangzhou / Suzhou, China<br>
📍 Open to opportunities across Sydney / Melbourne / Brisbane / Adelaide, Australia & Auckland, New Zealand (Work visa holder)<br>
<br>

Email: leileonwang@163.com / leonleiwang@outlook.com<br>
GitHub: https://github.com/leonleiwang


## 📄 许可证 License

MIT
