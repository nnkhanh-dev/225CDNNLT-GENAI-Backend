import io
import base64
from fastapi import FastAPI, UploadFile, File
from PIL import Image

from schemas import GenerateRequest, CustomPromptRequest
from services.vision_service import get_image_description, get_room_description
from services.trellis_service import call_trellis_api

app = FastAPI(title="GenAI Nội Thất 3D API")


@app.get("/health")
def health():
    return {"status": "ok", "service": "Generate3DModelService"}


@app.post("/generate")
def generate_3d_model(request: GenerateRequest):
    prompt = f"A 3d model of a {request.object} in {request.style} style, high quality, 4k resolution"
    return call_trellis_api({"prompt": prompt})


@app.post("/generate_custom")
def generate_custom_prompt(request: CustomPromptRequest):
    return call_trellis_api({"prompt": request.description})


@app.post("/generate_from_image")
async def generate_from_image(file: UploadFile = File(...)):
    """Generate a 3D model from an uploaded image by first asking the Vision model
    to describe the image, then feeding that description to Trellis.
    """
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        image.thumbnail((800, 800))
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=80)
        base64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

        description = get_image_description(base64_image, "image/jpeg")
        return call_trellis_api({"prompt": description})

    except Exception as e:
        return {"success": "false", "error": f"Image processing error: {str(e)}"}


@app.post("/generate_room_from_image")
async def generate_room_from_image(file: UploadFile = File(...)):
    """Generate a 3D model of a room from an uploaded image."""
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        image.thumbnail((800, 800))
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=80)
        base64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

        description = get_room_description(base64_image, "image/jpeg")
        
        desc_upper = description.strip().upper()
        if "FALSE" in desc_upper or "NOT DEPICT" in desc_upper or "NOT A ROOM" in desc_upper:
            return {"success": "false", "error": "Ảnh cung cấp không phải là một căn phòng."}

        return call_trellis_api({"prompt": description})

    except Exception as e:
        return {"success": "false", "error": f"Image processing error: {str(e)}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
