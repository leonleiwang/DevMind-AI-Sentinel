from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import engine, Base
from app.api.v1.router import api_router  # 稍后你会创建它

# 创建所有数据库表（简单项目可以这样；生产环境用 Alembic 迁移）
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    # allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",   # 增加这一行，防止浏览器使用127.0.0.1访问
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "DevMind AI Sentinel is running", "version": settings.VERSION}

# 暂时注释掉路由导入，等创建 api_router 后再取消