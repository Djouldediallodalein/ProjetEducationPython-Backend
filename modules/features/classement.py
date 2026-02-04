"""
Système de classement et compétition
Permet de se mesurer globalement et par domaine
"""

import json
import os
from datetime import datetime
from modules.core.progression import charger_progression, obtenir_progression_domaine
from modules.core.domaines import charger_domaines, obtenir_nom_domaine


FICHIER_CLASSEMENT = 'classement.json'


def calculer_points_competence_domaine(prog_domaine):
    """Calcule les points de compétence pour un domaine"""
    niveau = prog_domaine.get('niveau', 1)
    xp = prog_domaine.get('xp_total', 0)
    reussis = prog_domaine.get('exercices_reussis', 0)
    totaux = prog_domaine.get('exercices_totaux', 1)
    badges = len(prog_domaine.get('badges', []))
    
    # Formule de calcul des points
    points = (niveau * 100) + (xp * 0.5) + (reussis * 10) + (badges * 50)
    
    # Bonus pour taux de réussite élevé
    if totaux > 0:
        taux = reussis / totaux
        if taux >= 0.9:
            points *= 1.2
        elif taux >= 0.75:
            points *= 1.1
    
    return int(points)


def calculer_points_globaux():
    """Calcule les points globaux sur tous les domaines"""
    progression = charger_progression()
    domaines_dict = charger_domaines()
    
    points_total = 0
    
    for domaine_id in domaines_dict.keys():
        prog_dom = obtenir_progression_domaine(domaine_id)
        points_total += calculer_points_competence_domaine(prog_dom)
    
    return points_total


def obtenir_titre_selon_points(points):
    """Retourne un titre selon les points"""
    if points >= 50000:
        return "🏆 Légende"
    elif points >= 30000:
        return "⭐ Maître"
    elif points >= 15000:
        return "💎 Expert"
    elif points >= 8000:
        return "🎯 Avancé"
    elif points >= 4000:
        return "📈 Intermédiaire"
    elif points >= 1000:
        return "🌱 Apprenti"
    else:
        return "🥚 Débutant"


def afficher_classement_domaine(domaine):
    """Affiche le classement pour un domaine spécifique"""
    prog_domaine = obtenir_progression_domaine(domaine)
    points = calculer_points_competence_domaine(prog_domaine)
    nom_domaine = obtenir_nom_domaine(domaine)
    
    print("\n" + "="*70)
    print(f"🏅 CLASSEMENT - {nom_domaine}")
    print("="*70)
    
    print(f"\nVos points: {points:,}")
    print(f"Titre: {obtenir_titre_selon_points(points)}")
    
    # Métriques détaillées
    print("\n\nDétail des points:")
    print("-"*70)
    
    niveau = prog_domaine.get('niveau', 1)
    xp = prog_domaine.get('xp_total', 0)
    reussis = prog_domaine.get('exercices_reussis', 0)
    badges = len(prog_domaine.get('badges', []))
    
    print(f"Niveau {niveau}: {niveau * 100:,} points")
    print(f"XP ({xp}): {int(xp * 0.5):,} points")
    print(f"Exercices réussis ({reussis}): {reussis * 10:,} points")
    print(f"Badges ({badges}): {badges * 50:,} points")
    
    # Prochain titre
    print("\n\nProchain objectif:")
    print("-"*70)
    
    titres_seuils = [
        (50000, "🏆 Légende"),
        (30000, "⭐ Maître"),
        (15000, "💎 Expert"),
        (8000, "🎯 Avancé"),
        (4000, "📈 Intermédiaire"),
        (1000, "🌱 Apprenti"),
        (0, "🥚 Débutant")
    ]
    
    for seuil, titre in titres_seuils:
        if points < seuil:
            restant = seuil - points
            print(f"{titre}: {restant:,} points restants")
            break
    
    print("\n" + "="*70)


