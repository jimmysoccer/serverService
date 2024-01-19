from pydantic import BaseModel, Field


class testResponse(BaseModel):
    message: str
