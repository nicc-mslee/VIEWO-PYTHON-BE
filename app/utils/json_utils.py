"""JSON 처리 헬퍼"""
import json
from pathlib import Path
from typing import Optional, Dict, Any, Union, List

def load_json_file(file_path: Path) -> Optional[Union[Dict[str, Any], List[Any]]]:
    """JSON 파일 로드"""
    if not file_path.exists():
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"JSON 파일 로드 실패 ({file_path}): {e}")
        return None

def save_json_file(file_path: Path, data: Union[Dict[str, Any], List[Any]]):
    """JSON 파일 저장"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_json(filename: str, base_dir: Path) -> Dict[str, Any]:
    """JSON 파일 로드 (하위 호환성)"""
    file_path = base_dir / filename
    result = load_json_file(file_path)
    if result is None:
        return {}
    return result

def save_json(filename: str, data: Dict[str, Any], base_dir: Path):
    """JSON 파일 저장 (하위 호환성)"""
    file_path = base_dir / filename
    save_json_file(file_path, data)