def afficher_classement_global():
    """Affiche le classement global tous domaines confondus"""
    points_total = calculer_points_globaux()
    progression = charger_progression()
    
    print("\n" + "="*70)
    print("🌟 CLASSEMENT GLOBAL")
    print("="*70)
    
    print(f"\nPoints totaux: {points_total:,}")
    print(f"Titre global: {obtenir_titre_selon_points(points_total)}")
    
    # Statistiques globales
    print("\n\nStatistiques globales:")
    print("-"*70)
    
    total_exercices = 0
    total_reussis = 0
    total_badges = 0
    niveaux_sum = 0
    domaines_count = 0
    
    domaines_dict = charger_domaines()
    for domaine_id in domaines_dict.keys():
        prog_dom = obtenir_progression_domaine(domaine_id)
        total_exercices += prog_dom.get('exercices_totaux', 0)
        total_reussis += prog_dom.get('exercices_reussis', 0)
        total_badges += len(prog_dom.get('badges', []))
        niveaux_sum += prog_dom.get('niveau', 1)
        domaines_count += 1
    
    niveau_moyen = niveaux_sum / domaines_count if domaines_count > 0 else 0
    taux_global = (total_reussis / total_exercices * 100) if total_exercices > 0 else 0
    
    print(f"Exercices réussis: {total_reussis:,}/{total_exercices:,}")
    print(f"Taux de réussite global: {taux_global:.1f}%")
    print(f"Niveau moyen: {niveau_moyen:.1f}")
    print(f"Badges totaux: {total_badges}")
    print(f"Streak actuel: {progression.get('streak_actuel', 0)} jours")
    
    # Classement par domaine
    print("\n\nPoints par domaine:")
    print("-"*70)
    
    domaines_points = []
    for domaine_id in domaines_dict.keys():
        prog_dom = obtenir_progression_domaine(domaine_id)
        points_dom = calculer_points_competence_domaine(prog_dom)
        domaines_points.append((obtenir_nom_domaine(domaine_id), points_dom))
    
    domaines_points.sort(key=lambda x: x[1], reverse=True)
    
    for i, (nom, points) in enumerate(domaines_points[:5], 1):
        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        print(f"{emoji} {nom}: {points:,} points")
    
    print("\n" + "="*70)


def obtenir_badges_prestige():
    """Retourne les badges de prestige obtenus"""
    points_total = calculer_points_globaux()
    progression = charger_progression()
    
    badges_prestige = []
    
    # Badge de points
    if points_total >= 50000:
        badges_prestige.append("🏆 Légende Absolue")
    elif points_total >= 30000:
        badges_prestige.append("⭐ Grand Maître")
    elif points_total >= 15000:
        badges_prestige.append("💎 Expert Confirmé")
    
    # Badge de streak
    streak = progression.get('streak_actuel', 0)
    if streak >= 100:
        badges_prestige.append("🔥 Centenaire")
    elif streak >= 30:
        badges_prestige.append("🔥 Marathonien")
    elif streak >= 7:
        badges_prestige.append("🔥 Assidu")
    
    # Badge multi-domaines
    domaines_dict = charger_domaines()
    domaines_niv5_plus = 0
    for domaine_id in domaines_dict.keys():
        prog_dom = obtenir_progression_domaine(domaine_id)
        if prog_dom.get('niveau', 1) >= 5:
            domaines_niv5_plus += 1
    
    if domaines_niv5_plus >= 5:
        badges_prestige.append("🌍 Polyglotte")
    elif domaines_niv5_plus >= 3:
        badges_prestige.append("🌍 Multi-Compétent")
    
    # Badge de perfection
    total_exercices = 0
    total_reussis = 0
    for domaine_id in domaines_dict.keys():
        prog_dom = obtenir_progression_domaine(domaine_id)
        total_exercices += prog_dom.get('exercices_totaux', 0)
        total_reussis += prog_dom.get('exercices_reussis', 0)
    
    if total_exercices > 0:
        taux = total_reussis / total_exercices
        if taux >= 0.95 and total_exercices >= 100:
            badges_prestige.append("💯 Perfectionniste")
        elif taux >= 0.90 and total_exercices >= 50:
            badges_prestige.append("✨ Excellence")
    
    return badges_prestige


