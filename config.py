import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR=Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
JSON_FILE = DATA_DIR / "raw_supabase_data.json"

def ensure_dirs():
    """Run this to make sure folders exist before saving files"""
    try:
        DATA_DIR.mkdir(exist_ok=True)
        MODELS_DIR.mkdir(exist_ok=True)
    except:
        raise FileNotFoundError


