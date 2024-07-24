from typing import Optional
from pydantic import BaseModel, validator


# Models
class User(BaseModel):
    username: str
    full_name: Optional[str] = None
    email: str = None
    hashed_password: str


class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    is_mfa: bool = False


class UpdateUser(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None
    is_enabled: Optional[bool] = None


class UserLogin(BaseModel):
    username: str
    password: str


class Sendotp(BaseModel):
    username: str
    password: str
    email: str


class Verifyotp(BaseModel):
    username: str
    otp: str


class ChangePassword(BaseModel):
    old_password: str
    new_password: str
    verify_new_password: str


class TokenData(BaseModel):
    username: Optional[str] = None


class MFAUpdate(BaseModel):
    username: Optional[str] = None
    is_mfa: bool


class EmailConfig(BaseModel):
    smtp_server: str
    smtp_port: int
    sender_email: str
    sender_name: str
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    use_tls: bool = True

    @validator('smtp_port')
    def validate_smtp_port(cls, v):
        if not (1 <= v <= 65535):
            raise ValueError('Port number must be between 1 and 65535')
        return v


class UpdateEmailConfig(BaseModel):
    smtp_server: Optional[str]
    smtp_port: Optional[int]
    sender_email: Optional[str]
    sender_name: Optional[str]
    smtp_username: Optional[str]
    smtp_password: Optional[str]
    use_tls: Optional[bool]
