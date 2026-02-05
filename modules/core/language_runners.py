"""
Système d'exécution multi-langages sécurisé
Supporte: Python, JavaScript, Java, C, C++, SQL, etc.
"""

import subprocess
import os
import tempfile
import shutil
from pathlib import Path
import re

# Langages supportés par défaut
LANGAGES_SUPPORTES = {
    'python': {
        'extension': '.py',
        'commande': ['python', '-u'],  # -u pour unbuffered output
        'validation': r'^\s*(import|from|def|class|if|for|while|print|input|#)',
        'timeout': 5,
        'compilation': False
    },
    'javascript': {
        'extension': '.js',
        'commande': ['node'],
        'validation': r'^\s*(const|let|var|function|class|if|for|while|console\.)',
        'timeout': 5,
        'compilation': False
    },
    'java': {
        'extension': '.java',
        'commande_compilation': ['javac'],
        'commande_execution': ['java'],
        'validation': r'^\s*(public|private|class|import|package)',
        'timeout': 10,
        'compilation': True,
        'classe_principale': 'Main'  # Nom par défaut
    },
    'c': {
        'extension': '.c',
        'commande_compilation': ['gcc', '-o'],
        'validation': r'^\s*(#include|int main|void|return)',
        'timeout': 10,
        'compilation': True
    },
    'cpp': {
        'extension': '.cpp',
        'commande_compilation': ['g++', '-o'],
        'validation': r'^\s*(#include|using namespace|int main|void|return)',
        'timeout': 10,
        'compilation': True
    },
    'sql': {
        'extension': '.sql',
        'commande': ['sqlite3', ':memory:'],
        'validation': r'^\s*(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER)',
        'timeout': 5,
        'compilation': False
    }
}


def valider_code_langage(code, langage):
    """
    Valide que le code correspond bien au langage déclaré
    SÉCURITÉ: Empêche l'exécution de code d'un autre langage
    """
    if langage not in LANGAGES_SUPPORTES:
        return False, f"Langage '{langage}' non supporté"
    
    config = LANGAGES_SUPPORTES[langage]
    pattern = config.get('validation', '')
    
    if not pattern:
        return True, "Pas de validation pattern"
    
    # Vérifier que le code contient au moins une instruction valide du langage
    if re.search(pattern, code, re.MULTILINE | re.IGNORECASE):
        return True, "Code valide"
    else:
        return False, f"Le code ne semble pas être du {langage} valide"


def executer_code_langage(code, langage, inputs=None, domaine='python'):
    """
    Exécute du code dans le langage spécifié de manière sécurisée
    
    Args:
        code: Le code source à exécuter
        langage: Le langage du code ('python', 'java', 'c', etc.)
        inputs: Liste d'inputs pour le programme (pour input())
        domaine: Le domaine d'apprentissage (pour vérifier cohérence)
    
    Returns:
        {
            'success': bool,
            'output': str,
            'error': str,
            'execution_time': float
        }
    """
    import time
    
    # SÉCURITÉ 1: Vérifier que le langage correspond au domaine
    if not verifier_coherence_domaine_langage(domaine, langage):
        return {
            'success': False,
            'output': '',
            'error': f"Sécurité: Le domaine '{domaine}' n'autorise pas l'exécution de code {langage}",
            'execution_time': 0
        }
    
    # SÉCURITÉ 2: Valider que le code est bien du langage déclaré
    est_valide, msg = valider_code_langage(code, langage)
    if not est_valide:
        return {
            'success': False,
            'output': '',
            'error': f"Validation échouée: {msg}",
            'execution_time': 0
        }
    
    # Exécuter selon le langage
    if langage == 'python':
        return executer_python(code, inputs)
    elif langage == 'javascript':
        return executer_javascript(code, inputs)
    elif langage == 'java':
        return executer_java(code, inputs)
    elif langage in ['c', 'cpp']:
        return executer_c_cpp(code, langage, inputs)
    elif langage == 'sql':
        return executer_sql(code)
    else:
        return {
            'success': False,
            'output': '',
            'error': f"Langage '{langage}' pas encore implémenté",
            'execution_time': 0
        }


