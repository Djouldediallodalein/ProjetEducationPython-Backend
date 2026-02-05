"""
Module de verrouillage thread-safe pour les opérations sur fichiers JSON
Protection contre les race conditions et corruption de données
"""

import json
import os
import threading
import tempfile
import shutil
from contextlib import contextmanager
from typing import Any, Dict
from datetime import datetime

# Lock global pour chaque fichier (dict de locks par chemin de fichier)
_file_locks: Dict[str, threading.Lock] = {}
_locks_registry_lock = threading.Lock()


def _get_lock_for_file(filepath: str) -> threading.Lock:
    """
    Obtient ou crée un lock thread-safe pour un fichier spécifique
    
    Args:
        filepath: Chemin du fichier
        
    Returns:
        threading.Lock: Lock dédié à ce fichier
    """
    # Normaliser le chemin
    filepath = os.path.abspath(filepath)
    
    with _locks_registry_lock:
        if filepath not in _file_locks:
            _file_locks[filepath] = threading.Lock()
        return _file_locks[filepath]


@contextmanager
def atomic_json_writer(filepath: str):
    """
    Context manager pour écriture atomique de fichiers JSON
    
    Garantit :
    - Aucune corruption même en cas d'erreur
    - Écriture atomique (temp file + rename)
    - Thread-safety avec locks
    
    Usage:
        with atomic_json_writer('data.json') as writer:
            data = {'key': 'value'}
            writer(data)
    
    Args:
        filepath: Chemin du fichier JSON
        
    Yields:
        Fonction d'écriture à appeler avec les données
    """
    filepath = os.path.abspath(filepath)
    lock = _get_lock_for_file(filepath)
    
    # Acquérir le lock
    lock.acquire()
    
    try:
        written = False
        
        def write_data(data: Any):
            """Fonction interne d'écriture atomique"""
            nonlocal written
            
            # Créer le dossier parent si nécessaire
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Écrire dans un fichier temporaire
            temp_fd, temp_path = tempfile.mkstemp(
                dir=os.path.dirname(filepath),
                prefix='.tmp_',
                suffix='.json',
                text=True
            )
            
            try:
                with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                    f.flush()
                    os.fsync(f.fileno())  # Force l'écriture sur disque
                
                # Remplacer atomiquement l'ancien fichier
                # Sur Windows, on doit supprimer l'ancien fichier d'abord
                if os.path.exists(filepath):
                    backup_path = filepath + '.backup'
                    shutil.copy2(filepath, backup_path)
                    try:
                        os.replace(temp_path, filepath)
                        # Supprimer le backup si succès
                        if os.path.exists(backup_path):
                            os.remove(backup_path)
                    except Exception as e:
                        # Restaurer depuis le backup en cas d'erreur
                        if os.path.exists(backup_path):
                            shutil.copy2(backup_path, filepath)
                            os.remove(backup_path)
                        raise e
                else:
                    os.replace(temp_path, filepath)
                
                written = True
                
            except Exception as e:
                # Nettoyer le fichier temporaire en cas d'erreur
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except:
                        pass
                raise IOError(f"Erreur lors de l'écriture atomique de {filepath}: {str(e)}")
        
        yield write_data
        
        if not written:
            raise IOError(f"Aucune donnée n'a été écrite dans {filepath}")
            
    finally:
        # Toujours libérer le lock
        lock.release()


@contextmanager
def safe_json_read(filepath: str):
    """
    Context manager pour lecture thread-safe de fichiers JSON
    
    Usage:
        with safe_json_read('data.json') as data:
            print(data)
    
    Args:
        filepath: Chemin du fichier JSON
        
    Yields:
        dict: Données JSON chargées
    """
    filepath = os.path.abspath(filepath)
    lock = _get_lock_for_file(filepath)
    
    lock.acquire()
    
    try:
        if not os.path.exists(filepath):
            yield {}
        else:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                yield data
    except json.JSONDecodeError as e:
        # Tenter de restaurer depuis le backup
        backup_path = filepath + '.backup'
        if os.path.exists(backup_path):
            try:
                with open(backup_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Restaurer le fichier corrompu
                    shutil.copy2(backup_path, filepath)
                    yield data
            except:
                raise IOError(f"Fichier JSON corrompu et backup invalide: {filepath}")
        else:
            raise IOError(f"Fichier JSON corrompu sans backup: {filepath}")
    except Exception as e:
        raise IOError(f"Erreur lors de la lecture de {filepath}: {str(e)}")
    finally:
        lock.release()


def safe_json_update(filepath: str, update_func):
    """
    Met à jour un fichier JSON de manière thread-safe et atomique
    
    CRITIQUE : Cette fonction garde le lock pendant toute la durée
    de la lecture + modification + écriture pour garantir l'atomicité
    
    Usage:
        def update(data):
            data['counter'] = data.get('counter', 0) + 1
            return data
        
        safe_json_update('data.json', update)
    
    Args:
        filepath: Chemin du fichier JSON
        update_func: Fonction qui prend les données et retourne les données modifiées
        
    Returns:
        dict: Données mises à jour
    """
    filepath = os.path.abspath(filepath)
    lock = _get_lock_for_file(filepath)
    
    # Acquérir le lock une seule fois pour toute l'opération
    lock.acquire()
    
    try:
        # 1. Lire les données actuelles
        if not os.path.exists(filepath):
            data = {}
        else:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                # Tenter de restaurer depuis le backup
                backup_path = filepath + '.backup'
                if os.path.exists(backup_path):
                    with open(backup_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                else:
                    data = {}
        
        # 2. Appliquer la fonction de mise à jour
        updated_data = update_func(data)
        
        # 3. Écrire atomiquement (sans lock car déjà acquis)
        # Créer le dossier parent si nécessaire
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Écrire dans un fichier temporaire
        temp_fd, temp_path = tempfile.mkstemp(
            dir=os.path.dirname(filepath),
            prefix='.tmp_',
            suffix='.json',
            text=True
        )
        
        try:
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                json.dump(updated_data, f, indent=4, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
            
            # Remplacer atomiquement
            if os.path.exists(filepath):
                backup_path = filepath + '.backup'
                shutil.copy2(filepath, backup_path)
                try:
                    os.replace(temp_path, filepath)
                    if os.path.exists(backup_path):
                        os.remove(backup_path)
                except Exception as e:
                    if os.path.exists(backup_path):
                        shutil.copy2(backup_path, filepath)
                        os.remove(backup_path)
                    raise e
            else:
                os.replace(temp_path, filepath)
        
        except Exception as e:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
            raise IOError(f"Erreur lors de l'écriture de {filepath}: {str(e)}")
        
        return updated_data
    
    finally:
        # Toujours libérer le lock
        lock.release()


# Logs des opérations (pour debugging)
def log_file_operation(operation: str, filepath: str, success: bool = True, error: str = None):
    """Log les opérations sur fichiers (optionnel)"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'operation': operation,
        'filepath': os.path.basename(filepath),
        'success': success,
        'error': error
    }
    
    # Écrire dans un fichier de log dédié (sans lock pour éviter deadlock)
    log_file = 'logs/file_operations.log'
    try:
        os.makedirs('logs', exist_ok=True)
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    except:
        pass  # Ne pas bloquer l'opération si le log échoue
