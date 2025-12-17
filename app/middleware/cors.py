"""CORS 설정"""
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import CORS_CONFIG

def setup_cors(app):
    """CORS 미들웨어 설정"""
    app.add_middleware(CORSMiddleware, **CORS_CONFIG)

