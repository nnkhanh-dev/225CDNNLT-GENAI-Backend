import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("API_KEY")
TRELLIS_INVOKE_URL = os.getenv("INVOKE_URL")
VISION_INVOKE_URL = os.getenv("VISION_INVOKE_URL")

# Output directory for generated 3D files
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
os.makedirs(OUTPUT_DIR, exist_ok=True)
