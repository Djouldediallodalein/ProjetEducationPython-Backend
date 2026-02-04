"""
Module de sécurité - Authentification JWT + Bcrypt
"""
import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration JWT
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev_secret_key_change_me_in_production')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', 30))
JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRE_DAYS', 7))


def hash_password(password: str) -> str:
    """
    Hash un mot de passe avec bcrypt
    
    Args:
        password: Le mot de passe en clair
        
    Returns:
        str: Le hash du mot de passe
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Vérifie un mot de passe contre son hash
    
    Args:
        password: Le mot de passe en clair
        hashed_password: Le hash stocké
        
    Returns:
        bool: True si le mot de passe correspond
    """
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False


def create_access_token(user_id: str, username: str, role: str = 'user') -> str:
    """
    Crée un JWT access token
    
    Args:
        user_id: ID de l'utilisateur
        username: Nom d'utilisateur
        role: Rôle de l'utilisateur (user, admin, teacher)
        
    Returns:
        str: Le JWT token
    """
    expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'exp': expire,
        'iat': datetime.utcnow(),
        'type': 'access'
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    """
    Crée un JWT refresh token
    
    Args:
        user_id: ID de l'utilisateur
        
    Returns:
        str: Le JWT refresh token
    """
    expire = datetime.utcnow() + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        'user_id': user_id,
        'exp': expire,
        'iat': datetime.utcnow(),
        'type': 'refresh'
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Décode et vérifie un JWT token
    
    Args:
        token: Le JWT token
        
    Returns:
        dict: Les données du token ou None si invalide
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def require_auth(f):
    """
    Décorateur pour protéger les routes avec JWT
    Usage: @require_auth
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Récupérer le token depuis le header Authorization
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({
                'success': False,
                'error': 'Token d\'authentification manquant',
                'code': 'NO_TOKEN'
            }), 401
        
        # Format: "Bearer <token>"
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({
                'success': False,
                'error': 'Format du token invalide',
                'code': 'INVALID_TOKEN_FORMAT'
            }), 401
        
        token = parts[1]
        payload = decode_token(token)
        
        if not payload:
            return jsonify({
                'success': False,
                'error': 'Token invalide ou expiré',
                'code': 'INVALID_TOKEN'
            }), 401
        
        # Vérifier que c'est un access token
        if payload.get('type') != 'access':
            return jsonify({
                'success': False,
                'error': 'Type de token invalide',
                'code': 'INVALID_TOKEN_TYPE'
            }), 401
        
        # Ajouter les infos utilisateur à la requête
        request.user_id = payload.get('user_id')
        request.username = payload.get('username')
        request.user_role = payload.get('role', 'user')
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_role(*roles):
    """
    Décorateur pour restreindre l'accès par rôle
    Usage: @require_role('admin', 'teacher')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # S'assurer que l'authentification est requise
            if not hasattr(request, 'user_role'):
                return jsonify({
                    'success': False,
                    'error': 'Authentification requise',
                    'code': 'AUTHENTICATION_REQUIRED'
                }), 401
            
            # Vérifier le rôle
            if request.user_role not in roles:
                return jsonify({
                    'success': False,
                    'error': 'Permission refusée',
                    'code': 'INSUFFICIENT_PERMISSIONS',
                    'required_roles': list(roles),
                    'your_role': request.user_role
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def validate_password_strength(password: str) -> tuple:
    """
    Valide la force d'un mot de passe
    
    Args:
        password: Le mot de passe à valider
        
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if len(password) < 8:
        return False, "Le mot de passe doit contenir au moins 8 caractères"
    
    if not any(c.isupper() for c in password):
        return False, "Le mot de passe doit contenir au moins une majuscule"
    
    if not any(c.islower() for c in password):
        return False, "Le mot de passe doit contenir au moins une minuscule"
    
    if not any(c.isdigit() for c in password):
        return False, "Le mot de passe doit contenir au moins un chiffre"
    
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        return False, "Le mot de passe doit contenir au moins un caractère spécial (!@#$%^&*()_+-=[]{}|;:,.<>?)"
    
    return True, None
