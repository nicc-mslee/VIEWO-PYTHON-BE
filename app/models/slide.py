"""슬라이드 관련 모델"""
from pydantic import BaseModel

class SlideImage(BaseModel):
    id: int
    filename: str
    path: str
    order: int
    created_at: str

