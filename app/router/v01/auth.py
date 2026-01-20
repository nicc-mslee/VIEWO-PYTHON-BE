"""인증 라우터 - JWT 기반"""
from fastapi import APIRouter, HTTPException, Request, Header
from typing import Optional
from app.models.auth import (
    LoginRequest, LoginResponse, 
    RefreshTokenRequest, TokenResponse,
    LogoutRequest
)
from app.utils.jwt_utils import (
    create_access_token, create_refresh_token,
    verify_access_token, verify_refresh_token,
    revoke_refresh_token, revoke_all_user_tokens,
    authenticate_user, get_user_by_id
)
from app.config.paths import USER_FILE
from app.utils.json_utils import load_json_file, save_json_file
from app.utils.datetime_utils import get_timestamp

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, req: Request):
    """관리자 로그인 - JWT 토큰 발급"""
    # 클라이언트 정보
    client_ip = req.client.host if req.client else None
    user_agent = req.headers.get("user-agent", "unknown")
    
    # 1. DB 기반 인증 시도
    user = authenticate_user(request.username, request.password)
    
    # 2. DB에 없으면 JSON 파일 기반 인증 (하위 호환)
    if not user:
        try:
            user_data = load_json_file(USER_FILE)
            if user_data:
                users = user_data.get("users", [])
                for u in users:
                    if u["username"] == request.username and u["password"] == request.password:
                        u["last_login"] = get_timestamp()
                        save_json_file(USER_FILE, user_data)
                        user = {
                            "id": u.get("id", 1),
                            "username": u["username"],
                            "name": u.get("name", u["username"]),
                            "email": u.get("email"),
                            "role": u.get("role", "admin")
                        }
                        break
        except Exception as e:
            print(f"JSON 인증 오류: {e}")
    
    if not user:
        return LoginResponse(
            success=False, 
            message="아이디 또는 비밀번호가 올바르지 않습니다."
        )
    
    # JWT 토큰 생성
    access_token = create_access_token(
        user_id=user["id"],
        username=user["username"],
        role=user.get("role", "admin")
    )
    refresh_token = create_refresh_token(
        user_id=user["id"],
        device_info=user_agent,
        ip_address=client_ip
    )
    
    return LoginResponse(
        success=True,
        message="로그인 성공",
        user=user,
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer"
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """Access Token 갱신"""
    # Refresh Token 검증
    payload = verify_refresh_token(request.refresh_token)
    
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="유효하지 않거나 만료된 Refresh Token입니다."
        )
    
    user_id = int(payload.get("sub") or payload.get("admin_id"))
    
    # 사용자 정보 조회
    user = get_user_by_id(user_id)
    
    if not user:
        # JSON 파일에서 조회 (하위 호환)
        try:
            user_data = load_json_file(USER_FILE)
            if user_data:
                users = user_data.get("users", [])
                for u in users:
                    if u.get("id") == user_id:
                        user = {
                            "id": u.get("id", 1),
                            "username": u["username"],
                            "name": u.get("name", u["username"]),
                            "role": u.get("role", "admin")
                        }
                        break
        except Exception:
            pass
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="사용자를 찾을 수 없습니다."
        )
    
    # 새 Access Token 발급
    new_access_token = create_access_token(
        user_id=user["id"],
        username=user["username"],
        role=user.get("role", "admin")
    )
    
    return TokenResponse(
        success=True,
        message="토큰이 갱신되었습니다.",
        access_token=new_access_token,
        token_type="Bearer"
    )


@router.post("/logout")
async def logout(request: LogoutRequest):
    """로그아웃 - Refresh Token 폐기"""
    revoked = revoke_refresh_token(request.refresh_token)
    
    return {
        "code": 200,
        "success": True,
        "message": "로그아웃되었습니다." if revoked else "로그아웃 처리됨"
    }


@router.post("/logout-all")
async def logout_all(authorization: Optional[str] = Header(None)):
    """모든 기기에서 로그아웃"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="인증이 필요합니다.")
    
    token = authorization.split(" ")[1]
    payload = verify_access_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")
    
    user_id = int(payload.get("sub"))
    count = revoke_all_user_tokens(user_id)
    
    return {
        "code": 200,
        "success": True,
        "message": f"모든 기기에서 로그아웃되었습니다. ({count}개 세션 종료)"
    }


@router.get("/me")
async def get_current_user(authorization: Optional[str] = Header(None)):
    """현재 로그인한 사용자 정보"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="인증이 필요합니다.")
    
    token = authorization.split(" ")[1]
    payload = verify_access_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="유효하지 않거나 만료된 토큰입니다.")
    
    user_id = int(payload.get("sub"))
    user = get_user_by_id(user_id)
    
    if not user:
        # JSON 파일에서 조회 (하위 호환)
        try:
            user_data = load_json_file(USER_FILE)
            if user_data:
                users = user_data.get("users", [])
                for u in users:
                    if u.get("id") == user_id or u["username"] == payload.get("username"):
                        user = {
                            "id": u.get("id", 1),
                            "username": u["username"],
                            "name": u.get("name", u["username"]),
                            "email": u.get("email"),
                            "role": u.get("role", "admin")
                        }
                        break
        except Exception:
            pass
    
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    
    return {
        "code": 200,
        "user": user
    }


@router.get("/check")
async def check_auth(authorization: Optional[str] = Header(None)):
    """인증 상태 확인"""
    if not authorization or not authorization.startswith("Bearer "):
        return {
            "code": 401,
            "authenticated": False,
            "message": "인증이 필요합니다."
        }
    
    token = authorization.split(" ")[1]
    payload = verify_access_token(token)
    
    if not payload:
        return {
            "code": 401,
            "authenticated": False,
            "message": "토큰이 만료되었거나 유효하지 않습니다."
        }
    
    return {
        "code": 200,
        "authenticated": True,
        "user_id": payload.get("sub"),
        "username": payload.get("username"),
        "role": payload.get("role")
    }
