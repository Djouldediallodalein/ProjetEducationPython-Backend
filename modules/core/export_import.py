"""
Système d'export et import de données
Permet de sauvegarder et restaurer la progression
"""

import json
import os
from datetime import datetime
import shutil


DOSSIER_SAUVEGARDES = 'sauvegardes'


def initialiser_dossier_sauvegardes():
    """Crée le dossier de sauvegardes s'il n'existe pas"""
    if not os.path.exists(DOSSIER_SAUVEGARDES):
        os.makedirs(DOSSIER_SAUVEGARDES)


def exporter_progression(nom_sauvegarde=None):
    """
    Exporte toutes les données de progression
    
    Args:
        nom_sauvegarde: Nom personnalisé pour la sauvegarde (optionnel)
    
    Returns:
        str: Chemin du fichier de sauvegarde créé
    """
    initialiser_dossier_sauvegardes()
    
    # Créer un nom de fichier avec timestamp
    if not nom_sauvegarde:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nom_sauvegarde = f"sauvegarde_{timestamp}"
    
    # Nettoyer le nom (enlever les caractères spéciaux)
    nom_sauvegarde = "".join(c for c in nom_sauvegarde if c.isalnum() or c in ('_', '-'))
    
    chemin_sauvegarde = os.path.join(DOSSIER_SAUVEGARDES, nom_sauvegarde + '.json')
    
    # Collecter toutes les données
    donnees = {
        'date_export': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'version': '2.0',
        'fichiers': {}
    }
    
    # Fichiers à sauvegarder
    fichiers_a_sauvegarder = [
        'progression_utilisateur.json',
        'banque_exercices.json',
        'utilisateurs.json',
        'domaines.json'
    ]
    
    for fichier in fichiers_a_sauvegarder:
        if os.path.exists(fichier):
            with open(fichier, 'r', encoding='utf-8') as f:
                donnees['fichiers'][fichier] = json.load(f)
    
    # Sauvegarder les progressions des utilisateurs
    dossier_progressions = 'progressions'
    if os.path.exists(dossier_progressions):
        donnees['progressions_utilisateurs'] = {}
        for fichier in os.listdir(dossier_progressions):
            if fichier.endswith('.json'):
                chemin = os.path.join(dossier_progressions, fichier)
                with open(chemin, 'r', encoding='utf-8') as f:
                    donnees['progressions_utilisateurs'][fichier] = json.load(f)
    
    # Écrire la sauvegarde
    with open(chemin_sauvegarde, 'w', encoding='utf-8') as f:
        json.dump(donnees, f, indent=4, ensure_ascii=False)
    
    print(f"\nSauvegarde creee : {chemin_sauvegarde}")
    print(f"Taille : {os.path.getsize(chemin_sauvegarde) / 1024:.2f} Ko")
    
    return chemin_sauvegarde


def importer_progression(chemin_sauvegarde):
    """
    Importe une sauvegarde de progression
    
    Args:
        chemin_sauvegarde: Chemin vers le fichier de sauvegarde
    
    Returns:
        bool: True si import réussi, False sinon
    """
    if not os.path.exists(chemin_sauvegarde):
        print(f"\nErreur: Le fichier '{chemin_sauvegarde}' n'existe pas.")
        return False
    
    try:
        # Lire la sauvegarde
        with open(chemin_sauvegarde, 'r', encoding='utf-8') as f:
            donnees = json.load(f)
        
        # Vérifier la version
        version = donnees.get('version', '1.0')
        print(f"\nImport d'une sauvegarde version {version}")
        print(f"Date de creation : {donnees.get('date_export', 'inconnue')}")
        
        # Demander confirmation
        confirmation = input("\nVoulez-vous vraiment restaurer cette sauvegarde ? (oui/non) : ")
        if confirmation.lower() not in ['oui', 'o', 'yes', 'y']:
            print("Import annule.")
            return False
        
        # Créer une sauvegarde automatique avant d'écraser
        print("\nCreation d'une sauvegarde automatique avant restauration...")
        exporter_progression("avant_import_" + datetime.now().strftime('%Y%m%d_%H%M%S'))
        
        # Restaurer les fichiers
        if 'fichiers' in donnees:
            for nom_fichier, contenu in donnees['fichiers'].items():
                with open(nom_fichier, 'w', encoding='utf-8') as f:
                    json.dump(contenu, f, indent=4, ensure_ascii=False)
                print(f"Restaure : {nom_fichier}")
        
        # Restaurer les progressions des utilisateurs
        if 'progressions_utilisateurs' in donnees:
            dossier_progressions = 'progressions'
            if not os.path.exists(dossier_progressions):
                os.makedirs(dossier_progressions)
            
            for nom_fichier, contenu in donnees['progressions_utilisateurs'].items():
                chemin = os.path.join(dossier_progressions, nom_fichier)
                with open(chemin, 'w', encoding='utf-8') as f:
                    json.dump(contenu, f, indent=4, ensure_ascii=False)
                print(f"Restaure : {chemin}")
        
        print("\nImport termine avec succes !")
        return True
    
    except Exception as e:
        print(f"\nErreur lors de l'import : {e}")
        return False


