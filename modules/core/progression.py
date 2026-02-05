import json
import os
from datetime import datetime
from modules.core.file_lock import atomic_json_writer, safe_json_read, safe_json_update


def obtenir_fichier_progression():
    """Obtient le fichier de progression selon le système d'utilisateurs"""
    try:
        from modules.core.utilisateurs import obtenir_fichier_progression_actif
        return obtenir_fichier_progression_actif()
    except ImportError:
        # Si le module utilisateurs n'est pas disponible, utiliser le fichier par défaut
        return 'progression_utilisateur.json'


FICHIER_PROGRESSION = obtenir_fichier_progression()



def initialiser_progression():
    """Crée la structure de progression initiale pour un nouvel utilisateur"""
    return {
        'domaine_actif': 'python',  # Domaine par défaut
        'domaines': {
            'python': {
                'niveau': 1,
                'exercices_reussis': 0,
                'exercices_totaux': 0,
                'themes': {},
                'exercices_completes': [],
                'badges': [],
                'historique': []
            }
        },
        'streak_actuel': 0,
        'streak_record': 0,
        'derniere_connexion': datetime.now().strftime('%Y-%m-%d'),
        'date_creation': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'xp_total': 0
    }
    


def charger_progression():
    """Charge la progression depuis le fichier JSON ou crée une nouvelle progression (thread-safe)"""
    fichier = obtenir_fichier_progression()
    if not os.path.exists(fichier):
        return initialiser_progression()
    
    with safe_json_read(fichier) as prog:
        # Migration : si ancien format (sans domaines), migrer
        if 'domaines' not in prog:
            prog = migrer_vers_multi_domaines(prog)
        return prog


