"""부서 관리 CRUD (DB 기반)"""
import sqlite3
from typing import List, Dict, Any, Optional
from app.config.paths import DB_PATH

def row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    """sqlite3.Row를 dict로 변환"""
    return dict(row)

def get_db_connection():
    """DB 연결 생성"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_all_departments() -> List[Dict[str, Any]]:
    """모든 부서 조회"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM departments ORDER BY id ASC")
        rows = cursor.fetchall()
        conn.close()
        return [row_to_dict(row) for row in rows]
    except Exception as e:
        print(f"부서 조회 오류: {e}")
        return []

def get_department_by_id(department_id: int) -> Optional[Dict[str, Any]]:
    """ID로 부서 조회"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM departments WHERE id = ?", (department_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return row_to_dict(row)
        return None
    except Exception as e:
        print(f"부서 상세 조회 오류: {e}")
        return None

def create_department(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """부서 생성"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # INSERT
        fields = ["building", "floor", "department", "team", "position", "task"]
        # 존재하지 않는 키는 빈 문자열로 처리 (혹은 update_department처럼 체크)
        values = [data.get(f, "") for f in fields]
        
        cursor.execute("""
            INSERT INTO departments (building, floor, department, team, position, task)
            VALUES (?, ?, ?, ?, ?, ?)
        """, values)
        
        new_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return get_department_by_id(new_id)
    except Exception as e:
        print(f"부서 생성 오류: {e}")
        import traceback
        traceback.print_exc()
        return None

def update_department(department_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """부서 수정"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        update_fields = []
        values = []
        possible_fields = ["building", "floor", "department", "team", "position", "task"]
        
        for field in possible_fields:
            if field in data:
                update_fields.append(f"{field} = ?")
                values.append(data[field])
                
        if not update_fields:
            conn.close()
            return get_department_by_id(department_id)
            
        values.append(department_id)
        query = f"UPDATE departments SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        
        cursor.execute(query, values)
        conn.commit()
        conn.close()
        
        return get_department_by_id(department_id)
    except Exception as e:
        print(f"부서 수정 오류: {e}")
        return None

def delete_department(department_id: int) -> bool:
    """부서 삭제"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM departments WHERE id = ?", (department_id,))
        conn.commit()
        count = cursor.rowcount
        conn.close()
        return count > 0
    except Exception as e:
        print(f"부서 삭제 오류: {e}")
        return False

def search_departments(query: str) -> List[Dict[str, Any]]:
    """부서 검색"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        search_term = f"%{query}%"
        sql = """
            SELECT * FROM departments 
            WHERE building LIKE ? OR floor LIKE ? OR department LIKE ? 
               OR team LIKE ? OR position LIKE ? OR task LIKE ?
        """
        cursor.execute(sql, (search_term, search_term, search_term, search_term, search_term, search_term))
        rows = cursor.fetchall()
        conn.close()
        return [row_to_dict(row) for row in rows]
    except Exception as e:
        print(f"부서 검색 오류: {e}")
        return []
