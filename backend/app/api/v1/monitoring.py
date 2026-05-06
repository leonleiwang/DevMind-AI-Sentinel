# backend/app/api/v1/monitoring.py
import random
import time
from fastapi import APIRouter, Depends
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/metrics")
async def get_metrics(current_user=Depends(get_current_user)):
    """返回模拟的实时监控指标"""
    t = int(time.time())
    return {
        "cpu": {
            "labels": ["订单服务", "用户服务", "网关"],
            "values": [round(random.uniform(20, 80), 1) for _ in range(3)]
        },
        "memory": {
            "labels": ["订单服务", "用户服务", "网关"],
            "values": [round(random.uniform(40, 90), 1) for _ in range(3)]
        },
        "latency": {
            "timestamps": [t - i*60 for i in range(10)][::-1],  # 最近10分钟
            "values": [round(random.uniform(0.1, 2.5), 2) for _ in range(10)]
        }
    }