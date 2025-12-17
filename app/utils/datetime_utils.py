"""날짜/시간 헬퍼"""
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
from app.config.paths import TIME_CONFIG_FILE
from app.utils.json_utils import load_json_file, save_json_file


# 시간 설정 관리 함수들
def load_time_config() -> Dict[str, Any]:
    """시간 설정 파일을 로드합니다."""
    if not TIME_CONFIG_FILE.exists():
        # 기본 시간 설정 파일이 없으면 기본값 생성
        default_config = {
            "timezone": "Asia/Seoul",
            "locale": "ko-KR",
            "format": {
                "field": {
                    "date": "YYYY-MM-DD",
                    "time": "HH:mm:ss",
                    "datetime": "YYYY-MM-DDTHH:mm:ss"
                },
                "filename": {
                    "date": "YYYYMMDD",
                    "time": "HHmmss",
                    "datetime": "YYYYMMDD_HHmmss"
                }
            }
        }
        save_json_file(TIME_CONFIG_FILE, default_config)
        return default_config
    
    config = load_json_file(TIME_CONFIG_FILE)
    if not config:
        # 파일이 비어있으면 기본값 반환
        return {
            "timezone": "Asia/Seoul",
            "locale": "ko-KR",
            "format": {
                "field": {
                    "date": "YYYY-MM-DD",
                    "time": "HH:mm:ss",
                    "datetime": "YYYY-MM-DDTHH:mm:ss"
                },
                "filename": {
                    "date": "YYYYMMDD",
                    "time": "HHmmss",
                    "datetime": "YYYYMMDD_HHmmss"
                }
            }
        }
    
    return config

def convert_format_to_strftime(format_str: str) -> str:
    """time.json의 포맷 문자열을 Python strftime 형식으로 변환
    
    YYYY -> %Y (4자리 연도)
    MM -> %m (월)
    DD -> %d (일)
    HH -> %H (24시간 형식 시간)
    mm -> %M (분)
    ss -> %S (초)
    """
    # 순서가 중요: 먼저 긴 패턴부터 변환
    # YYYY를 먼저 변환 (YY와 구분)
    format_str = format_str.replace("YYYY", "%Y")
    format_str = format_str.replace("MM", "%m")
    format_str = format_str.replace("DD", "%d")
    format_str = format_str.replace("HH", "%H")
    # mm은 분(minute)이므로 %M으로 변환
    format_str = format_str.replace("mm", "%M")
    format_str = format_str.replace("ss", "%S")
    return format_str

def get_time_format(format_type: str = "field", format_key: str = "datetime") -> str:
    """시간 포맷 문자열 반환
    
    Args:
        format_type: "field" 또는 "filename"
        format_key: "date", "time", "datetime"
    
    Returns:
        Python strftime 형식 문자열
    """
    config = load_time_config()
    format_str = config.get("format", {}).get(format_type, {}).get(format_key, "")
    
    if not format_str:
        # 기본값
        if format_type == "field":
            defaults = {
                "date": "YYYY-MM-DD",
                "time": "HH:mm:ss",
                "datetime": "YYYY-MM-DDTHH:mm:ss"
            }
        else:  # filename
            defaults = {
                "date": "YYYYMMDD",
                "time": "HHmmss",
                "datetime": "YYYYMMDD_HHmmss"
            }
        format_str = defaults.get(format_key, "YYYY-MM-DDTHH:mm:ss")
    
    return convert_format_to_strftime(format_str)

def get_timezone() -> str:
    """타임존 반환"""
    config = load_time_config()
    return config.get("timezone", "Asia/Seoul")

def get_locale() -> str:
    """로케일 반환"""
    config = load_time_config()
    return config.get("locale", "ko-KR")


# 날짜/시간 문자열 생성 함수들
def _get_datetime_with_timezone():
    """타임존을 고려한 현재 시간 반환"""
    timezone_str = get_timezone()
    
    # Python 3.9+에서는 zoneinfo 사용, 그 이하는 기본 datetime 사용
    try:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo(timezone_str)
        return datetime.now(tz)
    except ImportError:
        # Python 3.8 이하에서는 pytz 시도
        try:
            import pytz
            tz = pytz.timezone(timezone_str)
            return datetime.now(tz)
        except ImportError:
            # pytz도 없으면 기본 datetime 사용
            return datetime.now()
    except Exception:
        # 타임존 설정이 잘못된 경우 기본값 사용
        return datetime.now()

def get_timestamp() -> str:
    """field 포맷의 datetime 타임스탬프 반환 (time.json 설정 사용)"""
    format_str = get_time_format("field", "datetime")
    now = _get_datetime_with_timezone()
    return now.strftime(format_str)

def get_timestamp_filename() -> str:
    """파일명용 타임스탬프 반환 (time.json 설정 사용)"""
    format_str = get_time_format("filename", "datetime")
    now = _get_datetime_with_timezone()
    return now.strftime(format_str)

def get_date_string() -> str:
    """field 포맷의 date 문자열 반환"""
    format_str = get_time_format("field", "date")
    now = _get_datetime_with_timezone()
    return now.strftime(format_str)

def get_time_string() -> str:
    """field 포맷의 time 문자열 반환"""
    format_str = get_time_format("field", "time")
    now = _get_datetime_with_timezone()
    return now.strftime(format_str)

def get_filename_date_string() -> str:
    """filename 포맷의 date 문자열 반환"""
    format_str = get_time_format("filename", "date")
    now = _get_datetime_with_timezone()
    return now.strftime(format_str)

def get_filename_time_string() -> str:
    """filename 포맷의 time 문자열 반환"""
    format_str = get_time_format("filename", "time")
    now = _get_datetime_with_timezone()
    return now.strftime(format_str)

