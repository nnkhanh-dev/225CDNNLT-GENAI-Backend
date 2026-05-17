from functools import lru_cache
import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()


@lru_cache(maxsize=1)
def get_llm() -> ChatGoogleGenerativeAI:
	api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
	if not api_key:
		raise RuntimeError("Missing GOOGLE_API_KEY for Gemini chat model")

	return ChatGoogleGenerativeAI(
		model=os.getenv("GEMINI_CHAT_MODEL", "gemini-1.5-flash"),
		google_api_key=api_key,
		temperature=0.3,
	)