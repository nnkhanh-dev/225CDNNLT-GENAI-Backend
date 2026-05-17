from functools import lru_cache
from pathlib import Path
from typing import Iterable
import os

from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from models.embedding import get_embeddings


load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_PERSIST_DIRECTORY = Path(os.getenv("CHROMA_PERSIST_DIRECTORY", BASE_DIR / "chroma_db"))
COLLECTION_NAME = "generate_prompt_styles"
SUPPORTED_TEXT_EXTENSIONS = {".txt", ".md", ".markdown", ".rst", ".json", ".csv", ".html", ".htm"}


def normalize_style(style: str) -> str:
	return style.strip().lower()


@lru_cache(maxsize=1)
def get_vectorstore() -> Chroma:
	return Chroma(
		collection_name=COLLECTION_NAME,
		persist_directory=str(DEFAULT_PERSIST_DIRECTORY),
		embedding_function=get_embeddings(),
	)


def _resolve_document_path(document_path: str) -> Path:
	path = Path(document_path).expanduser()
	if not path.is_absolute():
		path = (BASE_DIR / path).resolve()

	return path


def _read_pdf_text(path: Path) -> str:
	reader = PdfReader(str(path))
	parts = []
	for page in reader.pages:
		parts.append(page.extract_text() or "")

	return "\n".join(parts).strip()


def _read_text_file(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _load_file_documents(path: Path, style: str, document_id: str) -> list[Document]:
	if path.suffix.lower() == ".pdf":
		text = _read_pdf_text(path)
	else:
		text = _read_text_file(path)

	if not text.strip():
		return []

	return [
		Document(
			page_content=text,
			metadata={
				"style": normalize_style(style),
				"document_id": document_id,
				"source": str(path),
			},
		)
	]


def load_source_documents(document_path: str, style: str, document_id: str) -> list[Document]:
	path = _resolve_document_path(document_path)
	if not path.exists():
		raise FileNotFoundError(f"Document path not found: {document_path}")

	if path.is_dir():
		documents: list[Document] = []
		for file_path in sorted(path.rglob("*")):
			if not file_path.is_file():
				continue
			if file_path.suffix.lower() not in SUPPORTED_TEXT_EXTENSIONS and file_path.suffix.lower() != ".pdf":
				continue
			documents.extend(_load_file_documents(file_path, style, document_id))
		return documents

	if path.suffix.lower() != ".pdf" and path.suffix.lower() not in SUPPORTED_TEXT_EXTENSIONS:
		raise ValueError(f"Unsupported document type: {path.suffix}")

	return _load_file_documents(path, style, document_id)


def split_documents(documents: list[Document]) -> list[Document]:
	splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=150)
	chunks = splitter.split_documents(documents)
	for index, chunk in enumerate(chunks):
		chunk.metadata["chunk_index"] = index

	return chunks


def add_documents(style: str, document_id: str, document_path: str) -> int:
	documents = load_source_documents(document_path, style, document_id)
	if not documents:
		return 0

	chunks = split_documents(documents)
	if not chunks:
		return 0

	vectorstore = get_vectorstore()
	vectorstore.add_documents(chunks, ids=[f"{document_id}-{index}" for index in range(len(chunks))])
	return len(chunks)


def delete_documents_by_document_id(document_id: str) -> int:
	vectorstore = get_vectorstore()
	stored = vectorstore.get(where={"document_id": document_id})
	ids = stored.get("ids", []) if stored else []
	if not ids:
		return 0

	vectorstore.delete(ids=ids)
	return len(ids)


def list_style_documents(style: str, limit: int = 4) -> list[Document]:
	vectorstore = get_vectorstore()
	style_key = normalize_style(style)
	results = vectorstore.similarity_search(style, k=limit, filter={"style": style_key})
	if results:
		return results

	return vectorstore.similarity_search(style, k=limit)