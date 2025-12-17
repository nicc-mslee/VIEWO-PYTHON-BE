"""테마 관련 모델"""
from pydantic import BaseModel
from typing import Optional, Dict, Any

class ThemeColors(BaseModel):
    primary: str
    primaryDark: Optional[str] = None
    primaryLight: Optional[str] = None
    danger: Optional[str] = None
    dangerDark: Optional[str] = None
    dangerLight: Optional[str] = None
    success: Optional[str] = None
    successLight: Optional[str] = None
    warning: Optional[str] = None
    warningLight: Optional[str] = None
    sidebarBg: Optional[str] = None
    sidebarText: Optional[str] = None
    sidebarActiveText: Optional[str] = None
    sidebarActiveBg: Optional[str] = None
    bgMain: Optional[str] = None
    bgCard: Optional[str] = None
    textPrimary: Optional[str] = None
    textSecondary: Optional[str] = None
    borderDefault: Optional[str] = None
    logoColor: Optional[str] = None
    logoColorInverse: Optional[str] = None
    currentLocation: Optional[str] = None

class Theme(BaseModel):
    id: str
    name: str
    description: Optional[str] = ""
    colors: ThemeColors

class ThemeConfig(BaseModel):
    currentTheme: str
    themes: Dict[str, Theme]

class ThemeUpdate(BaseModel):
    currentTheme: Optional[str] = None
    themes: Optional[Dict[str, Theme]] = None

