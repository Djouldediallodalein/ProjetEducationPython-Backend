# 🎮 PyQuest Backend - API REST Éducative avec IA

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com)
[![Tests](https://img.shields.io/badge/Tests-16%2F16%20passing-success.svg)](tests/)
[![Security](https://img.shields.io/badge/Security-A+-brightgreen.svg)](SECURITY.md)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Backend professionnel pour PyQuest, une plateforme d'apprentissage gamifiée utilisant l'IA pour générer des exercices personnalisés.

## ✨ Fonctionnalités

### 🔐 Sécurité de niveau production
- Authentification JWT (access + refresh tokens)
- Hash Bcrypt des mots de passe
- Rate limiting sur tous les endpoints
- Validation et sanitization des entrées
- Exécution sécurisée de code Python
- Headers de sécurité (CSP, XSS, HSTS)
- Blocage des fichiers sensibles
- Logging complet avec rotation

### 🎯 API REST complète (15 endpoints)
- Authentification (register, login, refresh)
- Génération d'exercices par IA (Ollama)
- Vérification et exécution de code
- Système de progression (XP, niveaux)
- Badges et achievements
- Quêtes et défis quotidiens
- Classement multi-utilisateurs
- Multi-domaines (Python, JS, SQL, etc.)

### 🧠 Intelligence Artificielle
- Génération d'exercices adaptatifs via Ollama
- Modèle: qwen2.5-coder:14b
- Correction automatique avec feedback
- Banque d'exercices intelligente
- Répétition espacée (SRS scientifique)

### 📊 Système de gamification
- XP et système de niveaux
- 15+ badges déblocables
- Quêtes progressives
- Défis quotidiens
- Classement et compétition

## 🚀 Installation rapide

### Pré-requis
- Python 3.8 ou supérieur
- pip
- Ollama avec qwen2.5-coder:14b

### 1. Cloner le projet

```bash
git clone https://github.com/Djouldediallodalein/ProjetEducationPython-Backend.git
cd ProjetEducationPython-Backend
```

### 2. Environnement virtuel

```bash
# Créer l'environnement
python -m venv venv

# Activer (Windows)
venv\Scripts\activate

# Activer (Linux/Mac)
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configuration

```bash
# Copier le fichier de configuration
cp .env.example .env

# Générer des secrets forts
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_hex(32))"
python -c "import secrets; print('FLASK_SECRET_KEY=' + secrets.token_hex(32))"

# Éditer .env avec vos secrets
nano .env  # ou notepad .env
```

### 5. Vérifier Ollama

```bash
# Lister les modèles installés
ollama list

# Installer le modèle si nécessaire
ollama pull qwen2.5-coder:14b
```

### 6. Lancer l'API

```bash
python api/app.py
```

🎉 L'API est maintenant accessible sur **http://localhost:5000**

## 📡 Utilisation de l'API

### Health Check

```bash
curl http://localhost:5000/api/health
```

### Inscription

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123!@#"
  }'
```

### Connexion

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecurePass123!@#"
  }'
```

### Générer un exercice

```bash
curl -X POST http://localhost:5000/api/exercices/generer \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer VOTRE_TOKEN" \
  -d '{
    "niveau": 1,
    "theme": "Variables et types de données",
    "domaine": "python"
  }'
```

## 🧪 Tests

```bash
# Lancer tous les tests
python -m pytest tests/ -v

# Tests avec couverture
python -m pytest tests/ --cov=modules --cov=api --cov-report=html

# Tests basiques uniquement
python -m pytest tests/test_basic.py -v

# Tests API uniquement
python -m pytest tests/test_api.py -v
```

**Résultats:** 16/16 tests passent ✅

## 📁 Structure du projet

```
backend/
├── api/                      # API REST Flask
│   ├── app.py               # Application principale
│   └── routes.py            # 15 endpoints (1395 lignes)
├── modules/
│   ├── core/                # 9 modules de base
│   │   ├── fonctions.py     # Génération exercices
│   │   ├── progression.py   # Système progression
│   │   ├── domaines.py      # Multi-domaines
│   │   ├── xp_systeme.py    # XP et niveaux
│   │   ├── security.py      # JWT + Bcrypt
│   │   ├── validation.py    # Sanitization
│   │   └── ...
│   └── features/            # 10 modules avancés
│       ├── defis_quotidiens.py
│       ├── classement.py
│       ├── quetes.py
│       └── ...
├── tests/                   # Tests automatisés
│   ├── test_basic.py       # 10 tests unitaires
│   └── test_api.py         # 6 tests intégration
├── data/                    # Données JSON
│   ├── domaines.json
│   ├── utilisateurs.json
│   └── progression_utilisateur.json
├── logs/                    # Logs avec rotation
├── .env.example            # Configuration exemple
├── requirements.txt        # Dépendances Python
├── DEPLOYMENT.md          # Guide déploiement
├── CHANGELOG.md           # Historique versions
├── CONTRIBUTING.md        # Guide contribution
└── README.md              # Ce fichier
```

## 🔒 Sécurité

### Checklist de sécurité

- [x] JWT avec secrets forts
- [x] Hash Bcrypt des mots de passe
- [x] Rate limiting (100/hour par défaut)
- [x] Validation des entrées (XSS, SQL injection)
- [x] Headers de sécurité (CSP, HSTS, etc.)
- [x] Exécution sécurisée du code Python
- [x] Blocage des imports dangereux
- [x] Logging complet des événements
- [x] CORS restreint aux domaines autorisés
- [x] Timeout sur l'exécution de code
- [x] Protection des fichiers sensibles

### Rapporter une vulnérabilité

Voir [SECURITY.md](SECURITY.md)

## 📊 Métriques

| Métrique | Valeur |
|----------|--------|
| Endpoints API | 15 |
| Modules | 19 (9 core + 10 features) |
| Tests | 16 (100% réussite) |
| Lignes de code | ~7000+ |
| Couverture tests | ~40% |
| Domaines supportés | 8 |
| Badges disponibles | 15+ |

## 🛠️ Technologies

- **Backend**: Flask 3.0.0
- **Auth**: PyJWT, Bcrypt
- **IA**: Ollama (qwen2.5-coder:14b)
- **Tests**: Pytest
- **Sécurité**: Flask-Limiter, Flask-CORS
- **Logs**: Rotating File Handler
- **Python**: 3.8+

## 📚 Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Guide de déploiement complet
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Comment contribuer
- **[CHANGELOG.md](CHANGELOG.md)** - Historique des versions
- **[LICENSE](LICENSE)** - Licence MIT

## 🤝 Contribution

Les contributions sont les bienvenues ! Consultez [CONTRIBUTING.md](CONTRIBUTING.md) pour les directives.

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'feat: Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 🐛 Rapporter un bug

Ouvrez une [issue](https://github.com/Djouldediallodalein/ProjetEducationPython-Backend/issues) avec:
- Description du problème
- Steps de reproduction
- Comportement attendu vs actuel
- Screenshots si applicable
- Logs d'erreur

## 📝 Roadmap

### v1.1.0 (Q1 2026)
- [ ] Pagination des endpoints de liste
- [ ] Cache Redis pour exercices
- [ ] Backup automatique
- [ ] Webhooks
- [ ] Métriques Prometheus

### v1.2.0 (Q2 2026)
- [ ] WebSocket pour notifications temps réel
- [ ] Support PostgreSQL
- [ ] API GraphQL
- [ ] Documentation Swagger/OpenAPI

## 👥 Auteurs

- **Mamadou Djouldé Diallo Dalein** - [@Djouldediallodalein](https://github.com/Djouldediallodalein)

## 📄 License

Ce projet est sous licence MIT - voir [LICENSE](LICENSE) pour plus de détails.

## 🙏 Remerciements

- Ollama pour le modèle IA
- Flask pour le framework web
- Tous les contributeurs

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Djouldediallodalein/ProjetEducationPython-Backend/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Djouldediallodalein/ProjetEducationPython-Backend/discussions)

---

**Fait avec ❤️ pour l'éducation accessible à tous**
