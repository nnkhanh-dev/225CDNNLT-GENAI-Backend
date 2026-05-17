from vectorstore.chroma import add_documents, delete_documents_by_document_id


def delete_document_by_id(document_id: str) -> int:
	return delete_documents_by_document_id(document_id)


def index_document(style: str, document_id: str, document_path: str) -> int:
	delete_documents_by_document_id(document_id)
	return add_documents(style=style, document_id=document_id, document_path=document_path)