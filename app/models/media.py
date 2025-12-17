"""미디어 관련 모델"""
from pydantic import BaseModel
from typing import Optional, List

class MediaItem(BaseModel):
    id: int
    filename: str
    path: str
    order: int
    created_at: str

class MediaList(BaseModel):
    images: List[MediaItem]

class MediaUpload(BaseModel):
    order: Optional[int] = None

