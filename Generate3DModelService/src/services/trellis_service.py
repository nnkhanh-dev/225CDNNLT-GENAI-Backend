import os
import uuid
import base64
import time
import requests
from .nvidia_client import API_KEY, TRELLIS_INVOKE_URL, OUTPUT_DIR

def call_trellis_api(payload_data: dict):
    if not API_KEY:
        raise RuntimeError("API_KEY is missing in environment")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    payload = {
        "slat_cfg_scale": 3,
        "ss_cfg_scale": 7.5,
        "slat_sampling_steps": 25,
        "ss_sampling_steps": 25,
        "seed": 0
    }
    payload.update(payload_data)

    max_retries = 3
    last_error = "Unknown error"

    for i in range(max_retries):
        try:
            resp = requests.post(TRELLIS_INVOKE_URL, headers=headers, json=payload)

            if resp.status_code == 500:
                time.sleep(5)
                continue

            if resp.status_code != 200:
                last_error = f"NVIDIA API Error {resp.status_code}: {resp.text}"
                if 400 <= resp.status_code < 500:
                    break
                time.sleep(2)
                continue

            data = resp.json()
            assets = data.get('assets', []) or data.get('artifacts', [])

            if assets:
                b64_data = assets[0].get('base64')
                if b64_data:
                    filename = f"{uuid.uuid4().hex}.glb"
                    filepath = os.path.join(OUTPUT_DIR, filename)
                    with open(filepath, "wb") as f:
                        f.write(base64.b64decode(b64_data))
                    return {"success": "true", "path": filepath}

            last_error = "API response does not contain assets data"
        except Exception as e:
            last_error = str(e)
            time.sleep(2)

    return {"success": "false", "error": last_error}
