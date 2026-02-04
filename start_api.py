"""
Script de démarrage simplifié pour l'API
Lance l'API Flask avec la configuration appropriée
"""
import sys
import os

# Ajouter le dossier backend au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importer l'app
from api.app import app
from config import Config

if __name__ == '__main__':
    print("\n" + "="*70)
    print(f"🚀 {Config.APP_NAME} - API REST v{Config.APP_VERSION}")
    print("="*70)
    print(f"📍 URL : http://localhost:{Config.API_PORT}")
    print(f"🤖 Modèle IA : {Config.OLLAMA_MODEL}")
    print(f"🔧 Mode Debug : {'Activé' if Config.API_DEBUG else 'Désactivé'}")
    print("="*70)
    print("\n💡 Testez l'API : http://localhost:{}/api/health\n".format(Config.API_PORT))
    
    try:
        app.run(
            debug=Config.API_DEBUG,
            host=Config.API_HOST,
            port=Config.API_PORT
        )
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print("⚠️  Arrêt de l'API...")
        print("="*70)
        sys.exit(0)
