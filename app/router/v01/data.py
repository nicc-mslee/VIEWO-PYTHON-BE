"""데이터 API 라우터"""
from fastapi import APIRouter
from app.utils.json_utils import load_json_file
from app.services.building_service import get_all_buildings, get_building_floors

router = APIRouter(prefix="/data", tags=["Data"])

@router.get("/dummy-table")
async def get_dummy_table():
    """dummy_table.json 데이터 반환 (레거시 지원 - 빈 데이터 반환)"""
    # 새로운 구조에서는 건물별로 관리하므로 빈 데이터 반환
    return {"code": 200, "data": {}}

@router.get("/floor-info")
async def get_floor_info():
    """모든 건물의 층 정보 반환 (하위 호환성)"""
    # 모든 건물의 층 데이터 수집
    all_floors = []
    buildings = get_all_buildings()
    
    for building in buildings:
        building_id = building.get("id")
        if building_id:
            floors = get_building_floors(building_id)
            all_floors.extend(floors)
    
    # 층 번호로 정렬
    all_floors.sort(key=lambda x: x.get("floor", 0))
    
    return {"code": 200, "data": all_floors}

