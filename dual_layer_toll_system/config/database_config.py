import os
from pathlib import Path

class DatabaseConfig:
    # Database paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    
    # SQLite database
    PLATES_DB_PATH = DATA_DIR / "plates.db"
    
    # Text-based databases (fallback)
    AUTHORIZED_PLATES_FILE = DATA_DIR / "authorized_plates.txt"
    VEHICLES_DATABASE_FILE = DATA_DIR / "vehicles_database.json"
    TOLL_RATES_FILE = DATA_DIR / "toll_rates.json"
    
    # Log files
    LOGS_DIR = BASE_DIR / "logs"
    DETECTION_LOG = LOGS_DIR / "detections.log"
    VIOLATION_LOG = LOGS_DIR / "violations.log"
    SYSTEM_LOG = LOGS_DIR / "system.log"
    
    # Ensure directories exist
    DATA_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)
    
    # Database connection settings
    DB_CONNECTION_TIMEOUT = 30
    DB_MAX_RETRIES = 3
    
    # Table schemas
    AUTHORIZED_PLATES_SCHEMA = """
        CREATE TABLE IF NOT EXISTS authorized_plates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plate_number TEXT UNIQUE NOT NULL,
            owner_name TEXT,
            vehicle_type TEXT,
            registration_date TEXT,
            expiry_date TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """
    
    DETECTION_HISTORY_SCHEMA = """
        CREATE TABLE IF NOT EXISTS detection_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plate_number TEXT NOT NULL,
            detection_time TEXT DEFAULT CURRENT_TIMESTAMP,
            confidence_score REAL,
            image_path TEXT,
            is_authorized BOOLEAN,
            violation_type TEXT,
            camera_id TEXT,
            session_id TEXT
        )
    """
    
    TOLL_TRANSACTIONS_SCHEMA = """
        CREATE TABLE IF NOT EXISTS toll_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plate_number TEXT NOT NULL,
            transaction_time TEXT DEFAULT CURRENT_TIMESTAMP,
            toll_amount REAL,
            transaction_status TEXT,
            payment_method TEXT,
            gate_id TEXT,
            session_id TEXT
        )
    """
