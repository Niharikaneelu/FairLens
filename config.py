import os
from dotenv import load_dotenv
 
load_dotenv()
 
# Load API key from .env file — never hardcode secrets here
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
 
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"csv"}
 