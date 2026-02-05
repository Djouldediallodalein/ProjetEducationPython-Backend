## Fichier contenant toutes les fonctions utilitaires pour l'application d'apprentissage

import ollama
import random 
import json
import os
from modules.core.progression import est_exercice_complete
from modules.core.file_lock import atomic_json_writer, safe_json_read
try:
    from modules.core.domaines import obtenir_config_ia, obtenir_themes_domaine
except ImportError:
    # Éviter les imports circulaires
    obtenir_config_ia = None
    obtenir_themes_domaine = None

# Chemins absolus basés sur le répertoire backend
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FICHIER_BANQUE = os.path.join(BASE_DIR, 'banque_exercices.json')

def charger_banque():
    """Charge la banque d'exercices depuis le fichier JSON (thread-safe)"""
    if not os.path.exists(FICHIER_BANQUE):
        return {}
    
    with safe_json_read(FICHIER_BANQUE) as data:
        return data

def sauvegarder_banque(banque):
    """Sauvegarde la banque d'exercices dans le fichier JSON (atomique et thread-safe)"""
    with atomic_json_writer(FICHIER_BANQUE) as writer:
        writer(banque)
        
        


def ajouter_exercice_banque(theme, niveau, exercice):
    """Ajoute un exercice généré par l'IA dans la banque s'il n'existe pas déjà
    
    Structure de l'exercice :
    {
        "type": "code" | "texte" | "qcm",
        "enonce": "...",
        "id": "unique_id",
        "solution": "code complet de la solution",
        "utilise_input": true/false,
        "cas_test": [{"inputs": [...], "output_attendu": "..."}],
        "mots_cles": ["input", "int", "print"],
        "indice": "...",
        "exemple": "..."
    }
    """
    banque = charger_banque()
    
    if theme not in banque:
        banque[theme] = {"1": [], "2": [], "3": []}
    
    niveau_str = str(niveau)
    if niveau_str not in banque[theme]:
        banque[theme][niveau_str] = []
    
    # Générer un ID unique si pas présent
    if 'id' not in exercice:
        import hashlib
        exercice['id'] = hashlib.md5(exercice['enonce'].encode()).hexdigest()[:10]
    
    # Vérifier si l'exercice existe déjà (par ID)
    exercice_existe = any(ex.get('id') == exercice.get('id') for ex in banque[theme][niveau_str])
    
    if not exercice_existe:
        banque[theme][niveau_str].append(exercice)
        sauvegarder_banque(banque)
        return True
    return False


def obtenir_exercice_par_id(exercice_id):
    """Récupère un exercice de la banque par son ID"""
    banque = charger_banque()
    
    for theme in banque.values():
        for niveau in theme.values():
            for exercice in niveau:
                if exercice.get('id') == exercice_id:
                    return exercice
    return None



