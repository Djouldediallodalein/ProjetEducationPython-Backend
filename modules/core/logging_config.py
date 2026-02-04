"""
Système de logging et monitoring sécurisé
"""
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
import json


# Créer le dossier logs s'il n'existe pas
LOG_DIR = 'logs'
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)


# Configuration du logger principal
def setup_logger(name='security', log_file='logs/security.log', level=logging.INFO):
    """Configure un logger avec rotation de fichiers"""
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Éviter les doublons
    if logger.handlers:
        return logger
    
    # Format des logs
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler fichier avec rotation (10MB max, 5 backups)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Handler console (développement)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


# Loggers spécialisés
security_logger = setup_logger('security', 'logs/security.log', logging.INFO)
api_logger = setup_logger('api', 'logs/api.log', logging.INFO)
auth_logger = setup_logger('auth', 'logs/auth.log', logging.INFO)
error_logger = setup_logger('error', 'logs/error.log', logging.ERROR)


def log_security_event(event_type: str, user_id: str = None, details: dict = None, severity: str = 'INFO'):
    """
    Log un événement de sécurité
    
    Args:
        event_type: Type d'événement (login, failed_login, token_expired, etc.)
        user_id: ID de l'utilisateur concerné
        details: Détails supplémentaires
        severity: Niveau de gravité (INFO, WARNING, ERROR, CRITICAL)
    """
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,
        'user_id': user_id,
        'details': details or {}
    }
    
    message = json.dumps(log_entry, ensure_ascii=False)
    
    if severity == 'CRITICAL':
        security_logger.critical(message)
    elif severity == 'ERROR':
        security_logger.error(message)
    elif severity == 'WARNING':
        security_logger.warning(message)
    else:
        security_logger.info(message)


def log_api_request(endpoint: str, method: str, user_id: str = None, status_code: int = None, ip_address: str = None):
    """Log une requête API"""
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'endpoint': endpoint,
        'method': method,
        'user_id': user_id,
        'status_code': status_code,
        'ip_address': ip_address
    }
    
    api_logger.info(json.dumps(log_entry, ensure_ascii=False))


def log_auth_attempt(username: str, success: bool, ip_address: str = None, reason: str = None):
    """Log une tentative d'authentification"""
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'username': username,
        'success': success,
        'ip_address': ip_address,
        'reason': reason
    }
    
    if success:
        auth_logger.info(json.dumps(log_entry, ensure_ascii=False))
    else:
        auth_logger.warning(json.dumps(log_entry, ensure_ascii=False))


def log_error(error_type: str, error_message: str, traceback: str = None, user_id: str = None):
    """Log une erreur"""
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'error_type': error_type,
        'error_message': error_message,
        'traceback': traceback,
        'user_id': user_id
    }
    
    error_logger.error(json.dumps(log_entry, ensure_ascii=False))


def log_code_execution(user_id: str, code_length: int, execution_time: float, success: bool, dangerous_attempt: bool = False):
    """Log une exécution de code"""
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'user_id': user_id,
        'code_length': code_length,
        'execution_time': execution_time,
        'success': success,
        'dangerous_attempt': dangerous_attempt
    }
    
    if dangerous_attempt:
        security_logger.warning(json.dumps(log_entry, ensure_ascii=False))
    else:
        api_logger.info(json.dumps(log_entry, ensure_ascii=False))
