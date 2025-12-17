"""Pydantic 모델 정의"""
from .client import ClientInfo, AliasRequest, CommandRequest
from .auth import LoginRequest, LoginResponse
from .building import Building, BuildingCreate
from .floor import Floor, FloorCreate, FloorUpdate
from .media import MediaItem, MediaList, MediaUpload
from .theme import Theme, ThemeConfig, ThemeUpdate, ThemeColors
from .icon import Icon, IconList, IconCreate, IconUpdate
from .department import Department, DepartmentCreate, DepartmentUpdate
# from .slide import SlideImage

__all__ = [
    "ClientInfo",
    "AliasRequest",
    "CommandRequest",
    "LoginRequest",
    "LoginResponse",
    "Building",
    "BuildingCreate",
    "Floor",
    "FloorCreate",
    "FloorUpdate",
    "MediaItem",
    "MediaList",
    "MediaUpload",
    "Theme",
    "ThemeConfig",
    "ThemeUpdate",
    "ThemeColors",
    "Icon",
    "IconList",
    "IconCreate",
    "IconUpdate",
    "Department",
    "DepartmentCreate",
    "DepartmentUpdate",
    # "SlideImage",
]