def lister_sauvegardes():
    """Liste toutes les sauvegardes disponibles"""
    initialiser_dossier_sauvegardes()
    
    fichiers = [f for f in os.listdir(DOSSIER_SAUVEGARDES) if f.endswith('.json')]
    
    if not fichiers:
        print("\nAucune sauvegarde disponible.")
        return []
    
    print("\n" + "="*60)
    print("SAUVEGARDES DISPONIBLES")
    print("="*60)
    
    sauvegardes = []
    for i, fichier in enumerate(sorted(fichiers, reverse=True), 1):
        chemin = os.path.join(DOSSIER_SAUVEGARDES, fichier)
        taille = os.path.getsize(chemin) / 1024
        date_modif = datetime.fromtimestamp(os.path.getmtime(chemin))
        
        print(f"\n{i}. {fichier}")
        print(f"   Taille: {taille:.2f} Ko")
        print(f"   Date: {date_modif.strftime('%Y-%m-%d %H:%M:%S')}")
        
        sauvegardes.append(chemin)
    
    return sauvegardes


def supprimer_sauvegarde(chemin_sauvegarde):
    """Supprime une sauvegarde"""
    if not os.path.exists(chemin_sauvegarde):
        print(f"\nErreur: Le fichier n'existe pas.")
        return False
    
    confirmation = input(f"\nVoulez-vous vraiment supprimer cette sauvegarde ? (oui/non) : ")
    if confirmation.lower() not in ['oui', 'o', 'yes', 'y']:
        print("Suppression annulee.")
        return False
    
    os.remove(chemin_sauvegarde)
    print(f"\nSauvegarde supprimee.")
    return True


