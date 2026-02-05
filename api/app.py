from flask import Flask, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import sys
from dotenv import load_dotenv

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Charger les variables d'environnement
load_dotenv()

# Importer la validation des secrets (cela vérifiera en production)
from modules.core.security import FLASK_SECRET_KEY
from modules.core.utilisateurs import initialiser_systeme_utilisateurs

app = Flask(__name__)

# Initialiser le système d'utilisateurs au démarrage
initialiser_systeme_utilisateurs()

# Configuration de sécurité
app.config['SECRET_KEY'] = FLASK_SECRET_KEY
app.config['JSON_AS_ASCII'] = False
app.config['JSON_SORT_KEYS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# CORS - Ouvert pour développement, restreindre en production via .env
allowed_origins = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173').split(',')
CORS(app, 
     resources={r"/api/*": {"origins": allowed_origins}},
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization', 'X-User-Id'],
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

# Bloquer l'accès direct aux fichiers JSON
@app.before_request
def block_json_access():
    """Bloquer l'accès direct aux fichiers sensibles"""
    from flask import abort
    blocked_extensions = ['.json', '.log', '.env', '.py', '.pyc']
    if any(request.path.endswith(ext) for ext in blocked_extensions):
        abort(403)

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
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.routes import register_routes
register_routes(app, limiter)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