def generer_exercice(niveau, theme, domaine='python'):
    """Génère un exercice : d'abord depuis la banque (non complété), sinon via l'IA"""
    
    banque = charger_banque()
    niveau_str = str(niveau)
    
    # Chercher dans la banque (structure : domaine -> theme -> niveau)
    cle_banque = f"{domaine}:{theme}"
    if cle_banque in banque and niveau_str in banque[cle_banque] and banque[cle_banque][niveau_str]:
        exercices_disponibles = [
            ex for ex in banque[cle_banque][niveau_str] 
            if not est_exercice_complete(theme, niveau, str(ex))
        ]
        
        if exercices_disponibles:
            exercice = random.choice(exercices_disponibles)
            print("[Exercice depuis la banque]")
            return exercice
    
    print("[Generation par IA...]")
    
    # Obtenir la config IA du domaine
    if obtenir_config_ia:
        config = obtenir_config_ia(domaine)
        role = config.get('role', 'professeur')
        type_ex = config.get('type_exercice', 'code')
    else:
        role = 'professeur de Python'
        type_ex = 'code'
    
    # Adapter le prompt selon le type d'exercice
    if type_ex == 'code':
        exemple_format = '''{{
  "enonce": "Créez un script qui demande l'âge et la taille, puis affiche ces infos avec leurs types.",
  "solution": "age = int(input('Entrez votre âge : '))\\ntaille = float(input('Entrez votre taille en cm : '))\\nprint(f'Vous avez {{age}} ans (type: {{type(age).__name__}}) et mesurez {{taille}} cm (type: {{type(taille).__name__}}).')",
  "utilise_input": true,
  "cas_test": [{{"inputs": ["30", "175.5"], "output_attendu": "Vous avez 30 ans (type: int) et mesurez 175.5 cm (type: float)."}}],
  "mots_cles": ["input", "int", "float", "print", "type"]
}}'''
    elif type_ex == 'qcm':
        exemple_format = '''{{
  "enonce": "Quel type de données est retourné par la fonction input() en Python ?",
  "choix": ["int", "str", "float", "bool"],
  "reponse_correcte": "str",
  "explication": "La fonction input() retourne toujours une chaîne de caractères (str)",
  "indice": "Pensez au type par défaut"
}}'''
    else:
        exemple_format = '''{{
  "enonce": "Traduisez en anglais : Bonjour, comment allez-vous ?",
  "solution": "Hello, how are you?",
  "mots_cles": ["hello", "how", "you"]
}}'''
    
    messages = [
    {
        'role': 'user',
        'content' : f'''Tu es un {role}. Crée un exercice de niveau {niveau} (1=facile, 2=moyen, 3=difficile) sur le thème : {theme}

Format de réponse OBLIGATOIRE (JSON strict) :

POUR CODE:
{{
  "enonce": "L'énoncé de l'exercice (2-3 phrases)",
  "solution": "Le code complet de la solution",
  "utilise_input": true/false,
  "cas_test": [{{"inputs": ["val1", "val2"], "output_attendu": "résultat exact"}}],
  "mots_cles": ["mot1", "mot2", "mot3"]
}}

POUR QCM:
{{
  "enonce": "La question",
  "choix": ["Choix A", "Choix B", "Choix C", "Choix D"],
  "reponse_correcte": "Choix B",
  "explication": "Pourquoi c'est correct",
  "indice": "Un indice"
}}

EXEMPLE POUR CE TYPE ({type_ex}):
{exemple_format}

Réponds UNIQUEMENT avec le JSON, rien d'autre.'''
    }
]
    response = ollama.chat(model='qwen2.5-coder:14b', messages = messages)
    exercice_ia = response['message']['content'].strip()
    
    # Parser le JSON
    import json
    try:
        # Extraire le JSON si entouré de ```
        if '```json' in exercice_ia:
            exercice_ia = exercice_ia.split('```json')[1].split('```')[0].strip()
        elif '```' in exercice_ia:
            exercice_ia = exercice_ia.split('```')[1].split('```')[0].strip()
        
        exercice_data = json.loads(exercice_ia)
        
        # Différencier CODE et QCM
        if type_ex == 'qcm':
            exercice = {
                "type": "qcm",
                "enonce": exercice_data.get('enonce', ''),
                "choix": exercice_data.get('choix', []),
                "reponse_correcte": exercice_data.get('reponse_correcte', ''),
                "explication": exercice_data.get('explication', ''),
                "indice": exercice_data.get('indice', '')
            }
        else:
            exercice = {
                "type": type_ex,
                "enonce": exercice_data.get('enonce', ''),
                "solution": exercice_data.get('solution', ''),
                "utilise_input": exercice_data.get('utilise_input', False),
                "cas_test": exercice_data.get('cas_test', []),
                "mots_cles": exercice_data.get('mots_cles', [])
            }
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Erreur parsing JSON IA: {e}")
        # Fallback : exercice simple sans tests
        exercice = {
            "type": type_ex,
            "enonce": exercice_ia,
            "solution": "",
            "utilise_input": False,
            "cas_test": [],
            "mots_cles": []
        }
    
    ajouter_exercice_banque(cle_banque, niveau, exercice)
    
    return exercice



