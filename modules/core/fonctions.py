## Fichier contenant toutes les fonctions utilitaires pour l'application d'apprentissage

import ollama
import random 
import json
import os
from modules.core.progression import est_exercice_complete
try:
    from modules.core.domaines import obtenir_config_ia, obtenir_themes_domaine
except ImportError:
    # Éviter les imports circulaires
    obtenir_config_ia = None
    obtenir_themes_domaine = None

FICHIER_BANQUE = 'banque_exercices.json'

def charger_banque():
    """Charge la banque d'exercices depuis le fichier JSON"""
    if os.path.exists(FICHIER_BANQUE):
        with open(FICHIER_BANQUE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {}

def sauvegarder_banque(banque):
    """Sauvegarde la banque d'exercices dans le fichier JSON"""
    with open(FICHIER_BANQUE, 'w', encoding='utf-8') as f:
        json.dump(banque, f, indent=2, ensure_ascii=False)
        
        


def ajouter_exercice_banque(theme, niveau, exercice):
    """Ajoute un exercice généré par l'IA dans la banque s'il n'existe pas déjà"""
    banque = charger_banque()
    
    if theme not in banque:
        banque[theme] = {"1": [], "2": [], "3": []}
    
    niveau_str = str(niveau)
    if niveau_str not in banque[theme]:
        banque[theme][niveau_str] = []
    
    if exercice not in banque[theme][niveau_str]:
        banque[theme][niveau_str].append(exercice)
        sauvegarder_banque(banque)



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
        exemple = "Exemple : 'Écrivez une fonction qui prend un nombre en paramètre et retourne True s'il est pair, False sinon.'"
    else:
        exemple = "Exemple : 'Traduisez la phrase suivante en anglais : Bonjour, comment allez-vous ?'"
    
    messages = [
    {
        'role': 'user',
        'content' : f'''Tu es un {role}. Crée un exercice de niveau {niveau} (1=facile, 2=moyen, 3=difficile) sur le thème : {theme}

IMPORTANT : 
- Donne UNIQUEMENT l\'énoncé de l\'exercice (2-3 phrases maximum)
- NE donne PAS la solution
- NE donne PAS d\'exemple
- NE donne PAS d\'explications

{exemple}

Énoncé :'''
    }
]
    response = ollama.chat(model='qwen2.5-coder:14b', messages = messages)
    exercice_ia = response['message']['content']
    
    exercice = {
        "type": type_ex,
        "enonce": exercice_ia
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

# Liste des imports dangereux à bloquer
IMPORTS_INTERDITS = [
    'os', 'sys', 'subprocess', 'shutil', 'socket',
    'requests', 'urllib', 'pathlib', '__import__',
    'eval', 'exec', 'compile', '__builtins__'
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
    
    # Vérifier les mots-clés dangereux
    mots_dangereux = ['exec(', 'eval(', 'compile(', 'open(', '__import__']
    for mot in mots_dangereux:
        if mot.lower() in code.lower():
            return False, f"Instruction dangereuse detectee : {mot}"
    
    return True, ""

def executer_code_securise(code, timeout_secondes=5):
    """
    Exécute du code Python de manière sécurisée avec restrictions renforcées
    
    Args:
        code (str): Le code Python à exécuter
        timeout_secondes (int): Temps maximum d'exécution (défaut 5s)
    
    Returns:
        dict: {
            'success': bool,
            'output': str (stdout),
            'error': str (stderr ou message d'erreur),
            'timeout': bool
        }
    """
    import threading
    import time
    
    # Vérifier les imports dangereux
    safe, message = verifier_code_dangereux(code)
    if not safe:
        return {
            'success': False,
            'output': '',
            'error': message,
            'timeout': False,
            'dangerous_attempt': True
        }
    
    # Limiter la taille du code (protection DoS)
    if len(code) > 50000:
        return {
            'success': False,
            'output': '',
            'error': 'Code trop long (maximum 50KB)',
            'timeout': False
        }
    
    # Compter les boucles (protection boucles infinies)
    loop_count = code.count('while ') + code.count('for ')
    if loop_count > 20:
        return {
            'success': False,
            'output': '',
            'error': 'Trop de boucles detectees (maximum 20)',
            'timeout': False
        }
    
    # Vérifier la profondeur de récursion
    if 'def ' in code:
        # Limiter la profondeur de récursion
        import sys
        old_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(100)  # Maximum 100 niveaux
    
    # Préparer la capture des outputs
    stdout_capture = StringIO()
    stderr_capture = StringIO()
    
    # Créer un environnement restreint (whitelist de fonctions autorisées)
    environnement = {
        '__builtins__': {
            'print': print,
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
    result = {'success': False, 'output': '', 'error': 'Timeout', 'timeout': True}
    
    def execute_code():
        """Fonction qui exécute le code dans un thread"""
        nonlocal result
        try:
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(code, environnement)
            
            result = {
                'success': True,
                'output': stdout_capture.getvalue(),
                'error': stderr_capture.getvalue(),
                'timeout': False
            }
        except RecursionError:
            result = {
                'success': False,
                'output': stdout_capture.getvalue(),
                'error': 'Recursion trop profonde (maximum 100 niveaux)',
                'timeout': False
            }
        except MemoryError:
            result = {
                'success': False,
                'output': stdout_capture.getvalue(),
                'error': 'Memoire insuffisante',
                'timeout': False
            }
        except Exception as e:
            result = {
                'success': False,
                'output': stdout_capture.getvalue(),
                'error': f'Erreur d\'execution : {type(e).__name__}: {str(e)}',
                'timeout': False
            }
    
    # Exécuter dans un thread avec timeout
    thread = threading.Thread(target=execute_code)
    thread.daemon = True
    thread.start()
    thread.join(timeout_secondes)
    
    # Restaurer la limite de récursion
    if 'def ' in code:
        import sys
        sys.setrecursionlimit(old_limit)
    
    # Vérifier si le thread est toujours actif (timeout)
    if thread.is_alive():
        return {
            'success': False,
            'output': stdout_capture.getvalue(),
            'error': f'Timeout : Votre code prend trop de temps (max {timeout_secondes}s)',
            'timeout': True
        }
    
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

