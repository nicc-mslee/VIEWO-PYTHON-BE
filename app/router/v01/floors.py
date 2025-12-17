"""층 관리 라우터 (건물별)"""
# 이 파일은 buildings.py에 통합되어 있으므로 빈 라우터로 유지
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/floors", tags=["Floors Management"])

