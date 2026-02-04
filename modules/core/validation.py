"""
Module de validation et sanitization des inputs
Protection contre les injections et XSS
"""
import re
import bleach
from email_validator import validate_email, EmailNotValidError


def sanitize_string(text: str, max_length: int = 1000) -> str:
    """
    Nettoie une chaîne de caractères
    
    Args:
        text: Le texte à nettoyer
        max_length: Longueur maximale autorisée
        
    Returns:
        str: Le texte nettoyé
    """
    if not isinstance(text, str):
        return ""
    
    # Limiter la longueur
    text = text[:max_length]
    
    # Supprimer les balises HTML
    text = bleach.clean(text, tags=[], strip=True)
    
    # Supprimer les espaces multiples
    text = re.sub(r'\s+', ' ', text)
    
    # Trim
    text = text.strip()
    
    return text


def validate_username(username: str) -> tuple:
    """
    Valide un nom d'utilisateur
    
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if not username:
        return False, "Le nom d'utilisateur est requis"
    
    # Nettoyer
    username = sanitize_string(username, max_length=50)
    
    # Longueur
    if len(username) < 3:
        return False, "Le nom d'utilisateur doit contenir au moins 3 caractères"
    
    if len(username) > 50:
        return False, "Le nom d'utilisateur ne peut pas dépasser 50 caractères"
    
    # Format: lettres, chiffres, tirets, underscores uniquement
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "Le nom d'utilisateur ne peut contenir que des lettres, chiffres, tirets et underscores"
    
    # Pas de mots réservés
    reserved = ['admin', 'root', 'system', 'api', 'null', 'undefined', 'delete', 'drop']
    if username.lower() in reserved:
        return False, "Ce nom d'utilisateur est réservé"
    
    return True, None


def validate_email_address(email: str) -> tuple:
    """
    Valide une adresse email
    
    Returns:
        tuple: (is_valid: bool, error_message: str or None, normalized_email: str or None)
    """
    if not email:
        return False, "L'email est requis", None
    
    # Nettoyer
    email = sanitize_string(email, max_length=255)
    
    try:
        # Validation stricte avec email-validator
        valid = validate_email(email, check_deliverability=False)
        normalized_email = valid.normalized
        return True, None, normalized_email
    except EmailNotValidError as e:
        return False, f"Email invalide: {str(e)}", None


def validate_code_input(code: str) -> tuple:
    """
    Valide et sécurise le code Python soumis
    
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if not code:
        return False, "Le code est requis"
    
    # Limiter la taille (protection contre DoS)
    if len(code) > 50000:  # 50KB max
        return False, "Le code est trop long (maximum 50KB)"
    
    # Vérifier les caractères suspects
    dangerous_patterns = [
        r'\\x[0-9a-fA-F]{2}',  # Octets hexadécimaux
        r'\\u[0-9a-fA-F]{4}',  # Unicode escape
        r'chr\(\d+\)',  # chr() peut créer des caractères dangereux
        r'ord\([^)]+\)',  # ord()
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, code):
            return False, f"Pattern suspect détecté: {pattern}"
    
    return True, None


def validate_integer(value, min_val: int = None, max_val: int = None, field_name: str = "valeur") -> tuple:
    """
    Valide un entier
    
    Returns:
        tuple: (is_valid: bool, error_message: str or None, value: int or None)
    """
    try:
        val = int(value)
        
        if min_val is not None and val < min_val:
            return False, f"{field_name} doit être >= {min_val}", None
        
        if max_val is not None and val > max_val:
            return False, f"{field_name} doit être <= {max_val}", None
        
        return True, None, val
    except (ValueError, TypeError):
        return False, f"{field_name} doit être un nombre entier", None


def validate_json_keys(data: dict, required_keys: list, optional_keys: list = None) -> tuple:
    """
    Valide les clés d'un dictionnaire JSON
    
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if not isinstance(data, dict):
        return False, "Les données doivent être un objet JSON"
    
    # Vérifier les clés requises
    missing = [key for key in required_keys if key not in data]
    if missing:
        return False, f"Clés manquantes: {', '.join(missing)}"
    
    # Vérifier les clés inattendues
    if optional_keys is not None:
        allowed = set(required_keys + optional_keys)
        unexpected = [key for key in data.keys() if key not in allowed]
        if unexpected:
            return False, f"Clés non autorisées: {', '.join(unexpected)}"
    
    return True, None


def sanitize_filename(filename: str) -> str:
    """
    Nettoie un nom de fichier pour éviter path traversal
    
    Returns:
        str: Nom de fichier sécurisé
    """
    # Supprimer les caractères dangereux
    filename = re.sub(r'[^\w\s.-]', '', filename)
    
    # Supprimer les path traversal
    filename = filename.replace('..', '')
    filename = filename.replace('/', '')
    filename = filename.replace('\\', '')
    
    # Limiter la longueur
    filename = filename[:255]
    
    return filename


def validate_domain(domain: str) -> tuple:
    """
    Valide un nom de domaine
    
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if not domain:
        return False, "Le domaine est requis"
    
    # Nettoyer
    domain = sanitize_string(domain, max_length=50)
    
    # Format: lettres, chiffres, underscores uniquement
    if not re.match(r'^[a-zA-Z0-9_]+$', domain):
        return False, "Le domaine ne peut contenir que des lettres, chiffres et underscores"
    
    # Liste de domaines valides (whitelist)
    valid_domains = [
        'python', 'javascript', 'html_css', 'sql',
        'java', 'c', 'anglais', 'maths'
    ]
    
    if domain not in valid_domains:
        return False, f"Domaine invalide. Domaines autorisés: {', '.join(valid_domains)}"
    
    return True, None


def rate_limit_key_func():
    """
    Fonction pour générer la clé de rate limiting
    Utilise l'IP du client
    """
    from flask import request
    return request.remote_addr
