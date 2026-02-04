"""
API Flask - Point d'entrée principal avec sécurité renforcée
"""
from flask import Flask, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)

# Configuration de sécurité
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev_secret_key_change_me')
app.config['JSON_AS_ASCII'] = False
app.config['JSON_SORT_KEYS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# CORS restreint aux domaines autorisés
allowed_origins = os.getenv('CORS_ORIGINS', 'http://localhost:5173').split(',')
CORS(app, 
     origins=allowed_origins,
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# Rate Limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[os.getenv('RATE_LIMIT_DEFAULT', "100 per hour")],
    storage_uri=os.getenv('RATE_LIMIT_STORAGE_URL', "memory://")
)

# Headers de sécurité
@app.after_request
def set_security_headers(response):
    """Ajoute les headers de sécurité à toutes les réponses"""
    # Protection XSS
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Content Security Policy
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self'; "
        "connect-src 'self';"
    )
    
    # HTTPS (si activé)
    if os.getenv('FORCE_HTTPS', 'False') == 'True':
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    return response

# Logger les requêtes
@app.before_request
def log_request():
    """Log toutes les requêtes entrantes"""
    from modules.core.logging_config import log_api_request
    log_api_request(
        endpoint=request.endpoint or request.path,
        method=request.method,
        ip_address=request.remote_addr
    )

# Enregistrer les routes
from api.routes import register_routes
register_routes(app, limiter)

if __name__ == '__main__':
    print("="*60)
    print("🚀 API REST Flask - Application d'Apprentissage")
    print("="*60)
    print("📍 URL: http://localhost:5000")
    print("📚 Endpoints disponibles:")
    print("   - GET  /api/health")
    print("   - POST /api/exercices/generer")
    print("   - POST /api/exercices/verifier")
    print("   - POST /api/exercices/executer")
    print("   - POST /api/exercices/tester")
    print("   - GET  /api/progression")
    print("   - POST /api/progression/update")
    print("   - GET  /api/domaines")
    print("   - GET  /api/domaines/<id>/themes")
    print("   - GET  /api/utilisateurs")
    print("   - POST /api/utilisateurs/creer")
    print("   - GET  /api/badges")
    print("   - GET  /api/xp")
    print("="*60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
