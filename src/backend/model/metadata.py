from pydantic import BaseModel, Field


class Health(BaseModel):
    status: str = Field(default="ok")


class Version(BaseModel):
    version: str
