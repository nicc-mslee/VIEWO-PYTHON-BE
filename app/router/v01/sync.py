"""동기화 라우터"""
from fastapi import APIRouter, Query
from app.services.client_registry import client_registry
from app.utils.datetime_utils import get_timestamp

router = APIRouter(prefix="/sync", tags=["Sync"])

@router.get("/version")
async def get_sync_version():
    """현재 데이터 버전 및 동기화 상태 반환"""
    return {
        "code": 200,
        "data": {
            "version": client_registry.version,
            "lastUpdate": get_timestamp(),  # field 포맷 사용
            "connectedClients": client_registry.get_client_count()
        }
    }

@router.get("/status")
async def get_sync_status(clientId: str = Query(None)):
    """클라이언트별 동기화 상태 확인"""
    if clientId:
        client = client_registry.get_client(clientId)
        if not client:
            return {"code": 404, "message": "클라이언트를 찾을 수 없습니다."}
        
        return {
            "code": 200,
            "data": {
                "clientId": clientId,
                "isConnected": True,
                "lastHeartbeat": client.last_heartbeat,
                "serverVersion": client_registry.version
            }
        }
    
    return {
        "code": 200,
        "data": {
            "serverVersion": client_registry.version,
            "connectedClients": client_registry.get_all_clients()
        }
    }

