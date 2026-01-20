"""FastAPI 애플리케이션 엔트리포인트"""
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import logging

from app.config.settings import APP_CONFIG, SERVER_CONFIG
from app.config.paths import CONTENT_DIR, ensure_directories
from app.router.v01.router import api_router
from app.router.v01.admin import router as admin_router
from app.router.v01.sse import set_app_instance
from app.services.client_registry import client_registry
from app.middleware.cors import setup_cors

# 디렉토리 생성
ensure_directories()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # 로깅 설정 (JSON 파일에서 로드한 설정 사용)
    log_level = SERVER_CONFIG.get("log_level", "info").upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    print("Viewo service is started.")
    logging.info("Viewo service is started.")
    app.state.is_shutting_down = False
    
    # SSE 라우터에 app 인스턴스 설정
    set_app_instance(app)
    
    yield
    
    app.state.is_shutting_down = True
    logging.info("Viewo service is stopped.")
    print("Viewo service is stopped.")

app = FastAPI(**APP_CONFIG, lifespan=lifespan)

# CORS 설정
setup_cors(app)

# 라우터 등록
app.include_router(api_router)
app.include_router(admin_router)

# 나머지 라우터 등록
from app.router.v01 import buildings, floors, media, icons, floor_plan

app.include_router(buildings.router)
app.include_router(floors.router)
app.include_router(media.router)
app.include_router(icons.router)
app.include_router(floor_plan.router)

# 정적 파일 서빙
DEPARTMENTS_DIR = CONTENT_DIR / "departments"
FACILITIES_DIR = CONTENT_DIR / "facilities"
MEDIA_DIR = CONTENT_DIR / "media"
STATIC_DIR = CONTENT_DIR.parent / "static"

app.mount("/content/departments", StaticFiles(directory=str(DEPARTMENTS_DIR)), name="departments")
app.mount("/content/facilities", StaticFiles(directory=str(FACILITIES_DIR)), name="facilities")
app.mount("/content/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# # Admin SPA Handling
# @app.get("/admin/{full_path:path}")
# async def serve_admin(full_path: str):
#     """Admin SPA Serving"""
#     # 1. Try to serve static file if explicitly requested (e.g. /admin/css/style.css)
#     # We map /admin/* to be/static/*
#     target_file = STATIC_DIR / full_path
#     if full_path and target_file.exists() and target_file.is_file():
#         return FileResponse(target_file)
    
#     # 2. Fallback to index.html for client-side routing
#     return FileResponse(STATIC_DIR / "index.html")

@app.get("/")
async def root():
    """API 상태 확인"""
    return {
        "message": "Viewo API 서버가 실행 중입니다.",
        "version": "1.0.0",
        "docs": "/docs",
        "admin": "/admin",
        "connectedClients": client_registry.get_client_count(),
        "dataVersion": client_registry.version
    }

# # 하위 호환성을 위한 기존 API 엔드포인트 (deprecated)
# @app.get("/api/dummy-table")
# async def get_dummy_table_legacy():
#     """[Deprecated] dummy_table.json 데이터 반환 - /api/v1/data/dummy-table 사용 권장"""
#     # 새로운 구조에서는 빈 데이터 반환
#     return {"code": 200, "data": {}}

# @app.get("/api/floor-info")
# async def get_floor_info_legacy():
#     """층 정보 반환 - 모든 건물의 층 데이터 반환 (하위 호환성)"""
#     from app.services.building_service import get_all_buildings, get_building_floors
    
#     try:
#         all_floors = []
#         buildings = get_all_buildings()
        
#         for building in buildings:
#             building_id = building.get("id")
#             if building_id:
#                 floors = get_building_floors(building_id)
#                 all_floors.extend(floors)
        
#         # 층 번호로 정렬
#         all_floors.sort(key=lambda x: x.get("floor", 0))
        
#         return {"code": 200, "data": all_floors}
#     except Exception as e:
#         return {"code": 500, "data": [], "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    
    # JSON 파일에서 서버 설정 로드
    host = SERVER_CONFIG.get("host", "0.0.0.0")
    port = SERVER_CONFIG.get("port", 8000)
    log_level = SERVER_CONFIG.get("log_level", "info")
    
    uvicorn.run(
        app, 
        host=host, 
        port=port, 
        log_level=log_level,
        lifespan="on"
    )
