"""
Viewo SQLite Database Initialization Script
- 스키마 생성
- departments.json 데이터 마이그레이션
"""

import sqlite3
import json
import os
from pathlib import Path

# 경로 설정
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
SQL_DIR = BASE_DIR / "sql"
CONTENT_DIR = BASE_DIR / "content"

DB_PATH = DATA_DIR / "viewo.db"
SCHEMA_PATH = SQL_DIR / "schema.sql"
DEPARTMENTS_JSON_PATH = CONTENT_DIR / "departments" / "departments.json"


def init_db():
    """데이터베이스 초기화"""
    # data 폴더 생성
    DATA_DIR.mkdir(exist_ok=True)
    
    # DB 연결
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"📂 DB 경로: {DB_PATH}")
    
    # 스키마 적용
    if SCHEMA_PATH.exists():
        with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        cursor.executescript(schema_sql)
        print("✅ 스키마 적용 완료")
    else:
        print(f"❌ 스키마 파일을 찾을 수 없습니다: {SCHEMA_PATH}")
        return
    
    conn.commit()
    conn.close()
    print("✅ 데이터베이스 초기화 완료")


def migrate_departments():
    """departments.json 데이터를 DB로 마이그레이션"""
    if not DEPARTMENTS_JSON_PATH.exists():
        print(f"❌ departments.json 파일을 찾을 수 없습니다: {DEPARTMENTS_JSON_PATH}")
        return
    
    # JSON 데이터 로드
    with open(DEPARTMENTS_JSON_PATH, 'r', encoding='utf-8') as f:
        departments = json.load(f)
    
    print(f"📊 총 {len(departments)}개의 부서 데이터 발견")
    
    # DB 연결
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 기존 데이터 삭제 (재마이그레이션 시)
    cursor.execute("DELETE FROM departments")
    
    # 데이터 삽입
    insert_sql = """
        INSERT INTO departments (building, floor, department, team, position, task)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    
    for dept in departments:
        cursor.execute(insert_sql, (
            dept.get('building', '정보없음'),
            dept.get('floor', '정보없음'),
            dept.get('department', ''),
            dept.get('team'),  # None 허용
            dept.get('position', ''),
            dept.get('task', '')
        ))
    
    conn.commit()
    
    # 확인
    cursor.execute("SELECT COUNT(*) FROM departments")
    count = cursor.fetchone()[0]
    print(f"✅ {count}개의 부서 데이터 마이그레이션 완료")
    
    conn.close()


def create_default_admin():
    """기본 어드민 계정 생성 (테스트용)"""
    import hashlib
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 이미 존재하는지 확인
    cursor.execute("SELECT id FROM admin_users WHERE username = ?", ('admin',))
    if cursor.fetchone():
        print("ℹ️ 기본 어드민 계정이 이미 존재합니다")
        conn.close()
        return
    
    # 간단한 해시 (실제 운영시에는 bcrypt 사용 권장)
    password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
    
    cursor.execute("""
        INSERT INTO admin_users (username, password_hash, name, email, role)
        VALUES (?, ?, ?, ?, ?)
    """, ('admin', password_hash, '관리자', 'admin@viewo.local', 'super_admin'))
    
    conn.commit()
    conn.close()
    print("✅ 기본 어드민 계정 생성 완료 (ID: admin / PW: admin123)")
    print("⚠️  운영 환경에서는 비밀번호를 반드시 변경하세요!")


if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Viewo Database Initialization")
    print("=" * 50)
    
    # 1. DB 초기화
    init_db()
    
    # 2. 부서 데이터 마이그레이션
    migrate_departments()
    
    # 3. 기본 어드민 계정 생성
    create_default_admin()
    
    print("=" * 50)
    print("✨ 모든 작업이 완료되었습니다!")
    print(f"📂 DB 위치: {DB_PATH}")
    print("=" * 50)
