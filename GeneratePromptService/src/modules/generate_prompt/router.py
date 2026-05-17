from fastapi import APIRouter, HTTPException

from schemas import GeneratePromptRequest, GeneratePromptResponse

from .service import build_generate_prompt


router = APIRouter()


@router.post("/generate-prompt", response_model=GeneratePromptResponse)
def generate_prompt(request: GeneratePromptRequest):
	try:
		prompt = build_generate_prompt(request.style)
	except Exception as exc:
		raise HTTPException(status_code=500, detail=str(exc)) from exc

	return GeneratePromptResponse(prompt=prompt)