def afficher_qcm(exercice):
    """Affiche un QCM et retourne la réponse de l'utilisateur"""
    print(exercice['question'])
    print()
    
    for i, choix in enumerate(exercice['choix'], 1):
        print(f"{i}. {choix}")
    
    print()
    while True:
        try:
            reponse_num = int(input("Votre réponse (1-4) : "))
            if 1 <= reponse_num <= len(exercice['choix']):
                return exercice['choix'][reponse_num - 1]
            else:
                print("Choix invalide. Entrez un nombre entre 1 et 4.")
        except ValueError:
            print("Veuillez entrer un nombre.")



def verifier_reponse_optimisee(exercice, code_utilisateur):
    """
    Vérifie la réponse de l'utilisateur SANS appeler l'IA si possible.
    
    Stratégie:
    1. Si QCM → Comparaison directe de la réponse
    2. Si exercice a des cas_test → Exécuter avec inputs prédéfinis et comparer
    3. Sinon, fallback sur vérification IA (ancienne méthode)
    
    Retourne: (est_correct: bool, message: str)
    """
    
    # CAS 1 : QCM (Quiz à choix multiples)
    type_exercice = exercice.get('type', 'code')
    if type_exercice == 'qcm':
        print("[Vérification QCM - SANS IA]")
        reponse_correcte = exercice.get('reponse_correcte', '')
        reponse_utilisateur = code_utilisateur.strip()
        
        if reponse_utilisateur.lower() == reponse_correcte.lower():
            explication = exercice.get('explication', '')
            return True, f"CORRECT: Bravo ! {explication}"
        else:
            indice = exercice.get('indice', 'Réessayez')
            return False, f"INCORRECT: Ce n'est pas la bonne réponse. Indice : {indice}"
    
    # CAS 2 : CODE avec cas de test
    # Vérifier si l'exercice a des cas de test prédéfinis
    cas_test = exercice.get('cas_test', [])
    
    if cas_test and len(cas_test) > 0:
        print("[Vérification automatique - SANS IA]")
        
        # Prendre le premier cas de test
        test = cas_test[0]
        inputs_prevus = test.get('inputs', [])
        output_attendu = test.get('output_attendu', '')
        
        try:
            # Exécuter le code avec les inputs mockés
            resultat = executer_code_securise(code_utilisateur, inputs_prevus)
            
            if not resultat['success']:
                # SANITISER l'erreur pour ne pas révéler la solution
                erreur_brute = resultat.get('error', '')
                # Retirer les chemins de fichiers et infos sensibles
                erreur_sanitisee = erreur_brute.split('\n')[-1] if '\n' in erreur_brute else erreur_brute
                return False, f"INCORRECT: Erreur d'exécution. {erreur_sanitisee}"
            
            output_utilisateur = resultat.get('output', '').strip()
            
            # COMPARAISON INTELLIGENTE (tolérance ordre, espaces, casse)
            output_attendu_norm = output_attendu.strip().lower()
            output_utilisateur_norm = output_utilisateur.strip().lower()
            
            # Méthode 1 : Comparaison exacte (normalizée)
            if output_attendu_norm == output_utilisateur_norm:
                return True, "CORRECT: Bravo ! Votre code fonctionne parfaitement."
            
            # Méthode 2 : Comparaison par contenu (toutes les infos présentes)
            # Extraire les nombres et mots importants
            import re
            nombres_attendus = set(re.findall(r'\d+\.?\d*', output_attendu_norm))
            nombres_utilisateur = set(re.findall(r'\d+\.?\d*', output_utilisateur_norm))
            
            mots_attendus = set(re.findall(r'\b[a-z]+\b', output_attendu_norm))
            mots_utilisateur = set(re.findall(r'\b[a-z]+\b', output_utilisateur_norm))
            
            # Vérifier que tous les nombres et mots-clés importants sont présents
            if nombres_attendus.issubset(nombres_utilisateur) and len(mots_attendus.intersection(mots_utilisateur)) >= len(mots_attendus) * 0.7:
                return True, "CORRECT: Bravo ! Votre code produit le bon résultat."
            
            # Méthode 3 : Vérifier si output contient les informations essentielles
            if output_attendu_norm in output_utilisateur_norm or output_utilisateur_norm in output_attendu_norm:
                return True, "CORRECT: Bravo ! Votre code fonctionne parfaitement."
            else:
                # Vérifier les mots-clés si présents
                mots_cles = exercice.get('mots_cles', [])
                code_lower = code_utilisateur.lower()
                mots_manquants = [mot for mot in mots_cles if mot.lower() not in code_lower]
                
                if mots_manquants:
                    return False, f"INCORRECT: Votre code ne produit pas le résultat attendu. Indice : Utilisez {', '.join(mots_manquants[:2])}"
                else:
                    return False, f"INCORRECT: Le résultat affiché n'est pas correct. Attendu: '{output_attendu}'"
                    
        except Exception as e:
            return False, f"INCORRECT: Erreur lors de l'exécution. {str(e)}"
    
    else:
        # Pas de cas de test → Vérifier les mots-clés simples si disponibles
        mots_cles = exercice.get('mots_cles', [])
        
        if mots_cles:
            print("[Vérification par mots-clés - SANS IA]")
            code_lower = code_utilisateur.lower()
            mots_manquants = [mot for mot in mots_cles if mot.lower() not in code_lower]
            
            if not mots_manquants:
                # Tous les mots-clés présents, exécuter pour voir si pas d'erreur
                try:
                    resultat = executer_code_securise(code_utilisateur)
                    if resultat['success']:
                        return True, "CORRECT: Bravo ! Votre code contient les éléments requis."
                    else:
                        return False, f"INCORRECT: Erreur d'exécution. {resultat.get('error', '')}"
                except:
                    return False, "INCORRECT: Erreur lors de l'exécution."
            else:
                return False, f"INCORRECT: Éléments manquants. Indice: Utilisez {', '.join(mots_manquants[:2])}"
        
        # Aucune vérification automatique possible → Appel IA
        print("[Vérification par IA - Fallback]")
        return None, None  # Signal pour appeler verifier_reponse() classique


