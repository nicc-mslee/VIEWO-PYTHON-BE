"""부서 관련 모델"""
from pydantic import BaseModel
from typing import Optional

class Department(BaseModel):
    building: Optional[str] = None
    floor: Optional[str] = None
    department: Optional[str] = None
    team: Optional[str] = None
    position: Optional[str] = None
    task: Optional[str] = None

class DepartmentCreate(BaseModel):
    building: Optional[str] = None
    floor: Optional[str] = None
    department: Optional[str] = None
    team: Optional[str] = None
    position: Optional[str] = None
    task: Optional[str] = None

class DepartmentUpdate(BaseModel):
    building: Optional[str] = None
    floor: Optional[str] = None
    department: Optional[str] = None
    team: Optional[str] = None
    position: Optional[str] = None
    task: Optional[str] = None

