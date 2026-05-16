from pydantic import BaseModel
from typing import Optional


class ObjectBase(BaseModel):
    name: str


class ObjectCreate(ObjectBase):
    pass


class ObjectRead(ObjectBase):
    id: int

    class Config:
        orm_mode = True


class StyleBase(BaseModel):
    name: str
    prompt: str


class StyleCreate(StyleBase):
    pass


class StyleRead(StyleBase):
    id: int

    class Config:
        orm_mode = True