def verifier_reponse(exercice, reponse_utilisateur, domaine='python'):
    """ Cette fonction permet de verifier la reponse de l'utilisateur"""
    
    # Obtenir la config IA du domaine
    if obtenir_config_ia:
        config = obtenir_config_ia(domaine)
        role = config.get('role', 'professeur')
        verification = config.get('verification', 'réponse')
        type_ex = config.get('type_exercice', 'code')
    else:
        role = 'professeur de Python'
        verification = 'code Python'
        type_ex = 'code'
    
    # Adapter le prompt selon le type
    if type_ex == 'code':
        regles = f'''RÈGLES DE CORRECTION :
1. Vérifie que c\'est du CODE (pas juste du texte ou l\'énoncé recopié)
2. Vérifie que le code répond EXACTEMENT à la question
3. Si ce n\'est PAS du code → INCORRECT
4. Si le code ne résout pas l\'exercice → INCORRECT'''
    else:
        regles = f'''RÈGLES DE CORRECTION :
1. Vérifie que la réponse est pertinente et complète
2. Vérifie qu\'elle répond EXACTEMENT à la question
3. Si la réponse est incomplète → INCORRECT
4. Si la réponse est hors sujet → INCORRECT'''
    
    messages = [
    {
        'role': 'user',
        'content': f'''Tu es un correcteur STRICT, {role}.

EXERCICE :
{exercice}

RÉPONSE DE L\'ÉLÈVE :
{reponse_utilisateur}

{regles}

Réponse (15 mots max) :
- Si CORRECT : "CORRECT : Bravo !"
- Si INCORRECT : "INCORRECT : [raison courte]. Indice : [2-3 mots]"'''
    }
]
    
    correction = ollama.chat(model='qwen2.5-coder:14b', messages = messages)
    return correction['message']['content']
    





