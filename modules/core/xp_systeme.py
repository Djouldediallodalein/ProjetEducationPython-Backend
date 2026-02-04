"""
Système de points d'expérience (XP) et de niveaux
"""

from modules.core.progression import charger_progression, sauvegarder_progression, obtenir_domaine_actif, obtenir_progression_domaine

# Configuration des points
POINTS_PAR_TYPE = {
    'qcm': 10,      # QCM = 10 points de base
    'code': 25      # Exercice de code = 25 points de base
}

POINTS_PAR_NIVEAU = {
    1: 1.0,   # Niveau 1 = x1
    2: 1.5,   # Niveau 2 = x1.5
    3: 2.0    # Niveau 3 = x2
}

# Seuils XP pour les niveaux
SEUILS_NIVEAU = {
    1: 0,
    2: 100,
    3: 250,
    4: 500,
    5: 850,
    6: 1300,
    7: 1900,
    8: 2600,
    9: 3400,
    10: 4300,
    11: 5300,
    12: 6400,
    13: 7600,
    14: 8900,
    15: 10300
}

# Multiplicateurs de streak
MULTIPLICATEURS_STREAK = {
    0: 1.0,
    1: 1.0,
    2: 1.1,    # 2 jours = +10%
    3: 1.15,   # 3 jours = +15%
    5: 1.25,   # 5 jours = +25%
    7: 1.5,    # 7 jours = +50%
    14: 2.0,   # 14 jours = +100%
    30: 3.0    # 30 jours = +200%
}


def calculer_xp(type_exercice, niveau_exercice, tentatives, streak_actuel):
    """
    Calcule les points XP gagnés pour un exercice
    
    Args:
        type_exercice: 'qcm' ou 'code'
        niveau_exercice: 1, 2 ou 3
        tentatives: nombre de tentatives utilisées
        streak_actuel: streak actuel de l'utilisateur
    
    Returns:
        int: Points XP gagnés
    """
    # Points de base selon le type
    points_base = POINTS_PAR_TYPE.get(type_exercice, 10)
    
    # Multiplicateur de niveau
    mult_niveau = POINTS_PAR_NIVEAU.get(niveau_exercice, 1.0)
    
    # Multiplicateur de streak
    mult_streak = 1.0
    for seuil in sorted(MULTIPLICATEURS_STREAK.keys(), reverse=True):
        if streak_actuel >= seuil:
            mult_streak = MULTIPLICATEURS_STREAK[seuil]
            break
    
    # Bonus première tentative
    bonus_tentatives = 1.0
    if tentatives == 1:
        bonus_tentatives = 1.5  # +50% si réussi du premier coup
    elif tentatives == 2:
        bonus_tentatives = 1.2  # +20% si réussi en 2 coups
    
    # Calcul final
    xp = int(points_base * mult_niveau * mult_streak * bonus_tentatives)
    
    return xp


def obtenir_multiplicateur_streak(streak):
    """Retourne le multiplicateur actif pour un streak donné"""
    mult = 1.0
    for seuil in sorted(MULTIPLICATEURS_STREAK.keys(), reverse=True):
        if streak >= seuil:
            mult = MULTIPLICATEURS_STREAK[seuil]
            break
    return mult


def ajouter_xp(xp_gagne, domaine=None):
    """
    Ajoute de l'XP à la progression de l'utilisateur
    Gère automatiquement les montées de niveau
    
    Args:
        xp_gagne: Points XP à ajouter
        domaine: ID du domaine (None = domaine actif)
    
    Returns:
        tuple: (niveau_avant, niveau_apres, niveau_monte)
    """
    progression = charger_progression()
    
    # Obtenir le domaine
    if domaine is None:
        domaine = obtenir_domaine_actif()
    
    # Obtenir la progression du domaine
    prog_domaine = obtenir_progression_domaine(domaine)
    
    # Initialiser l'XP si nécessaire
    if 'xp_total' not in prog_domaine:
        prog_domaine['xp_total'] = 0
    
    niveau_avant = prog_domaine['niveau']
    prog_domaine['xp_total'] += xp_gagne
    
    # Calculer le nouveau niveau
    nouveau_niveau = calculer_niveau(prog_domaine['xp_total'])
    niveau_monte = nouveau_niveau > niveau_avant
    
    if niveau_monte:
        prog_domaine['niveau'] = nouveau_niveau
    
    # Mettre à jour dans la structure principale (toujours, pas seulement si niveau monte)
    if 'domaines' not in progression:
        progression['domaines'] = {}
    progression['domaines'][domaine] = prog_domaine
    
    sauvegarder_progression(progression)
    
    return niveau_avant, nouveau_niveau, niveau_monte


