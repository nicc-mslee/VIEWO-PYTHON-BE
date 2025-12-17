"""애플리케이션 설정"""
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from app.config.paths import SERVER_CONFIG_FILE
from app.utils.json_utils import load_json_file

CORS_CONFIG = {
    "allow_origins": ["*"],
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}

APP_CONFIG = {
    "title": "Viewo API",
    "description": "청사 안내 데이터 API",
    "version": "1.0.0",
}

def load_server_config():
    """서버 설정 파일을 로드합니다."""
    if not SERVER_CONFIG_FILE.exists():
        # 기본 서버 설정 파일이 없으면 기본값 생성
        default_config = {
            "host": "0.0.0.0",
            "port": 8000,
            "debug": False,
            "log_level": "info",
            "log_file": "logs/viewo.log"
        }
        from app.utils.json_utils import save_json_file
        save_json_file(SERVER_CONFIG_FILE, default_config)
        return default_config
    
    config = load_json_file(SERVER_CONFIG_FILE)
    if not config:
        # 파일이 비어있으면 기본값 반환
        return {
            "host": "0.0.0.0",
            "port": 8000,
            "debug": False,
            "log_level": "info",
            "log_file": "logs/viewo.log"
        }
    
    return config

# 서버 설정 로드
SERVER_CONFIG = load_server_config()