def afficher_badges_prestige():
    """Affiche les badges de prestige"""
    badges = obtenir_badges_prestige()
    
    print("\n" + "="*70)
    print("🎖️  BADGES DE PRESTIGE")
    print("="*70)
    
    if not badges:
        print("\nAucun badge de prestige pour le moment.")
        print("Continuez à progresser pour en débloquer !")
    else:
        print(f"\nVous avez {len(badges)} badge(s) de prestige:")
        print()
        for badge in badges:
            print(f"  {badge}")
    
    print("\n\nBadges disponibles:")
    print("-"*70)
    print("🏆 Légende Absolue - 50,000+ points")
    print("⭐ Grand Maître - 30,000+ points")
    print("💎 Expert Confirmé - 15,000+ points")
    print("🔥 Centenaire - 100 jours de streak")
    print("🔥 Marathonien - 30 jours de streak")
    print("🔥 Assidu - 7 jours de streak")
    print("🌍 Polyglotte - Niveau 5+ dans 5 domaines")
    print("🌍 Multi-Compétent - Niveau 5+ dans 3 domaines")
    print("💯 Perfectionniste - 95%+ de réussite (100+ exercices)")
    print("✨ Excellence - 90%+ de réussite (50+ exercices)")
    
    print("\n" + "="*70)


def afficher_progression_vers_titre():
    """Affiche la progression vers le prochain titre"""
    points_total = calculer_points_globaux()
    
    print("\n" + "="*70)
    print("🎯 PROGRESSION VERS LE PROCHAIN TITRE")
    print("="*70)
    
    print(f"\nPoints actuels: {points_total:,}")
    print(f"Titre actuel: {obtenir_titre_selon_points(points_total)}")
    
    # Calculer le prochain seuil
    titres_seuils = [
        (50000, "🏆 Légende"),
        (30000, "⭐ Maître"),
        (15000, "💎 Expert"),
        (8000, "🎯 Avancé"),
        (4000, "📈 Intermédiaire"),
        (1000, "🌱 Apprenti"),
        (0, "🥚 Débutant")
    ]
    
    prochain_seuil = None
    prochain_titre = None
    
    for seuil, titre in titres_seuils:
        if points_total < seuil:
            prochain_seuil = seuil
            prochain_titre = titre
    
    if prochain_seuil:
        restant = prochain_seuil - points_total
        progression_pct = (points_total / prochain_seuil) * 100
        
        print(f"\nProchain titre: {prochain_titre}")
        print(f"Points restants: {restant:,}")
        print(f"Progression: {progression_pct:.1f}%")
        
        # Barre de progression
        barre_longueur = 40
        barre_rempli = int((progression_pct / 100) * barre_longueur)
        barre = "█" * barre_rempli + "░" * (barre_longueur - barre_rempli)
        print(f"[{barre}]")
        
        # Estimation
        print("\n💡 Pour atteindre ce titre:")
        exercices_necessaires = int(restant / 10)
        print(f"   • ~{exercices_necessaires} exercices réussis")
        print(f"   • ou ~{int(restant / 50)} badges supplémentaires")
        print(f"   • ou atteindre niveau +{int(restant / 100)} dans un domaine")
    else:
        print("\n🏆 Vous avez atteint le titre maximum !")
    
    print("\n" + "="*70)


def menu_classement():
    """Menu du système de classement"""
    while True:
        print("\n" + "="*70)
        print("🏅 CLASSEMENT & COMPÉTITION")
        print("="*70)
        print("\n1. Classement global")
        print("2. Classement par domaine")
        print("3. Badges de prestige")
        print("4. Progression vers prochain titre")
        print("0. Retour")
        
        try:
            choix = int(input("\nVotre choix : "))
        except ValueError:
            print("Erreur: Entrez un numéro valide.")
            continue
        
        if choix == 0:
            break
        
        elif choix == 1:
            afficher_classement_global()
        
        elif choix == 2:
            domaines_dict = charger_domaines()
            print("\n\nChoisir un domaine:")
            for i, (dom_id, dom_info) in enumerate(domaines_dict.items(), 1):
                print(f"{i}. {dom_info['nom']}")
            
            try:
                choix_dom = int(input("\nDomaine (numéro) : "))
                domaines_list = list(domaines_dict.keys())
                if 1 <= choix_dom <= len(domaines_list):
                    afficher_classement_domaine(domaines_list[choix_dom - 1])
                else:
                    print("Numéro invalide.")
            except ValueError:
                print("Erreur: Entrez un numéro valide.")
        
        elif choix == 3:
            afficher_badges_prestige()
        
        elif choix == 4:
            afficher_progression_vers_titre()
        
        else:
            print("Choix invalide.")
