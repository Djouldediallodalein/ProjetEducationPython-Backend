# 🚀 API REST - Application d'Apprentissage

## Vue d'ensemble

Cette API REST permet au frontend (React) de communiquer avec le backend Python. Elle expose toutes les fonctionnalités de l'application via des endpoints HTTP.

---

## 🔧 Installation

### 1. Installer les dépendances

```bash
cd backend
pip install -r requirements.txt
```

### 2. Lancer l'API

**Option 1 : Depuis le dossier API**
```bash
cd backend/api
python app.py
```

**Option 2 : Script de démarrage (racine du projet)**
```bash
# Windows PowerShell
.\start_api.ps1

# Ou directement
cd backend
python start_api.py
```

L'API sera disponible sur : **http://localhost:5000**

---

## 📚 Endpoints Disponibles

### 🏥 Santé de l'API

#### `GET /api/health`
Vérifie que l'API fonctionne correctement.

**Réponse :**
```json
{
  "success": true,
  "message": "API fonctionnelle",
  "version": "1.0.0",
  "endpoints": 10
}
```

---

### 📝 Exercices

#### `POST /api/exercices/generer`
Génère un nouvel exercice avec l'IA.

**Body :**
```json
{
  "niveau": 2,
  "theme": "Boucles",
  "domaine": "python"
}
```

**Réponse :**
```json
{
  "success": true,
  "exercice": "Créez une fonction qui...",
  "niveau": 2,
  "theme": "Boucles",
  "domaine": "python"
}
```

#### `POST /api/exercices/verifier`
Vérifie une solution avec l'IA.

**Body :**
```json
{
  "exercice": "Créez une fonction...",
  "solution": "def ma_fonction():\n    return 42"
}
```

**Réponse :**
```json
{
  "success": true,
  "verification": "Votre solution est correcte car...",
  "reussi": true
}
```

#### `POST /api/exercices/executer`
Exécute du code Python de manière sécurisée.

**Body :**
```json
{
  "code": "print('Hello')\nprint(5 + 3)",
  "timeout": 5
}
```

**Réponse :**
```json
{
  "success": true,
  "output": "Hello\n8\n",
  "error": "",
  "timeout": false
}
```

#### `POST /api/exercices/tester`
Teste du code avec plusieurs cas de test.

**Body :**
```json
{
  "code": "def double(x):\n    return x * 2",
  "tests": [
    ["double(5)", 10],
    ["double(3)", 6],
    ["double(0)", 0]
  ]
}
```

**Réponse :**
```json
{
  "success": true,
  "tests_reussis": 3,
  "tests_total": 3,
  "details": [
    {
      "test": 1,
      "input": "double(5)",
      "expected": 10,
      "got": 10,
      "success": true
    },
    ...
  ]
}
```

---

### 📊 Progression

#### `GET /api/progression`
Récupère la progression complète de l'utilisateur actuel.

**Réponse :**
```json
{
  "success": true,
  "progression": {
    "niveau_global": 5,
    "xp": 1250,
    "badges_obtenus": ["Premier Pas", "Studieux"],
    "domaines": {
      "python": {
        "Variables": {
          "tentatives": 10,
          "reussites": 8
        }
      }
    }
  }
}
```

#### `POST /api/progression/update`
Met à jour la progression après un exercice.

**Body :**
```json
{
  "theme": "Boucles",
  "reussi": true,
  "domaine": "python"
}
```

**Réponse :**
```json
{
  "success": true,
  "message": "Progression mise a jour",
  "theme": "Boucles",
  "reussi": true
}
```

#### `GET /api/progression/stats`
Récupère les statistiques globales.

**Réponse :**
```json
{
  "success": true,
  "stats": {
    "total_exercices": 50,
    "reussis": 40,
    "taux_reussite": 80.0,
    "niveau": 5,
    "xp": 1250
  }
}
```

---

### 🌍 Domaines

#### `GET /api/domaines`
Liste tous les domaines d'apprentissage disponibles.

