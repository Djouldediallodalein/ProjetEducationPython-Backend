# 🚀 Guide de Déploiement - Backend PyQuest

## 📋 Pré-requis

- Python 3.8+
- pip
- Ollama avec le modèle qwen2.5-coder:14b
- (Optionnel) Redis pour le rate limiting en production

## ⚙️ Configuration

### 1. Cloner le projet

```bash
git clone <votre-repo>
cd backend
```

### 2. Créer l'environnement virtuel

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configuration des variables d'environnement

```bash
# Copier le fichier exemple
cp .env.example .env

# Générer des secrets forts
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_hex(32))"
python -c "import secrets; print('FLASK_SECRET_KEY=' + secrets.token_hex(32))"

# Éditer .env et remplacer les valeurs
nano .env  # ou notepad .env sur Windows
```

### 5. Vérifier Ollama

```bash
# S'assurer qu'Ollama tourne
ollama list

# Si le modèle n'est pas installé
ollama pull qwen2.5-coder:14b
```

### 6. Initialiser les dossiers

```bash
mkdir -p logs data/exports data/progressions data/sauvegardes
```

## 🧪 Tests

```bash
# Lancer tous les tests
python -m pytest tests/ -v

# Tests basiques uniquement
python -m pytest tests/test_basic.py -v

# Tests API uniquement
python -m pytest tests/test_api.py -v

# Avec couverture
python -m pytest tests/ --cov=modules --cov=api --cov-report=html
```

## 🏃 Lancement

### Développement

```bash
python api/app.py
```

L'API sera disponible sur http://localhost:5000

### Production (avec Gunicorn)

```bash
# Installer gunicorn
pip install gunicorn

# Lancer avec 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 api.app:app
```

## 📡 Endpoints API

### Health Check
```bash
curl http://localhost:5000/api/health
```

### Inscription
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"Test123!@#"}'
```

### Connexion
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"Test123!@#"}'
```

### Génération d'exercice (avec authentification)
```bash
curl -X POST http://localhost:5000/api/exercices/generer \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <votre_token>" \
  -d '{"niveau":1,"theme":"Variables et types de données","domaine":"python"}'
```

## 🔒 Sécurité

### Checklist de sécurité pour la production

- [ ] Secrets forts générés (JWT_SECRET_KEY, FLASK_SECRET_KEY)
- [ ] .env non commité dans Git
- [ ] CORS configuré avec vos vrais domaines
- [ ] HTTPS activé (FORCE_HTTPS=True)
- [ ] Rate limiting avec Redis (pas memory://)
- [ ] Logs rotationnés configurés
- [ ] Firewall configuré (ports 5000, 80, 443)
- [ ] Monitoring activé (Sentry, Prometheus, etc.)

### Générer de nouveaux secrets

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## 🐳 Docker (Optionnel)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "api.app:app"]
```

```bash
# Build
docker build -t pyquest-backend .

# Run
docker run -p 5000:5000 --env-file .env pyquest-backend
```

## 📊 Monitoring

### Logs

```bash
# Suivre les logs en temps réel
tail -f logs/security.log

# Rechercher des erreurs
grep -i "error\|critical" logs/security.log

# Statistiques
wc -l logs/security.log
```

### Métriques

Les métriques importantes à surveiller:
- Nombre de requêtes par endpoint
- Temps de réponse moyen
- Taux d'erreur (4xx, 5xx)
- Tentatives d'authentification échouées
- Rate limiting déclenchés

## 🔧 Dépannage

### Erreur: "Ollama connection refused"

```bash
# Vérifier qu'Ollama tourne
ollama list

# Redémarrer Ollama
# Linux/Mac: sudo systemctl restart ollama
# Windows: Redémarrer l'application Ollama
```

### Erreur: "JWT decode error"

- Vérifier que JWT_SECRET_KEY est identique entre les requêtes
- Token peut avoir expiré (30 minutes par défaut)
- Demander un nouveau token via /api/auth/login

### Erreur: "CORS policy"

- Vérifier CORS_ORIGINS dans .env
- Ajouter votre domaine frontend

### Performances lentes

- Vérifier la mémoire disponible
- Augmenter le nombre de workers Gunicorn
- Activer Redis pour le cache
- Optimiser les requêtes IA

## 📚 Documentation complète

- **API REST:** Voir `/api/routes.py` pour tous les endpoints
- **Modules:** Documentation dans chaque fichier `modules/`
- **Tests:** Documentation dans `tests/README.md`

## 🤝 Contribution

Pour contribuer au projet:

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📝 Changelog

Voir `CHANGELOG.md` pour l'historique des modifications.

## 📄 License

Ce projet est sous licence MIT - voir le fichier `LICENSE` pour plus de détails.

## 🆘 Support

- Issues: <repo-url>/issues
- Email: votre-email@example.com
- Discord: (optionnel)
