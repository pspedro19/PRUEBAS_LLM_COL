from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: EmailStr
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    level: Optional[int] = None
    xp: Optional[int] = None
    rank: Optional[str] = None
    clan_id: Optional[str] = None
    stats: Optional[Dict[str, int]] = None


class UserInDBBase(UserBase):
    id: str
    level: int = 1
    xp: int = 0
    rank: str = "Bronce I"
    clan_id: Optional[str] = None
    stats: Dict[str, int] = {}
    is_active: bool = True
    created_at: datetime

    class Config:
        from_attributes = True


class User(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    password_hash: str


class ClanBase(BaseModel):
    name: str
    description: Optional[str] = None


class ClanCreate(ClanBase):
    pass


class Clan(ClanBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserWithClan(User):
    clan: Optional[Clan] = None


class UserStats(BaseModel):
    level: int
    xp: int
    rank: str
    stats: Dict[str, int]
    clan: Optional[Clan] = None 