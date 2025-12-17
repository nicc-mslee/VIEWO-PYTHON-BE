"""동기화 관리 서비스"""
from typing import Optional, Dict, Any
from app.services.client_registry import ClientRegistry
from app.utils.datetime_utils import get_timestamp

class SyncService:
    """동기화 서비스"""
    
    def __init__(self, client_registry: ClientRegistry):
        self.client_registry = client_registry
    
    def get_sync_version(self) -> Dict[str, Any]:
        """현재 데이터 버전 및 동기화 상태 반환"""
        return {
            "version": self.client_registry.version,
            "lastUpdate": get_timestamp(),  # field 포맷 사용
            "connectedClients": self.client_registry.get_client_count()
        }
    
    def get_sync_status(self, client_id: Optional[str] = None) -> Dict[str, Any]:
        """클라이언트별 동기화 상태 확인"""
        if client_id:
            client = self.client_registry.get_client(client_id)
            if not client:
                return {
                    "code": 404,
                    "message": "클라이언트를 찾을 수 없습니다.",
                    "data": None
                }
            
            return {
                "code": 200,
                "data": {
                    "clientId": client_id,
                    "version": self.client_registry.version,
                    "lastHeartbeat": client.last_heartbeat,
                    "isOnline": True
                }
            }
        else:
            return {
                "code": 200,
                "data": {
                    "version": self.client_registry.version,
                    "connectedClients": self.client_registry.get_client_count(),
                    "clients": self.client_registry.get_all_clients()
                }
            }
    
    async def force_sync_client(self, client_id: str) -> Dict[str, Any]:
        """특정 클라이언트 강제 동기화"""
        client = self.client_registry.get_client(client_id)
        if not client:
            return {
                "code": 404,
                "message": "클라이언트를 찾을 수 없습니다."
            }
        
        await self.client_registry.send_to_client(client_id, "command", {
            "command": "force_sync",
            "targetClientId": client_id,
            "params": {
                "timestamp": get_timestamp()  # field 포맷 사용
            }
        })
        
        return {
            "code": 200,
            "message": "강제 동기화 명령이 전송되었습니다."
        }
    
    async def broadcast_sync(self) -> Dict[str, Any]:
        """모든 클라이언트 강제 동기화"""
        await self.client_registry.broadcast("command", {
            "command": "force_sync",
            "targetClientId": "all",
            "params": {
                "timestamp": get_timestamp()  # field 포맷 사용
            }
        })
        
        return {
            "code": 200,
            "message": "모든 클라이언트에 동기화 명령이 전송되었습니다."
        }

