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

def get_room_description(base64_image: str, mime_type: str) -> str:
    """
    Use NVIDIA Llama Vision model to describe a room image for 3D generation.
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
                        "text": "Act as an expert 3D asset prompt engineer for a text-to-3D AI model (Trellis). First, analyze the image. If the image does NOT clearly depict a room or interior space, you MUST reply ONLY with the exact word 'FALSE'.\n\nIf it IS a room, write a highly descriptive, optimized prompt to generate a 3D model of this exact room. Follow these strict rules for the 3D prompt:\n1. Start directly with 'A highly detailed 3D model of a [room type] interior, open top view without any ceiling...'\n2. Describe the overall layout (a complete room structure with 4 walls minus the ceiling).\n3. Detail the flooring and walls (materials, colors, textures like 'oak wood floor', 'white painted walls').\n4. Describe the main furniture, fixtures, and interior decor, including their specific positions, styles, and colors.\n5. If any parts of the room are hidden, make logical architectural assumptions to complete a cohesive 360-degree room structure.\n6. Add 3D-specific keywords at the end: 'architectural visualization, realistic materials, octane render, 4k resolution, isometric diorama style, highly detailed'.\n\nReturn EXACTLY and ONLY the final prompt text. No conversational filler, no introductions."
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
        "max_tokens": 512,
        "temperature": 0.3
    }

    resp = requests.post(VISION_INVOKE_URL, headers=headers, json=payload)
    if resp.status_code != 200:
        raise RuntimeError(f"Vision API error: {resp.status_code} {resp.text}")

    data = resp.json()
    return data['choices'][0]['message']['content']
