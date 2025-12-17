"""테마 설정 관리 서비스"""
from app.config.paths import THEME_CONFIG_FILE
from app.utils.json_utils import load_json_file, save_json_file

def load_themes():
    """테마 설정 파일을 로드합니다."""
    if not THEME_CONFIG_FILE.exists():
        # 기본 테마 파일이 없으면 기본값 생성
        default_themes = {
            "currentTheme": "default",
            "themes": {
                "default": {
                    "id": "default",
                    "name": "기본",
                    "description": "Viewo 기본 테마 - 클래식한 블루 컬러",
                    "colors": {
                        "primary": "#256ef4",
                        "primaryDark": "#1a5cd4",
                        "primaryLight": "#e8f1ff",
                        "danger": "#ef4444",
                        "dangerDark": "#dc2626",
                        "dangerLight": "#fef2f2",
                        "success": "#22c55e",
                        "successLight": "#f0fdf4",
                        "warning": "#f59e0b",
                        "warningLight": "#fffbeb",
                        "sidebarBg": "linear-gradient(180deg, #1f2937 0%, #111827 100%)",
                        "sidebarText": "#9ca3af",
                        "sidebarActiveText": "#256ef4",
                        "sidebarActiveBg": "rgba(37, 110, 244, 0.15)",
                        "bgMain": "#f3f4f6",
                        "bgCard": "#ffffff",
                        "textPrimary": "#111827",
                        "textSecondary": "#6b7280",
                        "borderDefault": "#d1d5db",
                        "logoColor": "#256ef4",
                        "logoColorInverse": "#ffffff",
                        "currentLocation": "#FFEB3B",
                        "currentLocationDark": "#FDD835"
                    }
                }
            }
        }
        save_json_file(THEME_CONFIG_FILE, default_themes)
        return default_themes
    
    return load_json_file(THEME_CONFIG_FILE) or {}

def save_themes(data: dict):
    """테마 설정 파일을 저장합니다."""
    save_json_file(THEME_CONFIG_FILE, data)