def verifier_coherence_domaine_langage(domaine, langage):
    """
    Vérifie que le langage correspond bien au domaine d'apprentissage
    SÉCURITÉ CRITIQUE: Empêche l'exécution de code malveillant
    """
    # Mapping domaine -> langages autorisés
    domaines_langages = {
        'python': ['python'],
        'javascript': ['javascript'],
        'java': ['java'],
        'c': ['c'],
        'cpp': ['cpp'],
        'c++': ['cpp'],
        'sql': ['sql'],
        'web': ['javascript', 'html', 'css'],
        'html_css': ['html', 'css', 'javascript'],
        'bases_de_donnees': ['sql']
    }
    
    domaine_lower = domaine.lower().replace(' ', '_')
    langages_autorises = domaines_langages.get(domaine_lower, [])
    
    # Si pas trouvé, essayer correspondance directe nom domaine = langage
    if not langages_autorises:
        langages_autorises = [domaine_lower]
    
    return langage.lower() in langages_autorises


def executer_python(code, inputs=None):
    """Exécute du code Python (ancien système)"""
    from modules.core.fonctions import executer_code_securise
    return executer_code_securise(code, inputs)


def executer_javascript(code, inputs=None):
    """Exécute du code JavaScript via Node.js"""
    import time
    
    # Créer un fichier temporaire
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False, encoding='utf-8') as f:
        # Si inputs, les injecter via readline-sync simulé
        if inputs:
            code_with_inputs = f"""
const inputs = {inputs};
let inputIndex = 0;
const readline = () => {{
    if (inputIndex < inputs.length) {{
        return inputs[inputIndex++];
    }}
    return '';
}};

// Remplacer prompt par readline
const prompt = (msg) => {{
    if (msg) console.log(msg);
    return readline();
}};

{code}
"""
            f.write(code_with_inputs)
        else:
            f.write(code)
        filepath = f.name
    
    try:
        start_time = time.time()
        result = subprocess.run(
            ['node', filepath],
            capture_output=True,
            text=True,
            timeout=5
        )
        execution_time = time.time() - start_time
        
        if result.returncode == 0:
            return {
                'success': True,
                'output': result.stdout,
                'error': '',
                'execution_time': execution_time
            }
        else:
            return {
                'success': False,
                'output': result.stdout,
                'error': result.stderr,
                'execution_time': execution_time
            }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'output': '',
            'error': 'Timeout: Exécution trop longue',
            'execution_time': 5
        }
    except FileNotFoundError:
        return {
            'success': False,
            'output': '',
            'error': 'Node.js non installé sur le serveur',
            'execution_time': 0
        }
    finally:
        if os.path.exists(filepath):
            os.unlink(filepath)


