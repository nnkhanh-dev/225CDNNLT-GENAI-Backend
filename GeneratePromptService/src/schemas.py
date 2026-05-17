from pydantic import BaseModel, ConfigDict, Field


class GeneratePromptRequest(BaseModel):
	style: str = Field(min_length=1)


class GeneratePromptResponse(BaseModel):
	prompt: str


class IndexDocumentRequest(BaseModel):
	model_config = ConfigDict(populate_by_name=True)

	style: str = Field(min_length=1)
	document_path: str = Field(alias="document-path", min_length=1)
	document_id: str = Field(alias="document-id", min_length=1)


class IndexDocumentResponse(BaseModel):
	success: bool
	total_chunks: int


class DeleteDocumentRequest(BaseModel):
	model_config = ConfigDict(populate_by_name=True)

	document_id: str = Field(alias="document-id", min_length=1)


class DeleteDocumentResponse(BaseModel):
	success: bool
	deleted_chunks: int