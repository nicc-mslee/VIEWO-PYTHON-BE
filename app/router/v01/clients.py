"""클라이언트 관리 라우터"""
from fastapi import APIRouter, HTTPException
from app.models.client import AliasRequest, CommandRequest
from app.services.client_registry import client_registry
from app.utils.datetime_utils import get_timestamp

router = APIRouter(prefix="/clients", tags=["Clients Management"])

@router.get("/")
async def get_connected_clients():
    """연결된 클라이언트 목록 조회"""
    clients = client_registry.get_all_clients()
    return {
        "code": 200,
        "data": {
            "clients": clients,
            "totalCount": len(clients)
        }
    }

@router.get("/{client_id}")
async def get_client_info(client_id: str):
    """특정 클라이언트 정보 조회"""
    client = client_registry.get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="클라이언트를 찾을 수 없습니다.")
    return {"code": 200, "data": client.to_dict()}

@router.patch("/{client_id}/alias")
async def set_client_alias(client_id: str, alias_data: AliasRequest):
    """클라이언트 별칭 설정"""
    alias = alias_data.alias
    client_registry.set_alias(client_id, alias)
    
    # 해당 클라이언트에 별칭 변경 알림
    await client_registry.send_to_client(client_id, "connection", {
        "status": "alias_updated",
        "alias": alias
    })
    
    return {"code": 200, "message": "별칭이 설정되었습니다.", "data": {"alias": alias}}

@router.post("/{client_id}/reset-indexeddb")
async def reset_client_indexeddb(client_id: str):
    """특정 클라이언트의 IndexedDB 초기화 명령"""
    client = client_registry.get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="클라이언트를 찾을 수 없습니다.")
    
    await client_registry.send_to_client(client_id, "command", {
        "command": "reset_indexeddb",
        "targetClientId": client_id,
        "params": {
            "reason": "관리자 요청",
            "timestamp": get_timestamp()  # field 포맷 사용
        }
    })
    
    return {"code": 200, "message": "IndexedDB 초기화 명령이 전송되었습니다."}

@router.post("/reset-all-indexeddb")
async def reset_all_indexeddb():
    """모든 클라이언트의 IndexedDB 초기화 명령"""
    await client_registry.broadcast("command", {
        "command": "reset_indexeddb",
        "targetClientId": "all",
        "params": {
            "reason": "관리자 전체 초기화 요청",
            "timestamp": get_timestamp()  # field 포맷 사용
        }
    })
    
    return {
        "code": 200, 
        "message": f"모든 클라이언트({client_registry.get_client_count()}대)에 초기화 명령이 전송되었습니다."
    }

@router.post("/{client_id}/force-sync")
async def force_client_sync(client_id: str):
    """특정 클라이언트 강제 동기화"""
    client = client_registry.get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="클라이언트를 찾을 수 없습니다.")
    
    await client_registry.send_to_client(client_id, "command", {
        "command": "force_sync",
        "targetClientId": client_id,
        "params": {
            "timestamp": get_timestamp()  # field 포맷 사용
        }
    })
    
    return {"code": 200, "message": "강제 동기화 명령이 전송되었습니다."}

@router.post("/broadcast-sync")
async def broadcast_force_sync():
    """모든 클라이언트 강제 동기화"""
    await client_registry.broadcast("command", {
        "command": "force_sync",
        "targetClientId": "all",
        "params": {
            "timestamp": get_timestamp()  # field 포맷 사용
        }
    })
    
    return {"code": 200, "message": "모든 클라이언트에 동기화 명령이 전송되었습니다."}

@router.post("/{client_id}/command")
async def send_client_command(client_id: str, command_data: CommandRequest):
    """특정 클라이언트에 명령 전송"""
    client = client_registry.get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="클라이언트를 찾을 수 없습니다.")
    
    await client_registry.send_to_client(client_id, "command", {
        "command": command_data.command,
        "targetClientId": client_id,
        "params": command_data.params or {}
    })
    
    return {"code": 200, "message": f"'{command_data.command}' 명령이 전송되었습니다."}

