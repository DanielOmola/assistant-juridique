# utils/utils_logging.py
import logging
import os

# Configuration globale des logs
LOG_LEVEL = os.environ.get("ASSISTANT_LOG_LEVEL", "INFO")
LOG_FILE = "/content/drive/MyDrive/assistant-juridique/logs/assistant.log"

# Créer le dossier logs
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# Configuration du logger racine
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler() if os.environ.get("SHOW_LOGS", "False") == "True" else logging.NullHandler()
    ]
)

def get_logger(name):
    """Retourne un logger configuré"""
    return logging.getLogger(name)