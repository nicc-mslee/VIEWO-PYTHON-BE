"""메인 라우터 (모든 라우터 통합)"""
from fastapi import APIRouter
from . import sse, clients, sync, auth, config, data, department

api_router = APIRouter(prefix="/api/v1")

# 라우터 등록
api_router.include_router(sse.sse_router)
api_router.include_router(clients.router)
api_router.include_router(sync.router)
api_router.include_router(auth.router)
api_router.include_router(config.router)
api_router.include_router(data.router)
api_router.include_router(department.router)

