"""
Système de gestion des utilisateurs multiples
"""

import json
import os
from datetime import datetime
from modules.core.progression import initialiser_progression
from modules.core.file_lock import atomic_json_writer, safe_json_read, safe_json_update

# Chemins absolus basés sur le répertoire backend
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FICHIER_UTILISATEURS = os.path.join(BASE_DIR, 'utilisateurs.json')
DOSSIER_PROGRESSIONS = os.path.join(BASE_DIR, 'progressions')


def initialiser_systeme_utilisateurs():
    """Initialise le système de gestion des utilisateurs"""
    # Créer le dossier des progressions s'il n'existe pas
    if not os.path.exists(DOSSIER_PROGRESSIONS):
        os.makedirs(DOSSIER_PROGRESSIONS)
    
    # Créer le fichier utilisateurs s'il n'existe pas
    if not os.path.exists(FICHIER_UTILISATEURS):
        utilisateurs = {
            'utilisateur_actif': None,
            'utilisateurs': {}
        }
        sauvegarder_utilisateurs(utilisateurs)


def charger_utilisateurs():
    """Charge la liste des utilisateurs de manière thread-safe"""
    if not os.path.exists(FICHIER_UTILISATEURS):
        return {'utilisateur_actif': None, 'utilisateurs': {}}
    
    with safe_json_read(FICHIER_UTILISATEURS) as data:
        # S'assurer que la structure est valide
        if 'utilisateur_actif' not in data:
            data['utilisateur_actif'] = None
        if 'utilisateurs' not in data:
            data['utilisateurs'] = {}
        return data


def sauvegarder_utilisateurs(utilisateurs):
    """Sauvegarde la liste des utilisateurs de manière atomique et thread-safe"""
    with atomic_json_writer(FICHIER_UTILISATEURS) as writer:
        writer(utilisateurs)


def creer_utilisateur(nom_utilisateur, niveau=1, email='', password_hash='', role='user'):
    """
    Crée un nouveau profil utilisateur
    
    Args:
        nom_utilisateur: Nom du nouvel utilisateur
        niveau: Niveau initial de l'utilisateur (défaut: 1)
        email: Email de l'utilisateur (optionnel)
        password_hash: Hash bcrypt du mot de passe
        role: Rôle de l'utilisateur (user, teacher, admin)
    
    Returns:
        dict: Données de l'utilisateur créé ou False si échec
    """
    utilisateurs = charger_utilisateurs()
    
    # Vérifier si le nom existe déjà
    if nom_utilisateur in utilisateurs['utilisateurs']:
        print(f"\nErreur: L'utilisateur '{nom_utilisateur}' existe deja.")
        return False
    
    # Créer le profil
    utilisateurs['utilisateurs'][nom_utilisateur] = {
        'nom': nom_utilisateur,
        'email': email,
        'password_hash': password_hash,
        'niveau': niveau,
        'role': role,
        'date_creation': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'fichier_progression': f'{DOSSIER_PROGRESSIONS}/{nom_utilisateur}.json'
    }
    
    # Créer le fichier de progression
    progression = initialiser_progression()
    fichier_prog = utilisateurs['utilisateurs'][nom_utilisateur]['fichier_progression']
    
    with atomic_json_writer(fichier_prog) as writer:
        writer(progression)
    
    sauvegarder_utilisateurs(utilisateurs)
    print(f"\nUtilisateur '{nom_utilisateur}' cree avec succes !")
    return utilisateurs['utilisateurs'][nom_utilisateur]


def supprimer_utilisateur(nom_utilisateur):
    """
    Supprime un profil utilisateur
    
    Args:
        nom_utilisateur: Nom de l'utilisateur à supprimer
    
    Returns:
        bool: True si suppression réussie, False sinon
    """
    utilisateurs = charger_utilisateurs()
    
    if nom_utilisateur not in utilisateurs['utilisateurs']:
        print(f"\nErreur: L'utilisateur '{nom_utilisateur}' n'existe pas.")
        return False
    
    # Demander confirmation
    confirmation = input(f"\nEtes-vous sur de vouloir supprimer '{nom_utilisateur}' ? (oui/non): ")
    if confirmation.lower() not in ['oui', 'o', 'yes', 'y']:
        print("Suppression annulee.")
        return False
    
    # Supprimer le fichier de progression
    fichier_prog = utilisateurs['utilisateurs'][nom_utilisateur]['fichier_progression']
    if os.path.exists(fichier_prog):
        os.remove(fichier_prog)
    
    # Retirer de la liste
    del utilisateurs['utilisateurs'][nom_utilisateur]
    
    # Si c'était l'utilisateur actif, le désactiver
    if utilisateurs['utilisateur_actif'] == nom_utilisateur:
        utilisateurs['utilisateur_actif'] = None
    
    sauvegarder_utilisateurs(utilisateurs)
    print(f"\nUtilisateur '{nom_utilisateur}' supprime avec succes.")
    return True


