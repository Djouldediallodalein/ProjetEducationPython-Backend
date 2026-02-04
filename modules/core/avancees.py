## Fichier pour les fonctionnalités avancées : badges, révisions, analyse

import json
from datetime import datetime, timedelta
from modules.core.progression import charger_progression, sauvegarder_progression, obtenir_domaine_actif, obtenir_progression_domaine


# Définition des badges disponibles
BADGES = {
    'premier_pas': {'nom': 'Premier Pas', 'desc': 'Réussir votre premier exercice', 'condition': lambda p: p.get('exercices_reussis', 0) >= 1},
    'debutant': {'nom': 'Débutant', 'desc': 'Réussir 5 exercices', 'condition': lambda p: p.get('exercices_reussis', 0) >= 5},
    'apprenti': {'nom': 'Apprenti', 'desc': 'Réussir 10 exercices', 'condition': lambda p: p.get('exercices_reussis', 0) >= 10},
    'competent': {'nom': 'Compétent', 'desc': 'Réussir 25 exercices', 'condition': lambda p: p.get('exercices_reussis', 0) >= 25},
    'expert': {'nom': 'Expert', 'desc': 'Réussir 50 exercices', 'condition': lambda p: p.get('exercices_reussis', 0) >= 50},
    'maitre': {'nom': 'Maître', 'desc': 'Réussir 100 exercices', 'condition': lambda p: p.get('exercices_reussis', 0) >= 100},
    'perfectionniste': {'nom': 'Perfectionniste', 'desc': 'Atteindre 90% de taux de réussite avec au moins 20 exercices', 'condition': lambda p: p.get('exercices_totaux', 0) >= 20 and (p.get('exercices_reussis', 0) / max(p.get('exercices_totaux', 1), 1)) >= 0.9},
    'explorateur': {'nom': 'Explorateur', 'desc': 'Essayer 5 thèmes différents', 'condition': lambda p: len(p.get('themes', {})) >= 5},
    'specialiste': {'nom': 'Spécialiste', 'desc': 'Réussir 10 exercices dans un seul thème', 'condition': lambda p: any(stats.get('reussis', 0) >= 10 for stats in p.get('themes', {}).values())},
}


def verifier_nouveaux_badges():
    """Vérifie et attribue les nouveaux badges gagnés"""
    progression = charger_progression()
    domaine_actif = obtenir_domaine_actif()
    prog_domaine = obtenir_progression_domaine(domaine_actif)
    
    if 'badges' not in prog_domaine:
        prog_domaine['badges'] = []
    
    nouveaux_badges = []
    
    for badge_id, badge_info in BADGES.items():
        if badge_id not in prog_domaine['badges']:
            if badge_info['condition'](prog_domaine):
                prog_domaine['badges'].append(badge_id)
                nouveaux_badges.append(badge_info['nom'])
    
    if nouveaux_badges:
        progression['domaines'][domaine_actif] = prog_domaine
        sauvegarder_progression(progression)
    
    return nouveaux_badges


def afficher_badges():
    """Affiche tous les badges de l'utilisateur"""
    progression = charger_progression()
    domaine_actif = obtenir_domaine_actif()
    prog_domaine = obtenir_progression_domaine(domaine_actif)
    badges_obtenus = prog_domaine.get('badges', [])
    
    print("\nVOS BADGES")
    print("="*60)
    
    if badges_obtenus:
        for badge_id in badges_obtenus:
            if badge_id in BADGES:
                badge = BADGES[badge_id]
                print(f"  {badge['nom']} - {badge['desc']}")
    else:
        print("Aucun badge obtenu pour le moment.")
    
    print("\nBADGES DISPONIBLES")
    print("-"*60)
    for badge_id, badge in BADGES.items():
        if badge_id not in badges_obtenus:
            print(f"  [ ] {badge['nom']} - {badge['desc']}")


def analyser_faiblesses():
    """Analyse les thèmes où l'utilisateur a le plus de difficultés"""
    progression = charger_progression()
    domaine_actif = obtenir_domaine_actif()
    prog_domaine = obtenir_progression_domaine(domaine_actif)
    themes = prog_domaine.get('themes', {})
    
    if not themes:
        return None
    
    faiblesses = []
    for theme, stats in themes.items():
        if stats.get('totaux', 0) >= 3:
            taux = stats.get('reussis', 0) / max(stats.get('totaux', 1), 1)
            if taux < 0.5:
                faiblesses.append((theme, taux))
    
    faiblesses.sort(key=lambda x: x[1])
    return faiblesses[:3] if faiblesses else None


def suggerer_theme_revision():
    """Suggère un thème à réviser basé sur les faiblesses"""
    faiblesses = analyser_faiblesses()
    
    if faiblesses:
        return faiblesses[0][0]
    
    progression = charger_progression()
    domaine_actif = obtenir_domaine_actif()
    prog_domaine = obtenir_progression_domaine(domaine_actif)
    themes = prog_domaine.get('themes', {})
    
    if themes:
        theme_moins_pratique = min(themes.items(), key=lambda x: x[1].get('totaux', 0))
        return theme_moins_pratique[0]
    
    return None
    
    return None