def migrer_vers_multi_domaines(ancienne_prog):
    """Migre une progression de l'ancien format vers le nouveau format multi-domaines"""
    nouvelle_prog = initialiser_progression()
    
    # Copier les données de Python dans le nouveau format
    nouvelle_prog['domaines']['python'] = {
        'niveau': ancienne_prog.get('niveau', 1),
        'exercices_reussis': ancienne_prog.get('exercices_reussis', 0),
        'exercices_totaux': ancienne_prog.get('exercices_totaux', 0),
        'themes': ancienne_prog.get('themes', {}),
        'exercices_completes': ancienne_prog.get('exercices_completes', []),
        'badges': ancienne_prog.get('badges', []),
        'historique': ancienne_prog.get('historique', [])
    }
    
    # Copier les données globales
    nouvelle_prog['streak_actuel'] = ancienne_prog.get('streak_actuel', 0)
    nouvelle_prog['streak_record'] = ancienne_prog.get('streak_record', 0)
    nouvelle_prog['derniere_connexion'] = ancienne_prog.get('derniere_connexion', datetime.now().strftime('%Y-%m-%d'))
    nouvelle_prog['date_creation'] = ancienne_prog.get('date_creation', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    nouvelle_prog['xp_total'] = ancienne_prog.get('xp_total', 0)
    
    return nouvelle_prog


def obtenir_domaine_actif():
    """Retourne le domaine actuellement actif"""
    prog = charger_progression()
    return prog.get('domaine_actif', 'python')


def changer_domaine_actif(id_domaine):
    """Change le domaine actif"""
    prog = charger_progression()
    
    # Créer le domaine s'il n'existe pas encore
    if id_domaine not in prog['domaines']:
        prog['domaines'][id_domaine] = {
            'niveau': 1,
            'exercices_reussis': 0,
            'exercices_totaux': 0,
            'themes': {},
            'exercices_completes': [],
            'badges': [],
            'historique': []
        }
    
    prog['domaine_actif'] = id_domaine
    sauvegarder_progression(prog)
    return prog


def obtenir_progression_domaine(domaine=None):
    """Obtient la progression pour un domaine spécifique"""
    prog = charger_progression()
    
    if domaine is None:
        domaine = prog.get('domaine_actif', 'python')
    
    # Si le domaine n'existe pas, le créer
    if domaine not in prog['domaines']:
        prog['domaines'][domaine] = {
            'niveau': 1,
            'exercices_reussis': 0,
            'exercices_totaux': 0,
            'themes': {},
            'exercices_completes': [],
            'badges': [],
            'historique': []
        }
        sauvegarder_progression(prog)
    
    return prog['domaines'][domaine]




def sauvegarder_progression(progression):
    """Sauvegarde la progression dans le fichier JSON de manière atomique et thread-safe"""
    fichier = obtenir_fichier_progression()
    with atomic_json_writer(fichier) as writer:
        writer(progression)



def mettre_a_jour_progression(theme, reussi, domaine=None):
    """Met à jour la progression après un exercice"""
    progression = charger_progression()
    
    # Obtenir le domaine actif
    if domaine is None:
        domaine = progression.get('domaine_actif', 'python')
    
    # S'assurer que le domaine existe
    if domaine not in progression['domaines']:
        progression['domaines'][domaine] = {
            'niveau': 1,
            'exercices_reussis': 0,
            'exercices_totaux': 0,
            'themes': {},
            'exercices_completes': [],
            'badges': [],
            'historique': []
        }
    
    prog_domaine = progression['domaines'][domaine]
    
    # Mise à jour des compteurs du domaine
    prog_domaine['exercices_totaux'] += 1
    if reussi:
        prog_domaine['exercices_reussis'] += 1
    
    # Mise à jour par thème
    if theme not in prog_domaine['themes']:
        prog_domaine['themes'][theme] = {'reussis': 0, 'totaux': 0}
    
    prog_domaine['themes'][theme]['totaux'] += 1
    if reussi:
        prog_domaine['themes'][theme]['reussis'] += 1
    
    # Augmentation du niveau tous les 5 exercices réussis
    if prog_domaine['exercices_reussis'] % 5 == 0 and reussi:
        prog_domaine['niveau'] += 1
        print(f"\nNIVEAU SUPÉRIEUR ! Vous êtes maintenant au niveau {prog_domaine['niveau']} !")
    
    sauvegarder_progression(progression)
    return progression



def afficher_progression(domaine=None):
    """Affiche les statistiques de progression de l'utilisateur"""
    progression = charger_progression()
    
    if domaine is None:
        domaine = progression.get('domaine_actif', 'python')
    
    prog_domaine = obtenir_progression_domaine(domaine)
    
    # Obtenir le nom du domaine
    try:
        from modules.core.domaines import obtenir_nom_domaine
        nom_domaine = obtenir_nom_domaine(domaine)
    except:
        nom_domaine = domaine.upper()

    print(f"\nVOTRE PROGRESSION - {nom_domaine}")
    print("="*50)
    print(f"Niveau actuel : {prog_domaine['niveau']}")
    print(f"Exercices réussis : {prog_domaine['exercices_reussis']}/{prog_domaine['exercices_totaux']}")
    
    if prog_domaine['exercices_totaux'] > 0:
        taux = (prog_domaine['exercices_reussis'] / prog_domaine['exercices_totaux']) * 100
        print(f"Taux de réussite : {taux:.1f}%")

    print("\nPROGRESSION PAR THÈME")
    print("="*50)
    
    if prog_domaine['themes']:
        for theme, stats in prog_domaine['themes'].items():
            taux_theme = (stats['reussis'] / stats['totaux']) * 100 if stats['totaux'] > 0 else 0
            print(f"{theme} : {stats['reussis']}/{stats['totaux']} ({taux_theme:.0f}%)")
    else:
        print("Aucun exercice effectué pour le moment.")
        
        


def marquer_exercice_complete(theme, niveau, exercice, domaine=None):
    """Marque un exercice comme complété pour éviter de le reproposer"""
    progression = charger_progression()
    
    if domaine is None:
        domaine = progression.get('domaine_actif', 'python')
    
    prog_domaine = obtenir_progression_domaine(domaine)
    
    if 'exercices_completes' not in prog_domaine:
        prog_domaine['exercices_completes'] = []
    
    exercice_str = str(exercice)[:50]
    identifiant = f"{theme}|{niveau}|{exercice_str}"
    
    if identifiant not in prog_domaine['exercices_completes']:
        prog_domaine['exercices_completes'].append(identifiant)
        progression['domaines'][domaine] = prog_domaine
        sauvegarder_progression(progression)


def est_exercice_complete(theme, niveau, exercice, domaine=None):
    """Vérifie si un exercice a déjà été complété"""
    progression = charger_progression()
    
    if domaine is None:
        domaine = progression.get('domaine_actif', 'python')
    
    prog_domaine = obtenir_progression_domaine(domaine)
    
    if 'exercices_completes' not in prog_domaine:
        return False
    
    exercice_str = str(exercice)[:50]
    identifiant = f"{theme}|{niveau}|{exercice_str}"
    
    return identifiant in prog_domaine['exercices_completes']
    """Vérifie si un exercice a déjà été complété"""
    progression = charger_progression()
    
    if 'exercices_completes' not in progression:
        return False
    
    exercice_str = str(exercice)[:50]
    identifiant = f"{theme}|{niveau}|{exercice_str}"
    return identifiant in progression['exercices_completes']

def mettre_a_jour_streak():
    """Met à jour le streak quotidien de l'utilisateur"""
    progression = charger_progression()
    
    aujourd_hui = datetime.now().strftime('%Y-%m-%d')
    
    # Initialiser si nécessaire
    if 'streak_actuel' not in progression:
        progression['streak_actuel'] = 1
        progression['streak_record'] = 1
        progression['derniere_connexion'] = aujourd_hui
        sauvegarder_progression(progression)
        return 1, True
    
    derniere_connexion = progression.get('derniere_connexion', aujourd_hui)
    
    # Calculer la différence de jours
    date_derniere = datetime.strptime(derniere_connexion, '%Y-%m-%d')
    date_aujourd_hui = datetime.strptime(aujourd_hui, '%Y-%m-%d')
    diff_jours = (date_aujourd_hui - date_derniere).days
    
    if diff_jours == 0:
        # Même jour, pas de changement
        return progression['streak_actuel'], False
    elif diff_jours == 1:
        # Jour consécutif, on incrémente
        progression['streak_actuel'] += 1
        nouveau_streak = True
    else:
        # Streak cassé, on recommence à 1
        progression['streak_actuel'] = 1
        nouveau_streak = False
    
    # Mise à jour du record
    if progression['streak_actuel'] > progression.get('streak_record', 0):
        progression['streak_record'] = progression['streak_actuel']
    
    # Mise à jour de la date
    progression['derniere_connexion'] = aujourd_hui
    
    sauvegarder_progression(progression)
    
    return progression['streak_actuel'], nouveau_streak


def afficher_streak():
    """Affiche le streak actuel de l'utilisateur"""
    progression = charger_progression()
    streak = progression.get('streak_actuel', 0)
    record = progression.get('streak_record', 0)
    
    if streak > 0:
        print(f"\nSTREAK : {streak} jour{'s' if streak > 1 else ''} consecutif{'s' if streak > 1 else ''} !")
        if record > streak:
            print(f"Record : {record} jours")
        else:
            print("C'est votre record !")
    else:
        print("\nCommencez votre streak aujourd'hui !")


def ajouter_a_historique(theme, niveau, exercice, tentatives, reussi):
    """Ajoute une entrée dans l'historique des exercices"""
    progression = charger_progression()
    
    if 'historique' not in progression:
        progression['historique'] = []
    
    # Extraire l'énoncé ou la question
    if isinstance(exercice, dict):
        exercice_text = exercice.get('question', exercice.get('enonce', str(exercice)[:50]))
    else:
        exercice_text = str(exercice)[:50]
    
    entree = {
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'theme': theme,
        'niveau': niveau,
        'exercice': exercice_text,
        'tentatives': tentatives,
        'reussi': reussi
    }
    
    progression['historique'].append(entree)
    sauvegarder_progression(progression)


def afficher_historique():
    """Affiche l'historique des derniers exercices"""
    progression = charger_progression()
    historique = progression.get('historique', [])
    
    print("\n" + "="*60)
    print("HISTORIQUE DES EXERCICES")
    print("="*60)
    
    if not historique:
        print("\nAucun exercice dans l'historique.")
        return
    
    # Afficher les 10 derniers exercices
    derniers = historique[-10:]
    
    for i, entree in enumerate(reversed(derniers), 1):
        statut = "✓ REUSSI" if entree['reussi'] else "✗ PASSE"
        print(f"\n{i}. [{entree['date']}] - {statut}")
        print(f"   Theme: {entree['theme']} (Niveau {entree['niveau']})")
        print(f"   Exercice: {entree['exercice']}")
        print(f"   Tentatives: {entree['tentatives']}")


def afficher_statistiques_detaillees():
    """Affiche des statistiques détaillées basées sur l'historique"""
    progression = charger_progression()
    historique = progression.get('historique', [])
    
    print("\n" + "="*60)
    print("STATISTIQUES DETAILLEES")
    print("="*60)
    
    if not historique:
        print("\nAucune donnee disponible.")
        return
    
    # Statistiques globales
    total_exercices = len(historique)
    reussis = sum(1 for e in historique if e['reussi'])
    taux_reussite = (reussis / total_exercices) * 100
    tentatives_moyennes = sum(e['tentatives'] for e in historique) / total_exercices
    
    print(f"\nSTATISTIQUES GLOBALES")
    print(f"Total d'exercices: {total_exercices}")
    print(f"Reussis: {reussis} ({taux_reussite:.1f}%)")
    print(f"Tentatives moyennes: {tentatives_moyennes:.1f}")
    
    # Statistiques par thème
    stats_themes = {}
    for entree in historique:
        theme = entree['theme']
        if theme not in stats_themes:
            stats_themes[theme] = {'total': 0, 'reussis': 0, 'tentatives': 0}
        
        stats_themes[theme]['total'] += 1
        stats_themes[theme]['reussis'] += 1 if entree['reussi'] else 0
        stats_themes[theme]['tentatives'] += entree['tentatives']
    
    print(f"\n\nSTATISTIQUES PAR THEME")
    print("-" * 60)
    for theme, stats in stats_themes.items():
        taux = (stats['reussis'] / stats['total']) * 100
        moy_tent = stats['tentatives'] / stats['total']
        print(f"\n{theme}:")
        print(f"  Exercices: {stats['total']}")
        print(f"  Taux de reussite: {taux:.1f}%")
        print(f"  Tentatives moyennes: {moy_tent:.1f}")


# Fin du fichier    
