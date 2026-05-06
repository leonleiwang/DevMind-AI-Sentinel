from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# 创建引擎
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URL,
    pool_size=20,             # 连接池大小，根据负载调整
    max_overflow=10,          # 溢出连接数
    pool_pre_ping=True,       # 防止连接断开
    echo=settings.ENVIRONMENT == "development"  # 开发环境打印SQL
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 所有模型的基类
Base = declarative_base()

def get_db():
    """FastAPI 依赖注入：获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()