**Réponse :**
```json
{
  "success": true,
  "domaines": {
    "python": {
      "nom": "Python",
      "emoji": "🐍",
      "themes": ["Variables", "Boucles", "Fonctions", ...]
    },
    "javascript": {
      "nom": "JavaScript",
      "emoji": "⚡",
      "themes": ["Variables", "Fonctions", "DOM", ...]
    },
    ...
  },
  "count": 8
}
```

#### `GET /api/domaines/<domaine_id>/themes`
Liste les thèmes d'un domaine spécifique.

**Exemple :** `GET /api/domaines/python/themes`

**Réponse :**
```json
{
  "success": true,
  "domaine": "python",
  "themes": [
    "Variables",
    "Boucles",
    "Fonctions",
    "Listes",
    "Dictionnaires",
    "Classes",
    "Fichiers",
    "Exceptions"
  ],
  "count": 8
}
```

---

### 👤 Utilisateurs

#### `GET /api/utilisateurs`
Liste tous les utilisateurs.

**Réponse :**
```json
{
  "success": true,
  "utilisateurs": ["Mamad", "Alice", "Bob"],
  "actuel": "Mamad",
  "count": 3
}
```

#### `POST /api/utilisateurs/creer`
Crée un nouvel utilisateur.

**Body :**
```json
{
  "nom": "Charlie"
}
```

**Réponse :**
```json
{
  "success": true,
  "message": "Utilisateur Charlie cree avec succes",
  "nom": "Charlie"
}
```

#### `POST /api/utilisateurs/selectionner`
Sélectionne un utilisateur actif.

**Body :**
```json
{
  "nom": "Alice"
}
```

**Réponse :**
```json
{
  "success": true,
  "message": "Utilisateur Alice selectionne",
  "nom": "Alice"
}
```

---

### 🏆 Badges et XP

#### `GET /api/badges`
Liste les badges obtenus par l'utilisateur.

**Réponse :**
```json
{
  "success": true,
  "badges": ["Premier Pas", "Studieux", "Explorateur"],
  "nouveaux": ["Explorateur"],
  "count": 3
}
```

#### `GET /api/xp`
Récupère les informations XP et niveau.

**Réponse :**
```json
{
  "success": true,
  "xp": 1250,
  "niveau": 5,
  "xp_prochain_niveau": 1500,
  "progression_niveau": 100,
  "xp_requis_niveau": 250
}
```

---

## 🔒 Sécurité

### Exécution de Code Sécurisée

L'endpoint `/api/exercices/executer` utilise un système de **sandbox** pour exécuter le code Python de manière sécurisée :

**Protection :**
- ✅ **Imports interdits** : os, sys, subprocess, socket, requests, etc.
- ✅ **Instructions dangereuses bloquées** : eval, exec, open, __import__
- ✅ **Environnement limité** : Seulement fonctions Python de base autorisées
- ✅ **Timeout** : 5 secondes maximum par exécution
- ✅ **Isolation** : Aucun accès au système de fichiers

**Fonctions autorisées :**
```python
print, len, range, str, int, float, bool, list, dict, tuple, set,
sum, max, min, abs, round, enumerate, zip, map, filter, sorted,
reversed, any, all, type, isinstance, chr, ord, pow, divmod
```

### CORS

L'API est configurée avec **Flask-CORS** pour permettre les requêtes cross-origin depuis le frontend :

```python
CORS(app)  # Autorise toutes les origines en développement
```

**Note :** En production, il faudra restreindre les origines autorisées.

---

## 🧪 Tests

### Tester avec curl

```bash
# Health check
curl http://localhost:5000/api/health

# Lister les domaines
curl http://localhost:5000/api/domaines

# Générer un exercice
curl -X POST http://localhost:5000/api/exercices/generer \
  -H "Content-Type: application/json" \
  -d '{"niveau": 2, "theme": "Boucles", "domaine": "python"}'

# Exécuter du code
curl -X POST http://localhost:5000/api/exercices/executer \
  -H "Content-Type: application/json" \
  -d '{"code": "print(\"Hello from API!\")"}'
```

