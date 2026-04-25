import os
from dotenv import load_dotenv

# Load .env from project root and support normal environment variables too.
_env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(_env_path)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip().strip('"').strip("'")

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"csv"}
