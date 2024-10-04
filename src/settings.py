import logging
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
ENV_FILE = BASE_DIR / ".env"

load_dotenv(override=True)


NO_DATA = "No data"
COMMAND = ["vnstat", "--json", "a", "2"]

INTERFACE_NAME = os.getenv("INTERFACE_NAME", "eth0")
LOCAL_SERVICE_NAME = os.getenv("LOCAL_SERVICE_NAME", "local")
REMOTE_SERVICE_NAME = os.getenv("REMOTE_SERVICE_NAME", "remote")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

VPS_HOST = os.getenv("VPS_HOST")
VPS_PORT = int(os.getenv("VPS_PORT", 22))
VPS_USERNAME = os.getenv("VPS_USERNAME")
VPS_JSON_FILE_PATH = os.getenv("VPS_JSON_FILE_PATH", "$HOME/vnstat.json")
LOCAL_FILE_NAME = DATA_DIR / os.getenv("LOCAL_FILE_PATH", "vnstat_remote.json")
VPS_SSH_KEY_PATH = os.getenv("VPS_SSH_KEY_PATH", "$HOME/.ssh/id_rsa")

LOG_DIR = BASE_DIR / os.getenv("LOG_DIR", "logs")
LOG_FILE = LOG_DIR / os.getenv("LOG_FILE", "vnstat.log")
LOG_FILE_SIZE = int(os.getenv("LOG_FILE_SIZE", 1 * 1024 * 1024))
LOG_FILES_TO_KEEP = int(os.getenv("LOG_FILES_TO_KEEP", 5))
LOG_FORMAT = os.getenv(
    "LOG_FORMAT", "%(asctime)s - %(levelname)s - %(message)s"
)
LOG_DT_FMT = os.getenv("LOG_DT_FMT", "%Y-%m-%d %H:%M:%S")
LOG_FILE_LEVEL = os.getenv("LOG_FILE_LEVEL", logging.DEBUG)
