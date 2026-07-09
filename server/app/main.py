import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.internal import router as internal_router
from app.api.routes import router as api_router
from app.config import settings

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Price Hub API",
    description="每日价格聚合服务 — 黄金、油价、生活必需品、大宗商品、汇率、股票与科技",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(internal_router)


@app.get("/health")
def health():
    return {"status": "ok"}