### Tester avec Python

Utiliser le script de test fourni :

```bash
cd backend
python test_api.py
```

Ce script teste automatiquement tous les endpoints de l'API.

### Tester avec le navigateur

Ouvrir dans votre navigateur :
```
http://localhost:5000/api/health
```

---

## 📊 Gestion d'Erreurs

L'API retourne des codes HTTP standards :

| Code | Signification | Exemple |
|------|---------------|---------|
| **200** | Succès | Requête réussie |
| **201** | Créé | Utilisateur créé |
| **400** | Requête invalide | Paramètres manquants |
| **404** | Non trouvé | Endpoint inexistant |
| **405** | Méthode non autorisée | GET au lieu de POST |
| **500** | Erreur serveur | Erreur interne |

**Format des erreurs :**
```json
{
  "success": false,
  "error": "Message d'erreur descriptif",
  "code": 400
}
```

---

## 🚀 Utilisation avec React

### Exemple avec fetch

```javascript
// Générer un exercice
async function genererExercice() {
  const response = await fetch('http://localhost:5000/api/exercices/generer', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      niveau: 2,
      theme: 'Boucles',
      domaine: 'python'
    })
  });
  
  const data = await response.json();
  if (data.success) {
    console.log('Exercice:', data.exercice);
  }
}

// Exécuter du code
async function executerCode(code) {
  const response = await fetch('http://localhost:5000/api/exercices/executer', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ code })
  });
  
  const data = await response.json();
  return data;
}
```

### Exemple avec axios

```javascript
import axios from 'axios';

const API_URL = 'http://localhost:5000';

// Créer une instance axios
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Générer un exercice
async function genererExercice(niveau, theme, domaine) {
  try {
    const response = await api.post('/api/exercices/generer', {
      niveau,
      theme,
      domaine
    });
    return response.data;
  } catch (error) {
    console.error('Erreur:', error);
  }
}

// Obtenir la progression
async function obtenirProgression() {
  try {
    const response = await api.get('/api/progression');
    return response.data.progression;
  } catch (error) {
    console.error('Erreur:', error);
  }
}
```

---

## 📝 Configuration

### Variables d'environnement (optionnel)

Créer un fichier `.env` dans `backend/` :

```
# Ollama
OLLAMA_MODEL=qwen2.5-coder:14b
OLLAMA_HOST=http://localhost:11434

# API
API_PORT=5000
API_HOST=0.0.0.0
DEBUG=True

# Sécurité
CODE_TIMEOUT=5
```

### Mode Production

Pour déployer en production, utiliser **gunicorn** :

```bash
pip install gunicorn

# Lancer avec gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api.app:app
```

---

## 🛠️ Développement

### Ajouter un nouvel endpoint

1. Ouvrir `backend/api/routes.py`
2. Ajouter la nouvelle route :

```python
@app.route('/api/mon-endpoint', methods=['POST'])
def mon_endpoint():
    """Documentation de l'endpoint"""
    try:
        data = request.json or {}
        # Traitement...
        
        return jsonify({
            'success': True,
            'resultat': '...'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

3. Tester l'endpoint
4. Mettre à jour la documentation

---

## 📚 Ressources

- **Flask Documentation** : https://flask.palletsprojects.com/
- **Flask-CORS** : https://flask-cors.readthedocs.io/
- **REST API Best Practices** : https://restfulapi.net/

---

## 🎯 Prochaines Étapes

1. ✅ API fonctionnelle avec 13 endpoints
2. ⏳ Connexion avec le frontend React
3. ⏳ Ajout de tests automatisés
4. ⏳ Documentation Swagger/OpenAPI
5. ⏳ Rate limiting pour production
6. ⏳ Authentification JWT (si nécessaire)

---

**Version :** 1.0.0  
**Status :** ✅ Production Ready  
**Port :** 5000  
**URL :** http://localhost:5000
