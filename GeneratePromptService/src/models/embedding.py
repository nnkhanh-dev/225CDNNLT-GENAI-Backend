from functools import lru_cache
import os

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings


load_dotenv()


@lru_cache(maxsize=1)
def get_embeddings() -> GoogleGenerativeAIEmbeddings:
	api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
	if not api_key:
		raise RuntimeError("Missing GOOGLE_API_KEY for Gemini embeddings")

	return GoogleGenerativeAIEmbeddings(
		model=os.getenv("GEMINI_EMBEDDING_MODEL", "models/gemini-embedding-001"),
		google_api_key=api_key,
	)
