from langchain_core.documents import Document

from vectorstore.chroma import list_style_documents


def retrieve_style_context(style: str, limit: int = 4) -> list[Document]:
	return list_style_documents(style=style, limit=limit)