from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Document(Base):
	__tablename__ = "documents"

	id: Mapped[int] = mapped_column(
		Integer,
		primary_key=True,
		index=True,
	)

	name: Mapped[str] = mapped_column(
		String(255),
		nullable=False,
		unique=True,
	)

	style: Mapped[str] = mapped_column(
		String(255),
		nullable=False,
	)

	document_path: Mapped[str] = mapped_column(
		String(1024),
		nullable=False,
	)

	document_id: Mapped[str] = mapped_column(
		String(255),
		nullable=False,
		unique=True,
		index=True,
	)