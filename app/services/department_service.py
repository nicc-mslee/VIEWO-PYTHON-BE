"""부서 데이터 관리 서비스"""
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.config.paths import DEPARTMENTS_DATA_DIR
from app.utils.json_utils import load_json_file, save_json_file

DEPARTMENTS_FILE = DEPARTMENTS_DATA_DIR / "departments.json"

def load_departments() -> List[Dict[str, Any]]:
    """모든 부서 데이터 로드"""
    departments = load_json_file(DEPARTMENTS_FILE)
    if departments is None:
        return []
    if isinstance(departments, list):
        return departments
    return []

def save_departments(departments: List[Dict[str, Any]]):
    """부서 데이터 저장"""
    DEPARTMENTS_DATA_DIR.mkdir(parents=True, exist_ok=True)
    save_json_file(DEPARTMENTS_FILE, departments)

def get_all_departments() -> List[Dict[str, Any]]:
    """모든 부서 목록 조회"""
    return load_departments()

def get_department_by_index(index: int) -> Optional[Dict[str, Any]]:
    """인덱스로 부서 조회"""
    departments = load_departments()
    if 0 <= index < len(departments):
        return departments[index]
    return None

def create_department(department_data: Dict[str, Any]) -> Dict[str, Any]:
    """새 부서 생성"""
    departments = load_departments()
    departments.append(department_data)
    save_departments(departments)
    return department_data

def update_department(index: int, department_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """부서 업데이트"""
    departments = load_departments()
    if 0 <= index < len(departments):
        departments[index].update(department_data)
        save_departments(departments)
        return departments[index]
    return None

def delete_department(index: int) -> bool:
    """부서 삭제"""
    departments = load_departments()
    if 0 <= index < len(departments):
        departments.pop(index)
        save_departments(departments)
        return True
    return False

def search_departments(query: str) -> List[Dict[str, Any]]:
    """부서 검색"""
    departments = load_departments()
    query_lower = query.lower()
    
    matched = []
    for dept in departments:
        search_fields = [
            dept.get("building", ""),
            dept.get("floor", ""),
            dept.get("department", ""),
            dept.get("team", ""),
            dept.get("position", ""),
            dept.get("task", "")
        ]
        
        if any(query_lower in str(field).lower() for field in search_fields):
            matched.append(dept)
    
    return matched