def calculer_niveau(xp_total):
    """Calcule le niveau basé sur l'XP total"""
    niveau = 1
    for niv, seuil in sorted(SEUILS_NIVEAU.items()):
        if xp_total >= seuil:
            niveau = niv
        else:
            break
    return min(niveau, 15)  # Niveau max = 15


def xp_pour_prochain_niveau(xp_actuel):
    """Calcule l'XP nécessaire pour atteindre le prochain niveau"""
    niveau_actuel = calculer_niveau(xp_actuel)
    
    if niveau_actuel >= 15:
        return 0  # Niveau max atteint
    
    prochain_niveau = niveau_actuel + 1
    xp_requis = SEUILS_NIVEAU[prochain_niveau]
    xp_restant = xp_requis - xp_actuel
    
    return xp_restant


def afficher_info_xp(domaine=None):
    """Affiche les informations détaillées sur l'XP et le niveau
    
    Args:
        domaine: ID du domaine (None = domaine actif)
    """
    progression = charger_progression()
    
    # Obtenir le domaine
    if domaine is None:
        domaine = obtenir_domaine_actif()
    
    # Obtenir la progression du domaine
    prog_domaine = obtenir_progression_domaine(domaine)
    
    xp_total = prog_domaine.get('xp_total', 0)
    niveau = prog_domaine.get('niveau', 1)
    streak = progression.get('streak_actuel', 0)
    
    print("\n" + "="*60)
    print("SYSTEME D'EXPERIENCE (XP)")
    print("="*60)
    
    print(f"\nNiveau actuel: {niveau}")
    print(f"XP total: {xp_total}")
    
    if niveau < 15:
        xp_restant = xp_pour_prochain_niveau(xp_total)
        xp_actuel_niveau = xp_total - SEUILS_NIVEAU[niveau]
        xp_requis_niveau = SEUILS_NIVEAU[niveau + 1] - SEUILS_NIVEAU[niveau]
        progression_pct = (xp_actuel_niveau / xp_requis_niveau) * 100
        
        print(f"XP pour niveau {niveau + 1}: {xp_restant}")
        print(f"Progression: {xp_actuel_niveau}/{xp_requis_niveau} ({progression_pct:.1f}%)")
        
        # Barre de progression
        barre_longueur = 30
        barre_rempli = int((progression_pct / 100) * barre_longueur)
        barre = "█" * barre_rempli + "░" * (barre_longueur - barre_rempli)
        print(f"[{barre}]")
    else:
        print("\nNIVEAU MAXIMUM ATTEINT ! Vous etes un MAITRE !")
    
    # Afficher le multiplicateur de streak
    mult_streak = obtenir_multiplicateur_streak(streak)
    if mult_streak > 1.0:
        bonus_pct = (mult_streak - 1) * 100
        print(f"\nBONUS STREAK ACTIF: +{bonus_pct:.0f}% XP (Streak: {streak} jours)")
    
    # Afficher les paliers de streak
    print("\n\nPALIERS DE STREAK:")
    print("-" * 60)
    paliers_tries = sorted(MULTIPLICATEURS_STREAK.items())
    for jours, mult in paliers_tries:
        if jours > 1:  # Ignorer 0 et 1
            bonus = (mult - 1) * 100
            etat = "✓" if streak >= jours else "✗"
            print(f"{etat} {jours} jours: x{mult} (+{bonus:.0f}% XP)")


def afficher_details_xp_gagne(xp_gagne, type_exercice, niveau_exercice, tentatives, streak):
    """Affiche les détails du calcul d'XP"""
    points_base = POINTS_PAR_TYPE.get(type_exercice, 10)
    mult_niveau = POINTS_PAR_NIVEAU.get(niveau_exercice, 1.0)
    mult_streak = obtenir_multiplicateur_streak(streak)
    
    bonus_tentatives = 1.0
    if tentatives == 1:
        bonus_tentatives = 1.5
    elif tentatives == 2:
        bonus_tentatives = 1.2
    
    print(f"\n+{xp_gagne} XP GAGNES !")
    print(f"  Base ({type_exercice.upper()}): {points_base} XP")
    print(f"  Niveau {niveau_exercice}: x{mult_niveau}")
    
    if mult_streak > 1.0:
        print(f"  Streak ({streak} jours): x{mult_streak}")
    
    if bonus_tentatives > 1.0:
        bonus_pct = (bonus_tentatives - 1) * 100
        print(f"  Bonus tentatives: +{bonus_pct:.0f}%")
