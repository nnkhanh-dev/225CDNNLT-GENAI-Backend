import io
import base64
from fastapi import FastAPI, UploadFile, File
from PIL import Image

from schemas import GenerateRequest, CustomPromptRequest
from services.vision_service import validate_object_image
from services.trellis_service import call_trellis_api
from services.tripo_service import call_tripo_image_to_3d, call_tripo_text_to_3d

app = FastAPI(title="GenAI Nội Thất 3D API", root_path="/model")


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
    """
    Tạo 3D Model Đồ Vật trực tiếp từ File Ảnh sử dụng Tripo3D.
    Sử dụng Vision LLM để kiểm tra ảnh, sau đó dùng prompt cứng để điều hướng Tripo3D tập trung tạo đúng đồ vật, bỏ qua background.
    """
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        fmt = "png" if image.format == "PNG" else "jpeg"
        if image.mode in ("RGBA", "P") and fmt != "png":
            image = image.convert("RGB")

        buffer = io.BytesIO()
        image.save(buffer, format=fmt.upper(), quality=80 if fmt == "jpeg" else None)
        img_bytes = buffer.getvalue()

        base64_image = base64.b64encode(img_bytes).decode('utf-8')
        is_valid = validate_object_image(base64_image, f"image/{fmt}")
        
        if not is_valid:
            return {"success": "false", "error": "Ảnh cung cấp không hợp lệ hoặc không có đồ nội thất/vật thể rõ ràng để tạo 3D."}

        hardcoded_prompt = "A standalone 3D model of this furniture/object. Completely ignore any background or environment. Ensure it is fully generated in full 360 degrees on all sides."
        return call_tripo_image_to_3d(img_bytes, option_prompt=hardcoded_prompt, ext=fmt)

    except Exception as e:
        return {"success": "false", "error": f"Tripo3D processing error: {str(e)}"}


@app.post("/generate_room_from_image")
async def generate_room_from_image(file: UploadFile = File(...)):
    """
    Tạo 3D Model Căn Phòng bằng cách phớt lờ ảnh đầu vào và sử dụng trực tiếp Text-To-3D bằng Tripo3D.
    Sử dụng một prompt cực kỳ chi tiết miêu tả sa bàn căn phòng trống bọc kín.
    """
    try:
        # Vẫn read file để FastAPI không bị nghẽn Stream, nhưng ta sẽ CHỦ ĐỘNG BỎ QUA nội dung ảnh
        contents = await file.read()

        # Hardcoded prompt miêu tả cực kỳ chi tiết về 1 căn phòng theo yêu cầu
        hardcoded_prompt = (
            "A high-quality 3D architectural diorama of an empty room, viewed from an isometric angle. "
            "The room has exactly 4 solid walls made of beige painted plaster and a floor made of natural oak wood planks. "
            "There is strictly NO roof and NO ceiling, leaving the top completely completely open and visible. "
            "There is absolutely NO furniture, no objects, and no decorations inside. "
            "One of the walls has a large glass window with a modern grey metal frame. "
            "Clean topology, photorealistic textures, well-lit from the open top, simple and empty."
        )
        
        # Gọi thẳng hàm text-to-3d của Tripo thay vì image-to-3d
        return call_tripo_text_to_3d(prompt=hardcoded_prompt)

    except Exception as e:
        return {"success": "false", "error": f"Tripo3D processing error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
