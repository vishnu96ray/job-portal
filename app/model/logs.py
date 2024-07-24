from datetime import datetime
from typing import Any, Optional

from beanie import Document
from pydantic import BaseModel


class RequestBaseModel(BaseModel):
    method: Optional[str]
    path: Optional[str]
    ip: Optional[str]


class ResponseBaseModel(BaseModel):
    status: Optional[str]
    status_code: Optional[int]
    time_taken: Optional[str]
    body: Optional[Any]


class LoggingModel(Document):
    service_name: str
    description: str
    request_id: str
    request: RequestBaseModel
    response: ResponseBaseModel
    time_taken: Optional[str]
    user: Optional[str]
    request_time: datetime
    user: Optional[str]
    request_time: datetime