def analyser_verdict(correction):
    """Cette fonction permet de gerer le verdict de l'ia sur la reponse de l'etudiant"""
    
    correction_upper = correction.upper()
    
    if 'CORRECT' in correction_upper and 'INCORRECT' not in correction_upper:
        return True
    else:
        return False




def choisir_theme_aleatoire(domaine='python'):
    """Retourne un thème aléatoire parmi les thèmes disponibles du domaine"""
    
    # Obtenir les thèmes du domaine
    if obtenir_themes_domaine:
        themes = obtenir_themes_domaine(domaine)
    else:
        themes = [
            'Variables et types de données',
            'Conditions (if/elif/else)',
            'Boucles (for/while)',
            'Fonctions',
            'Listes et tuples',
            'Dictionnaires',
            'Manipulation de strings',
            'Fichiers (lecture/écriture)',
            'Gestion des erreurs (try/except)',
            'Programmation orientée objet (classes)'
        ]
    
    theme_selectionne = random.choice(themes)
    print(f"Theme aleatoire selectionne : {theme_selectionne}")
    return theme_selectionne



def choisir_theme(domaine='python'):
    """Permet à l'utilisateur de choisir un thème d'exercice"""
    
    # Obtenir les thèmes du domaine
    if obtenir_themes_domaine:
        themes_liste = obtenir_themes_domaine(domaine)
    else:
        # Fallback sur Python si le module n'est pas disponible
        themes_liste = [
            'Variables et types de données',
            'Conditions (if/elif/else)',
            'Boucles (for/while)',
            'Fonctions',
            'Listes et tuples',
            'Dictionnaires',
            'Manipulation de strings',
            'Fichiers (lecture/écriture)',
            'Gestion des erreurs (try/except)',
            'Programmation orientée objet (classes)'
        ]
    
    themes_disponibles = {str(i): theme for i, theme in enumerate(themes_liste, 1)}
    
    print("\nCHOIX DU THEME D'APPRENTISSAGE")
    print("="*50)
    
    for key, value in themes_disponibles.items():
        print(f"{key}. {value}")
    
    nb_themes = len(themes_disponibles)
    print(f"\n{nb_themes + 1}. Theme aleatoire")
    print(f"{nb_themes + 2}. Sujet libre (n'importe quel thème !)")
    print("0. Retour au menu principal")
    print("="*50)
    
    choix_theme = input(f"\nChoisissez un theme (1-{nb_themes + 2} ou 0 pour retourner) : ")
    
    if choix_theme == '0':
        return None
    elif choix_theme == str(nb_themes + 1):
        return choisir_theme_aleatoire(domaine)
    elif choix_theme == str(nb_themes + 2):
        return mode_sujet_libre()
    elif choix_theme in themes_disponibles:
        theme_selectionne = themes_disponibles[choix_theme]
        print(f"Theme selectionne : {theme_selectionne}")
        return theme_selectionne
    else:
        print("Choix invalide ! Veuillez reessayer.")
        return choisir_theme(domaine)


def mode_sujet_libre():
    """Permet d'apprendre n'importe quel sujet via IA"""
    print("\nMODE SUJET LIBRE")
    print("="*50)
    print("Vous pouvez apprendre n'importe quel sujet !")
    print("Exemples : JavaScript, Espagnol, Physique, SQL, etc.")
    print("="*50)
    
    sujet = input("\nEntrez le sujet que vous voulez apprendre : ").strip()
    
    if not sujet:
        print("Sujet invalide. Retour au menu.")
        return None
    
    print(f"\nMode apprentissage : {sujet}")
    print("Note : Les exercices seront generés par l'IA en temps réel.")
    
    return f"[Sujet Libre] {sujet}"


# ==================== VALIDATION SÉCURISÉE DU CODE ====================

import signal
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO

