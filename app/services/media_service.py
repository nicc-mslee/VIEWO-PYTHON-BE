"""미디어 콘텐츠 관리 서비스"""
from pathlib import Path
from typing import Literal, List, Dict, Any, Optional
from app.config.paths import (
    DASHBOARD_MEDIA_DIR, PR_MEDIA_DIR,
    DASHBOARD_METADATA_FILE, PR_METADATA_FILE
)
from app.utils.json_utils import load_json_file, save_json_file
from app.utils.datetime_utils import get_timestamp
from app.config.constants import ALLOWED_IMAGE_EXTENSIONS

ImageType = Literal["dashboard", "pr"]

def get_media_dir(image_type: ImageType) -> Path:
    """미디어 디렉토리 경로 반환"""
    return DASHBOARD_MEDIA_DIR if image_type == "dashboard" else PR_MEDIA_DIR

def get_metadata_file(image_type: ImageType) -> Path:
    """메타데이터 파일 경로 반환"""
    return DASHBOARD_METADATA_FILE if image_type == "dashboard" else PR_METADATA_FILE

def load_media_config(image_type: ImageType) -> Dict[str, Any]:
    """미디어 설정 파일 로드"""
    config_file = get_metadata_file(image_type)
    config = load_json_file(config_file)
    return config if config else {"images": []}

def save_media_config(image_type: ImageType, data: Dict[str, Any]):
    """미디어 설정 파일 저장"""
    config_file = get_metadata_file(image_type)
    save_json_file(config_file, data)

def scan_media_files(image_type: ImageType) -> Dict[str, Any]:
    """미디어 폴더를 스캔하여 설정 파일 동기화"""
    config = load_media_config(image_type)
    existing_files = {img["filename"] for img in config.get("images", [])}
    
    media_dir = get_media_dir(image_type)
    image_path_prefix = f"media/dashboard" if image_type == "dashboard" else "media/pr"
    
    # 폴더에서 이미지 파일 스캔
    if media_dir.exists():
        for file_path in sorted(media_dir.iterdir()):
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
        actual_files = {f.name for f in media_dir.iterdir() if f.is_file()}
        config["images"] = [img for img in config.get("images", []) if img["filename"] in actual_files]
        
        # 기존 이미지에 name 필드가 없으면 추가
        for img in config.get("images", []):
            if "name" not in img:
                img["name"] = img.get("created_at", get_timestamp())
        
        # ID 재정렬
        for i, img in enumerate(config.get("images", []), 1):
            img["id"] = i
        
        save_media_config(image_type, config)
    
    return config

def get_media_list(image_type: ImageType) -> List[Dict[str, Any]]:
    """미디어 목록 조회"""
    config = scan_media_files(image_type)
    return config.get("images", [])

def add_media_item(image_type: ImageType, filename: str, order: Optional[int] = None) -> Dict[str, Any]:
    """미디어 항목 추가"""
    config = load_media_config(image_type)
    image_path_prefix = f"media/dashboard" if image_type == "dashboard" else "media/pr"
    default_name = get_timestamp()  # 기본 이름: 날짜+시간
    
    new_image = {
        "id": len(config.get("images", [])) + 1,
        "filename": filename,
        "path": f"{image_path_prefix}/{filename}",
        "name": default_name,
        "order": order if order is not None else len(config.get("images", [])) + 1,
        "created_at": get_timestamp()
    }
    
    if "images" not in config:
        config["images"] = []
    config["images"].append(new_image)
    save_media_config(image_type, config)
    
    return new_image

def remove_media_item(image_type: ImageType, image_id: int) -> bool:
    """미디어 항목 삭제"""
    config = load_media_config(image_type)
    
    image_to_delete = None
    for img in config.get("images", []):
        if img["id"] == image_id:
            image_to_delete = img
            break
    
    if not image_to_delete:
        return False
    
    # 파일 삭제
    media_dir = get_media_dir(image_type)
    file_path = media_dir / image_to_delete["filename"]
    if file_path.exists():
        file_path.unlink()
    
    # 설정에서 제거
    config["images"] = [img for img in config.get("images", []) if img["id"] != image_id]
    
    # ID 재정렬
    for i, img in enumerate(config.get("images", []), 1):
        img["id"] = i
    
    save_media_config(image_type, config)
    return True

def update_media_order(image_type: ImageType, image_id: int, order: int) -> bool:
    """미디어 순서 업데이트"""
    config = load_media_config(image_type)
    
    for img in config.get("images", []):
        if img["id"] == image_id:
            img["order"] = order
            save_media_config(image_type, config)
            return True
    
    return False

