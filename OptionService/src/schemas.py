from pydantic import BaseModel, ConfigDict


class ObjectBase(BaseModel):
    name: str


class ObjectCreate(ObjectBase):
    pass


class ObjectRead(ObjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class StyleBase(BaseModel):
    name: str
    prompt: str


class StyleCreate(StyleBase):
    pass


class StyleRead(StyleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class DocumentBase(BaseModel):
    name: str
    style: str
    document_path: str


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(DocumentBase):
    pass


class DocumentRead(DocumentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class DocumentReindexResponse(BaseModel):
    success: bool
    total_chunks: int


class FileUploadResponse(BaseModel):
    filename: str
    file_path: str
    file_size: int
