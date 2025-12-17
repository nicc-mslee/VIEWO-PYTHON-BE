"""아이콘 관련 모델"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class Icon(BaseModel):
    id: str
    name: Optional[str] = None
    path: str
    category: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

class IconList(BaseModel):
    icons: List[Icon]

class IconCreate(BaseModel):
    name: Optional[str] = None
    path: str
    category: Optional[str] = None

class IconUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None

