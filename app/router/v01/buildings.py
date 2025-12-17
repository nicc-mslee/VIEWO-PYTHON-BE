"""건물 관리 라우터"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pathlib import Path
import shutil
from app.services.building_service import (
    get_all_buildings, load_building_json, save_building_json,
    get_building_floors, load_building_floor_json, save_building_floor_json,
    get_building_dir,
    generate_building_id,
    get_default_icon_types,
    get_current_location_icon
)
from app.utils.datetime_utils import get_timestamp, get_timestamp_filename
from app.utils.image_utils import get_image_size
from app.services.client_registry import client_registry
from app.config.constants import ALLOWED_IMAGE_EXTENSIONS

router = APIRouter(prefix="/api/v1/buildings", tags=["Buildings Management"])



@router.get("/")
async def get_buildings():
    """모든 건물 목록 조회"""
    try:
        buildings = get_all_buildings()
        return {"code": 200, "data": buildings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"건물 목록 조회 실패: {str(e)}")

@router.post("/")
async def create_building(building_data: dict):
    """새 건물 생성"""
    try:
        name = building_data.get("name", "새 건물")
        building_id = generate_building_id()
        
        new_building = {
            "id": building_id,
            "name": name,
            "description": building_data.get("description", ""),
            "createdAt": get_timestamp(),
            "updatedAt": get_timestamp()
        }
        
        # 건물 디렉토리 생성
        building_dir = get_building_dir(building_id)
        building_dir.mkdir(parents=True, exist_ok=True)
        
        # 빈 floors.json 초기화
        from app.services.building_service import save_building_floors_json
        save_building_floors_json(building_id, [])
        
        # 건물 메타데이터 저장
        save_building_json(building_id, new_building)
        
        # SSE 브로드캐스트
        await client_registry.broadcast("building", {
            "action": "create",
            "payload": new_building
        })
        
        return {"code": 200, "message": "건물 생성 성공", "data": new_building}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"건물 생성 실패: {str(e)}")

@router.get("/{building_id}")
async def get_building(building_id: str):
    """특정 건물 정보 조회"""
    try:
        building = load_building_json(building_id)
        if not building:
            raise HTTPException(status_code=404, detail="건물을 찾을 수 없습니다.")
        
        # 해당 건물의 층 정보도 함께 반환
        floors = get_building_floors(building_id)
        building["floors"] = floors
        
        return {"code": 200, "data": building}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"건물 정보 조회 실패: {str(e)}")

@router.put("/{building_id}")
async def update_building(building_id: str, building_data: dict):
    """건물 정보 수정"""
    try:
        existing = load_building_json(building_id)
        if not existing:
            raise HTTPException(status_code=404, detail="건물을 찾을 수 없습니다.")
        
        existing["name"] = building_data.get("name", existing["name"])
        existing["description"] = building_data.get("description", existing.get("description", ""))
        existing["updatedAt"] = get_timestamp()
        
        save_building_json(building_id, existing)
        
        # SSE 브로드캐스트
        await client_registry.broadcast("building", {
            "action": "update",
            "payload": existing
        })
        
        return {"code": 200, "message": "건물 정보 수정 성공", "data": existing}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"건물 정보 수정 실패: {str(e)}")

@router.delete("/{building_id}")
async def delete_building(building_id: str):
    """건물 삭제"""
    try:
        building_dir = get_building_dir(building_id)
        if not building_dir.exists():
            raise HTTPException(status_code=404, detail="건물을 찾을 수 없습니다.")
        
        # 건물 데이터 디렉토리 삭제 (이미지 포함)
        shutil.rmtree(building_dir)
        
        # SSE 브로드캐스트
        await client_registry.broadcast("building", {
            "action": "delete",
            "payload": {"buildingId": building_id}
        })
        
        return {"code": 200, "message": "건물 삭제 성공"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"건물 삭제 실패: {str(e)}")

@router.get("/{building_id}/floors")
async def get_building_floors_api(building_id: str):
    """특정 건물의 모든 층 조회"""
    try:
        building = load_building_json(building_id)
        if not building:
            raise HTTPException(status_code=404, detail="건물을 찾을 수 없습니다.")
        
        floors = get_building_floors(building_id)
        return {"code": 200, "data": floors}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"층 목록 조회 실패: {str(e)}")

@router.get("/{building_id}/floors/{floor_number}")
async def get_building_floor(building_id: str, floor_number: int):
    """특정 건물의 특정 층 데이터 조회"""
    try:
        floor_data = load_building_floor_json(building_id, floor_number)
        if not floor_data:
            raise HTTPException(status_code=404, detail=f"{floor_number}층 데이터를 찾을 수 없습니다.")
        return {"code": 200, "data": floor_data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"층 데이터 조회 실패: {str(e)}")

@router.post("/{building_id}/floors/upload-image")
async def upload_building_floor_image(
    building_id: str,
    file: UploadFile = File(...),
    floor_number: int = Form(...)
):
    """특정 건물의 청사도 이미지 업로드"""
    try:
        # 건물 존재 확인
        building = load_building_json(building_id)
        if not building:
            raise HTTPException(status_code=404, detail="건물을 찾을 수 없습니다.")
        
        # 파일 확장자 확인
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in ALLOWED_IMAGE_EXTENSIONS:
            raise HTTPException(status_code=400, detail="지원하지 않는 이미지 형식입니다.")
        
        # 파일명 생성
        timestamp = get_timestamp_filename()
        new_filename = f"floor_plan_{timestamp}{file_ext}"
        
        # 건물 디렉토리에 이미지 저장 (새 구조: content/facilities/buildings/{building_id}/)
        building_dir = get_building_dir(building_id)
        building_dir.mkdir(parents=True, exist_ok=True)
        file_path = building_dir / new_filename
        
        import shutil
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 이미지 크기 확인
        width, height = get_image_size(file_path)
        
        # 층별 JSON 파일 업데이트
        floor_data = load_building_floor_json(building_id, floor_number)
        # 새로운 경로 구조에 맞게 경로 설정 (/content/ 접두사 포함)
        image_path = f"/content/facilities/buildings/{building_id}/{new_filename}"
        
        if floor_data:
            floor_data["floorImage"] = image_path
            floor_data["imageSize"] = {"width": width, "height": height}
            floor_data["updatedAt"] = get_timestamp()
        else:
            # icon.json에서 기본 아이콘 타입 로드
            default_icon_types = get_default_icon_types()
            current_location_icon = get_current_location_icon()
            
            floor_data = {
                "floor": floor_number,
                "floorName": f"{floor_number}층",
                "buildingId": building_id,
                "floorImage": image_path,
                "imageSize": {"width": width, "height": height},
                "createdAt": get_timestamp(),
                "updatedAt": get_timestamp(),
                "iconTypes": default_icon_types,
                "elements": [],
                "currentLocation": {
                    "enabled": False,
                    "x1": 0, "y1": 0, "x2": 50, "y2": 50,
                    "icon": current_location_icon,
                    "showLabel": True,
                    "labelText": "현위치",
                    "labelStyle": {
                        "fontSize": 11, "fontFamily": "Pretendard", "fontWeight": "bold",
                        "color": "#000000", "backgroundColor": "#FFEB3B", "borderRadius": 12
                    }
                }
            }
        
        save_building_floor_json(building_id, floor_number, floor_data)
        
        # SSE 브로드캐스트
        await client_registry.broadcast("floor_image", {
            "action": "update",
            "payload": {
                "buildingId": building_id,
                "floorNumber": floor_number,
                "imagePath": image_path,
                "imageSize": {"width": width, "height": height}
            }
        })
        
        return {
            "code": 200,
            "message": "이미지 업로드 성공",
            "data": {
                "filename": new_filename,
                "path": image_path,
                "imageSize": {"width": width, "height": height}
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이미지 업로드 실패: {str(e)}")

@router.put("/{building_id}/floors/{floor_number}")
async def update_building_floor(building_id: str, floor_number: int, floor_data: dict):
    """특정 건물의 청사도 데이터 저장"""
    try:
        # 건물 존재 확인
        building = load_building_json(building_id)
        if not building:
            raise HTTPException(status_code=404, detail="건물을 찾을 수 없습니다.")
        
        # currentLocation 아이콘을 elements에서 제거
        if "elements" in floor_data:
            floor_data["elements"] = [
                e for e in floor_data["elements"]
                if e.get("type") != "icon" or e.get("iconType") != "currentLocation"
            ]
        
        floor_data["updatedAt"] = get_timestamp()
        floor_data["floor"] = floor_number
        floor_data["buildingId"] = building_id
        
        # currentLocation 기본값 설정
        current_location_icon = get_current_location_icon()
        if "currentLocation" not in floor_data:
            floor_data["currentLocation"] = {
                "enabled": False,
                "x1": 0, "y1": 0, "x2": 50, "y2": 50,
                "icon": current_location_icon,
                "showLabel": True,
                "labelText": "현위치",
                "labelStyle": {
                    "fontSize": 11, "fontFamily": "Pretendard", "fontWeight": "bold",
                    "color": "#000000", "backgroundColor": "#FFEB3B", "borderRadius": 12
                }
            }
        elif "icon" not in floor_data["currentLocation"] or not floor_data["currentLocation"]["icon"]:
            floor_data["currentLocation"]["icon"] = current_location_icon
        
        save_building_floor_json(building_id, floor_number, floor_data)
        
        # SSE 브로드캐스트
        await client_registry.broadcast("floor", {
            "action": "update",
            "payload": {
                "buildingId": building_id,
                "floorNumber": floor_number,
                "data": floor_data
            }
        })
        
        return {"code": 200, "message": "청사도 데이터 저장 성공", "data": floor_data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 저장 실패: {str(e)}")

@router.delete("/{building_id}/floors/{floor_number}")
async def delete_building_floor(building_id: str, floor_number: int):
    """특정 건물의 특정 층 삭제"""
    try:
        floor_data = load_building_floor_json(building_id, floor_number)
        if not floor_data:
            raise HTTPException(status_code=404, detail=f"{floor_number}층을 찾을 수 없습니다.")
        
        # floors.json에서 해당 층 제거
        from app.services.building_service import load_building_floors_json, save_building_floors_json
        floors = load_building_floors_json(building_id)
        floors = [floor for floor in floors if floor.get("floor") != floor_number]
        save_building_floors_json(building_id, floors)
        
        # SSE 브로드캐스트
        await client_registry.broadcast("floor", {
            "action": "delete",
            "payload": {
                "buildingId": building_id,
                "floorNumber": floor_number
            }
        })
        
        return {"code": 200, "message": f"{floor_number}층 삭제 성공"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"층 삭제 실패: {str(e)}")

