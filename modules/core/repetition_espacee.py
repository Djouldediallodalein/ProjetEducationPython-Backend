"""
Système de répétition espacée (Spaced Repetition System - SRS)
Basé sur l'algorithme SM-2 simplifié
"""

from datetime import datetime, timedelta
from modules.core.progression import charger_progression, sauvegarder_progression, obtenir_domaine_actif, obtenir_progression_domaine
import json


# Intervalles de révision en jours
INTERVALLES = {
    0: 0,      # Nouveau ou échec → immédiat
    1: 1,      # Premier succès → 1 jour
    2: 3,      # Deuxième succès → 3 jours  
    3: 7,      # Troisième succès → 1 semaine
    4: 14,     # Quatrième succès → 2 semaines
    5: 30,     # Cinquième succès → 1 mois
    6: 60,     # Sixième succès → 2 mois
    7: 120     # Septième succès et + → 4 mois
}


def initialiser_srs(domaine=None):
    """Initialise la structure SRS dans la progression
    
    Args:
        domaine: ID du domaine (None = domaine actif)
    """
    progression = charger_progression()
    
    # Obtenir le domaine
    if domaine is None:
        domaine = obtenir_domaine_actif()
    
    # S'assurer que la structure domaines existe
    if 'domaines' not in progression:
        progression['domaines'] = {}
    
    if domaine not in progression['domaines']:
        progression['domaines'][domaine] = {
            'niveau': 1,
            'xp_total': 0,
            'themes': {}
        }
    
    # Initialiser SRS pour ce domaine
    if 'srs' not in progression['domaines'][domaine]:
        progression['domaines'][domaine]['srs'] = {
            'exercices': {}  # Format: {identifiant: {niveau, prochaine_revision, historique}}
        }
        sauvegarder_progression(progression)


def obtenir_identifiant_exercice(theme, niveau, exercice):
    """Crée un identifiant unique pour un exercice"""
    if isinstance(exercice, dict):
        exercice_str = exercice.get('question', exercice.get('enonce', str(exercice)[:30]))
    else:
        exercice_str = str(exercice)[:30]
    
    return f"{theme}|{niveau}|{exercice_str}"


def enregistrer_revision(theme, niveau_ex, exercice, reussi, tentatives, domaine=None):
    """
    Enregistre une révision d'exercice et calcule la prochaine date
    
    Args:
        theme: Thème de l'exercice
        niveau_ex: Niveau de l'exercice (1-3)
        exercice: L'exercice lui-même
        reussi: Boolean, True si réussi
        tentatives: Nombre de tentatives utilisées
        domaine: ID du domaine (None = domaine actif)
    """
    # Obtenir le domaine
    if domaine is None:
        domaine = obtenir_domaine_actif()
    
    initialiser_srs(domaine)
    progression = charger_progression()
    
    identifiant = obtenir_identifiant_exercice(theme, niveau_ex, exercice)
    
    # Obtenir le SRS du domaine
    prog_domaine = progression['domaines'][domaine]
    
    # Récupérer ou créer l'entrée SRS
    if identifiant not in prog_domaine['srs']['exercices']:
        prog_domaine['srs']['exercices'][identifiant] = {
            'niveau_srs': 0,
            'theme': theme,
            'niveau_exercice': niveau_ex,
            'prochaine_revision': datetime.now().strftime('%Y-%m-%d'),
            'historique': []
        }
    
    entree = prog_domaine['srs']['exercices'][identifiant]
    
    # Mettre à jour le niveau SRS
    if reussi:
        # Ajuster selon le nombre de tentatives
        if tentatives == 1:
            # Parfait, on avance de 1 niveau
            entree['niveau_srs'] = min(entree['niveau_srs'] + 1, 7)
        elif tentatives <= 2:
            # Bien, on avance aussi
            entree['niveau_srs'] = min(entree['niveau_srs'] + 1, 7)
        else:
            # Réussi mais avec difficultés, on n'avance pas beaucoup
            entree['niveau_srs'] = max(1, entree['niveau_srs'])
    else:
        # Échec, on redescend
        entree['niveau_srs'] = max(0, entree['niveau_srs'] - 1)
    
    # Calculer la prochaine date de révision
    intervalle = INTERVALLES.get(entree['niveau_srs'], 120)
    prochaine_date = datetime.now() + timedelta(days=intervalle)
    entree['prochaine_revision'] = prochaine_date.strftime('%Y-%m-%d')
    
    # Ajouter à l'historique
    entree['historique'].append({
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'reussi': reussi,
        'tentatives': tentatives,
        'niveau_srs': entree['niveau_srs']
    })
    
    sauvegarder_progression(progression)


