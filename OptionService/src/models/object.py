from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class Object(Base):
    __tablename__ = "objects"

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