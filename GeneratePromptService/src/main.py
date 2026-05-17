from datetime import datetime
from fastapi import FastAPI

from modules.generate_prompt.router import router as generate_prompt_router
from modules.manage_document.router import router as manage_document_router


app = FastAPI(title="GeneratePromptService")
app.include_router(generate_prompt_router)
app.include_router(manage_document_router)

STARTUP_TIME = datetime.utcnow()


@app.get("/health")
def health():
	return {
		"status": "ok",
		"service": "GeneratePromptService",
		"uptime_seconds": (datetime.utcnow() - STARTUP_TIME).total_seconds(),
		"time": datetime.utcnow().isoformat() + "Z",
	}

if __name__ == "__main__":
	import uvicorn

	uvicorn.run(app, host="0.0.0.0", port=8001)
