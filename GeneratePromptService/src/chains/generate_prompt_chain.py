from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from models.llm import get_llm
from prompts.system_prompt import SYSTEM_PROMPT
from retrievers.retriever import retrieve_style_context


def _format_context(style: str) -> str:
	documents = retrieve_style_context(style)
	if not documents:
		return "No knowledge base context was found for this style."

	parts = []
	for index, document in enumerate(documents, start=1):
		parts.append(f"Source {index}: {document.page_content.strip()}")

	return "\n\n".join(parts)


def generate_style_prompt(style: str) -> str:
	context = _format_context(style)
	chat_prompt = ChatPromptTemplate.from_messages(
		[
			("system", SYSTEM_PROMPT),
			(
				"human",
				"Style: {style}\n\nKnowledge base context:\n{context}\n\nCreate the final Trellis prompt.",
			),
		]
	)
	chain = chat_prompt | get_llm() | StrOutputParser()
	return chain.invoke({"style": style.strip(), "context": context}).strip()