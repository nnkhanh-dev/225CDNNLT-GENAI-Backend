from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="GeneratePromptService")

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
