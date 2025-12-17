"""인증 라우터"""
from fastapi import APIRouter, HTTPException
from app.models.auth import LoginRequest, LoginResponse
from app.config.paths import USER_FILE
from app.utils.json_utils import load_json_file, save_json_file
from app.utils.datetime_utils import get_timestamp

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """관리자 로그인"""
    try:
        user_data = load_json_file(USER_FILE)
        if not user_data:
            raise HTTPException(status_code=500, detail="사용자 데이터를 찾을 수 없습니다.")
        
        users = user_data.get("users", [])

        for user in users:
            if user["username"] == request.username and user["password"] == request.password:
                # 마지막 로그인 시간 업데이트
                user["last_login"] = get_timestamp()
                save_json_file(USER_FILE, user_data)

                # 비밀번호 제외하고 반환
                user_info = {k: v for k, v in user.items() if k != "password"}
                return LoginResponse(success=True, message="로그인 성공", user=user_info)

        return LoginResponse(success=False, message="아이디 또는 비밀번호가 올바르지 않습니다.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"로그인 처리 실패: {str(e)}")

@router.get("/check")
async def check_auth():
    """인증 상태 확인 (간단한 세션 체크용)"""
    return {"code": 200, "message": "인증 상태 확인용 엔드포인트"}

