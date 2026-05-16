from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class Style(Base):
    __tablename__ = "styles"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True
    )

    prompt: Mapped[str] = mapped_column(
        String,
        nullable=False
    )