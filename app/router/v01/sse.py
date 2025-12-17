"""SSE 라우터"""
from fastapi import APIRouter, Request, Query
from fastapi.responses import StreamingResponse
import json
import asyncio
from app.services.client_registry import client_registry
from app.utils.datetime_utils import get_timestamp
from typing import Optional

sse_router = APIRouter(prefix="/sse", tags=["SSE"])

# app 인스턴스는 main.py에서 설정
_app_instance: Optional[object] = None

def set_app_instance(app):
    """app 인스턴스 설정 (main.py에서 호출)"""
    global _app_instance
    _app_instance = app

@sse_router.get("/events")
async def sse_events(
    request: Request,
    clientId: str = Query(..., description="클라이언트 UUID")
):
    """SSE 이벤트 스트림"""
    
    async def event_generator():
        # 클라이언트 등록
        user_agent = request.headers.get("user-agent")
        ip_address = request.client.host if request.client else None
        client = await client_registry.register(clientId, user_agent, ip_address)
        
        try:
            # 연결 성공 이벤트 전송
            connection_data = {
                "status": "connected",
                "clientId": clientId,
                "alias": client.alias,
                "serverTime": get_timestamp(),  # field 포맷 사용
                "serverVersion": client_registry.version
            }
            yield f"event: connection\ndata: {json.dumps(connection_data, ensure_ascii=False)}\n\n"
            # app이 설정되지 않았거나 종료 중이 아닐 때 계속 실행
            while True:
                if _app_instance and getattr(_app_instance.state, 'is_shutting_down', False):
                    break
                # 클라이언트 연결 상태 확인
                if await request.is_disconnected():
                    break
                
                try:
                    # 메시지 대기 (30초 타임아웃)
                    message = await asyncio.wait_for(client.queue.get(), timeout=30)
                    yield f"event: {message['type']}\ndata: {json.dumps(message, ensure_ascii=False)}\n\n"
                except asyncio.TimeoutError:
                    # 하트비트 전송
                    client_registry.update_heartbeat(clientId)
                    heartbeat_data = {
                        "clientId": clientId,
                        "timestamp": get_timestamp(),  # field 포맷 사용
                        "serverVersion": client_registry.version
                    }
                    yield f"event: heartbeat\ndata: {json.dumps(heartbeat_data, ensure_ascii=False)}\n\n"
                    
        finally:
            # 클라이언트 해제
            client_registry.unregister(clientId)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*"
        }
    )

