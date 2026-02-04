# 🔐 Guide d'Authentification JWT - PyQuest API

## Vue d'ensemble

L'API PyQuest utilise une authentification JWT (JSON Web Tokens) avec deux types de tokens :
- **Access Token** : Courte durée (30 minutes) - pour les requêtes API
- **Refresh Token** : Longue durée (7 jours) - pour renouveler l'access token

## Flux d'authentification

```
┌─────────┐                  ┌─────────┐                  ┌─────────┐
│ Client  │                  │   API   │                  │  Base   │
│         │                  │         │                  │ Données │
└────┬────┘                  └────┬────┘                  └────┬────┘
     │                            │                            │
     │  1. POST /api/auth/login   │                            │
     ├───────────────────────────>│                            │
     │   {username, password}     │                            │
     │                            │  2. Vérifier credentials   │
     │                            ├───────────────────────────>│
     │                            │<───────────────────────────┤
     │                            │                            │
     │  3. Return tokens          │                            │
     │<───────────────────────────┤                            │
     │   {access_token,           │                            │
     │    refresh_token}          │                            │
     │                            │                            │
     │  4. GET /api/progression   │                            │
     │    Authorization: Bearer   │                            │
     ├───────────────────────────>│  5. Vérifier token         │
     │                            │────┐                       │
     │                            │<───┘                       │
     │                            │  6. Get data               │
     │                            ├───────────────────────────>│
     │  7. Return data            │<───────────────────────────┤
     │<───────────────────────────┤                            │
     │                            │                            │
```

## Endpoints d'authentification

### 1. Inscription (Register)

**Endpoint** : `POST /api/auth/register`  
**Rate Limit** : 5 requêtes/heure  
**Auth** : Aucune

**Request** :
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "niveau": "debutant"
}
```

**Response** (201 Created) :
```json
{
  "message": "Utilisateur créé avec succès",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "username": "john_doe",
    "email": "john@example.com",
    "niveau": "debutant",
    "role": "user"
  }
}
```

**Erreurs** :
- `400` : Validation échouée (email invalide, mot de passe faible, etc.)
- `409` : Utilisateur déjà existant
- `429` : Rate limit dépassé

---

### 2. Connexion (Login)

**Endpoint** : `POST /api/auth/login`  
**Rate Limit** : 10 requêtes/heure  
**Auth** : Aucune

**Request** :
```json
{
  "username": "john_doe",
  "password": "SecurePass123!"
}
```

**Response** (200 OK) :
```json
{
  "message": "Connexion réussie",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "username": "john_doe",
    "email": "john@example.com",
    "niveau": "debutant",
    "role": "user",
    "xp_total": 250,
    "niveau_actuel": 3
  }
}
```

**Erreurs** :
- `401` : Identifiants incorrects
- `429` : Rate limit dépassé

---

### 3. Rafraîchir le token (Refresh)

**Endpoint** : `POST /api/auth/refresh`  
**Rate Limit** : 20 requêtes/heure  
**Auth** : Aucune (utilise le refresh token)

**Request** :
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response** (200 OK) :
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Erreurs** :
- `401` : Refresh token invalide ou expiré
- `429` : Rate limit dépassé

---

### 4. Informations utilisateur (Me)

**Endpoint** : `GET /api/auth/me`  
**Rate Limit** : 50 requêtes/heure  
**Auth** : ✅ Requise (Bearer token)

**Headers** :
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Response** (200 OK) :
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "niveau": "debutant",
  "role": "user",
  "xp_total": 250,
  "niveau_actuel": 3,
  "badges": ["first_step", "python_lover"]
}
```

**Erreurs** :
- `401` : Token manquant, invalide ou expiré
- `404` : Utilisateur non trouvé

---

## Utilisation côté client

### JavaScript/TypeScript (Fetch API)

```javascript
// 1. Login et stockage des tokens
async function login(username, password) {
  const response = await fetch('http://localhost:5000/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ username, password })
  });

  if (!response.ok) {
    throw new Error('Login failed');
  }

  const data = await response.json();
  
  // Stocker les tokens (localStorage ou sessionStorage)
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);
  
  return data.user;
}

// 2. Requête protégée avec Bearer token
async function getProgression() {
  const accessToken = localStorage.getItem('access_token');
  
  const response = await fetch('http://localhost:5000/api/progression', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`
    }
  });

  if (response.status === 401) {
    // Token expiré, rafraîchir
    await refreshAccessToken();
    return getProgression(); // Retry
  }

  return await response.json();
}

