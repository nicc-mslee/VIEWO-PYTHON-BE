"""이미지 처리 헬퍼"""
from pathlib import Path
from typing import Tuple, Optional

def get_image_size(image_path: Path) -> Tuple[int, int]:
    """이미지 크기 반환 (width, height)"""
    try:
        from PIL import Image
        with Image.open(image_path) as img:
            return img.size
    except ImportError:
        # PIL이 없으면 기본값 사용
        return (800, 600)
    except Exception:
        return (800, 600)

