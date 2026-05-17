import logging
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from typing import List
from sqlalchemy.orm import Session

from config.database import SessionLocal, engine
from app.models.base import Base

import models.object as object_model
import models.document as document_model
import models.style as style_model

from services import (
	create_object, get_object, get_objects, update_object, delete_object,
	create_document, get_document, get_documents, update_document, delete_document, reindex_document, upload_file,
	create_style, get_style, get_styles, update_style, delete_style, generate_prompt,
)

from schemas import (
	ObjectCreate, ObjectRead, StyleCreate, StyleRead,
	DocumentCreate, DocumentRead, DocumentUpdate, DocumentReindexResponse, FileUploadResponse,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="OptionService", root_path="/option")


@app.get("/health")
def health():
	return {"status": "ok", "service": "OptionService"}


# Create tables
Base.metadata.create_all(bind=engine)


# Default seed data
DEFAULT_OBJECTS = ['Sofa', 'Chair', 'Table', 'Bed', 'Bookshelf', 'Cabinet', 'Lamp', 'Plant Pot']
DEFAULT_STYLES = [
	{"name": "Modern", "prompt": "modern style, clean lines, contemporary design"},
	{"name": "Classic", "prompt": "classic style, ornate details, traditional elegance"},
	{"name": "Minimalist", "prompt": "minimalist style, simple form, less is more"},
	{"name": "Industrial", "prompt": "industrial style, raw materials, metal and wood"},
	{"name": "Scandinavian", "prompt": "scandinavian style, light wood, cozy and functional"},
	{"name": "Vintage", "prompt": "vintage style, retro charm, antique finish"},
]


@app.on_event("startup")
def seed_database():
	"""Seed database with default objects and styles if empty."""
	db = SessionLocal()
	try:
		# Seed objects
		existing_objects = db.query(object_model.Object).count()
		if existing_objects == 0:
			logger.info("Seeding default objects...")
			for name in DEFAULT_OBJECTS:
				obj = object_model.Object(name=name)
				db.add(obj)
			db.commit()
			logger.info(f"Seeded {len(DEFAULT_OBJECTS)} objects.")

		# Seed styles
		existing_styles = db.query(style_model.Style).count()
		if existing_styles == 0:
			logger.info("Seeding default styles...")
			for s in DEFAULT_STYLES:
				style = style_model.Style(name=s["name"], prompt=s["prompt"])
				db.add(style)
			db.commit()
			logger.info(f"Seeded {len(DEFAULT_STYLES)} styles.")

		# Ensure documents table exists and document count is visible
		logger.info(f"Database ready: {db.query(object_model.Object).count()} objects, {db.query(style_model.Style).count()} styles, {db.query(document_model.Document).count()} documents")
	except Exception as e:
		logger.error(f"Error seeding database: {e}")
		db.rollback()
	finally:
		db.close()


def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


# ─── Object CRUD ───

@app.post("/objects", response_model=ObjectRead)
def create_object_endpoint(obj_in: ObjectCreate, db: Session = Depends(get_db)):
	existing = db.query(object_model.Object).filter(object_model.Object.name == obj_in.name).first()
	if existing:
		raise HTTPException(status_code=400, detail="Object with this name already exists")
	return create_object(db, obj_in)


@app.get("/objects", response_model=List[ObjectRead])
def list_objects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
	return get_objects(db, skip, limit)


@app.get("/objects/{id}", response_model=ObjectRead)
def get_object_endpoint(id: int, db: Session = Depends(get_db)):
	obj = get_object(db, id)
	if not obj:
		raise HTTPException(status_code=404, detail="Not found")
	return obj


@app.put("/objects/{id}", response_model=ObjectRead)
def update_object_endpoint(id: int, obj_in: ObjectCreate, db: Session = Depends(get_db)):
	obj = update_object(db, id, obj_in)
	if not obj:
		raise HTTPException(status_code=404, detail="Not found")
	return obj