// 3. Rafraîchir l'access token
async function refreshAccessToken() {
  const refreshToken = localStorage.getItem('refresh_token');
  
  const response = await fetch('http://localhost:5000/api/auth/refresh', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ refresh_token: refreshToken })
  });

  if (!response.ok) {
    // Refresh token invalide, rediriger vers login
    localStorage.clear();
    window.location.href = '/login';
    return;
  }

  const data = await response.json();
  localStorage.setItem('access_token', data.access_token);
}

// 4. Logout
function logout() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  window.location.href = '/login';
}
```

---

### React avec Axios (Recommandé)

```javascript
import axios from 'axios';

// Configuration d'Axios avec intercepteur
const api = axios.create({
  baseURL: 'http://localhost:5000/api'
});

// Ajouter automatiquement le Bearer token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Gérer automatiquement le refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Si 401 et pas déjà retry
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(
          'http://localhost:5000/api/auth/refresh',
          { refresh_token: refreshToken }
        );

        const { access_token } = response.data;
        localStorage.setItem('access_token', access_token);

        // Retry la requête originale
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed, logout
        localStorage.clear();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;

// Utilisation
import api from './api';

// Login
const login = async (username, password) => {
  const response = await api.post('/auth/login', { username, password });
  localStorage.setItem('access_token', response.data.access_token);
  localStorage.setItem('refresh_token', response.data.refresh_token);
  return response.data.user;
};

// Requête protégée (Bearer token ajouté automatiquement)
const getProgression = async () => {
  const response = await api.get('/progression');
  return response.data;
};
```

---

## Structure du JWT

### Access Token

```json
{
  "user_id": "john_doe",
  "exp": 1704123456,
  "iat": 1704121656,
  "type": "access"
}
```

### Refresh Token

```json
{
  "user_id": "john_doe",
  "exp": 1704728256,
  "iat": 1704121656,
  "type": "refresh"
}
```

---

## Sécurité

### Bonnes pratiques

✅ **À FAIRE** :
- Stocker les tokens dans `localStorage` ou `sessionStorage`
- Toujours envoyer le token dans le header `Authorization: Bearer <token>`
- Vérifier le statut 401 et rafraîchir automatiquement
- Nettoyer les tokens au logout

❌ **À NE PAS FAIRE** :
- Stocker les tokens dans des cookies non-HttpOnly
- Envoyer le token dans l'URL
- Partager le token entre domaines non sécurisés
- Ignorer les erreurs 401

### Gestion des erreurs

```javascript
try {
  await api.get('/progression');
} catch (error) {
  if (error.response?.status === 401) {
    console.log('Non authentifié');
    // Rediriger vers login
  } else if (error.response?.status === 429) {
    console.log('Rate limit dépassé');
    // Afficher message d'attente
  } else {
    console.log('Erreur:', error.message);
  }
}
```

---

## Endpoints protégés

Tous les endpoints suivants nécessitent un Bearer token :

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/auth/me` | GET | Infos utilisateur |
| `/api/exercices/generer` | POST | Générer exercice |
| `/api/exercices/executer` | POST | Exécuter code |
| `/api/progression` | GET | Progression utilisateur |
| `/api/progression` | POST | Mettre à jour progression |
| `/api/domaines` | GET | Liste des domaines |
| `/api/users/<username>/stats` | GET | Stats utilisateur |
| `/api/admin/*` | * | Endpoints admin (role required) |

---

## Troubleshooting

### "Token invalide ou expiré"
- Vérifier que le token n'est pas vide
- Vérifier la date d'expiration
- Essayer de rafraîchir avec le refresh token

### "Authorization header manquant"
- Vérifier que le header est bien `Authorization: Bearer <token>`
- Pas `Authorization: <token>` (manque "Bearer")

### "Rate limit exceeded"
- Attendre avant de retenter
- Vérifier qu'il n'y a pas de boucle infinie de requêtes

### "CORS error"
- Vérifier que l'origine est autorisée dans `.env`
- Ajouter `http://localhost:5173` si en développement
