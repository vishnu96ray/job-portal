from datetime import datetime
from typing import Optional

from beanie import Document
from pydantic import Field


class UserDocument(Document):
    username: str
    password: str
    email: Optional[str] = None
    role: str
    hashed_password: str
    is_verify: bool = False
    is_enabled: bool = False
    is_delete: bool = False
    is_mfa: bool = False
    otp: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Token(Document):
    username: str
    token: str
    active: bool
    created_at: datetime = Field(default_factory=datetime.utcnow)


class EmailConfigDocument(Document):
    smtp_server: str
    smtp_port: int
    sender_email: str
    sender_name: str
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    use_tls: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

    class Settings:
        collection = "email_configs"
