# Tests Backend

## Lancer tous les tests

```bash
cd backend
pytest tests/ -v
```

## Lancer un test spécifique

```bash
# Tests basiques
pytest tests/test_basic.py -v

# Tests API
pytest tests/test_api.py -v
```

## Avec couverture de code

```bash
pytest tests/ --cov=modules --cov-report=html
```

Le rapport sera dans `htmlcov/index.html`
