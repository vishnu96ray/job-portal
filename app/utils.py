import re
from datetime import datetime, timedelta
from typing import Optional

import aiohttp
import async_timeout
from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.model.user import UserDocument
from app.schemas import user


# def create_url_from_register_service(service: RegisterService,
#                                      api_path: str,
#                                      suffix: str = None):
#     """Create a URL from a registered service"""
#     if service.remote_port:
#         base_url = f"{service.protocol}://{service.remote_ip}:{service.remote_port}"  # noqa
#     else:
#         base_url = f"{service.protocol}://{service.remote_ip}"

#     if suffix:
#         return f"{base_url}{api_path.replace(service.local_prefix, service.remote_prefix)}{suffix}"  # noqa

#     return f"{base_url}{api_path.replace(service.local_prefix, service.remote_prefix)}"  # noqa


def create_redoc(redoc_path):
    """
    Create a redoc html file from the given redoc path.
    """
    redoc_html = f"""
<!DOCTYPE html>
<html>
  <head>
    <title>ReDoc</title>
    <!-- Needed for adaptive design -->
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- ReDoc doesn't change outer page styles -->
    <style>
      body {{
        margin: 0;
        padding: 0;
      }}
    </style>
  </head>
  <body>
    <redoc spec-url='/{redoc_path}'></redoc>
    <script src="/static/js/redoc.standalone.js"></script>
  </body>
</html>
"""

    return redoc_html


async def make_request(url: str,
                       method: str,
                       data: dict = None,
                       headers: dict = None):
    """
    Make a request to the given url with the given method and data.
    """
    if not data:
        data = {}

    with async_timeout.timeout(40):
        async with aiohttp.ClientSession() as session:
            request = getattr(session, method)
            if url.startswith('https://'):
                print(url)
                async with request(
                        url,
                        json=data,
                        headers=headers,
                        verify_ssl=False,
                ) as response:
                    try:
                        data = await response.json()
                    except aiohttp.ContentTypeError:
                        data = await response.text()
                    return (data, response.status)
            elif url.startswith('http://'):
                print(url)
                async with request(
                        url,
                        json=data,
                        headers=headers,
                ) as response:
                    try:
                        data = await response.json()
                    except aiohttp.ContentTypeError:
                        data = await response.text()
                    return (data, response.status)


def get_path_from_request(request: Request) -> tuple[str, str | None]:
    """
    return api path and suffix from request
    """
    suffix = None
    if len(request.url.path.split("/")) >= 3:
        _, api_path, suffix = request.url.path.split("/", 2)
    else:
        _, api_path = request.url.path.split("/", 1)
    return "/" + api_path, suffix


# async def get_service_name_from_request(
#         request: Request) -> RegisterService | None:
#     """
#     return service name from request
#     """
#     api_path, _ = get_path_from_request(request)
#     return await RegisterService.find_one(
#         RegisterService.local_prefix == api_path,
#         RegisterService.is_deleted == False,  # noqa
#     )


def convert_seconds(seconds: int) -> str:
    """Convert seconds to a human-readable format."""
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.2f} minutes" if minutes != 1 else "1 minute"
    elif seconds < 86400:
        hours = seconds / 3600
        return f"{hours:.2f} hours" if hours != 1 else "1 hour"
    else:
        days = seconds / 86400
        return f"{days:.2f} days" if days != 1 else "1 day"


# Constants
# trunk-ignore(bandit/B105)
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3600
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def is_valid_email(email: str) -> bool:
    pat = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"  # noqa
    if re.match(pat, email):
        return True
    return False


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)


class TokenManager:

    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict,
                            expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=30)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_access_token(x_auth_token: str = Header(None)):
        if x_auth_token is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="x-auth-token header missing",
            )
        try:
            payload = jwt.decode(x_auth_token,
                                 SECRET_KEY,
                                 algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid x_auth_token",
                )
            return user.TokenData(username=username)
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid x_auth_token")

    @staticmethod
    def get_current_user(token: str = Depends(Header(None))):
        token_data = TokenManager.decode_access_token(token)
        user = UserDocument.get(token_data.user)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid token")
        return user