# ============================================================================
# SECURITY NOTE: Software Sandbox Active (Blacklist-based)
# ============================================================================
# This implementation uses a blacklist approach to block dangerous operations.
# For production deployment with untrusted users, migrate to containerized
# isolation (Docker/nsjail) as specified in ROADMAP_V2.md.
#
# Current protections:
# - Blocked imports: os, sys, subprocess, socket, file operations
# - Blocked functions: eval(), exec(), compile(), open(), __import__()
# - Execution timeout: 2 seconds default
# - Memory limit: 50KB code size
# - Recursion limit: 100 levels
# ============================================================================

# Liste renforcée des imports dangereux à bloquer
IMPORTS_INTERDITS = [
    'os', 'sys', 'subprocess', 'shutil', 'socket',
    'requests', 'urllib', 'pathlib', '__import__',
    'eval', 'exec', 'compile', '__builtins__',
    'importlib', 'ctypes', 'multiprocessing', 'threading',
    'pickle', 'shelve', 'tempfile', 'glob', 'fnmatch'
]

class TimeoutException(Exception):
    """Exception levée en cas de timeout"""
    pass

def timeout_handler(signum, frame):
    """Handler pour le timeout (Linux/Mac uniquement)"""
    raise TimeoutException("Timeout : Le code prend trop de temps")

def verifier_code_dangereux(code):
    """
    Vérifie si le code contient des imports ou instructions dangereux
    
    SÉCURITÉ RENFORCÉE :
    - Blacklist étendue d'imports système/réseau/fichiers
    - Détection de patterns d'obfuscation (avec/sans espaces)
    - Blocage des fonctions d'exécution dynamique
    
    Args:
        code (str): Le code Python à vérifier
        
    Returns:
        tuple: (bool, str) - (True si sûr, message d'erreur si dangereux)
    """
    # Vérifier les imports interdits (avec et sans espaces)
    for interdit in IMPORTS_INTERDITS:
        # Vérifier "import os", "from os import", etc.
        patterns = [
            f'import {interdit}',
            f'from {interdit}',
            f'import{interdit}',  # sans espace
            f'from{interdit}'     # sans espace
        ]
        for pattern in patterns:
            if pattern.lower() in code.lower():
                return False, f"Import interdit detecte : {interdit}"
    
    # Vérifier les mots-clés dangereux (liste étendue)
    mots_dangereux = [
        'exec(', 'eval(', 'compile(', 'open(', '__import__(',
        'globals(', 'locals()', 'vars(', 'dir(',
        'getattr(', 'setattr(', 'delattr(', 'hasattr('
    ]
    for mot in mots_dangereux:
        if mot.lower() in code.lower():
            return False, f"Instruction dangereuse detectee : {mot}"
    
    return True, ""

