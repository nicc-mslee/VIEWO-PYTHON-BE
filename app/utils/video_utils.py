"""영상 처리 헬퍼"""
from pathlib import Path
from typing import Optional, Tuple
import mimetypes

# 지원하는 비디오 확장자
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".webm", ".ogg", ".mov", ".avi"}

def is_video_file(file_path: Path) -> bool:
    """파일이 비디오 파일인지 확인"""
    return file_path.suffix.lower() in ALLOWED_VIDEO_EXTENSIONS

def get_video_mime_type(file_path: Path) -> Optional[str]:
    """비디오 파일의 MIME 타입 반환"""
    mime_type, _ = mimetypes.guess_type(str(file_path))
    return mime_type

def validate_video_file(file_path: Path) -> Tuple[bool, Optional[str]]:
    """비디오 파일 유효성 검사"""
    if not file_path.exists():
        return False, "파일이 존재하지 않습니다."
    
    if not is_video_file(file_path):
        return False, f"지원하지 않는 비디오 형식입니다. 지원 형식: {', '.join(ALLOWED_VIDEO_EXTENSIONS)}"
    
    return True, None

def get_video_info(file_path: Path) -> Optional[dict]:
    """비디오 파일 정보 반환 (기본 정보만)"""
    if not validate_video_file(file_path)[0]:
        return None
    
    return {
        "filename": file_path.name,
        "size": file_path.stat().st_size,
        "mimeType": get_video_mime_type(file_path),
        "extension": file_path.suffix.lower()
    }

