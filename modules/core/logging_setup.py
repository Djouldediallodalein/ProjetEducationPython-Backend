# Configuration de logging avec rotation
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging():
    """Configure le système de logging avec rotation des fichiers"""
    
    # Créer le dossier logs s'il n'existe pas
    os.makedirs('logs', exist_ok=True)
    
    # Configuration de base
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    log_file = os.getenv('LOG_FILE', 'logs/security.log')
    max_bytes = int(os.getenv('LOG_MAX_BYTES', 10485760))  # 10MB par défaut
    backup_count = int(os.getenv('LOG_BACKUP_COUNT', 5))
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler avec rotation
    handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    handler.setFormatter(formatter)
    
    # Console handler pour développement
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configuration du logger racine
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.addHandler(handler)
    
    # Ajouter console uniquement en développement
    if os.getenv('FLASK_ENV') == 'development':
        root_logger.addHandler(console_handler)
    
    return root_logger

# Initialiser le logging
logger = setup_logging()

def log_info(message):
    """Log un message d'information"""
    logger.info(message)

def log_warning(message):
    """Log un avertissement"""
    logger.warning(message)

def log_error(message, exc_info=None):
    """Log une erreur"""
    logger.error(message, exc_info=exc_info)

def log_critical(message):
    """Log une erreur critique"""
    logger.critical(message)

def log_debug(message):
    """Log un message de débogage"""
    logger.debug(message)