def exporter_statistiques():
    """Exporte les statistiques sous forme de rapport texte"""
    from modules.core.progression import charger_progression, obtenir_domaine_actif, obtenir_progression_domaine
    from modules.core.domaines import charger_domaines, obtenir_nom_domaine
    
    initialiser_dossier_sauvegardes()
    
    progression = charger_progression()
    domaine_actif = obtenir_domaine_actif()
    domaines = charger_domaines()
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nom_rapport = f"rapport_stats_{timestamp}.txt"
    chemin_rapport = os.path.join(DOSSIER_SAUVEGARDES, nom_rapport)
    
    with open(chemin_rapport, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("RAPPORT DE STATISTIQUES\n")
        f.write("="*60 + "\n")
        f.write(f"\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Domaine actif: {obtenir_nom_domaine(domaine_actif)}\n")
        
        # Statistiques par domaine
        f.write(f"\n\nSTATISTIQUES PAR DOMAINE\n")
        f.write("-" * 60 + "\n")
        
        for domaine_id, prog_dom in progression.get('domaines', {}).items():
            nom_domaine = obtenir_nom_domaine(domaine_id)
            f.write(f"\n{nom_domaine}:\n")
            f.write(f"  Niveau: {prog_dom.get('niveau', 1)}\n")
            f.write(f"  XP Total: {prog_dom.get('xp_total', 0)}\n")
            f.write(f"  Exercices reussis: {prog_dom.get('exercices_reussis', 0)}\n")
            f.write(f"  Exercices totaux: {prog_dom.get('exercices_totaux', 0)}\n")
            
            if prog_dom.get('exercices_totaux', 0) > 0:
                taux = (prog_dom.get('exercices_reussis', 0) / prog_dom['exercices_totaux']) * 100
                f.write(f"  Taux de reussite: {taux:.1f}%\n")
        
        # Streaks
        f.write(f"\nStreak actuel: {progression.get('streak_actuel', 0)} jours\n")
        f.write(f"Record de streak: {progression.get('streak_record', 0)} jours\n")
        
        # Badges du domaine actif
        prog_domaine_actif = obtenir_progression_domaine(domaine_actif)
        badges = prog_domaine_actif.get('badges', [])
        f.write(f"\n\nBADGES - {obtenir_nom_domaine(domaine_actif)} ({len(badges)})\n")
        f.write("-" * 60 + "\n")
        for badge in badges:
            f.write(f"- {badge}\n")
        
        # Thèmes du domaine actif
        f.write(f"\n\nPROGRESSION PAR THEME - {obtenir_nom_domaine(domaine_actif)}\n")
        f.write("-" * 60 + "\n")
        for theme, stats in prog_domaine_actif.get('themes', {}).items():
            taux = (stats['reussis'] / stats['totaux']) * 100 if stats['totaux'] > 0 else 0
            f.write(f"\n{theme}:\n")
            f.write(f"  Reussis: {stats['reussis']}/{stats['totaux']} ({taux:.1f}%)\n")
        
        # Historique récent du domaine actif
        historique = prog_domaine_actif.get('historique', [])
        if historique:
            f.write(f"\n\nHISTORIQUE RECENT - {obtenir_nom_domaine(domaine_actif)} (10 derniers)\n")
            f.write("-" * 60 + "\n")
            for entree in historique[-10:]:
                statut = "REUSSI" if entree['reussi'] else "PASSE"
                f.write(f"\n[{entree['date']}] - {statut}\n")
                f.write(f"  Theme: {entree['theme']}\n")
                f.write(f"  Tentatives: {entree['tentatives']}\n")
    
    print(f"\nRapport de statistiques cree : {chemin_rapport}")
    return chemin_rapport


def menu_export_import():
    """Menu de gestion des sauvegardes"""
    while True:
        print("\n" + "="*60)
        print("GESTION DES SAUVEGARDES")
        print("="*60)
        print("\n1. Creer une sauvegarde")
        print("2. Restaurer une sauvegarde")
        print("3. Lister les sauvegardes")
        print("4. Supprimer une sauvegarde")
        print("5. Exporter rapport de statistiques")
        print("0. Retour")
        
        try:
            choix = int(input("\nVotre choix : "))
        except ValueError:
            print("Erreur: Entrez un numero valide.")
            continue
        
        if choix == 0:
            break
        
        elif choix == 1:
            nom = input("\nNom de la sauvegarde (vide pour auto) : ").strip()
            exporter_progression(nom if nom else None)
        
        elif choix == 2:
            sauvegardes = lister_sauvegardes()
            if sauvegardes:
                try:
                    num = int(input("\nNumero de la sauvegarde a restaurer : "))
                    if 1 <= num <= len(sauvegardes):
                        importer_progression(sauvegardes[num - 1])
                    else:
                        print("Numero invalide.")
                except ValueError:
                    print("Erreur: Entrez un numero valide.")
        
        elif choix == 3:
            lister_sauvegardes()
        
        elif choix == 4:
            sauvegardes = lister_sauvegardes()
            if sauvegardes:
                try:
                    num = int(input("\nNumero de la sauvegarde a supprimer : "))
                    if 1 <= num <= len(sauvegardes):
                        supprimer_sauvegarde(sauvegardes[num - 1])
                    else:
                        print("Numero invalide.")
                except ValueError:
                    print("Erreur: Entrez un numero valide.")
        
        elif choix == 5:
            exporter_statistiques()
        
        else:
            print("Choix invalide.")
