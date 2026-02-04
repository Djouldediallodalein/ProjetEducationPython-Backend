"""
Gestion centralisée des erreurs et logging
"""

import logging
import os
from datetime import datetime
import traceback


# Configuration du logging
DOSSIER_LOGS = 'logs'
FICHIER_LOG = None


def initialiser_logging():
    """Initialise le système de logging"""
    global FICHIER_LOG
    
    # Créer le dossier de logs
    if not os.path.exists(DOSSIER_LOGS):
        os.makedirs(DOSSIER_LOGS)
    
    # Nom du fichier de log avec date
    date_str = datetime.now().strftime('%Y%m%d')
    FICHIER_LOG = os.path.join(DOSSIER_LOGS, f'app_{date_str}.log')
    
    # Configuration du logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(FICHIER_LOG, encoding='utf-8'),
            logging.StreamHandler()  # Afficher aussi dans la console (optionnel)
        ]
    )
    
    # Supprimer le StreamHandler pour ne pas polluer la console
    logger = logging.getLogger()
    logger.handlers = [h for h in logger.handlers if not isinstance(h, logging.StreamHandler)]
    
    logging.info("="*60)
    logging.info("Application demarree")
    logging.info("="*60)


def log_erreur(message, exception=None, afficher=True):
    """
    Enregistre une erreur dans les logs
    
    Args:
        message: Message d'erreur
        exception: Exception Python (optionnel)
        afficher: Si True, affiche aussi à l'utilisateur
    """
    if exception:
        logging.error(f"{message}: {str(exception)}")
        logging.error(traceback.format_exc())
    else:
        logging.error(message)
    
    if afficher:
        print(f"\nErreur: {message}")
        if exception and hasattr(exception, '__class__'):
            print(f"Type: {exception.__class__.__name__}")


def log_info(message):
    """Enregistre une information dans les logs"""
    logging.info(message)


def log_avertissement(message, afficher=False):
    """Enregistre un avertissement dans les logs"""
    logging.warning(message)
    if afficher:
        print(f"\nAvertissement: {message}")


def executer_securise(fonction, *args, message_erreur="Operation echouee", **kwargs):
    """
    Execute une fonction avec gestion d'erreurs
    
    Args:
        fonction: Fonction à exécuter
        *args: Arguments positionnels
        message_erreur: Message en cas d'erreur
        **kwargs: Arguments nommés
    
    Returns:
        tuple: (succes: bool, resultat: any)
    """
    try:
        resultat = fonction(*args, **kwargs)
        return True, resultat
    except Exception as e:
        log_erreur(message_erreur, e)
        return False, None


def verifier_fichier_json(chemin_fichier, creer_si_absent=False, contenu_defaut=None):
    """
    Vérifie qu'un fichier JSON est valide
    
    Args:
        chemin_fichier: Chemin du fichier
        creer_si_absent: Si True, crée le fichier s'il n'existe pas
        contenu_defaut: Contenu par défaut si création
    
    Returns:
        bool: True si fichier OK, False sinon
    """
    import json
    
    if not os.path.exists(chemin_fichier):
        if creer_si_absent:
            try:
                with open(chemin_fichier, 'w', encoding='utf-8') as f:
                    json.dump(contenu_defaut or {}, f, indent=4, ensure_ascii=False)
                log_info(f"Fichier cree: {chemin_fichier}")
                return True
            except Exception as e:
                log_erreur(f"Impossible de creer {chemin_fichier}", e)
                return False
        else:
            log_avertissement(f"Fichier manquant: {chemin_fichier}")
            return False
    
    # Vérifier que c'est un JSON valide
    try:
        with open(chemin_fichier, 'r', encoding='utf-8') as f:
            json.load(f)
        return True
    except json.JSONDecodeError as e:
        log_erreur(f"JSON invalide dans {chemin_fichier}", e)
        return False
    except Exception as e:
        log_erreur(f"Erreur lecture de {chemin_fichier}", e)
        return False


def sauvegarder_json_securise(chemin_fichier, donnees, sauvegarde_backup=True):
    """
    Sauvegarde un fichier JSON avec backup automatique
    
    Args:
        chemin_fichier: Chemin du fichier
        donnees: Données à sauvegarder
        sauvegarde_backup: Si True, crée une copie de backup
    
    Returns:
        bool: True si succès, False sinon
    """
    import json
    
    try:
        # Créer un backup si le fichier existe
        if sauvegarde_backup and os.path.exists(chemin_fichier):
            backup = chemin_fichier + '.backup'
            try:
                import shutil
                shutil.copy2(chemin_fichier, backup)
            except Exception as e:
                log_avertissement(f"Impossible de creer backup de {chemin_fichier}", afficher=False)
        
        # Écrire le fichier
        with open(chemin_fichier, 'w', encoding='utf-8') as f:
            json.dump(donnees, f, indent=4, ensure_ascii=False)
        
        return True
    
    except Exception as e:
        log_erreur(f"Impossible de sauvegarder {chemin_fichier}", e)
        
        # Tenter de restaurer le backup
        if sauvegarde_backup:
            backup = chemin_fichier + '.backup'
            if os.path.exists(backup):
                try:
                    import shutil
                    shutil.copy2(backup, chemin_fichier)
                    log_info(f"Backup restaure pour {chemin_fichier}")
                except:
                    pass
        
        return False