def executer_code_securise(code, timeout_secondes=2, test_inputs=None):
    """
    Exécute du code Python de manière sécurisée avec restrictions renforcées
    
    ⚠️ SECURITY NOTICE:
    This is a SOFTWARE SANDBOX using blacklist filtering. While suitable for
    educational purposes with trusted users, production deployment requires
    hardware-level isolation (Docker containers). See ROADMAP_V2.md.
    
    AMÉLIORATIONS DE SÉCURITÉ v2.0 :
    - Timeout strict réduit à 2 secondes par défaut
    - Gestion améliorée des timeouts avec cleanup
    - Capture spécifique des erreurs de mémoire
    - Messages d'erreur plus clairs et sécurisés
    - Support pour input() simulé avec valeurs de test
    
    Args:
        code (str): Le code Python à exécuter
        timeout_secondes (int): Temps maximum d'exécution (défaut 2s)
        test_inputs (list): Liste de valeurs à retourner pour input() (défaut ["30", "175.5"])
    
    Returns:
        dict: {
            'success': bool,
            'output': str (stdout),
            'error': str (stderr ou message d'erreur),
            'timeout': bool,
            'execution_time': float (temps d'exécution en secondes)
        }
    """
    import threading
    import time
    
    start_time = time.time()
    
    # Vérifier les imports dangereux
    safe, message = verifier_code_dangereux(code)
    if not safe:
        return {
            'success': False,
            'output': '',
            'error': message,
            'timeout': False,
            'dangerous_attempt': True,
            'execution_time': 0
        }
    
    # Limiter la taille du code (protection DoS)
    if len(code) > 50000:
        return {
            'success': False,
            'output': '',
            'error': 'Code trop long (maximum 50KB)',
            'timeout': False,
            'execution_time': 0
        }
    
    # Compter les boucles (protection boucles infinies)
    loop_count = code.count('while ') + code.count('for ')
    if loop_count > 20:
        return {
            'success': False,
            'output': '',
            'error': 'Trop de boucles detectees (maximum 20)',
            'timeout': False,
            'execution_time': 0
        }
    
    # Vérifier la profondeur de récursion
    recursion_limit_changed = False
    if 'def ' in code:
        # Limiter la profondeur de récursion
        import sys
        old_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(100)  # Maximum 100 niveaux
        recursion_limit_changed = True
    
    # Préparer la capture des outputs
    stdout_capture = StringIO()
    stderr_capture = StringIO()
    
    # Créer une fonction input() simulée avec des valeurs de test
    if test_inputs is None:
        test_inputs = ["30", "175.5"]  # Valeurs de test par défaut
    input_index = [0]  # Liste pour pouvoir modifier dans la closure
    
    def mock_input(prompt=""):
        """Fonction input() simulée qui retourne des valeurs prédéfinies"""
        if prompt:
            print(prompt, end='')
        if input_index[0] < len(test_inputs):
            value = test_inputs[input_index[0]]
            input_index[0] += 1
            print(value)  # Afficher la valeur comme si l'utilisateur l'avait saisie
            return value
        return ""
    
    # Créer un environnement restreint (whitelist de fonctions autorisées)
    environnement = {
        '__builtins__': {
            'print': print,
            'input': mock_input,  # Ajouter input() simulé
            'len': len,
            'range': range,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
            'tuple': tuple,
            'set': set,
            'True': True,
            'False': False,
            'None': None,
            'sum': sum,
            'max': max,
            'min': min,
            'abs': abs,
            'round': round,
            'enumerate': enumerate,
            'zip': zip,
            'map': map,
            'filter': filter,
            'sorted': sorted,
            'reversed': reversed,
            'any': any,
            'all': all,
            'type': type,
            'isinstance': isinstance,
            'chr': chr,
            'ord': ord,
            'pow': pow,
            'divmod': divmod,
        }
    }
    
    # Variable pour stocker le résultat de l'exécution
    result = {
        'success': False, 
        'output': '', 
        'error': 'Execution Timeout', 
        'timeout': True,
        'execution_time': 0
    }
    
    execution_exception = None
    
    def execute_code():
        """Fonction qui exécute le code dans un thread"""
        nonlocal result, execution_exception
        try:
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(code, environnement)
            
            result = {
                'success': True,
                'output': stdout_capture.getvalue(),
                'error': stderr_capture.getvalue(),
                'timeout': False,
                'execution_time': 0  # Sera mis à jour après
            }
        except RecursionError as e:
            execution_exception = e
            result = {
                'success': False,
                'output': stdout_capture.getvalue(),
                'error': 'RecursionError: Recursion trop profonde (maximum 100 niveaux)',
                'timeout': False,
                'execution_time': 0
            }
        except MemoryError as e:
            execution_exception = e
            result = {
                'success': False,
                'output': stdout_capture.getvalue(),
                'error': 'MemoryError: Memoire insuffisante - Votre code consomme trop de RAM',
                'timeout': False,
                'execution_time': 0
            }
        except KeyboardInterrupt:
            result = {
                'success': False,
                'output': stdout_capture.getvalue(),
                'error': 'Execution interrompue',
                'timeout': True,
                'execution_time': 0
            }
        except Exception as e:
            execution_exception = e
            result = {
                'success': False,
                'output': stdout_capture.getvalue(),
                'error': f'Erreur d\'execution : {type(e).__name__}: {str(e)}',
                'timeout': False,
                'execution_time': 0
            }
    
    # Exécuter dans un thread avec timeout strict
    thread = threading.Thread(target=execute_code, daemon=True)
    thread.start()
    thread.join(timeout=timeout_secondes)
    
    # Calculer le temps d'exécution
    execution_time = time.time() - start_time
    
    # Restaurer la limite de récursion si changée
    if recursion_limit_changed:
        import sys
        sys.setrecursionlimit(old_limit)
    
    # Vérifier si le thread est toujours actif (timeout)
    if thread.is_alive():
        # Thread toujours actif = timeout
        return {
            'success': False,
            'output': stdout_capture.getvalue(),
            'error': f'Execution Timed Out: Votre code a depasse le temps maximum autorise ({timeout_secondes}s). Verifiez les boucles infinies.',
            'timeout': True,
            'execution_time': execution_time
        }
    
    # Ajouter le temps d'exécution au résultat
    result['execution_time'] = execution_time
    
    return result

