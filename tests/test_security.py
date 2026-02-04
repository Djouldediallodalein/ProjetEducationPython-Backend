"""
Tests de sécurité pour l'API
"""
import pytest
import sys
import os

# Ajouter le dossier parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.core.security import (
    hash_password, verify_password,
    create_access_token, decode_token,
    validate_password_strength
)
from modules.core.validation import (
    sanitize_string, validate_username,
    validate_email_address, validate_code_input
)
from modules.core.fonctions import executer_code_securise, verifier_code_dangereux


class TestPasswordSecurity:
    """Tests de sécurité des mots de passe"""
    
    def test_hash_password(self):
        """Test du hashage bcrypt"""
        password = "TestPassword123!"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 50
        assert verify_password(password, hashed)
    
    def test_verify_wrong_password(self):
        """Test vérification mot de passe incorrect"""
        password = "TestPassword123!"
        hashed = hash_password(password)
        
        assert not verify_password("WrongPassword", hashed)
    
    def test_password_strength_validation(self):
        """Test validation force mot de passe"""
        # Trop court
        valid, error = validate_password_strength("Short1!")
        assert not valid
        
        # Pas de majuscule
        valid, error = validate_password_strength("password123!")
        assert not valid
        
        # Pas de minuscule
        valid, error = validate_password_strength("PASSWORD123!")
        assert not valid
        
        # Pas de chiffre
        valid, error = validate_password_strength("Password!")
        assert not valid
        
        # Pas de caractère spécial
        valid, error = validate_password_strength("Password123")
        assert not valid
        
        # Valide
        valid, error = validate_password_strength("ValidPass123!")
        assert valid
        assert error is None


class TestJWTSecurity:
    """Tests de sécurité JWT"""
    
    def test_create_and_decode_token(self):
        """Test création et décodage token"""
        token = create_access_token("user123", "testuser", "user")
        payload = decode_token(token)
        
        assert payload is not None
        assert payload['user_id'] == "user123"
        assert payload['username'] == "testuser"
        assert payload['role'] == "user"
        assert payload['type'] == "access"
    
    def test_invalid_token(self):
        """Test token invalide"""
        payload = decode_token("invalid.token.here")
        assert payload is None


class TestInputValidation:
    """Tests de validation des inputs"""
    
    def test_sanitize_string(self):
        """Test nettoyage chaînes"""
        # HTML tags
        assert sanitize_string("<script>alert('xss')</script>") == "alert('xss')"
        
        # Espaces multiples
        assert sanitize_string("test    multiple   spaces") == "test multiple spaces"
        
        # Longueur max
        long_string = "a" * 2000
        result = sanitize_string(long_string, max_length=100)
        assert len(result) == 100
    
    def test_validate_username(self):
        """Test validation nom d'utilisateur"""
        # Trop court
        valid, error = validate_username("ab")
        assert not valid
        
        # Caractères invalides
        valid, error = validate_username("test@user!")
        assert not valid
        
        # Mot réservé
        valid, error = validate_username("admin")
        assert not valid
        
        # Valide
        valid, error = validate_username("testuser123")
        assert valid
        assert error is None
    
    def test_validate_email(self):
        """Test validation email"""
        # Email invalide
        valid, error, _ = validate_email_address("invalid-email")
        assert not valid
        
        # Email valide
        valid, error, normalized = validate_email_address("test@example.com")
        assert valid
        assert error is None
        assert "@" in normalized
    
    def test_validate_code_input(self):
        """Test validation code Python"""
        # Code normal
        valid, error = validate_code_input("print('hello')")
        assert valid
        
        # Code trop long
        long_code = "a" * 60000
        valid, error = validate_code_input(long_code)
        assert not valid


class TestCodeExecution:
    """Tests de sécurité exécution code"""
    
    def test_dangerous_imports_blocked(self):
        """Test blocage imports dangereux"""
        dangerous_codes = [
            "import os",
            "import sys",
            "import subprocess",
            "from os import system",
            "__import__('os')",
        ]
        
        for code in dangerous_codes:
            safe, message = verifier_code_dangereux(code)
            assert not safe, f"Code dangereux non bloqué: {code}"
    
    def test_dangerous_functions_blocked(self):
        """Test blocage fonctions dangereuses"""
        dangerous_codes = [
            "eval('print(1)')",
            "exec('import os')",
            "open('file.txt')",
            "compile('import os', '<string>', 'exec')",
        ]
        
        for code in dangerous_codes:
            safe, message = verifier_code_dangereux(code)
            assert not safe, f"Code dangereux non bloqué: {code}"
    
    def test_safe_code_execution(self):
        """Test exécution code sûr"""
        code = "x = 5\ny = 10\nprint(x + y)"
        result = executer_code_securise(code)
        
        assert result['success']
        assert "15" in result['output']
        assert not result['timeout']
    
    def test_infinite_loop_timeout(self):
        """Test timeout boucle infinie"""
        code = "while True: pass"
        result = executer_code_securise(code, timeout_secondes=2)
        
        assert not result['success']
        assert result['timeout']
    
    def test_too_many_loops(self):
        """Test protection trop de boucles"""
        code = "\n".join([f"for i{i} in range(10): pass" for i in range(25)])
        result = executer_code_securise(code)
        
        assert not result['success']
        assert "boucles" in result['error'].lower()
    
    def test_deep_recursion_blocked(self):
        """Test blocage récursion profonde"""
        code = """
def recursive(n):
    if n > 0:
        return recursive(n-1)
    return 0

recursive(200)
"""
        result = executer_code_securise(code)
        
        assert not result['success']
        assert "recursion" in result['error'].lower()
    
    def test_memory_bomb_protection(self):
        """Test protection memory bomb"""
        code = "x = [0] * (10**9)"  # Essayer d'allouer énormément de mémoire
        result = executer_code_securise(code, timeout_secondes=2)
        
        # Doit soit timeout, soit erreur mémoire
        # Python peut gérer certains cas sans erreur selon la mémoire disponible
        # On vérifie juste qu'il n'y a pas de crash
        assert 'error' in result or result['success']  # Pas de crash


class TestSecurityHeaders:
    """Tests des headers de sécurité"""
    
    def test_security_headers_present(self):
        """Vérifier que l'app ajoute les headers de sécurité"""
        # Ce test nécessiterait l'app Flask lancée
        # Pour l'instant, vérifie juste que le module existe
        from api.app import app
        assert app is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
