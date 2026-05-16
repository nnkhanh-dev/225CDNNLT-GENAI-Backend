from sqlalchemy.orm import Session
from models.object import Object
from schemas import ObjectCreate


def create_object(db: Session, obj_in: ObjectCreate):
    obj = Object(name=obj_in.name)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_object(db: Session, id: int):
    return db.query(Object).filter(Object.id == id).first()


def get_objects(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Object).offset(skip).limit(limit).all()


def update_object(db: Session, id: int, obj_in: ObjectCreate):
    obj = get_object(db, id)
    if not obj:
        return None
    obj.name = obj_in.name
    db.commit()
    db.refresh(obj)
    return obj


def delete_object(db: Session, id: int):
    obj = get_object(db, id)
    if not obj:
        return None
    db.delete(obj)
    db.commit()
    return obj
