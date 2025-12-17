"""SSE 클라이언트 관리 서비스"""
import asyncio
from typing import Dict, Optional
from app.config.paths import CLIENT_INFO_FILE
from app.utils.json_utils import load_json_file, save_json_file
# from app.utils.datetime_utils import get_timestamp
def get_timestamp() -> str:
    return "test"

class ClientInfo:
    """개별 클라이언트 정보"""
    def __init__(self, client_id: str, queue: asyncio.Queue):
        self.client_id = client_id
        self.alias: Optional[str] = None
        self.connected_at: str = get_timestamp()  # field 포맷 사용
        self.last_heartbeat: str = self.connected_at
        self.queue = queue
        self.user_agent: Optional[str] = None
        self.ip_address: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "clientId": self.client_id,
            "alias": self.alias,
            "connectedAt": self.connected_at,
            "lastHeartbeat": self.last_heartbeat,
            "userAgent": self.user_agent,
            "ipAddress": self.ip_address,
            "isOnline": True
        }

class ClientRegistry:
    """클라이언트 등록 및 관리"""
    def __init__(self):
        self.clients: Dict[str, ClientInfo] = {}
        self.aliases: Dict[str, str] = {}  # clientId -> alias 매핑 (영구 저장용)
        self.version = 0
        self._load_aliases()
    
    async def register(self, client_id: str, user_agent: str = None, ip_address: str = None) -> ClientInfo:
        """새 클라이언트 등록"""
        queue = asyncio.Queue()
        client = ClientInfo(client_id, queue)
        client.user_agent = user_agent
        client.ip_address = ip_address
        
        # 기존 별칭이 있으면 복원
        if client_id in self.aliases:
            client.alias = self.aliases[client_id]
        
        self.clients[client_id] = client
        print(f"[ClientRegistry] 클라이언트 등록: {client_id} (총 {len(self.clients)}개)")
        return client
    
    def unregister(self, client_id: str):
        """클라이언트 연결 해제"""
        if client_id in self.clients:
            del self.clients[client_id]
            print(f"[ClientRegistry] 클라이언트 해제: {client_id} (남은 {len(self.clients)}개)")
    
    def update_heartbeat(self, client_id: str):
        """하트비트 시간 업데이트"""
        if client_id in self.clients:
            self.clients[client_id].last_heartbeat = get_timestamp()  # field 포맷 사용
    
    def set_alias(self, client_id: str, alias: str):
        """클라이언트 별칭 설정"""
        self.aliases[client_id] = alias
        if client_id in self.clients:
            self.clients[client_id].alias = alias
        # 영구 저장
        self._save_aliases()
    
    def get_client(self, client_id: str) -> Optional[ClientInfo]:
        """특정 클라이언트 조회"""
        return self.clients.get(client_id)
    
    def get_all_clients(self) -> list:
        """모든 연결된 클라이언트 목록"""
        return [client.to_dict() for client in self.clients.values()]
    
    def get_client_count(self) -> int:
        """연결된 클라이언트 수"""
        return len(self.clients)
    
    async def broadcast(self, event_type: str, data: dict, exclude_client: str = None):
        """모든 클라이언트에 메시지 전송"""
        self.version += 1
        message = {
            "type": event_type,
            "data": data,
            "timestamp": get_timestamp(),  # field 포맷 사용
            "version": self.version
        }
        
        for client_id, client in self.clients.items():
            if exclude_client and client_id == exclude_client:
                continue
            try:
                await client.queue.put(message)
            except Exception as e:
                print(f"[ClientRegistry] 브로드캐스트 실패 ({client_id}): {e}")
    
    async def send_to_client(self, client_id: str, event_type: str, data: dict) -> bool:
        """특정 클라이언트에 메시지 전송"""
        client = self.clients.get(client_id)
        if client:
            message = {
                "type": event_type,
                "data": data,
                "timestamp": get_timestamp(),  # field 포맷 사용
                "version": self.version
            }
            try:
                await client.queue.put(message)
                return True
            except Exception as e:
                print(f"[ClientRegistry] 전송 실패 ({client_id}): {e}")
        return False
    
    def _save_aliases(self):
        """별칭 정보 파일로 저장"""
        # client.json에 별칭 정보 저장
        client_info = load_json_file(CLIENT_INFO_FILE) or {}
        if not isinstance(client_info, dict):
            client_info = {}
        client_info["aliases"] = self.aliases
        save_json_file(CLIENT_INFO_FILE, client_info)
    
    def _load_aliases(self):
        """별칭 정보 파일에서 로드"""
        client_info = load_json_file(CLIENT_INFO_FILE)
        if client_info and isinstance(client_info, dict):
            # "aliases" 키가 있으면 사용, 없으면 전체를 aliases로 간주 (하위 호환성)
            if "aliases" in client_info:
                aliases = client_info.get("aliases", {})
            else:
                # 기존 형식: {"client_id": "alias"} -> aliases로 변환
                aliases = {k: v for k, v in client_info.items() if k != "aliases"}
            
            if aliases:
                self.aliases = aliases
            else:
                self.aliases = {}
        else:
            self.aliases = {}

# 전역 클라이언트 레지스트리 인스턴스
client_registry = ClientRegistry()

