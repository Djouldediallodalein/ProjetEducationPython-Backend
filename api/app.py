"""
API Flask - Point d'entrée principal
"""
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permet au frontend d'accéder à l'API depuis n'importe quel domaine

# Configuration
app.config['JSON_AS_ASCII'] = False  # Support UTF-8 pour les caractères spéciaux
app.config['JSON_SORT_KEYS'] = False  # Garder l'ordre des clés JSON

# Enregistrer les routes
from routes import register_routes
register_routes(app)

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
