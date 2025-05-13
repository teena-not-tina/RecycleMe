
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict
from datetime import datetime

class User(BaseModel):
    id: str
    email: EmailStr
    display_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    points: int = 0
    is_active: bool = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    display_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    
class PointsTransaction(BaseModel):
    id: str
    user_id: str
    amount: int
    transaction_type: str  # "earn" 또는 "spend"
    description: str
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict = Field(default_factory=dict)

class PointsBalance(BaseModel):
    user_id: str
    total_points: int
    recent_transactions: List[PointsTransaction] = []

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str

class TokenData(BaseModel):
    user_id: Optional[str] = None