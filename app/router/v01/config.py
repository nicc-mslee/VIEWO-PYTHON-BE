"""설정 라우터"""
from fastapi import APIRouter, HTTPException
from app.services.theme_service import load_themes, save_themes
from app.services.client_registry import client_registry

router = APIRouter(prefix="/config", tags=["Configuration"])

@router.get("/themes")
async def get_themes():
    """모든 테마 설정을 반환합니다."""
    try:
        themes = load_themes()
        return {"code": 200, "data": themes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/themes/{theme_id}")
async def set_theme(theme_id: str):
    """현재 테마를 변경합니다."""
    try:
        themes = load_themes()
        
        if theme_id not in themes.get("themes", {}):
            return {"code": 404, "message": f"테마 '{theme_id}'를 찾을 수 없습니다."}
        
        themes["currentTheme"] = theme_id
        save_themes(themes)
        
        # SSE 브로드캐스트
        await client_registry.broadcast("theme", {
            "action": "change",
            "payload": {
                "themeId": theme_id,
                "colors": themes["themes"][theme_id].get("colors", {})
            }
        })
        
        return {"code": 200, "message": f"테마가 '{theme_id}'로 변경되었습니다.", "data": themes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

