"""
Tests basiques pour vérifier que tout fonctionne
Execute : pytest tests/test_basic.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

# Tests des imports
def test_imports_core():
    """Vérifie que tous les modules core s'importent correctement"""
    from modules.core import fonctions
    from modules.core import progression
    from modules.core import domaines
    from modules.core import xp_systeme
    from modules.core import avancees
    from modules.core import utilisateurs
    from modules.core import repetition_espacee
    from modules.core import export_import
    from modules.core import gestion_erreurs
    assert True

def test_imports_features():
    """Vérifie que tous les modules features s'importent correctement"""
    from modules.features import defis_quotidiens
    from modules.features import comparaison_domaines
    from modules.features import classement
    from modules.features import quetes
    from modules.features import export_avance
    from modules.features import themes
    from modules.features import notifications
    from modules.features import mode_hors_ligne
    from modules.features import analytics
    from modules.features import collaboratif
    assert True

def test_config():
    """Vérifie que la configuration se charge"""
    from config import Config
    assert Config.OLLAMA_MODEL is not None
    assert Config.API_PORT > 0
    assert Config.CODE_TIMEOUT > 0

def test_charger_domaines():
    """Vérifie que les domaines se chargent"""
    from modules.core.domaines import charger_domaines
    domaines = charger_domaines()
    assert isinstance(domaines, dict)
    assert len(domaines) > 0

def test_charger_progression():
    """Vérifie que la progression se charge"""
    from modules.core.progression import charger_progression
    progression = charger_progression()
    assert isinstance(progression, dict)

def test_executer_code_simple():
    """Vérifie l'exécution de code simple"""
    from modules.core.fonctions import executer_code_securise
    
    code = "print('Hello World')"
    resultat = executer_code_securise(code)
    
    assert resultat['success'] == True
    assert 'Hello World' in resultat['output']

def test_executer_code_avec_erreur():
    """Vérifie la gestion d'erreur"""
    from modules.core.fonctions import executer_code_securise
    
    code = "print(variable_inexistante)"
    resultat = executer_code_securise(code)
    
    assert resultat['success'] == False
    assert resultat['error'] != ''

def test_bloquer_import_dangereux():
    """Vérifie le blocage des imports dangereux"""
    from modules.core.fonctions import executer_code_securise
    
    code = "import os\nos.system('ls')"
    resultat = executer_code_securise(code)
    
    assert resultat['success'] == False
    assert 'interdit' in resultat['error'].lower()

def test_calculer_xp():
    """Vérifie le calcul d'XP"""
    from modules.core.xp_systeme import calculer_xp
    
    xp = calculer_xp('code', 2, 1, 5)
    assert xp > 0

def test_calculer_niveau():
    """Vérifie le calcul de niveau"""
    from modules.core.xp_systeme import calculer_niveau
    
    niveau = calculer_niveau(100)
    assert niveau >= 1

if __name__ == '__main__':
    print("Lancement des tests...")
    pytest.main([__file__, '-v'])
