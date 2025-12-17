"""건물 데이터 관리 서비스"""
from pathlib import Path
from typing import Optional, List, Dict, Any
import uuid
from app.config.paths import BUILDINGS_DATA_DIR
from app.utils.json_utils import load_json_file, save_json_file
from app.config.paths import ICONS_METADATA_FILE
def get_building_dir(building_id: str) -> Path:
    """건물 데이터 디렉토리 경로 반환"""
    return BUILDINGS_DATA_DIR / building_id

def get_floors_file(building_id: str) -> Path:
    """건물의 층 데이터 파일 경로 반환"""
    return get_building_dir(building_id) / "floors.json"

def load_building_json(building_id: str) -> Optional[Dict[str, Any]]:
    """건물 메타데이터 로드"""
    file_path = get_building_dir(building_id) / "building.json"
    return load_json_file(file_path)

def save_building_json(building_id: str, data: Dict[str, Any]):
    """건물 메타데이터 저장"""
    building_dir = get_building_dir(building_id)
    building_dir.mkdir(parents=True, exist_ok=True)
    file_path = building_dir / "building.json"
    save_json_file(file_path, data)

def load_building_floors_json(building_id: str) -> List[Dict[str, Any]]:
    """건물의 모든 층 데이터 로드"""
    floors_file = get_floors_file(building_id)
    floors = load_json_file(floors_file)
    if floors is None:
        return []
    if isinstance(floors, list):
        return floors
    return []

def save_building_floors_json(building_id: str, floors: List[Dict[str, Any]]):
    """건물의 모든 층 데이터 저장"""
    building_dir = get_building_dir(building_id)
    building_dir.mkdir(parents=True, exist_ok=True)
    floors_file = get_floors_file(building_id)
    save_json_file(floors_file, floors)

def load_building_floor_json(building_id: str, floor_number: int) -> Optional[Dict[str, Any]]:
    """특정 건물의 특정 층 데이터 로드"""
    floors = load_building_floors_json(building_id)
    for floor in floors:
        if floor.get("floor") == floor_number:
            return floor
    return None

def save_building_floor_json(building_id: str, floor_number: int, data: Dict[str, Any]):
    """특정 건물의 특정 층 데이터 저장 또는 업데이트"""
    floors = load_building_floors_json(building_id)
    
    # 기존 층 찾기
    found = False
    for i, floor in enumerate(floors):
        if floor.get("floor") == floor_number:
            floors[i] = data
            found = True
            break
    
    # 새 층 추가
    if not found:
        floors.append(data)
    
    # 층 번호로 정렬
    floors.sort(key=lambda x: x.get("floor", 0))
    
    save_building_floors_json(building_id, floors)

def get_all_buildings() -> List[Dict[str, Any]]:
    """모든 건물 목록 조회"""
    buildings = []
    if BUILDINGS_DATA_DIR.exists():
        for building_dir in sorted(BUILDINGS_DATA_DIR.iterdir()):
            if building_dir.is_dir():
                building_data = load_building_json(building_dir.name)
                if building_data:
                    buildings.append(building_data)
    return buildings

def get_building_floors(building_id: str) -> List[Dict[str, Any]]:
    """특정 건물의 모든 층 데이터 조회"""
    floors = load_building_floors_json(building_id)
    floors.sort(key=lambda x: x.get("floor", 0))
    return floors

def generate_building_id() -> str:
    """UUID로 건물 ID 생성"""
    return str(uuid.uuid4())

def get_default_icon_types():
    """icon.json에서 모든 아이콘 타입 로드 (currentLocation 제외)"""
    icon_data = load_json_file(ICONS_METADATA_FILE)
    if icon_data and "iconTypes" in icon_data:
        icon_types = {}
        
        # iconTypes의 모든 아이콘 반환 (currentLocation 제외)
        for icon_id, icon_info in icon_data["iconTypes"].items():
            # currentLocation은 별도 필드로 관리하므로 제외
            if icon_id != "currentLocation":
                icon_path = icon_info.get("icon", "")
                # icon.json에 /content/가 없으면 추가
                if icon_path and not icon_path.startswith("/content/"):
                    icon_path = f"/content/{icon_path}"
                # floor_data에 필요한 형식으로 변환 (icon, label만)
                icon_types[icon_id] = {
                    "icon": icon_path,
                    "label": icon_info.get("label", "")
                }
        
        return icon_types
    
    # 기본값 (icon.json이 없을 경우)
    return {
        "toiletMan": {"icon": "/content/facilities/icons/toilet_man.svg", "label": "남자화장실"},
        "toiletWoman": {"icon": "/content/facilities/icons/toilet_woman.svg", "label": "여자화장실"},
        "restaurant": {"icon": "/content/facilities/icons/dish-02.svg", "label": "식당"},
        "printer": {"icon": "/content/facilities/icons/printer.svg", "label": "복사기"}
    }

def get_current_location_icon():
    """icon.json에서 currentLocation 아이콘 정보 로드"""
    icon_data = load_json_file(ICONS_METADATA_FILE)
    if icon_data and "iconTypes" in icon_data and "currentLocation" in icon_data["iconTypes"]:
        icon_info = icon_data["iconTypes"]["currentLocation"]
        icon_path = icon_info.get("icon", "/content/facilities/icons/current_location.svg")
        # icon.json에 /content/가 없으면 추가
        if not icon_path.startswith("/content/"):
            icon_path = f"/content/{icon_path}"
        return icon_path
    
    # 기본값
    return "/content/facilities/icons/current_location.svg"