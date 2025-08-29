from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class JSIHRecord(BaseModel):
    date: datetime
    number: float


class JSIHRecordCreate(BaseModel):
    date: str  # ISO format string
    number: float


class JSIHRecordResponse(BaseModel):
    id: str
    date: datetime
    number: float