def obtenir_exercices_a_reviser(domaine=None):
    """
    Obtient la liste des exercices à réviser aujourd'hui
    
    Args:
        domaine: ID du domaine (None = domaine actif)
    
    Returns:
        list: Liste de tuples (theme, niveau_exercice)
    """
    # Obtenir le domaine
    if domaine is None:
        domaine = obtenir_domaine_actif()
    
    initialiser_srs(domaine)
    progression = charger_progression()
    
    # Obtenir le SRS du domaine
    prog_domaine = progression['domaines'][domaine]
    
    aujourd_hui = datetime.now().date()
    exercices_a_reviser = []
    
    for identifiant, entree in prog_domaine.get('srs', {}).get('exercices', {}).items():
        date_revision = datetime.strptime(entree['prochaine_revision'], '%Y-%m-%d').date()
        
        if date_revision <= aujourd_hui:
            exercices_a_reviser.append({
                'theme': entree['theme'],
                'niveau': entree['niveau_exercice'],
                'niveau_srs': entree['niveau_srs'],
                'prochaine_revision': entree['prochaine_revision']
            })
    
    # Trier par priorité (niveau SRS le plus faible d'abord)
    exercices_a_reviser.sort(key=lambda x: x['niveau_srs'])
    
    return exercices_a_reviser


def afficher_exercices_a_reviser():
    """Affiche les exercices à réviser"""
    exercices = obtenir_exercices_a_reviser()
    
    print("\n" + "="*60)
    print("EXERCICES A REVISER")
    print("="*60)
    
    if not exercices:
        print("\nAucun exercice a reviser aujourd'hui ! Bien joue !")
        return
    
    print(f"\nVous avez {len(exercices)} exercice(s) a reviser :")
    
    # Grouper par thème
    par_theme = {}
    for ex in exercices:
        theme = ex['theme']
        if theme not in par_theme:
            par_theme[theme] = []
        par_theme[theme].append(ex)
    
    for theme, liste in par_theme.items():
        print(f"\n{theme} : {len(liste)} exercice(s)")
        for ex in liste:
            niveau_desc = ['Debutant', 'Intermediaire', 'Avance'][ex['niveau'] - 1]
            print(f"  - Niveau {ex['niveau']} ({niveau_desc}) - SRS: {ex['niveau_srs']}/7")


