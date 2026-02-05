# 🎯 BACKEND 100% PRODUCTION-READY - Guide Développeur

## 👋 Bienvenue !

Ce document est destiné aux développeurs qui rejoignent le projet PyQuest Backend.

## ✅ État du projet

### Version actuelle: **v1.0.0** (5 février 2026)

- ✅ **16/16 tests passent**
- ✅ **Sécurité niveau A+**
- ✅ **Documentation exhaustive**
- ✅ **Production-ready**

## 🚀 Démarrage rapide (5 minutes)

### 1. Cloner et installer

```bash
# Cloner le repo
git clone https://github.com/Djouldediallodalein/ProjetEducationPython-Backend.git
cd ProjetEducationPython-Backend

# Environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Dépendances
pip install -r requirements.txt
```

### 2. Configuration (.env)

```bash
# Copier le fichier exemple
cp .env.example .env

# Générer des secrets FORTS (IMPORTANT!)
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_hex(32))"
python -c "import secrets; print('FLASK_SECRET_KEY=' + secrets.token_hex(32))"

# Éditer .env et coller vos secrets
notepad .env  # Windows
# nano .env  # Linux
```

**⚠️ CRITIQUE:** Ne JAMAIS commiter le fichier `.env` !

### 3. Vérifier Ollama

```bash
# Vérifier qu'Ollama tourne
ollama list

# Installer le modèle si nécessaire
ollama pull qwen2.5-coder:14b
```

### 4. Lancer l'API

```bash
python api/app.py
```

✅ L'API tourne sur **http://localhost:5000**

### 5. Tester l'API

```bash
# Health check
curl http://localhost:5000/api/health

# Inscription
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"dev","email":"dev@test.com","password":"DevTest123!@#"}'
```

## 📚 Documents essentiels à lire

| Document | Contenu | Priorité |
|----------|---------|----------|
| [README.md](README.md) | Vue d'ensemble, installation, API | 🔴 HAUTE |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Guide de contribution, standards | 🔴 HAUTE |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Déploiement dev/prod | 🟡 MOYENNE |
| [SECURITY.md](SECURITY.md) | Sécurité, vulnérabilités | 🟡 MOYENNE |
| [CHANGELOG.md](CHANGELOG.md) | Historique versions | 🟢 BASSE |

## 🎯 Architecture du projet

```
backend/
├── api/
│   ├── app.py              # Point d'entrée Flask
│   └── routes.py           # 15 endpoints REST
├── modules/
│   ├── core/               # 9 modules de base
│   │   ├── security.py     # JWT + Bcrypt
│   │   ├── validation.py   # Sanitization
│   │   ├── fonctions.py    # Génération exercices
│   │   └── ...
│   └── features/           # 10 modules avancés
│       ├── defis_quotidiens.py
│       ├── classement.py
│       └── ...
├── tests/                  # 16 tests automatisés
├── data/                   # Fichiers JSON
├── logs/                   # Logs avec rotation
└── .env                    # Config (NE PAS COMMIT!)
```

## 🔑 Concepts clés

### 1. Authentification JWT

```python
# Toutes les routes protégées utilisent @require_auth
@app.route('/api/exercices/generer')
@require_auth  # Vérifie le JWT token
def generer_exercice():
    user = request.user  # Injecté par le décorateur
    # ...
```

### 2. Génération d'exercices IA

```python
# 1. Chercher dans la banque locale (non complétés)
# 2. Si pas trouvé → générer via Ollama (qwen2.5-coder:14b)
# 3. Ajouter à la banque pour réutilisation
exercice = generer_exercice(niveau=1, theme="Variables", domaine="python")
```

### 3. Système de progression

```
Utilisateur fait un exercice
  → Gagne XP (10-90 selon niveau/difficulté)
  → XP débloque des niveaux
  → Niveaux débloquent des badges
  → Badges visibles dans le profil
```

### 4. Sécurité du code Python

```python
# Exécution sécurisée avec:
# - Blocage imports dangereux (os, sys, subprocess)
# - Timeout 5 secondes
# - Sandbox isolé
# - Capture stdout/stderr
resultat = executer_code_securise(code_utilisateur)
```

## 🧪 Tests

