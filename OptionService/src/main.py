from fastapi import FastAPI, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session

from config.database import SessionLocal, engine
from app.models.base import Base

import models.object as object_model
import models.style as style_model

from services import (
	create_object, get_object, get_objects, update_object, delete_object,
	create_style, get_style, get_styles, update_style, delete_style,
)

from schemas import (
	ObjectCreate, ObjectRead, StyleCreate, StyleRead,
)

app = FastAPI(title="OptionService")


@app.get("/health")
def health():
	return {"status": "ok", "service": "OptionService"}


Base.metadata.create_all(bind=engine)


def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


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