def nettoyer_anciens_logs(jours_conservation=30):
    """
    Supprime les logs plus anciens que X jours
    
    Args:
        jours_conservation: Nombre de jours à conserver
    """
    if not os.path.exists(DOSSIER_LOGS):
        return
    
    limite = datetime.now().timestamp() - (jours_conservation * 24 * 3600)
    
    for fichier in os.listdir(DOSSIER_LOGS):
        if fichier.endswith('.log'):
            chemin = os.path.join(DOSSIER_LOGS, fichier)
            if os.path.getmtime(chemin) < limite:
                try:
                    os.remove(chemin)
                    log_info(f"Log ancien supprime: {fichier}")
                except Exception as e:
                    log_avertissement(f"Impossible de supprimer {fichier}")


def verifier_integrite_systeme():
    """
    Vérifie l'intégrité du système au démarrage
    
    Returns:
        bool: True si tout est OK, False si problèmes critiques
    """
    log_info("Verification de l'integrite du systeme...")
    
    problemes = []
    
    # Vérifier les fichiers essentiels
    fichiers_essentiels = [
        ('fonctions.py', 'Module fonctions'),
        ('progression.py', 'Module progression'),
        ('main.py', 'Programme principal')
    ]
    
    for fichier, description in fichiers_essentiels:
        if not os.path.exists(fichier):
            problemes.append(f"{description} manquant ({fichier})")
    
    # Vérifier les fichiers JSON
    verifier_fichier_json('progression_utilisateur.json', creer_si_absent=True)
    verifier_fichier_json('banque_exercices.json', creer_si_absent=False)
    
    # Vérifier Ollama (optionnel, ne pas bloquer)
    try:
        import ollama
        log_info("Module ollama disponible")
    except ImportError:
        log_avertissement("Module ollama non disponible (IA desactivee)", afficher=True)
    
    if problemes:
        log_erreur("Problemes detectes lors de la verification:")
        for probleme in problemes:
            log_erreur(f"  - {probleme}")
        return False
    
    log_info("Integrite du systeme: OK")
    return True


def gestionnaire_erreur_global():
    """Gestionnaire d'erreurs global pour l'application"""
    import sys
    
    def exception_handler(exc_type, exc_value, exc_traceback):
        """Capture toutes les exceptions non gérées"""
        if issubclass(exc_type, KeyboardInterrupt):
            # Ne pas logger les interruptions clavier
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        log_erreur(
            "Exception non geree",
            exc_value,
            afficher=False
        )
        
        print("\n" + "="*60)
        print("UNE ERREUR CRITIQUE EST SURVENUE")
        print("="*60)
        print(f"\nType: {exc_type.__name__}")
        print(f"Message: {exc_value}")
        print(f"\nLes details ont ete enregistres dans: {FICHIER_LOG}")
        print("\nVeuillez redemarrer l'application.")
        print("Si le probleme persiste, consultez le fichier de log.")
    
    sys.excepthook = exception_handler


def menu_logs():
    """Menu de consultation des logs"""
    if not os.path.exists(DOSSIER_LOGS):
        print("\nAucun log disponible.")
        return
    
    fichiers = sorted([f for f in os.listdir(DOSSIER_LOGS) if f.endswith('.log')], reverse=True)
    
    if not fichiers:
        print("\nAucun log disponible.")
        return
    
    print("\n" + "="*60)
    print("FICHIERS DE LOG")
    print("="*60)
    
    for i, fichier in enumerate(fichiers[:10], 1):  # 10 derniers
        chemin = os.path.join(DOSSIER_LOGS, fichier)
        taille = os.path.getsize(chemin) / 1024
        date_modif = datetime.fromtimestamp(os.path.getmtime(chemin))
        
        print(f"\n{i}. {fichier}")
        print(f"   Taille: {taille:.2f} Ko")
        print(f"   Date: {date_modif.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        choix = int(input("\nNumero du fichier a afficher (0 pour annuler) : "))
        if 1 <= choix <= len(fichiers):
            chemin = os.path.join(DOSSIER_LOGS, fichiers[choix - 1])
            
            with open(chemin, 'r', encoding='utf-8') as f:
                contenu = f.read()
            
            print("\n" + "="*60)
            print(f"CONTENU DE {fichiers[choix - 1]}")
            print("="*60)
            
            # Afficher les 50 dernières lignes
            lignes = contenu.split('\n')
            for ligne in lignes[-50:]:
                print(ligne)
            
            if len(lignes) > 50:
                print(f"\n... ({len(lignes) - 50} lignes precedentes non affichees)")
    
    except ValueError:
        print("Annule.")
    except Exception as e:
        print(f"Erreur: {e}")
