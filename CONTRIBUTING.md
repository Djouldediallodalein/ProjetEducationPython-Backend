# 🤝 Guide de Contribution - PyQuest Backend

Merci de votre intérêt pour contribuer à PyQuest ! Ce document fournit les directives pour contribuer efficacement au projet.

## 📋 Table des matières

- [Code de Conduite](#code-de-conduite)
- [Comment contribuer](#comment-contribuer)
- [Standards de code](#standards-de-code)
- [Process de développement](#process-de-développement)
- [Tests](#tests)
- [Documentation](#documentation)

## 🤝 Code de Conduite

En participant à ce projet, vous acceptez de maintenir un environnement respectueux et inclusif pour tous.

### Nos engagements

- Utiliser un langage accueillant et inclusif
- Respecter les différents points de vue et expériences
- Accepter les critiques constructives avec grâce
- Se concentrer sur ce qui est meilleur pour la communauté
- Faire preuve d'empathie envers les autres membres

## 🚀 Comment contribuer

### 1. Fork et Clone

```bash
# Fork le projet sur GitHub
# Puis cloner votre fork
git clone https://github.com/VOTRE_USERNAME/ProjetEducationPython-Backend.git
cd ProjetEducationPython-Backend
```

### 2. Créer une branche

```bash
# Créer une branche pour votre feature/fix
git checkout -b feature/ma-super-fonctionnalite

# Ou pour un bugfix
git checkout -b fix/correction-bug-xyz
```

### 3. Développer

- Écrivez du code propre et commenté
- Suivez les standards Python (PEP 8)
- Ajoutez des tests pour vos modifications
- Mettez à jour la documentation si nécessaire

### 4. Tester

```bash
# Lancer tous les tests
python -m pytest tests/ -v

# Vérifier la couverture
python -m pytest tests/ --cov=modules --cov=api --cov-report=html

# Vérifier le style de code
flake8 modules/ api/ --max-line-length=120

# Type checking (optionnel)
mypy modules/ api/
```

### 5. Commit

```bash
# Commits clairs et descriptifs
git add .
git commit -m "feat: Ajout de la fonctionnalité X"

# Types de commits recommandés:
# feat: Nouvelle fonctionnalité
# fix: Correction de bug
# docs: Documentation
# style: Formatage, points-virgules manquants, etc.
# refactor: Refactoring du code
# test: Ajout de tests
# chore: Maintenance, dépendances
```

### 6. Push et Pull Request

```bash
# Push vers votre fork
git push origin feature/ma-super-fonctionnalite

# Créer une Pull Request sur GitHub
# Remplir le template de PR avec:
# - Description claire des changements
# - Screenshots si applicable
# - Référence aux issues liées
# - Checklist complétée
```

## 📝 Standards de code

### Python Style Guide

Nous suivons la **PEP 8** avec quelques ajustements:

```python
# ✅ Bon
def calculer_xp_total(niveau: int, exercices_completes: int) -> int:
    """
    Calcule le total d'XP basé sur le niveau et les exercices.
    
    Args:
        niveau: Niveau actuel de l'utilisateur
        exercices_completes: Nombre d'exercices réussis
        
    Returns:
        Total d'XP calculé
    """
    base_xp = niveau * 100
    bonus = exercices_completes * 50
    return base_xp + bonus

# ❌ Mauvais
def calc_xp(n,e):
    return n*100+e*50
```

### Conventions de nommage

- **Variables et fonctions**: `snake_case`
- **Classes**: `PascalCase`
- **Constantes**: `UPPER_SNAKE_CASE`
- **Fichiers**: `snake_case.py`

```python
# Variables
utilisateur_actif = "Jean"
score_total = 1500

# Fonctions
def verifier_reponse(exercice, reponse):
    pass

# Classes
class GestionnaireUtilisateurs:
    pass

# Constantes
MAX_TENTATIVES = 3
SEUILS_NIVEAU = [0, 100, 300, 600]
```

### Documentation des fonctions

Toutes les fonctions publiques doivent avoir une docstring:

```python
def generer_exercice(niveau: int, theme: str, domaine: str = 'python') -> dict:
    """
    Génère un exercice adapté au niveau et thème spécifiés.
    
    Cherche d'abord dans la banque locale d'exercices non complétés.
    Si aucun n'est disponible, génère un nouvel exercice via l'IA.
    
    Args:
        niveau: Niveau de difficulté (1-3)
        theme: Thème de l'exercice (ex: "Variables et types")
        domaine: Domaine d'apprentissage (défaut: 'python')
    
    Returns:
        dict: {
            'type': 'code' ou 'qcm',
            'enonce': 'Description de l'exercice'
        }
    
    Raises:
        ValueError: Si le niveau n'est pas entre 1 et 3
        ConnectionError: Si l'IA n'est pas disponible
    
    Example:
        >>> ex = generer_exercice(1, "Variables", "python")
        >>> print(ex['type'])
        'code'
    """
    # Implementation...
```

### Gestion des erreurs

```python
# ✅ Bon - Spécifique et informatif
try:
    utilisateur = charger_utilisateur(user_id)
except FileNotFoundError:
    log_error(f"Utilisateur {user_id} introuvable")
    return {"error": "Utilisateur non trouvé"}, 404
except json.JSONDecodeError as e:
    log_error(f"Fichier utilisateur corrompu: {e}")
    return {"error": "Données corrompues"}, 500

# ❌ Mauvais - Trop générique
try:
    utilisateur = charger_utilisateur(user_id)
except Exception as e:
    print("Erreur")
    return None
```

## 🔄 Process de développement

### Workflow Git

```
main
  ├── develop (branche de développement)
  │   ├── feature/nouvelle-fonctionnalite
  │   ├── feature/autre-fonctionnalite
  │   └── fix/correction-bug
  └── hotfix/correction-urgente (merge direct dans main)
```

### Branches

- `main`: Code en production, stable
- `develop`: Code en cours de développement
- `feature/*`: Nouvelles fonctionnalités
- `fix/*`: Corrections de bugs
- `hotfix/*`: Corrections urgentes pour la production

### Pull Requests

**Template de PR:**

```markdown
## Description
[Description claire des changements]

## Type de changement
- [ ] Bugfix
- [ ] Nouvelle fonctionnalité
- [ ] Breaking change
- [ ] Documentation

## Tests
- [ ] Tests unitaires ajoutés/modifiés
- [ ] Tests passent en local
- [ ] Couverture de code maintenue/améliorée

## Checklist
- [ ] Code suit les standards du projet
- [ ] Documentation mise à jour
- [ ] Pas de warnings
- [ ] Changelog mis à jour

## Screenshots (si applicable)
[Captures d'écran]

## Issues liées
Closes #123
```

## 🧪 Tests

### Structure des tests

```
tests/
├── __init__.py
├── conftest.py              # Fixtures pytest
├── test_basic.py           # Tests unitaires modules
├── test_api.py             # Tests intégration API
├── test_security.py        # Tests sécurité
└── test_performance.py     # Tests de performance
```

### Écrire des tests

```python
import pytest
from modules.core.xp_systeme import calculer_xp

def test_calculer_xp_niveau_1():
    """Test du calcul XP pour niveau 1"""
    xp = calculer_xp(niveau=1, difficulte=1, reussi=True)
    assert xp == 10
    
def test_calculer_xp_echec():
    """Test XP = 0 en cas d'échec"""
    xp = calculer_xp(niveau=1, difficulte=1, reussi=False)
    assert xp == 0

@pytest.mark.parametrize("niveau,difficulte,attendu", [
    (1, 1, 10),
    (1, 2, 20),
    (2, 1, 20),
    (3, 3, 90),
])
def test_calculer_xp_parametres(niveau, difficulte, attendu):
    """Test XP avec différents paramètres"""
    xp = calculer_xp(niveau, difficulte, True)
    assert xp == attendu
```

### Coverage minimum

- **Nouveau code**: 80% de couverture minimum
- **Code critique** (sécurité, auth): 95%+
- **Code legacy**: Amélioration progressive

## 📚 Documentation

### README.md

Maintenir le README à jour avec:
- Instructions d'installation
- Exemples d'utilisation
- API endpoints
- FAQ

### Docstrings

Toutes les fonctions/classes publiques doivent avoir:
- Description courte
- Args avec types
- Returns avec type
- Raises si applicable
- Example si utile

### CHANGELOG.md

À chaque PR, mettre à jour le CHANGELOG avec:
- Section [Unreleased]
- Type de changement (Ajouté, Modifié, etc.)
- Description courte

## 🎯 Priorités de développement

### Haute priorité
- Corrections de bugs critiques
- Failles de sécurité
- Perte de données

### Moyenne priorité
- Nouvelles fonctionnalités
- Améliorations de performance
- Documentation

### Basse priorité
- Refactoring
- Optimisations mineures
- Nice-to-have features

## 🐛 Rapporter un bug

### Template d'issue

```markdown
## Description du bug
[Description claire et concise]

## Reproduction
1. Aller à '...'
2. Cliquer sur '...'
3. Scroller jusqu'à '...'
4. Voir l'erreur

## Comportement attendu
[Ce qui devrait se passer]

## Screenshots
[Si applicable]

## Environnement
- OS: [Windows 11]
- Python: [3.11.2]
- Version: [1.0.0]

## Logs
```
[Coller les logs pertinents]
```

## Informations additionnelles
[Tout contexte supplémentaire]
```

## 📞 Contact

- **Issues**: https://github.com/Djouldediallodalein/ProjetEducationPython-Backend/issues
- **Discussions**: https://github.com/Djouldediallodalein/ProjetEducationPython-Backend/discussions
- **Email**: (si applicable)

## 🙏 Remerciements

Merci à tous les contributeurs qui aident à améliorer PyQuest !

---

**Dernière mise à jour**: 5 février 2026
