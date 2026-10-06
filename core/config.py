import os
import warnings
import logging
from pathlib import Path
from dotenv import load_dotenv

# Suppress SDK warnings and internal loggers
warnings.filterwarnings("ignore")
logging.getLogger("google").setLevel(logging.ERROR)
logging.getLogger("google.genai").setLevel(logging.ERROR)
try:
    from google.genai.models import Models, AsyncModels
    Models._logged_afc_warning = True
    AsyncModels._logged_afc_warning = True
except Exception:
    pass

# Base Directory of the Project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env
load_dotenv(BASE_DIR / ".env")

# Settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
DATA_DIR = BASE_DIR / "data"
HARDWARE_DB_PATH = DATA_DIR / "pc_parts_db.json"
