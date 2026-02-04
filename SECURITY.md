# 🔒 DOCUMENTATION SÉCURITÉ - PyQuest API

## ✅ Mesures de Sécurité Implémentées

### 1. **Authentification & Authorization**

#### JWT (JSON Web Tokens)
- **Access Tokens** : Durée 30 minutes
- **Refresh Tokens** : Durée 7 jours
- **Algorithme** : HS256
- **Stockage** : Secret key dans `.env` (JAMAIS dans le code)

#### Bcrypt Password Hashing
- **Algorithme** : bcrypt avec salt automatique
- **Force minimale requise** :
  - Minimum 8 caractères
  - 1 majuscule
  - 1 minuscule
  - 1 chiffre
  - 1 caractère spécial (!@#$%^&*()_+-=[]{}|;:,.<>?)

#### Rôles (RBAC)
- `user` : Utilisateur standard
- `teacher` : Enseignant (accès étendu)
- `admin` : Administrateur (accès complet)

### 2. **Rate Limiting**

Protection contre les attaques par déni de service (DoS/DDoS) :

| Endpoint | Limite | Raison |
|----------|--------|--------|
| `/api/auth/register` | 5/hour | Anti-spam inscription |
| `/api/auth/login` | 10/hour | Anti brute-force |
| `/api/exercices/executer` | 15/hour | Protection ressources serveur |
| Tous les autres | 100/hour | Protection générale |

### 3. **Validation des Inputs**

#### Sanitization
- Suppression des balises HTML (protection XSS)
- Nettoyage des espaces multiples
- Limitation de longueur

#### Validation stricte
- **Usernames** : Lettres, chiffres, tirets, underscores uniquement (3-50 chars)
- **Emails** : Validation RFC 5322 avec `email-validator`
- **Code Python** : Maximum 50KB
- **Domaines** : Whitelist stricte (python, javascript, etc.)

### 4. **Sécurité de l'Exécution de Code**

#### Protections multiples
- ✅ **Whitelist builtins** : Seules les fonctions sûres autorisées
- ✅ **Blocage imports** : os, sys, subprocess, socket, etc.
- ✅ **Blocage fonctions** : eval, exec, open, compile, __import__
- ✅ **Timeout** : 5 secondes maximum (thread-based, compatible Windows)
- ✅ **Limite boucles** : Maximum 20 boucles par code
- ✅ **Limite récursion** : Maximum 100 niveaux
- ✅ **Détection tentatives** : Logs des codes dangereux

#### Code interdit (exemples)
```python
import os  # ❌ BLOQUÉ
eval('code')  # ❌ BLOQUÉ
__import__('sys')  # ❌ BLOQUÉ
open('file.txt')  # ❌ BLOQUÉ
while True: pass  # ❌ TIMEOUT après 5s
```

### 5. **Headers de Sécurité**

Tous les headers critiques sont ajoutés automatiquement :

```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'; ...
Strict-Transport-Security: max-age=31536000 (si HTTPS)
```

### 6. **CORS (Cross-Origin Resource Sharing)**

- **Domaines autorisés** : Configurables dans `.env`
- **Par défaut** : `http://localhost:5173` (dev)
- **Headers autorisés** : Content-Type, Authorization
- **Méthodes** : GET, POST, PUT, DELETE, OPTIONS

### 7. **Logging & Monitoring**

#### Fichiers de logs
- `logs/security.log` : Événements de sécurité
- `logs/api.log` : Requêtes API
- `logs/auth.log` : Authentifications
- `logs/error.log` : Erreurs

#### Événements loggés
- Tentatives de connexion (succès/échec)
- Tentatives d'exécution de code dangereux
- Erreurs d'authentification
- Rate limit dépassé
- Erreurs serveur

#### Rotation automatique
- Taille maximale : 10MB par fichier
- Historique : 5 fichiers
- Format : JSON structuré

### 8. **Variables d'Environnement**

Fichier `.env` (JAMAIS commit sur Git) :

```env
JWT_SECRET_KEY=votre_secret_super_securise
FLASK_SECRET_KEY=autre_secret_securise
CORS_ORIGINS=http://localhost:5173,https://votredomaine.com
RATE_LIMIT_DEFAULT=100 per hour
```

---

## 🚀 Configuration Production

### 1. Serveur WSGI (Gunicorn)

**Lancer avec Gunicorn** :
```bash
gunicorn -c gunicorn_config.py "api.app:app"
```

**Configuration** : `gunicorn_config.py`
- Workers : CPU * 2 + 1
- Timeout : 30s
- Logs : `logs/access.log` et `logs/error.log`

### 2. Reverse Proxy (Nginx)

**Configuration recommandée** :
```nginx
server {
    listen 80;
    server_name api.votredomaine.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Rate limiting supplémentaire
        limit_req zone=api burst=20 nodelay;
    }
}
```

### 3. HTTPS/SSL

**Activer HTTPS** :
1. Obtenir certificat SSL (Let's Encrypt)
2. Dans `.env` : `FORCE_HTTPS=True`
3. Configurer Nginx pour SSL

### 4. Firewall

**Règles recommandées** :
```bash
# Autoriser HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Bloquer accès direct port 5000
ufw deny 5000/tcp

# SSH uniquement
ufw allow 22/tcp
```

---

## 🧪 Tests de Sécurité

### Lancer les tests
```bash
cd backend
pytest tests/test_security.py -v
```

### Tests couverts
- ✅ Hash/vérification mots de passe
- ✅ Création/décodage JWT
- ✅ Validation inputs
- ✅ Sanitization XSS
- ✅ Blocage imports dangereux
- ✅ Blocage fonctions dangereuses
- ✅ Timeout boucles infinies
- ✅ Limite récursion
- ✅ Protection memory bomb

### Tests de pénétration (manuel)

**SQL Injection** :
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin' OR '1'='1", "password": "test"}'
```
→ ❌ Devrait échouer (validation)

**XSS** :
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "<script>alert('xss')</script>", ...}'
```
→ ❌ Devrait échouer (sanitization)

**Code Injection** :
```bash
curl -X POST http://localhost:5000/api/exercices/executer \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"code": "import os; os.system('ls')"}'
```
→ ❌ Devrait échouer (blocage imports)

---

## 📊 Checklist Sécurité

Avant mise en production :

- [ ] Changer tous les secrets dans `.env`
- [ ] Activer HTTPS
- [ ] Configurer Gunicorn
- [ ] Mettre Nginx en reverse proxy
- [ ] Configurer firewall
- [ ] Backup automatique de la DB
- [ ] Monitoring (Prometheus/Grafana)
- [ ] Tests de charge
- [ ] Tests de pénétration
- [ ] Audit de sécurité OWASP

---

## 🔗 Ressources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/2.3.x/security/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [bcrypt](https://github.com/pyca/bcrypt/)

---

## 📞 Contact Sécurité

Pour signaler une vulnérabilité : security@votredomaine.com

**Divulgation responsable** : Nous répondons sous 48h.
