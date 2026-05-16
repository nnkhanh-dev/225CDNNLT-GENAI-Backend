import os
import uuid
import base64
import time
import logging
import requests
from .nvidia_client import API_KEY, TRELLIS_INVOKE_URL, OUTPUT_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def call_trellis_api(payload_data: dict):
    if not API_KEY:
        raise RuntimeError("API_KEY is missing in environment")

    logger.info(f"API_KEY loaded: {API_KEY[:10]}...")
    logger.info(f"INVOKE_URL: {TRELLIS_INVOKE_URL}")
    logger.info(f"OUTPUT_DIR: {OUTPUT_DIR}")
    logger.info(f"OUTPUT_DIR exists: {os.path.exists(OUTPUT_DIR)}")

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
    logger.info(f"Sending payload: {payload}")

    max_retries = 3
    last_error = "Unknown error"

    for i in range(max_retries):
        try:
            logger.info(f"Attempt {i+1}/{max_retries}...")
            resp = requests.post(TRELLIS_INVOKE_URL, headers=headers, json=payload, timeout=300)
            logger.info(f"Response status: {resp.status_code}")

            if resp.status_code == 500:
                last_error = f"NVIDIA API returned 500: {resp.text[:500]}"
                logger.warning(f"Server error (500), retrying... Response: {resp.text[:500]}")
                time.sleep(5)
                continue

            if resp.status_code != 200:
                last_error = f"NVIDIA API Error {resp.status_code}: {resp.text[:500]}"
                logger.error(f"API error: {last_error}")
                if 400 <= resp.status_code < 500:
                    break
                time.sleep(2)
                continue

            data = resp.json()
            logger.info(f"Response keys: {list(data.keys())}")
            assets = data.get('assets', []) or data.get('artifacts', [])
            logger.info(f"Assets found: {len(assets) if assets else 0}")

            if assets:
                b64_data = assets[0].get('base64')
                if b64_data:
                    filename = f"{uuid.uuid4().hex}.glb"
                    filepath = os.path.join(OUTPUT_DIR, filename)
                    logger.info(f"Saving model to: {filepath}")
                    with open(filepath, "wb") as f:
                        f.write(base64.b64decode(b64_data))
                    logger.info(f"Model saved successfully! Size: {os.path.getsize(filepath)} bytes")
                    return {"success": "true", "path": f"models/{filename}"}

            last_error = f"API response does not contain assets data. Keys: {list(data.keys())}"
            logger.warning(last_error)
        except Exception as e:
            last_error = str(e)
            logger.error(f"Exception: {last_error}")
            time.sleep(2)

    logger.error(f"All retries failed. Last error: {last_error}")
    return {"success": "false", "error": last_error}