def executer_java(code, inputs=None):
    """Compile et exécute du code Java"""
    import time
    
    # Créer un répertoire temporaire
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Extraire le nom de la classe
        match = re.search(r'public\s+class\s+(\w+)', code)
        if not match:
            return {
                'success': False,
                'output': '',
                'error': 'Pas de classe publique trouvée. Utilisez: public class Main { ... }',
                'execution_time': 0
            }
        
        class_name = match.group(1)
        java_file = os.path.join(temp_dir, f'{class_name}.java')
        
        # Écrire le fichier Java
        with open(java_file, 'w', encoding='utf-8') as f:
            f.write(code)
        
        # Compilation
        start_time = time.time()
        compile_result = subprocess.run(
            ['javac', java_file],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if compile_result.returncode != 0:
            return {
                'success': False,
                'output': '',
                'error': f'Erreur de compilation:\n{compile_result.stderr}',
                'execution_time': time.time() - start_time
            }
        
        # Exécution
        input_str = '\n'.join(inputs) + '\n' if inputs else ''
        exec_result = subprocess.run(
            ['java', '-cp', temp_dir, class_name],
            input=input_str,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        execution_time = time.time() - start_time
        
        if exec_result.returncode == 0:
            return {
                'success': True,
                'output': exec_result.stdout,
                'error': '',
                'execution_time': execution_time
            }
        else:
            return {
                'success': False,
                'output': exec_result.stdout,
                'error': exec_result.stderr,
                'execution_time': execution_time
            }
            
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'output': '',
            'error': 'Timeout: Compilation/Exécution trop longue',
            'execution_time': 10
        }
    except FileNotFoundError:
        return {
            'success': False,
            'output': '',
            'error': 'Java JDK non installé sur le serveur',
            'execution_time': 0
        }
    finally:
        # Nettoyer
        shutil.rmtree(temp_dir, ignore_errors=True)


def executer_c_cpp(code, langage, inputs=None):
    """Compile et exécute du code C/C++"""
    import time
    
    extension = '.c' if langage == 'c' else '.cpp'
    compiler = 'gcc' if langage == 'c' else 'g++'
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        source_file = os.path.join(temp_dir, f'program{extension}')
        executable = os.path.join(temp_dir, 'program.exe' if os.name == 'nt' else 'program')
        
        # Écrire le fichier source
        with open(source_file, 'w', encoding='utf-8') as f:
            f.write(code)
        
        # Compilation
        start_time = time.time()
        compile_result = subprocess.run(
            [compiler, source_file, '-o', executable],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if compile_result.returncode != 0:
            return {
                'success': False,
                'output': '',
                'error': f'Erreur de compilation:\n{compile_result.stderr}',
                'execution_time': time.time() - start_time
            }
        
        # Exécution
        input_str = '\n'.join(inputs) + '\n' if inputs else ''
        exec_result = subprocess.run(
            [executable],
            input=input_str,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        execution_time = time.time() - start_time
        
        if exec_result.returncode == 0:
            return {
                'success': True,
                'output': exec_result.stdout,
                'error': '',
                'execution_time': execution_time
            }
        else:
            return {
                'success': False,
                'output': exec_result.stdout,
                'error': exec_result.stderr,
                'execution_time': execution_time
            }
            
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'output': '',
            'error': 'Timeout: Compilation/Exécution trop longue',
            'execution_time': 10
        }
    except FileNotFoundError:
        return {
            'success': False,
            'output': '',
            'error': f'{compiler} non installé sur le serveur',
            'execution_time': 0
        }
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def executer_sql(code):
    """Exécute des requêtes SQL via SQLite en mémoire"""
    import sqlite3
    import time
    
    try:
        start_time = time.time()
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        
        # Exécuter toutes les commandes
        output = []
        for statement in code.split(';'):
            statement = statement.strip()
            if not statement:
                continue
            
            try:
                cursor.execute(statement)
                
                # Si SELECT, récupérer les résultats
                if statement.upper().startswith('SELECT'):
                    rows = cursor.fetchall()
                    if rows:
                        # Afficher les colonnes
                        columns = [desc[0] for desc in cursor.description]
                        output.append(' | '.join(columns))
                        output.append('-' * 50)
                        for row in rows:
                            output.append(' | '.join(str(val) for val in row))
                    else:
                        output.append('(Aucun résultat)')
                else:
                    output.append(f'Commande exécutée: {cursor.rowcount} ligne(s) affectée(s)')
                
                conn.commit()
            except sqlite3.Error as e:
                return {
                    'success': False,
                    'output': '\n'.join(output),
                    'error': f'Erreur SQL: {str(e)}',
                    'execution_time': time.time() - start_time
                }
        
        conn.close()
        
        return {
            'success': True,
            'output': '\n'.join(output),
            'error': '',
            'execution_time': time.time() - start_time
        }
        
    except Exception as e:
        return {
            'success': False,
            'output': '',
            'error': f'Erreur: {str(e)}',
            'execution_time': 0
        }


def detecter_langage_depuis_domaine(domaine):
    """
    Détecte automatiquement le langage depuis le nom du domaine
    """
    domaine_lower = domaine.lower()
    
    if 'python' in domaine_lower:
        return 'python'
    elif 'javascript' in domaine_lower or 'js' in domaine_lower:
        return 'javascript'
    elif 'java' in domaine_lower and 'javascript' not in domaine_lower:
        return 'java'
    elif domaine_lower in ['c', 'langage c']:
        return 'c'
    elif 'c++' in domaine_lower or 'cpp' in domaine_lower:
        return 'cpp'
    elif 'sql' in domaine_lower or 'base' in domaine_lower:
        return 'sql'
    else:
        return 'python'  # Défaut
