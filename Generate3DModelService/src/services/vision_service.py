import requests
from .nvidia_client import API_KEY, VISION_INVOKE_URL

def validate_object_image(base64_image: str, mime_type: str) -> bool:
    """
    Sử dụng NVIDIA Llama Vision để kiểm tra ảnh. Chỉ trả về True nếu là đồ vật hợp lệ, ngược lại False.
    """
    if not API_KEY:
        raise RuntimeError("API_KEY is missing in environment")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "meta/llama-3.2-90b-vision-instruct",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Analyze this image. If it depicts a standalone object or furniture suitable for 3D modeling, reply EXACTLY and ONLY with 'TRUE'. Otherwise, reply EXACTLY and ONLY with 'FALSE'."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 10,
        "temperature": 0.0
    }

    resp = requests.post(VISION_INVOKE_URL, headers=headers, json=payload)
    if resp.status_code != 200:
        raise RuntimeError(f"Vision API error: {resp.status_code} {resp.text}")

    data = resp.json()
    result_text = data['choices'][0]['message']['content'].strip().upper()
    return "TRUE" in result_text