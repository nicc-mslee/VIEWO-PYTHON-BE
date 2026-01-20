"""JWT 토큰 유틸리티"""
import jwt
import hashlib
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Tuple
from pathlib import Path

# JWT 설정
JWT_SECRET_KEY = "viewo-admin-secret-key-2024-change-in-production"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30분
REFRESH_TOKEN_EXPIRE_DAYS = 7     # 7일

# DB 경로
DB_PATH = Path(__file__).parent.parent.parent / "data" / "viewo.db"


def create_access_token(user_id: int, username: str, role: str = "admin") -> str:
    """Access Token 생성"""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "type": "access",
        "exp": expire,
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: int, device_info: str = None, ip_address: str = None) -> str:
    """Refresh Token 생성 및 DB 저장"""
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": expire,
        "iat": datetime.utcnow()
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    # 토큰 해시 저장 (보안)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    # DB에 저장
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO refresh_tokens (admin_id, token_hash, device_info, ip_address, expires_at)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, token_hash, device_info, ip_address, expire.isoformat()))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Refresh token DB 저장 실패: {e}")
    
    return token


def verify_access_token(token: str) -> Optional[dict]:
    """Access Token 검증"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def verify_refresh_token(token: str) -> Optional[dict]:
    """Refresh Token 검증 (DB 확인 포함)"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            return None
        
        # DB에서 토큰 유효성 확인
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, admin_id, is_revoked, expires_at 
            FROM refresh_tokens 
            WHERE token_hash = ?
        """, (token_hash,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        token_id, admin_id, is_revoked, expires_at = result
        
        if is_revoked:
            return None
        
        # 만료 확인
        if datetime.fromisoformat(expires_at) < datetime.utcnow():
            return None
        
        payload["token_id"] = token_id
        payload["admin_id"] = admin_id
        return payload
        
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    except Exception as e:
        print(f"Refresh token 검증 오류: {e}")
        return None


def revoke_refresh_token(token: str) -> bool:
    """Refresh Token 폐기 (로그아웃)"""
    try:
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE refresh_tokens 
            SET is_revoked = 1, revoked_at = ?
            WHERE token_hash = ?
        """, (datetime.utcnow().isoformat(), token_hash))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        
        return affected > 0
    except Exception as e:
        print(f"Refresh token 폐기 오류: {e}")
        return False


def revoke_all_user_tokens(user_id: int) -> int:
    """특정 사용자의 모든 Refresh Token 폐기"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE refresh_tokens 
            SET is_revoked = 1, revoked_at = ?
            WHERE admin_id = ? AND is_revoked = 0
        """, (datetime.utcnow().isoformat(), user_id))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected
    except Exception as e:
        print(f"사용자 토큰 폐기 오류: {e}")
        return 0


def cleanup_expired_tokens():
    """만료된 토큰 정리 (스케줄러용)"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM refresh_tokens 
            WHERE expires_at < ?
        """, (datetime.utcnow().isoformat(),))
        conn.commit()
        deleted = cursor.rowcount
        conn.close()
        return deleted
    except Exception as e:
        print(f"토큰 정리 오류: {e}")
        return 0


def get_user_by_id(user_id: int) -> Optional[dict]:
    """DB에서 사용자 정보 조회"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, name, email, role, is_active
            FROM admin_users
            WHERE id = ? AND is_active = 1
        """, (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "id": result[0],
                "username": result[1],
                "name": result[2],
                "email": result[3],
                "role": result[4],
                "is_active": result[5]
            }
        return None
    except Exception as e:
        print(f"사용자 조회 오류: {e}")
        return None


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """사용자 인증 (DB 기반)"""
    try:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, password_hash, name, email, role, is_active
            FROM admin_users
            WHERE username = ? AND is_active = 1
        """, (username,))
        result = cursor.fetchone()
        
        if result and result["password_hash"] == password_hash:
            # 마지막 로그인 시간 업데이트
            cursor.execute("""
                UPDATE admin_users SET last_login_at = ? WHERE id = ?
            """, (datetime.utcnow().isoformat(), result["id"]))
            conn.commit()
            conn.close()
            
            return {
                "id": result["id"],
                "username": result["username"],
                "name": result["name"],
                "email": result["email"],
                "role": result["role"]
            }
        
        conn.close()
        return None
    except Exception as e:
        print(f"인증 오류: {e}")
        return None
