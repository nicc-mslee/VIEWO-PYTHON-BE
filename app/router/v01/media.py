"""콘텐츠 이미지 관리 라우터 (대시보드 및 홍보 이미지 통합)"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Body
from pathlib import Path
import os
import shutil
from typing import Literal
from app.config.paths import DASHBOARD_MEDIA_DIR, PR_MEDIA_DIR, DASHBOARD_METADATA_FILE, PR_METADATA_FILE
from app.utils.json_utils import load_json_file, save_json_file
from app.utils.datetime_utils import get_timestamp, get_timestamp_filename
from app.services.client_registry import client_registry
from app.config.constants import ALLOWED_IMAGE_EXTENSIONS

router = APIRouter(prefix="/api/v1/media", tags=["Media"])

ImageType = Literal["dashboard", "pr"]

def get_image_config(image_type: ImageType):
    """이미지 설정 파일 로드"""
    config_file = DASHBOARD_METADATA_FILE if image_type == "dashboard" else PR_METADATA_FILE
    config = load_json_file(config_file)
    return config if config else {"images": []}

def save_image_config(image_type: ImageType, data: dict):
    """이미지 설정 파일 저장"""
    config_file = DASHBOARD_METADATA_FILE if image_type == "dashboard" else PR_METADATA_FILE
    save_json_file(config_file, data)

def get_images_dir(image_type: ImageType) -> Path:
    """이미지 디렉토리 경로 반환"""
    return DASHBOARD_MEDIA_DIR if image_type == "dashboard" else PR_MEDIA_DIR

def scan_images(image_type: ImageType):
    """이미지 폴더를 스캔하여 설정 파일 동기화"""
    config = get_image_config(image_type)
    existing_files = {img["filename"] for img in config.get("images", [])}
    
    images_dir = get_images_dir(image_type)
    image_path_prefix = f"/content/media/dashboard" if image_type == "dashboard" else "/content/media/pr"
    
    # 디렉토리가 존재하지 않으면 생성
    if not images_dir.exists():
        images_dir.mkdir(parents=True, exist_ok=True)
    
    # 폴더에서 이미지 파일 스캔
    if images_dir.exists():
        for file_path in sorted(images_dir.iterdir()):
            if file_path.is_file() and file_path.suffix.lower() in ALLOWED_IMAGE_EXTENSIONS:
                if file_path.name not in existing_files:
                    # 새 이미지 발견
                    default_name = get_timestamp()  # 기본 이름: 날짜+시간
                    new_image = {
                        "id": len(config.get("images", [])) + 1,
                        "filename": file_path.name,
                        "path": f"{image_path_prefix}/{file_path.name}",
                        "name": default_name,
                        "order": len(config.get("images", [])) + 1,
                        "created_at": get_timestamp()
                    }
                    if "images" not in config:
                        config["images"] = []
                    config["images"].append(new_image)
        
        # 삭제된 파일 제거
        actual_files = {f.name for f in images_dir.iterdir() if f.is_file()}
        config["images"] = [img for img in config.get("images", []) if img["filename"] in actual_files]
    
    # 기존 이미지에 name 필드가 없으면 추가
    for img in config.get("images", []):
        if "name" not in img:
            img["name"] = img.get("created_at", get_timestamp())
    
    # ID 재정렬
    for i, img in enumerate(config["images"], 1):
        img["id"] = i
    
    save_image_config(image_type, config)
    return config

@router.get("/{image_type}")
async def get_images(image_type: ImageType):
    """이미지 목록 조회"""
    config = scan_images(image_type)
    return {"code": 200, "data": config}

@router.post("/{image_type}/upload")
async def upload_image(
    image_type: ImageType,
    file: UploadFile = File(...),
    order: int = Form(default=0)
):
    """이미지 업로드"""
    try:
        file_ext = Path(file.filename).suffix.lower()

        if file_ext not in ALLOWED_IMAGE_EXTENSIONS:
            raise HTTPException(status_code=400, detail="지원하지 않는 이미지 형식입니다.")

        timestamp = get_timestamp_filename()
        prefix = "dashboard" if image_type == "dashboard" else "pr"
        new_filename = f"{prefix}_{timestamp}{file_ext}"

        images_dir = get_images_dir(image_type)
        file_path = images_dir / new_filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        config = get_image_config(image_type)
        image_path_prefix = f"/content/media/dashboard" if image_type == "dashboard" else "/content/media/pr"
        default_name = get_timestamp()  # 기본 이름: 날짜+시간
        new_image = {
            "id": len(config["images"]) + 1,
            "filename": new_filename,
            "path": f"{image_path_prefix}/{new_filename}",
            "name": default_name,
            "order": order if order > 0 else len(config["images"]) + 1,
            "created_at": get_timestamp()
        }

        config["images"].append(new_image)
        save_image_config(image_type, config)

        # SSE 브로드캐스트
        event_type = "dashboard_image" if image_type == "dashboard" else "pr_image"
        await client_registry.broadcast(event_type, {
            "action": "create",
            "payload": new_image
        })

        return {"code": 200, "message": "이미지 업로드 성공", "data": new_image}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이미지 업로드 실패: {str(e)}")

@router.delete("/{image_type}/{image_id}")
async def delete_image(image_type: ImageType, image_id: int):
    """이미지 삭제"""
    try:
        config = get_image_config(image_type)

        image_to_delete = None
        for img in config["images"]:
            if img["id"] == image_id:
                image_to_delete = img
                break

        if not image_to_delete:
            raise HTTPException(status_code=404, detail="이미지를 찾을 수 없습니다.")

        images_dir = get_images_dir(image_type)
        file_path = images_dir / image_to_delete["filename"]
        if file_path.exists():
            os.remove(file_path)

        config["images"] = [img for img in config["images"] if img["id"] != image_id]
        
        # ID 재정렬
        for i, img in enumerate(config["images"], 1):
            img["id"] = i
        
        save_image_config(image_type, config)

        # SSE 브로드캐스트
        event_type = "dashboard_image" if image_type == "dashboard" else "pr_image"
        await client_registry.broadcast(event_type, {
            "action": "delete",
            "payload": {"id": image_id}
        })

        return {"code": 200, "message": "이미지 삭제 성공"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이미지 삭제 실패: {str(e)}")

@router.put("/{image_type}/{image_id}/order")
async def update_image_order(
    image_type: ImageType, 
    image_id: int, 
    order: int = Body(..., embed=True)
):
    """이미지 순서 변경"""
    config = get_image_config(image_type)

    for img in config["images"]:
        if img["id"] == image_id:
            img["order"] = order
            save_image_config(image_type, config)
            
            # SSE 브로드캐스트
            event_type = "dashboard_image" if image_type == "dashboard" else "pr_image"
            await client_registry.broadcast(event_type, {
                "action": "update",
                "payload": {"id": image_id, "order": order}
            })
            
            return {"code": 200, "message": "순서 변경 성공"}

    raise HTTPException(status_code=404, detail="이미지를 찾을 수 없습니다.")

@router.put("/{image_type}/{image_id}/name")
async def update_image_name(
    image_type: ImageType,
    image_id: int,
    name: str = Body(..., embed=True)
):
    """이미지 이름 변경"""
    config = get_image_config(image_type)

    for img in config["images"]:
        if img["id"] == image_id:
            img["name"] = name
            save_image_config(image_type, config)
            
            # SSE 브로드캐스트
            event_type = "dashboard_image" if image_type == "dashboard" else "pr_image"
            await client_registry.broadcast(event_type, {
                "action": "update",
                "payload": {"id": image_id, "name": name}
            })
            
            return {"code": 200, "message": "이름 변경 성공", "data": img}

    raise HTTPException(status_code=404, detail="이미지를 찾을 수 없습니다.")

