"""층 관련 모델"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class Floor(BaseModel):
    floor: int
    floorName: str
    buildingId: str
    floorImage: Optional[str] = None
    imageSize: Optional[Dict[str, int]] = None
    createdAt: str
    updatedAt: str
    iconTypes: Optional[Dict[str, Any]] = None
    elements: Optional[List[Dict[str, Any]]] = []
    currentLocation: Optional[Dict[str, Any]] = None

class FloorCreate(BaseModel):
    floor: int
    floorName: Optional[str] = None
    buildingId: str

class FloorUpdate(BaseModel):
    floorName: Optional[str] = None
    floorImage: Optional[str] = None
    imageSize: Optional[Dict[str, int]] = None
    iconTypes: Optional[Dict[str, Any]] = None
    elements: Optional[List[Dict[str, Any]]] = None
    currentLocation: Optional[Dict[str, Any]] = None

