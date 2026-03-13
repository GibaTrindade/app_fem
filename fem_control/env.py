from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent


def load_environment():
    load_dotenv(BASE_DIR / ".env")
