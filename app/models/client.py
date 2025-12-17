"""클라이언트 관련 모델"""
from pydantic import BaseModel
from typing import Optional

class ClientInfo(BaseModel):
    clientId: str
    alias: Optional[str] = None
    connectedAt: str
    lastHeartbeat: str
    userAgent: Optional[str] = None
    ipAddress: Optional[str] = None
    isOnline: bool = True

class AliasRequest(BaseModel):
    alias: str

class CommandRequest(BaseModel):
    command: str
    params: Optional[dict] = None

