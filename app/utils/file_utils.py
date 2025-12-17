"""파일 I/O 헬퍼"""
from pathlib import Path

def ensure_dir(path: Path):
    """디렉토리 생성 (없으면)"""
    path.mkdir(parents=True, exist_ok=True)

