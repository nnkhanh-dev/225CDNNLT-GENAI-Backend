import requests
from .nvidia_client import API_KEY, VISION_INVOKE_URL

def get_image_description(base64_image: str, mime_type: str) -> str:
    """
    Use NVIDIA Llama Vision model to describe an image for 3D generation.
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
                        "text": "Describe this furniture in extreme detail. Focus on its shape, style, material, color, and key features. Keep it to one detailed paragraph suitable for a 3D generative model."
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
        "max_tokens": 256,
        "temperature": 0.3
    }

    resp = requests.post(VISION_INVOKE_URL, headers=headers, json=payload)
    if resp.status_code != 200:
        raise RuntimeError(f"Vision API error: {resp.status_code} {resp.text}")

    data = resp.json()
    return data['choices'][0]['message']['content']
