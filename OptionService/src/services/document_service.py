import os
from typing import Any, Dict
from pathlib import Path

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
			"document-id": str(document.id),
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
	)
	db.add(document)
	db.commit()
	db.refresh(document)
	try:
		_index_document(document)
	except Exception:
		db.delete(document)
		db.commit()
		raise
	return document


def get_document(db: Session, id: int):
	return db.query(Document).filter(Document.id == id).first()


def get_documents(db: Session, skip: int = 0, limit: int = 100):
	return db.query(Document).offset(skip).limit(limit).all()


def update_document(db: Session, id: int, document_in: DocumentUpdate):
	document = get_document(db, id)
	if not document:
		return None

	old_document_id = str(document.id)
	old_name = document.name
	old_style = document.style
	old_document_path = document.document_path

	document.name = document_in.name
	document.style = document_in.style
	document.document_path = document_in.document_path
	db.commit()
	db.refresh(document)
	try:
		_delete_document_from_kb(old_document_id)
		_index_document(document)
	except Exception:
		document.name = old_name
		document.style = old_style
		document.document_path = old_document_path
		db.commit()
		raise
	return document


def delete_document(db: Session, id: int):
	document = get_document(db, id)
	if not document:
		return None

	_delete_document_from_kb(str(document.id))
	db.delete(document)
	db.commit()
	return document


def reindex_document(db: Session, id: int):
	document = get_document(db, id)
	if not document:
		return None

	_delete_document_from_kb(str(document.id))
	return _index_document(document)


def upload_file(file_content: bytes, filename: str) -> Dict[str, Any]:
	"""Upload file and return file path."""
	upload_dir = Path("uploads")
	upload_dir.mkdir(exist_ok=True)
	
	file_path = upload_dir / filename
	with open(file_path, "wb") as f:
		f.write(file_content)
	
	return {
		"filename": filename,
		"file_path": str(file_path),
		"file_size": len(file_content),
	}
