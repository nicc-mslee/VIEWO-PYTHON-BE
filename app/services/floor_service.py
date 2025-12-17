"""층 데이터 관리 서비스"""
from pathlib import Path
from typing import Optional, List, Dict, Any
from app.config.paths import BUILDINGS_DATA_DIR
from app.utils.json_utils import load_json_file, save_json_file

def get_building_dir(building_id: str) -> Path:
    """건물 데이터 디렉토리 경로 반환"""
    return BUILDINGS_DATA_DIR / building_id

def get_floors_file(building_id: str) -> Path:
    """건물의 층 데이터 파일 경로 반환"""
    return get_building_dir(building_id) / "floors.json"

def load_floors_json(building_id: str) -> List[Dict[str, Any]]:
    """건물의 모든 층 데이터 로드"""
    floors_file = get_floors_file(building_id)
    floors = load_json_file(floors_file)
    if floors is None:
        return []
    if isinstance(floors, list):
        return floors
    return []

def save_floors_json(building_id: str, floors: List[Dict[str, Any]]):
    """건물의 모든 층 데이터 저장"""
    building_dir = get_building_dir(building_id)
    building_dir.mkdir(parents=True, exist_ok=True)
    floors_file = get_floors_file(building_id)
    save_json_file(floors_file, floors)

def load_floor_json(building_id: str, floor_number: int) -> Optional[Dict[str, Any]]:
    """특정 건물의 특정 층 데이터 로드"""
    floors = load_floors_json(building_id)
    for floor in floors:
        if floor.get("floor") == floor_number:
            return floor
    return None

def save_floor_json(building_id: str, floor_number: int, floor_data: Dict[str, Any]):
    """특정 건물의 특정 층 데이터 저장 또는 업데이트"""
    floors = load_floors_json(building_id)
    
    # 기존 층 찾기
    found = False
    for i, floor in enumerate(floors):
        if floor.get("floor") == floor_number:
            floors[i] = floor_data
            found = True
            break
    
    # 새 층 추가
    if not found:
        floors.append(floor_data)
    
    # 층 번호로 정렬
    floors.sort(key=lambda x: x.get("floor", 0))
    
    save_floors_json(building_id, floors)

def get_floors(building_id: str) -> List[Dict[str, Any]]:
    """특정 건물의 모든 층 데이터 조회"""
    floors = load_floors_json(building_id)
    floors.sort(key=lambda x: x.get("floor", 0))
    return floors

def delete_floor(building_id: str, floor_number: int) -> bool:
    """특정 건물의 특정 층 삭제"""
    floors = load_floors_json(building_id)
    original_count = len(floors)
    
    floors = [floor for floor in floors if floor.get("floor") != floor_number]
    
    if len(floors) < original_count:
        save_floors_json(building_id, floors)
        return True
    return False

