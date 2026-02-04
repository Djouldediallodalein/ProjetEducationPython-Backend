# Backend - Projet Éducation Python

## 📁 Structure

```
backend/
├── modules/
│   ├── core/                    # Modules de base (9)
│   │   ├── fonctions.py        # Génération exercices (IA)
│   │   ├── progression.py      # Suivi progression
│   │   ├── domaines.py         # Gestion domaines
│   │   ├── xp_systeme.py       # Système XP/niveaux
│   │   ├── avancees.py         # Badges
│   │   ├── repetition_espacee.py # SRS
│   │   ├── utilisateurs.py     # Multi-utilisateurs
│   │   ├── export_import.py    # Sauvegarde
│   │   └── gestion_erreurs.py  # Logging
│   │
│   └── features/                # Améliorations (10)
│       ├── defis_quotidiens.py
│       ├── comparaison_domaines.py
│       ├── classement.py
│       ├── quetes.py
│       ├── export_avance.py
│       ├── themes.py
│       ├── notifications.py
│       ├── mode_hors_ligne.py
│       ├── analytics.py
│       └── collaboratif.py
│
├── data/                        # Données
│   ├── domaines.json           # Configuration domaines
│   ├── defis_quotidiens.json   # Défis
│   ├── utilisateurs.json       # Utilisateurs
│   ├── progression_utilisateur.json
│   ├── exports/                # Exports générés
│   ├── logs/                   # Logs système
│   ├── progressions/           # Progressions utilisateurs
│   └── sauvegardes/            # Backups
│
├── api/                         # API Flask (à venir)
│   └── (routes API pour frontend)
│
├── main.py                      # Point d'entrée
├── requirements.txt             # Dépendances
└── README.md                    # Ce fichier
```

## 🚀 Lancement

```bash
cd backend
python main.py
```

## 📦 Dépendances

Voir `requirements.txt`

```bash
pip install -r requirements.txt
```

## 🔧 Configuration

Les fichiers de configuration sont dans `data/`:
- `domaines.json` - Domaines d'apprentissage
- `utilisateurs.json` - Profils utilisateurs
- `progression_utilisateur.json` - Progression principale

## 🎯 Points d'Entrée

- **main.py** - Application CLI complète
- **api/** (à venir) - API REST pour le frontend

## 📚 Documentation

Consultez `/docs` pour la documentation complète.
