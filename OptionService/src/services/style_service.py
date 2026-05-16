from sqlalchemy.orm import Session
from models.style import Style
from schemas import StyleCreate


def create_style(db: Session, style_in: StyleCreate):
    style = Style(name=style_in.name, prompt=style_in.prompt)
    db.add(style)
    db.commit()
    db.refresh(style)
    return style


def get_style(db: Session, id: int):
    return db.query(Style).filter(Style.id == id).first()


def get_styles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Style).offset(skip).limit(limit).all()


def update_style(db: Session, id: int, style_in: StyleCreate):
    style = get_style(db, id)
    if not style:
        return None
    style.name = style_in.name
    style.prompt = style_in.prompt
    db.commit()
    db.refresh(style)
    return style


def delete_style(db: Session, id: int):
    style = get_style(db, id)
    if not style:
        return None
    db.delete(style)
    db.commit()
    return style
