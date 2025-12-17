"""건물 관련 모델"""
from pydantic import BaseModel
from typing import Optional

class Building(BaseModel):
    id: str
    name: str
    description: Optional[str] = ""
    createdAt: str
    updatedAt: str

class BuildingCreate(BaseModel):
    name: str
    description: Optional[str] = ""

