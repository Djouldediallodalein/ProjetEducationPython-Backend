"""
Configuration centralisée de l'application
Charge les variables depuis le fichier .env
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Charger le fichier .env s'il existe
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

class Config:
    """Configuration de l'application"""
    
    # Ollama
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'qwen2.5-coder:14b')
    OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    OLLAMA_TIMEOUT = int(os.getenv('OLLAMA_TIMEOUT', 120))
    
    # API
    API_PORT = int(os.getenv('API_PORT', 5000))
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_DEBUG = os.getenv('API_DEBUG', 'True').lower() == 'true'
    
    # Sécurité
    CODE_TIMEOUT = int(os.getenv('CODE_TIMEOUT', 5))
    MAX_REQUESTS_PER_MINUTE = int(os.getenv('MAX_REQUESTS_PER_MINUTE', 60))
    
    # Chemins
    DATA_PATH = os.getenv('DATA_PATH', './data')
    LOGS_PATH = os.getenv('LOGS_PATH', './data/logs')
    EXPORTS_PATH = os.getenv('EXPORTS_PATH', './data/exports')
    
    # Application
    APP_NAME = os.getenv('APP_NAME', 'ProjetEducationPython')
    APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
    
    @classmethod
    def afficher_config(cls):
        """Affiche la configuration actuelle"""
        print("="*60)
        print("CONFIGURATION APPLICATION")
        print("="*60)
        print(f"Modèle Ollama : {cls.OLLAMA_MODEL}")
        print(f"API Port : {cls.API_PORT}")
        print(f"Mode Debug : {cls.API_DEBUG}")
        print(f"Timeout code : {cls.CODE_TIMEOUT}s")
        print(f"Chemin données : {cls.DATA_PATH}")
        print("="*60)

if __name__ == '__main__':
    Config.afficher_config()
