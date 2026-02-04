"""
Tests de l'API REST
Execute : pytest tests/test_api.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from api.app import app

@pytest.fixture
def client():
    """Créer un client de test Flask"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Test du endpoint de santé"""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert 'version' in data

def test_generer_exercice(client):
    """Test de génération d'exercice"""
    response = client.post('/api/exercices/generer', json={
        'niveau': 1,
        'theme': 'Variables',
        'domaine': 'python'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert 'exercice' in data

def test_executer_code(client):
    """Test d'exécution de code"""
    response = client.post('/api/exercices/executer', json={
        'code': 'print("Test")',
        'timeout': 5
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert 'Test' in data['output']

def test_domaines(client):
    """Test de récupération des domaines"""
    response = client.get('/api/domaines')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert 'domaines' in data

def test_progression(client):
    """Test de récupération de la progression"""
    response = client.get('/api/progression')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert 'progression' in data

def test_error_404(client):
    """Test erreur 404"""
    response = client.get('/api/inexistant')
    assert response.status_code == 404
    data = response.get_json()
    assert data['success'] == False

if __name__ == '__main__':
    print("Lancement des tests API...")
    pytest.main([__file__, '-v'])
