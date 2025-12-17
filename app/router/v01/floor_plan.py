"""청사도 관리 라우터 (하위 호환성)"""
# TODO: 기존 main.py의 floor_plan_router 코드를 여기로 이동
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/floor-plan", tags=["Floor Plan Management (Legacy)"])

