import os
from dotenv import load_dotenv

load_dotenv()

# Use environment variables for secrets in production.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"csv"}
