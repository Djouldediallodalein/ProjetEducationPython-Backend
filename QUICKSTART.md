# 🎮 PyQuest Backend

[![Tests](https://img.shields.io/badge/Tests-16%2F16%20passing-success.svg)](tests/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com)
[![Security](https://img.shields.io/badge/Security-A+-brightgreen.svg)](SECURITY.md)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Backend API REST professionnel pour PyQuest - Plateforme d'apprentissage gamifiée avec IA

## ⚡ Démarrage ultra-rapide

```bash
# 1. Clone + Install (2 min)
git clone https://github.com/Djouldediallodalein/ProjetEducationPython-Backend.git
cd ProjetEducationPython-Backend
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt

# 2. Configuration (1 min)
cp .env.example .env
# Éditer .env avec vos secrets (voir instructions dans le fichier)

# 3. Lancer (30 sec)
python api/app.py
# ✅ API disponible sur http://localhost:5000
```

## 🚀 Features

- 🔐 **Auth JWT** (access + refresh tokens) + Bcrypt
- 🤖 **IA Ollama** pour génération d'exercices adaptatifs
- 🎯 **15 endpoints REST** (exercices, progression, badges, quêtes)
- 🛡️ **Sécurité A+** (rate limiting, validation, sandbox Python)
- 🏆 **Gamification** (XP, niveaux, badges, classement)
- 🧪 **16 tests** (100% réussite)
- 📚 **8 domaines** (Python, JS, SQL, etc.)

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [ONBOARDING.md](ONBOARDING.md) | 🎯 **START HERE** - Guide pour nouveaux devs |
| [README.md](README.md) | Vue d'ensemble complète |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Guide de déploiement |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Standards de contribution |
| [SECURITY.md](SECURITY.md) | Politique de sécurité |

## 🧪 Tests

```bash
python -m pytest tests/ -v  # 16/16 PASSED ✅
```

## 📊 Stats

- **15** endpoints REST
- **19** modules (9 core + 10 features)
- **16** tests automatisés (100% réussite)
- **~7000+** lignes de code
- **8** domaines d'apprentissage supportés

## 🤝 Contribuer

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'feat: Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

Voir [CONTRIBUTING.md](CONTRIBUTING.md) pour les détails.

## 📄 License

MIT © [Mamadou Djouldé Diallo Dalein](https://github.com/Djouldediallodalein)

---

**Version**: 1.0.0 | **Status**: Production-ready ✅
