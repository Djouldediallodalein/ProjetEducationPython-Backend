# Security Policy

## Versions supportées

| Version | Supportée          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Rapporter une vulnérabilité

Si vous découvrez une vulnérabilité de sécurité, merci de **NE PAS** ouvrir une issue publique.

### Process de divulgation responsable

1. **Email privé**: Envoyez les détails à [votre-email@example.com]
2. **Informations à inclure**:
   - Type de vulnérabilité
   - Étapes de reproduction
   - Impact potentiel
   - Version affectée
   - Suggestions de correctif (optionnel)

3. **Délai de réponse**: 
   - Accusé de réception: 48h
   - Correctif: 7-14 jours selon la gravité
   - Divulgation publique: Après le correctif

### Vulnérabilités en scope

- Injection SQL/NoSQL
- XSS (Cross-Site Scripting)
- CSRF (Cross-Site Request Forgery)
- Authentification/Autorisation
- Exposition de données sensibles
- Exécution de code arbitraire
- Déni de service (DoS)
- Rate limiting bypass

### Hors scope

- Vulnérabilités nécessitant un accès physique
- Social engineering
- DoS nécessitant des ressources massives
- Bugs UI/UX sans impact sécurité

## Sécurité implémentée

### ✅ Authentification
- JWT avec access/refresh tokens
- Bcrypt pour hash des mots de passe (12 rounds)
- Validation de la force des mots de passe
- Expiration automatique des tokens

### ✅ Protection des entrées
- Sanitization de tous les inputs
- Validation stricte (username, email, etc.)
- Limite de taille des requêtes (16MB)
- Blocage des caractères dangereux

### ✅ Exécution de code
- Sandbox Python sécurisé
- Blocage des imports dangereux (os, sys, subprocess)
- Timeout de 5 secondes
- Limite de taille du code (50KB)
- Détection des boucles infinies

### ✅ Headers de sécurité
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Content-Security-Policy
- Strict-Transport-Security (si HTTPS)

### ✅ Rate Limiting
- Global: 100 requêtes/heure
- Register: 5 requêtes/heure
- Login: 10 requêtes/heure
- Endpoints sensibles protégés

### ✅ CORS
- Whitelist de domaines autorisés
- Credentials supportés uniquement pour domaines approuvés
- Headers restreints

### ✅ Logging
- Log des tentatives d'authentification
- Log des événements de sécurité
- Log de l'exécution de code
- Rotation automatique des logs
- Pas de données sensibles loggées

## Best practices pour les développeurs

### Secrets et credentials
```bash
# ✅ FAIRE
JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")

# ❌ NE PAS FAIRE
JWT_SECRET_KEY=my_simple_secret_123
```

### Validation des entrées
```python
# ✅ FAIRE
username = sanitize_string(request.json.get('username', ''))
if not validate_username(username):
    return {"error": "Username invalide"}, 400

# ❌ NE PAS FAIRE
username = request.json['username']
# Utiliser directement sans validation
```

### Gestion des erreurs
```python
# ✅ FAIRE
try:
    user = get_user(user_id)
except UserNotFoundError:
    log_error(f"User {user_id} not found")
    return {"error": "User not found"}, 404

# ❌ NE PAS FAIRE
try:
    user = get_user(user_id)
except Exception as e:
    return {"error": str(e)}, 500  # Expose l'erreur interne
```

### Mots de passe
```python
# ✅ FAIRE
password_hash = hash_password(password)  # Bcrypt
store_user(username, password_hash)

# ❌ NE PAS FAIRE
store_user(username, password)  # Stockage en clair
store_user(username, hashlib.sha256(password))  # Hash faible
```

## Audit de sécurité

### Derniers audits
- **2026-02-05**: Audit interne complet
  - Vulnérabilités critiques: 0
  - Vulnérabilités haute: 0
  - Vulnérabilités moyenne: 2 (corrigées)
  - Vulnérabilités basse: 3 (en cours)

### Outils recommandés
- `bandit` pour l'analyse statique
- `safety` pour les dépendances
- `pytest` avec couverture de code
- `snyk` pour les vulnérabilités

### Commandes d'audit
```bash
# Analyse statique
bandit -r modules/ api/ -ll

# Vulnérabilités des dépendances
safety check

# Tests de sécurité
pytest tests/test_security.py -v
```

## Mises à jour de sécurité

Les correctifs de sécurité sont publiés:
- **Critiques**: Immédiatement (< 24h)
- **Hautes**: 48-72h
- **Moyennes**: 1-2 semaines
- **Basses**: Avec la prochaine version

### S'abonner aux alertes
- Watch le repo GitHub
- Activer les notifications de sécurité
- Suivre le CHANGELOG.md

## Récompenses

### Bug Bounty (futur)
Nous envisageons un programme bug bounty:
- Critiques: 500-1000€
- Hautes: 200-500€
- Moyennes: 50-200€
- Basses: Reconnaissance publique

## Conformité

### Standards suivis
- OWASP Top 10
- CWE/SANS Top 25
- GDPR (protection données)
- PCI-DSS Level 2 (si applicable)

## Contact sécurité

- **Email**: [votre-email@example.com]
- **PGP Key**: [Lien vers clé publique]
- **Response Time**: 48h maximum

## Historique des vulnérabilités

Aucune vulnérabilité publique à ce jour.

---

**Dernière mise à jour**: 5 février 2026