def selectionner_utilisateur(nom_utilisateur):
    """
    Sélectionne un utilisateur comme actif
    
    Args:
        nom_utilisateur: Nom de l'utilisateur à sélectionner
    
    Returns:
        str: Chemin vers le fichier de progression, ou None
    """
    utilisateurs = charger_utilisateurs()
    
    if nom_utilisateur not in utilisateurs['utilisateurs']:
        print(f"\nErreur: L'utilisateur '{nom_utilisateur}' n'existe pas.")
        return None
    
    utilisateurs['utilisateur_actif'] = nom_utilisateur
    sauvegarder_utilisateurs(utilisateurs)
    
    return utilisateurs['utilisateurs'][nom_utilisateur]['fichier_progression']


def obtenir_utilisateur_actif():
    """Retourne le nom de l'utilisateur actuellement actif"""
    utilisateurs = charger_utilisateurs()
    return utilisateurs.get('utilisateur_actif')


def obtenir_fichier_progression_actif():
    """Retourne le chemin du fichier de progression de l'utilisateur actif"""
    utilisateurs = charger_utilisateurs()
    utilisateur_actif = utilisateurs.get('utilisateur_actif')
    
    if utilisateur_actif and utilisateur_actif in utilisateurs['utilisateurs']:
        return utilisateurs['utilisateurs'][utilisateur_actif]['fichier_progression']
    
    # Par défaut, retourner le fichier de progression classique
    return 'progression_utilisateur.json'


def lister_utilisateurs():
    """Affiche la liste de tous les utilisateurs"""
    utilisateurs = charger_utilisateurs()
    utilisateur_actif = utilisateurs.get('utilisateur_actif')
    
    print("\n" + "="*60)
    print("LISTE DES UTILISATEURS")
    print("="*60)
    
    if not utilisateurs['utilisateurs']:
        print("\nAucun utilisateur cree.")
        return []
    
    liste = []
    for i, (nom, info) in enumerate(utilisateurs['utilisateurs'].items(), 1):
        actif = " (ACTIF)" if nom == utilisateur_actif else ""
        print(f"{i}. {nom}{actif}")
        print(f"   Cree le: {info['date_creation']}")
        liste.append(nom)
    
    return liste


def menu_utilisateurs():
    """Menu de gestion des utilisateurs"""
    while True:
        print("\n" + "="*60)
        print("GESTION DES UTILISATEURS")
        print("="*60)
        print("\n1. Creer un utilisateur")
        print("2. Selectionner un utilisateur")
        print("3. Supprimer un utilisateur")
        print("4. Liste des utilisateurs")
        print("0. Retour")
        
        try:
            choix = int(input("\nVotre choix : "))
        except ValueError:
            print("Erreur: Entrez un numero valide.")
            continue
        
        if choix == 0:
            break
        
        elif choix == 1:
            nom = input("\nNom du nouvel utilisateur : ").strip()
            if nom:
                creer_utilisateur(nom)
            else:
                print("Erreur: Le nom ne peut pas etre vide.")
        
        elif choix == 2:
            liste = lister_utilisateurs()
            if liste:
                try:
                    num = int(input("\nNumero de l'utilisateur a selectionner : "))
                    if 1 <= num <= len(liste):
                        selectionner_utilisateur(liste[num - 1])
                        print(f"\nUtilisateur '{liste[num - 1]}' selectionne !")
                    else:
                        print("Numero invalide.")
                except ValueError:
                    print("Erreur: Entrez un numero valide.")
        
        elif choix == 3:
            liste = lister_utilisateurs()
            if liste:
                try:
                    num = int(input("\nNumero de l'utilisateur a supprimer : "))
                    if 1 <= num <= len(liste):
                        supprimer_utilisateur(liste[num - 1])
                    else:
                        print("Numero invalide.")
                except ValueError:
                    print("Erreur: Entrez un numero valide.")
        
        elif choix == 4:
            lister_utilisateurs()
        
        else:
            print("Choix invalide.")
