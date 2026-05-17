import os
from typing import Any, Dict

import requests
from sqlalchemy.orm import Session

from models.document import Document
from schemas import DocumentCreate, DocumentUpdate


def _generate_prompt_service_url() -> str:
	return os.getenv("GENERATE_PROMPT_SERVICE_URL", "http://generatepromptservice:8001")


def _post_json(path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
	response = requests.post(f"{_generate_prompt_service_url()}{path}", json=payload, timeout=60)
	response.raise_for_status()
	return response.json()


def _index_document(document: Document) -> Dict[str, Any]:
	return _post_json(
		"/index-document",
		{
			"style": document.style,
			"document-path": document.document_path,
			"document-id": document.document_id,
		},
	)


def _delete_document_from_kb(document_id: str) -> Dict[str, Any]:
	return _post_json(
		"/delete-document",
		{"document-id": document_id},
	)


def create_document(db: Session, document_in: DocumentCreate):
	document = Document(
		name=document_in.name,
		style=document_in.style,
		document_path=document_in.document_path,
		document_id=document_in.document_id,
	)
	db.add(document)
	db.commit()
	db.refresh(document)
	_index_document(document)
	return document


def get_document(db: Session, id: int):
	return db.query(Document).filter(Document.id == id).first()


def get_documents(db: Session, skip: int = 0, limit: int = 100):
	return db.query(Document).offset(skip).limit(limit).all()


def update_document(db: Session, id: int, document_in: DocumentUpdate):
	document = get_document(db, id)
	if not document:
		return None

	old_document_id = document.document_id

	document.name = document_in.name
	document.style = document_in.style
	document.document_path = document_in.document_path
	document.document_id = document_in.document_id
	db.commit()
	db.refresh(document)
	_delete_document_from_kb(old_document_id)
	_index_document(document)
	return document


def delete_document(db: Session, id: int):
	document = get_document(db, id)
	if not document:
		return None

	_delete_document_from_kb(document.document_id)
	db.delete(document)
	db.commit()
	return document


def reindex_document(db: Session, id: int):
	document = get_document(db, id)
	if not document:
		return None

	_delete_document_from_kb(document.document_id)
	return _index_document(document)