def verifier_avec_tests(code, tests):
    """
    Vérifie le code avec une liste de tests
    
    Args:
        code (str): Le code de l'utilisateur (doit définir des fonctions)
        tests (list): Liste de tuples (appel_fonction, resultat_attendu)
            Exemple: [("fonction(5)", 10), ("fonction(3)", 6)]
        
    Returns:
        dict: {
            'success': bool,
            'tests_reussis': int,
            'tests_total': int,
            'details': list
        }
    """
    # Exécuter le code d'abord pour définir les fonctions
    resultat = executer_code_securise(code)
    
    if not resultat['success']:
        return {
            'success': False,
            'tests_reussis': 0,
            'tests_total': len(tests),
            'details': [{'erreur': resultat['error']}]
        }
    
    # Récupérer l'environnement avec les fonctions définies
    env = resultat.get('environnement', {})
    
    # Exécuter chaque test
    tests_reussis = 0
    details = []
    
    for i, (test_input, expected) in enumerate(tests):
        try:
            # Créer le code de test qui évalue l'expression
            code_test = code + f"\n__test_result__ = {test_input}"
            resultat_test = executer_code_securise(code_test)
            
            if resultat_test['success']:
                # Récupérer le résultat du test
                result = resultat_test.get('environnement', {}).get('__test_result__')
                
                if result == expected:
                    tests_reussis += 1
                    details.append({
                        'test': i + 1,
                        'input': test_input,
                        'expected': expected,
                        'got': result,
                        'success': True
                    })
                else:
                    details.append({
                        'test': i + 1,
                        'input': test_input,
                        'expected': expected,
                        'got': result,
                        'success': False,
                        'error': f'Attendu: {expected}, Obtenu: {result}'
                    })
            else:
                details.append({
                    'test': i + 1,
                    'input': test_input,
                    'expected': expected,
                    'success': False,
                    'error': resultat_test['error']
                })
        except Exception as e:
            details.append({
                'test': i + 1,
                'input': test_input,
                'expected': expected,
                'success': False,
                'error': f'Exception lors du test: {str(e)}'
            })
    
    return {
        'success': tests_reussis == len(tests),
        'tests_reussis': tests_reussis,
        'tests_total': len(tests),
        'details': details
    }

def tester_fonction(code, nom_fonction, tests):
    """
    Teste une fonction définie dans le code avec plusieurs cas de test
    
    Args:
        code (str): Le code contenant la définition de la fonction
        nom_fonction (str): Le nom de la fonction à tester
        tests (list): Liste de tuples (args, expected)
            Exemple: [((5,), 25), ((3,), 9)] pour tester carre(5) et carre(3)
    
    Returns:
        dict: Résultat des tests avec détails
    """
    # Convertir les tests au format attendu par verifier_avec_tests
    tests_formatte = []
    for args, expected in tests:
        if isinstance(args, tuple):
            args_str = ', '.join(str(arg) for arg in args)
        else:
            args_str = str(args)
        appel = f"{nom_fonction}({args_str})"
        tests_formatte.append((appel, expected))
    
    return verifier_avec_tests(code, tests_formatte)