def mode_revision(domaine=None):
    """Mode de révision dédié
    
    Args:
        domaine: ID du domaine (None = domaine actif)
    """
    from fonctions import generer_exercice, verifier_reponse, analyser_verdict
    from progression import mettre_a_jour_progression, ajouter_a_historique
    from xp_systeme import calculer_xp, ajouter_xp, afficher_details_xp_gagne
    
    # Obtenir le domaine
    if domaine is None:
        domaine = obtenir_domaine_actif()
    
    exercices = obtenir_exercices_a_reviser(domaine)
    
    if not exercices:
        print("\n" + "="*60)
        print("Aucun exercice a reviser aujourd'hui !")
        print("="*60)
        return
    
    print("\n" + "="*60)
    print(f"MODE REVISION - {len(exercices)} exercice(s)")
    print("="*60)
    
    for i, ex_info in enumerate(exercices, 1):
        print(f"\n\nExercice {i}/{len(exercices)}")
        print(f"Theme: {ex_info['theme']}")
        print(f"Niveau: {ex_info['niveau']}")
        print("-" * 60)
        
        theme = ex_info['theme']
        niveau = ex_info['niveau']
        
        # Générer un exercice pour ce thème/niveau
        exercice = generer_exercice(niveau, theme, domaine)
        
        # Gérer l'exercice (QCM ou Code)
        if isinstance(exercice, dict) and exercice.get('type') == 'qcm':
            # QCM
            print(exercice['question'])
            print()
            for j, choix in enumerate(exercice['choix'], 1):
                print(f"{j}. {choix}")
            
            tentatives = 0
            reussi = False
            
            while not reussi and tentatives < 3:
                tentatives += 1
                try:
                    reponse_num = int(input(f"\nTentative {tentatives} - Votre reponse (1-4) : "))
                    if 1 <= reponse_num <= len(exercice['choix']):
                        reponse_utilisateur = exercice['choix'][reponse_num - 1]
                        
                        if reponse_utilisateur == exercice['reponse']:
                            print("\nCORRECT !")
                            reussi = True
                        else:
                            print(f"\nINCORRECT. La bonne reponse : {exercice['reponse']}")
                    else:
                        print("Choix invalide.")
                        tentatives -= 1
                except ValueError:
                    print("Veuillez entrer un nombre.")
                    tentatives -= 1
        else:
            # Code
            enonce = exercice.get('enonce') if isinstance(exercice, dict) else exercice
            print(enonce)
            
            tentatives = 0
            reussi = False
            
            while not reussi and tentatives < 3:
                tentatives += 1
                solution = input(f"\nTentative {tentatives} - Votre solution Python :\n")
                
                verification = verifier_reponse(enonce, solution, domaine)
                print("\n" + verification)
                
                reussi = analyser_verdict(verification)
        
        # Enregistrer la révision
        enregistrer_revision(theme, niveau, exercice, reussi, tentatives, domaine)
        ajouter_a_historique(theme, niveau, exercice, tentatives, reussi, domaine)
        
        if reussi:
            # Calculer et ajouter l'XP (avec bonus de révision)
            progression = charger_progression()
            streak_actuel = progression.get('streak_actuel', 0)
            type_ex = exercice.get('type', 'code') if isinstance(exercice, dict) else 'code'
            
            xp_gagne = int(calculer_xp(type_ex, niveau, tentatives, streak_actuel) * 1.2)  # +20% en mode révision
            ajouter_xp(xp_gagne, domaine)
            print(f"\n+{xp_gagne} XP (avec bonus revision +20%)")
        
        mettre_a_jour_progression(theme, reussi, domaine)
        
        # Demander si continuer
        if i < len(exercices):
            continuer = input("\nContinuer les revisions ? (oui/non) : ")
            if continuer.lower() not in ['oui', 'o', 'yes', 'y']:
                print("\nRevisions interrompues. A bientot !")
                break
    
    print("\n" + "="*60)
    print("REVISIONS TERMINEES ! Bravo !")
    print("="*60)


def afficher_statistiques_srs(domaine=None):
    """Affiche des statistiques sur le système SRS
    
    Args:
        domaine: ID du domaine (None = domaine actif)
    """
    # Obtenir le domaine
    if domaine is None:
        domaine = obtenir_domaine_actif()
    
    initialiser_srs(domaine)
    progression = charger_progression()
    
    # Obtenir le SRS du domaine
    prog_domaine = progression['domaines'][domaine]
    
    print("\n" + "="*60)
    print("STATISTIQUES DE REPETITION ESPACEE")
    print("="*60)
    
    if not prog_domaine.get('srs', {}).get('exercices', {}):
        print("\nAucune donnee SRS disponible.")
        return
    
    # Compter par niveau SRS
    niveaux = {i: 0 for i in range(8)}
    for entree in prog_domaine['srs']['exercices'].values():
        niveaux[entree['niveau_srs']] += 1
    
    total = len(prog_domaine['srs']['exercices'])
    
    print(f"\nTotal d'exercices suivis: {total}")
    print("\nRepartition par maitrise:")
    
    labels = ['Nouveau', 'Debutant', 'Familier', 'Connu', 'Maitrise', 'Expert', 'Maitre', 'Legende']
    
    for niveau, count in niveaux.items():
        if count > 0:
            pct = (count / total) * 100
            barre = "█" * int(pct / 2)
            print(f"  Niveau {niveau} ({labels[niveau]}): {count} ({pct:.1f}%) {barre}")
    
    # Exercices à réviser
    a_reviser = obtenir_exercices_a_reviser(domaine)
    print(f"\nExercices a reviser aujourd'hui: {len(a_reviser)}")