```bash
# Tous les tests
python -m pytest tests/ -v

# Avec couverture
python -m pytest tests/ --cov=modules --cov=api --cov-report=html

# Résultat attendu: 16/16 PASSED ✅
```

## 📊 Endpoints API (15)

### Authentification
- `POST /api/auth/register` - Inscription
- `POST /api/auth/login` - Connexion
- `POST /api/auth/refresh` - Refresh token

### Exercices
- `POST /api/exercices/generer` - Générer exercice
- `POST /api/exercices/verifier` - Vérifier réponse
- `POST /api/exercices/executer` - Exécuter code
- `POST /api/exercices/tester` - Tester avec tests unitaires

### Progression
- `GET /api/progression` - Voir progression
- `POST /api/progression/update` - Mettre à jour
- `GET /api/progression/stats` - Statistiques

### Domaines & Données
- `GET /api/domaines` - Liste domaines
- `GET /api/domaines/<id>/themes` - Thèmes d'un domaine
- `GET /api/badges` - Badges disponibles
- `GET /api/xp` - Calcul XP
- `GET /api/health` - Health check

## 🔧 Commandes utiles

```bash
# Voir les logs en temps réel
tail -f logs/security.log

# Lancer un test spécifique
python -m pytest tests/test_api.py::test_generer_exercice -v

# Vérifier le style de code
flake8 modules/ api/ --max-line-length=120

# Voir les commits récents
git log --oneline -10
```

## 🐛 Dépannage fréquent

### Erreur: "Ollama connection refused"
```bash
# Vérifier qu'Ollama tourne
ollama list
# Redémarrer Ollama
```

### Erreur: "JWT decode error"
```bash
# Token expiré (30 minutes par défaut)
# Se reconnecter via /api/auth/login
```

### Erreur: "ModuleNotFoundError"
```bash
# Vérifier l'environnement virtuel
which python  # Doit pointer vers venv/
pip list  # Voir les packages installés
```

### Tests échouent
```bash
# Nettoyer les caches
find . -type d -name __pycache__ -exec rm -rf {} +
# Réinstaller
pip install -r requirements.txt --force-reinstall
```

## 📈 Prochaines étapes (Roadmap v1.1.0)

### Haute priorité
- [ ] Pagination sur `/api/utilisateurs` et `/api/leaderboard`
- [ ] Cache Redis pour exercices générés
- [ ] Backup automatique quotidien
- [ ] Tests de performance (Locust)

### Moyenne priorité
- [ ] Documentation Swagger/OpenAPI
- [ ] CI/CD avec GitHub Actions
- [ ] Monitoring Prometheus + Grafana
- [ ] Support WebSocket pour notifications temps réel

### Basse priorité
- [ ] Migration PostgreSQL (actuellement JSON)
- [ ] API GraphQL
- [ ] Support multi-langues (i18n)
- [ ] Docker Compose pour déploiement facile

## 🤝 Workflow de contribution

```bash
# 1. Créer une branche
git checkout -b feature/ma-fonctionnalite

# 2. Coder + tests
# Écrire du code propre (voir CONTRIBUTING.md)

# 3. Tester
python -m pytest tests/ -v

# 4. Commit
git add .
git commit -m "feat: Description de ma fonctionnalité"

# 5. Push
git push origin feature/ma-fonctionnalite

# 6. Pull Request sur GitHub
# Remplir le template de PR
```

## 📞 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/Djouldediallodalein/ProjetEducationPython-Backend/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Djouldediallodalein/ProjetEducationPython-Backend/discussions)
- **Email**: (si applicable)

## ✅ Checklist première contribution

- [ ] Environnement configuré et tests passent
- [ ] Lu README.md et CONTRIBUTING.md
- [ ] Compris l'architecture (api/ + modules/)
- [ ] Testé l'API en local avec curl/Postman
- [ ] Créé un compte test et généré un exercice
- [ ] Exploré le code (routes.py, fonctions.py, security.py)
- [ ] Identifié une issue ou fonctionnalité à développer

## 🎉 Bienvenue dans l'équipe !

N'hésitez pas à poser des questions dans les Discussions GitHub. Le code est bien documenté, explorez-le !

---

**Version**: 1.0.0 | **Dernière MAJ**: 5 février 2026 | **Status**: Production-ready ✅
