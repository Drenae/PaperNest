from pathlib import Path


APP_NAME = "PaperNest"

USER_DOCUMENTS = Path.home() / "Documents"

# Ancienne organisation de PaperNest.
LEGACY_STORAGE_ROOT = USER_DOCUMENTS
LEGACY_DATABASE_PATH = LEGACY_STORAGE_ROOT / "papernest.db"

# Nouvelle organisation.
APP_ROOT = USER_DOCUMENTS / APP_NAME

STORAGE_ROOT = APP_ROOT / "archives"
DATA_ROOT = APP_ROOT / "data"
LOG_ROOT = APP_ROOT / "logs"
BACKUP_ROOT = APP_ROOT / "sauvegardes"
TRASH_ROOT = APP_ROOT / "corbeille"
UNSORTED_ROOT = APP_ROOT / "non_classes"

DB_PATH = DATA_ROOT / "papernest.db"

SUPPORTED_TEXT_EXTENSIONS = {
    ".pdf",
}

COPY_BUFFER_SIZE = 1024 * 1024

DEFAULT_CATEGORIES = [
    (
        "01_Identité",
        "Identité",
        "BADGE_ROUNDED",
        "BLUE_600",
        "BLUE_50",
    ),
    (
        "02_Logement",
        "Logement",
        "OTHER_HOUSES_ROUNDED",
        "GREEN_600",
        "GREEN_50",
    ),
    (
        "03_Santé",
        "Santé",
        "HEALTH_AND_SAFETY_ROUNDED",
        "RED_600",
        "RED_50",
    ),
    (
        "04_Fiscalité",
        "Fiscalité",
        "REQUEST_QUOTE_ROUNDED",
        "AMBER_700",
        "AMBER_50",
    ),
    (
        "05_Banque",
        "Banque",
        "ACCOUNT_BALANCE_ROUNDED",
        "PURPLE_600",
        "PURPLE_50",
    ),
]