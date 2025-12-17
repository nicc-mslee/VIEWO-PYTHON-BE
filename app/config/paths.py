"""경로 설정 모듈"""
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
CONTENT_DIR = BASE_DIR / "content"
FACILITIES_DIR = CONTENT_DIR / "facilities"
MEDIA_DIR = CONTENT_DIR / "media"
DEPARTMENTS_DIR = CONTENT_DIR / "departments"
SYSTEM_DATA_DIR = BASE_DIR / "system"
STATIC_DIR = BASE_DIR / "static"

# 시설 데이터 경로
BUILDINGS_DATA_DIR = FACILITIES_DIR / "buildings"
ICONS_DATA_DIR = FACILITIES_DIR / "icons"

# 미디어 경로
DASHBOARD_MEDIA_DIR = MEDIA_DIR / "dashboard"
PR_MEDIA_DIR = MEDIA_DIR / "pr"

# 부서 경로
DEPARTMENTS_DATA_DIR = DEPARTMENTS_DIR

# 시스템 설정 파일 경로
SYSTEM_ACCOUNT_DIR = SYSTEM_DATA_DIR / "account"
SYSTEM_CONFIG_DIR = SYSTEM_DATA_DIR / "config"
SYSTEM_INFO_DIR = SYSTEM_DATA_DIR / "info"

USER_FILE = SYSTEM_ACCOUNT_DIR / "user.json"
SERVER_CONFIG_FILE = SYSTEM_CONFIG_DIR / "server.json"
THEME_CONFIG_FILE = SYSTEM_CONFIG_DIR / "theme.json"
TIME_CONFIG_FILE = SYSTEM_CONFIG_DIR / "time.json"
CLIENT_INFO_FILE = SYSTEM_INFO_DIR / "client.json"
SERVER_INFO_FILE = SYSTEM_INFO_DIR / "server.json"

# 콘텐츠 메타데이터 파일
DASHBOARD_METADATA_FILE = DASHBOARD_MEDIA_DIR / "dashboard.json"
PR_METADATA_FILE = PR_MEDIA_DIR / "pr.json"
ICONS_METADATA_FILE = ICONS_DATA_DIR / "icon.json"

# 정적 파일 경로
ADMIN_HTML_PATH = STATIC_DIR / "index.html"

# 디렉토리 생성 함수
def ensure_directories():
    """필요한 디렉토리들을 생성"""
    directories = [
        CONTENT_DIR,
        FACILITIES_DIR,
        BUILDINGS_DATA_DIR,
        ICONS_DATA_DIR,
        MEDIA_DIR,
        DASHBOARD_MEDIA_DIR,
        PR_MEDIA_DIR,
        DEPARTMENTS_DATA_DIR,
        SYSTEM_DATA_DIR,
        SYSTEM_ACCOUNT_DIR,
        SYSTEM_CONFIG_DIR,
        SYSTEM_INFO_DIR,
        STATIC_DIR,
    ]
    for directory in directories:
        if directory:
            directory.mkdir(parents=True, exist_ok=True)