@app.delete("/objects/{id}", response_model=ObjectRead)
def delete_object_endpoint(id: int, db: Session = Depends(get_db)):
	obj = delete_object(db, id)
	if not obj:
		raise HTTPException(status_code=404, detail="Not found")
	return obj


# ─── Style CRUD ───

@app.post("/styles", response_model=StyleRead)
def create_style_endpoint(style_in: StyleCreate, db: Session = Depends(get_db)):
	existing = db.query(style_model.Style).filter(style_model.Style.name == style_in.name).first()
	if existing:
		raise HTTPException(status_code=400, detail="Style with this name already exists")
	return create_style(db, style_in)


@app.get("/styles", response_model=List[StyleRead])
def list_styles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
	return get_styles(db, skip, limit)


@app.get("/styles/{id}", response_model=StyleRead)
def get_style_endpoint(id: int, db: Session = Depends(get_db)):
	style = get_style(db, id)
	if not style:
		raise HTTPException(status_code=404, detail="Not found")
	return style


@app.put("/styles/{id}", response_model=StyleRead)
def update_style_endpoint(id: int, style_in: StyleCreate, db: Session = Depends(get_db)):
	style = update_style(db, id, style_in)
	if not style:
		raise HTTPException(status_code=404, detail="Not found")
	return style


@app.delete("/styles/{id}", response_model=StyleRead)
def delete_style_endpoint(id: int, db: Session = Depends(get_db)):
	style = delete_style(db, id)
	if not style:
		raise HTTPException(status_code=404, detail="Not found")
	return style


@app.post("/styles/{id}/generate-prompt")
def generate_style_prompt_endpoint(id: int, db: Session = Depends(get_db)):
	try:
		result = generate_prompt(db, id)
	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(status_code=502, detail=f"Generate prompt failed: {str(e)}")
	if not result:
		raise HTTPException(status_code=404, detail="Style not found or generate failed")
	return result


# ─── Document CRUD ───

@app.post("/documents", response_model=DocumentRead)
def create_document_endpoint(document_in: DocumentCreate, db: Session = Depends(get_db)):
	existing = db.query(document_model.Document).filter(document_model.Document.name == document_in.name).first()
	if existing:
		raise HTTPException(status_code=400, detail="Document with this name already exists")

	return create_document(db, document_in)


@app.get("/documents", response_model=List[DocumentRead])
def list_documents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
	return get_documents(db, skip, limit)


@app.get("/documents/{id}", response_model=DocumentRead)
def get_document_endpoint(id: int, db: Session = Depends(get_db)):
	document = get_document(db, id)
	if not document:
		raise HTTPException(status_code=404, detail="Not found")
	return document


@app.put("/documents/{id}", response_model=DocumentRead)
def update_document_endpoint(id: int, document_in: DocumentUpdate, db: Session = Depends(get_db)):
	document = update_document(db, id, document_in)
	if not document:
		raise HTTPException(status_code=404, detail="Not found")
	return document


@app.delete("/documents/{id}", response_model=DocumentRead)
def delete_document_endpoint(id: int, db: Session = Depends(get_db)):
	document = delete_document(db, id)
	if not document:
		raise HTTPException(status_code=404, detail="Not found")
	return document


@app.post("/documents/{id}/reindex", response_model=DocumentReindexResponse)
def reindex_document_endpoint(id: int, db: Session = Depends(get_db)):
	result = reindex_document(db, id)
	if not result:
		raise HTTPException(status_code=404, detail="Not found")
	return DocumentReindexResponse(success=result.get("success", True), total_chunks=result.get("total_chunks", 0))


# ─── File Upload ───

@app.post("/upload", response_model=FileUploadResponse)
async def upload_file_endpoint(file: UploadFile = File(...)):
	try:
		content = await file.read()
		result = upload_file(content, file.filename)
		return FileUploadResponse(**result)
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

