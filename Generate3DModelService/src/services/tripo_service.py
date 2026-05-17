import os
import time
import uuid
import requests
import logging
from .nvidia_client import OUTPUT_DIR, TRIPO_API_KEY

logger = logging.getLogger(__name__)

def call_tripo_image_to_3d(image_bytes: bytes, option_prompt: str = "", ext: str = "jpg"):
    if not TRIPO_API_KEY:
        raise RuntimeError("TRIPO_API_KEY is missing. Vui lòng cung cấp key của Tripo3D trong biến môi trường TRIPO_API_KEY.")
        
    headers = {
        "Authorization": f"Bearer {TRIPO_API_KEY}"
    }
    
    logger.info("Uploading image to Tripo3D...")
    upload_res = requests.post(
        "https://api.tripo3d.ai/v2/openapi/upload",
        headers=headers,
        files={"file": (f"image.{ext}", image_bytes, f"image/{ext}")}
    )
    if upload_res.status_code != 200:
        return {"success": "false", "error": f"Upload failed: {upload_res.text}"}
    
    up_data = upload_res.json()
    image_token = up_data.get("data", {}).get("image_token")
    if not image_token:
        return {"success": "false", "error": "No image token returned"}

    logger.info("Creating Tripo3D task...")
    
    file_payload = {
        "type": ext,
        "file_token": image_token
    }
    
    task_payload = {
        "type": "image_to_model",
        "file": file_payload
    }
    
    if option_prompt:
        task_payload["prompt"] = option_prompt

    task_res = requests.post(
        "https://api.tripo3d.ai/v2/openapi/task",
        headers=headers,
        json=task_payload
    )
    if task_res.status_code != 200:
        return {"success": "false", "error": f"Task creation failed: {task_res.text}"}
        
    task_id = task_res.json().get("data", {}).get("task_id")
    if not task_id:
        return {"success": "false", "error": "No task id returned"}

    logger.info(f"Polling task {task_id}...")
    while True:
        poll_res = requests.get(
            f"https://api.tripo3d.ai/v2/openapi/task/{task_id}",
            headers=headers
        )
        if poll_res.status_code != 200:
            return {"success": "false", "error": f"Polling failed: {poll_res.text}"}
            
        poll_data = poll_res.json().get("data", {})
        status = poll_data.get("status")
        
        if status == "success":
            logger.info("Task completed successfully!")
            
            model_url = None
            if "result" in poll_data and "pbr_model" in poll_data["result"]:
                model_url = poll_data["result"]["pbr_model"].get("url")
            elif "output" in poll_data and "pbr_model" in poll_data["output"]:
                model_out = poll_data["output"]["pbr_model"]
                if isinstance(model_out, str):
                    model_url = model_out
                elif isinstance(model_out, dict):
                    model_url = model_out.get("url")
            
            if not model_url:
                logger.error(f"Payload success returned: {poll_data}")
                return {"success": "false", "error": f"Task success but no model URL found. Payload: {poll_data}"}
                
            logger.info("Downloading .glb model...")
            try:
                dl_res = requests.get(model_url, timeout=60)
                if dl_res.status_code == 200:
                    filename = f"tripo_{uuid.uuid4().hex}.glb"
                    filepath = os.path.join(OUTPUT_DIR, filename)
                    with open(filepath, "wb") as f:
                        f.write(dl_res.content)
                    logger.info(f"Saved model to {filepath}")
                    return {"success": "true", "path": f"models/{filename}", "url": model_url}
                return {"success": "false", "error": "Failed to download model file", "url": model_url}
            except Exception as e:
                logger.error(f"Server download exception: {str(e)}")
                return {
                    "success": "true", 
                    "warning": "Server could not download the file due to network/DNS limits. Please use the direct URL.", 
                    "url": model_url
                }
            
        elif status in ["failed", "cancelled", "timeout", "error"]:
            return {"success": "false", "error": f"Task failed with status: {status}"}
            
        logger.info(f"Task status is '{status}'. Waiting 5 seconds...")
        time.sleep(5)
