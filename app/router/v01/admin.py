"""관리자 페이지 라우터"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pathlib import Path
from app.config.paths import ADMIN_HTML_PATH

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/", response_class=HTMLResponse)
async def admin_page():
    """관리자 페이지 제공"""
    if ADMIN_HTML_PATH.exists():
        with open(ADMIN_HTML_PATH, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    raise HTTPException(status_code=404, detail="관리자 페이지를 찾을 수 없습니다.")

