from pydantic import BaseModel

class GenerateRequest(BaseModel):
    object: str
    style: str

class CustomPromptRequest(BaseModel):
    description: str
