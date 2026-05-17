from sqlalchemy.orm import Session
from models.style import Style
from schemas import StyleCreate
import os
import requests
from typing import Dict
from fastapi import HTTPException


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


def _generate_prompt_service_url() -> str:
    return os.getenv("GENERATE_PROMPT_SERVICE_URL", "http://generatepromptservice:8001")


def generate_prompt(db: Session, id: int) -> Dict[str, str]:
    """Call GeneratePromptService for the style identified by `id` and return the prompt."""
    style = get_style(db, id)
    if not style:
        return None

    resp = requests.post(f"{_generate_prompt_service_url()}/generate-prompt", json={"style": style.name}, timeout=180)
    if not resp.ok:
        try:
            detail = resp.json().get("detail", resp.text)
        except Exception:
            detail = resp.text
        raise HTTPException(status_code=resp.status_code, detail=detail)
    data = resp.json()

    prompt = data.get("prompt")
    if prompt:
        style.prompt = prompt
        db.commit()
        db.refresh(style)

    return data
