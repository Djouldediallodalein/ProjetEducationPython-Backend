"""
Système de comparaison de progression entre domaines
Permet de visualiser les compétences à travers tous les domaines
"""

import json
from modules.core.progression import charger_progression, obtenir_progression_domaine
from modules.core.domaines import charger_domaines, obtenir_nom_domaine


def obtenir_progression_tous_domaines():
    """
    Obtient la progression pour tous les domaines
    
    Returns:
        dict: {domaine_id: progression_domaine}
    """
    progression = charger_progression()
    domaines_dict = charger_domaines()
    
    resultats = {}
    
    for domaine_id in domaines_dict.keys():
        prog_dom = obtenir_progression_domaine(domaine_id)
        resultats[domaine_id] = prog_dom
    
    return resultats


def calculer_score_competence(prog_domaine):
    """
    Calcule un score de compétence basé sur plusieurs métriques
    
    Returns:
        int: Score de 0 à 100
    """
    niveau = prog_domaine.get('niveau', 1)
    xp = prog_domaine.get('xp_total', 0)
    reussis = prog_domaine.get('exercices_reussis', 0)
    totaux = prog_domaine.get('exercices_totaux', 1)
    badges = len(prog_domaine.get('badges', []))
    
    # Calcul pondéré
    score_niveau = min((niveau / 15) * 40, 40)  # Max 40 points
    score_xp = min((xp / 5000) * 30, 30)  # Max 30 points
    score_taux = (reussis / totaux) * 20 if totaux > 0 else 0  # Max 20 points
    score_badges = min((badges / 15) * 10, 10)  # Max 10 points
    
    return int(score_niveau + score_xp + score_taux + score_badges)


def afficher_tableau_comparaison():
    """Affiche un tableau comparatif de tous les domaines"""
    progressions = obtenir_progression_tous_domaines()
    domaines_dict = charger_domaines()
    
    print("\n" + "="*90)
    print("📊 COMPARAISON DES DOMAINES")
    print("="*90)
    
    # En-têtes
    print(f"\n{'Domaine':<20} {'Niveau':<10} {'XP':<12} {'Taux':<12} {'Badges':<10} {'Score':<10}")
    print("-"*90)
    
    # Données pour chaque domaine
    domaines_avec_score = []
    
    for domaine_id, prog_dom in progressions.items():
        nom = obtenir_nom_domaine(domaine_id)
        niveau = prog_dom.get('niveau', 1)
        xp = prog_dom.get('xp_total', 0)
        reussis = prog_dom.get('exercices_reussis', 0)
        totaux = prog_dom.get('exercices_totaux', 0)
        taux = (reussis / totaux * 100) if totaux > 0 else 0
        badges = len(prog_dom.get('badges', []))
        score = calculer_score_competence(prog_dom)
        
        # Emoji indicateur de niveau
        if niveau >= 10:
            emoji = "🏆"
        elif niveau >= 7:
            emoji = "⭐"
        elif niveau >= 4:
            emoji = "📈"
        else:
            emoji = "🌱"
        
        domaines_avec_score.append({
            'id': domaine_id,
            'nom': nom,
            'niveau': niveau,
            'xp': xp,
            'taux': taux,
            'badges': badges,
            'score': score,
            'emoji': emoji
        })
    
    # Trier par score décroissant
    domaines_avec_score.sort(key=lambda x: x['score'], reverse=True)
    
    # Afficher
    for i, dom in enumerate(domaines_avec_score, 1):
        rank_emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        
        print(f"{rank_emoji} {dom['emoji']} {dom['nom']:<15} "
              f"Niv {dom['niveau']:<5} "
              f"{dom['xp']:<10} XP "
              f"{dom['taux']:<8.1f}% "
              f"{dom['badges']:<8} "
              f"{dom['score']}/100")
    
    print("\n" + "="*90)
    
    # Suggestions
    print("\n💡 SUGGESTIONS:")
    
    # Domaine le plus faible
    domaine_faible = domaines_avec_score[-1]
    if domaine_faible['score'] < 30:
        print(f"   • Développer {domaine_faible['nom']} (score: {domaine_faible['score']}/100)")
    
    # Domaine le plus fort
    domaine_fort = domaines_avec_score[0]
    print(f"   • Continuer l'excellence en {domaine_fort['nom']} !")
    
    # Domaines moyens
    domaines_moyens = [d for d in domaines_avec_score if 30 <= d['score'] < 70]
    if domaines_moyens:
        print(f"   • Renforcer: {', '.join(d['nom'] for d in domaines_moyens[:3])}")
    
    print()


def afficher_graphique_radar_ascii():
    """Affiche un graphique radar ASCII des compétences"""
    progressions = obtenir_progression_tous_domaines()
    
    print("\n" + "="*70)
    print("🎯 PROFIL DE COMPÉTENCES (Graphique Radar)")
    print("="*70)
    
    # Calculer les scores
    domaines_scores = []
    for domaine_id, prog_dom in progressions.items():
        nom = obtenir_nom_domaine(domaine_id)
        score = calculer_score_competence(prog_dom)
        domaines_scores.append((nom, score))
    
    # Limiter à 8 domaines principaux
    domaines_scores = domaines_scores[:8]
    
    # Afficher les barres
    print()
    for nom, score in domaines_scores:
        barre_longueur = 40
        barre_rempli = int((score / 100) * barre_longueur)
        barre = "█" * barre_rempli + "░" * (barre_longueur - barre_rempli)
        
        print(f"{nom:<20} [{barre}] {score}/100")
    
    print("\n" + "="*70)


def obtenir_domaine_le_plus_fort():
    """Retourne le domaine avec le meilleur score"""
    progressions = obtenir_progression_tous_domaines()
    
    meilleur_domaine = None
    meilleur_score = -1
    
    for domaine_id, prog_dom in progressions.items():
        score = calculer_score_competence(prog_dom)
        if score > meilleur_score:
            meilleur_score = score
            meilleur_domaine = domaine_id
    
    return meilleur_domaine, meilleur_score


def obtenir_domaine_le_plus_faible():
    """Retourne le domaine avec le score le plus faible"""
    progressions = obtenir_progression_tous_domaines()
    
    pire_domaine = None
    pire_score = 101
    
    for domaine_id, prog_dom in progressions.items():
        score = calculer_score_competence(prog_dom)
        if score < pire_score:
            pire_score = score
            pire_domaine = domaine_id
    
    return pire_domaine, pire_score


def suggerer_domaine_a_travailler():
    """Suggère un domaine à travailler en priorité"""
    domaine_faible, score_faible = obtenir_domaine_le_plus_faible()
    nom = obtenir_nom_domaine(domaine_faible)
    
    print("\n" + "="*70)
    print("💡 SUGGESTION DE TRAVAIL")
    print("="*70)
    print(f"\nDomaine à renforcer: {nom}")
    print(f"Score actuel: {score_faible}/100")
    
    if score_faible < 20:
        print("Recommandation: Commencer par des exercices de niveau 1")
    elif score_faible < 50:
        print("Recommandation: Pratiquer régulièrement pour atteindre niveau 5")
    else:
        print("Recommandation: Consolider avec des exercices de niveau 2-3")
    
    print("="*70)


def calculer_score_global():
    """Calcule un score global sur tous les domaines"""
    progressions = obtenir_progression_tous_domaines()
    
    scores = []
    for prog_dom in progressions.values():
        scores.append(calculer_score_competence(prog_dom))
    
    if not scores:
        return 0
    
    return sum(scores) / len(scores)


def afficher_resume_global():
    """Affiche un résumé global des compétences"""
    score_global = calculer_score_global()
    domaine_fort, score_fort = obtenir_domaine_le_plus_fort()
    domaine_faible, score_faible = obtenir_domaine_le_plus_faible()
    
    print("\n" + "="*70)
    print("🌟 RÉSUMÉ GLOBAL")
    print("="*70)
    
    print(f"\nScore global: {score_global:.1f}/100")
    
    # Barre de progression globale
    barre_longueur = 40
    barre_rempli = int((score_global / 100) * barre_longueur)
    barre = "█" * barre_rempli + "░" * (barre_longueur - barre_rempli)
    print(f"[{barre}]")
    
    # Niveau global
    if score_global >= 80:
        niveau_desc = "🏆 Expert Multi-Domaines"
    elif score_global >= 60:
        niveau_desc = "⭐ Compétent Multi-Domaines"
    elif score_global >= 40:
        niveau_desc = "📈 En Progression"
    else:
        niveau_desc = "🌱 Débutant"
    
    print(f"\nNiveau: {niveau_desc}")
    
    print(f"\nDomaine le plus fort: {obtenir_nom_domaine(domaine_fort)} ({score_fort}/100)")
    print(f"Domaine à améliorer: {obtenir_nom_domaine(domaine_faible)} ({score_faible}/100)")
    
    # Équilibre
    ecart = score_fort - score_faible
    if ecart < 20:
        print("\n✅ Progression équilibrée entre les domaines !")
    elif ecart < 40:
        print("\n⚖️  Développement assez équilibré")
    else:
        print("\n⚠️  Grande différence entre domaines - pensez à diversifier")
    
    print("\n" + "="*70)


def comparer_deux_domaines(domaine1, domaine2):
    """Compare directement deux domaines"""
    prog1 = obtenir_progression_domaine(domaine1)
    prog2 = obtenir_progression_domaine(domaine2)
    
    nom1 = obtenir_nom_domaine(domaine1)
    nom2 = obtenir_nom_domaine(domaine2)
    
    score1 = calculer_score_competence(prog1)
    score2 = calculer_score_competence(prog2)
    
    print("\n" + "="*70)
    print(f"⚖️  COMPARAISON: {nom1} vs {nom2}")
    print("="*70)
    
    # Tableau comparatif
    print(f"\n{'Métrique':<20} {nom1:<20} {nom2:<20}")
    print("-"*70)
    
    print(f"{'Niveau':<20} {prog1.get('niveau', 1):<20} {prog2.get('niveau', 1):<20}")
    print(f"{'XP Total':<20} {prog1.get('xp_total', 0):<20} {prog2.get('xp_total', 0):<20}")
    
    taux1 = (prog1.get('exercices_reussis', 0) / prog1.get('exercices_totaux', 1) * 100) if prog1.get('exercices_totaux', 0) > 0 else 0
    taux2 = (prog2.get('exercices_reussis', 0) / prog2.get('exercices_totaux', 1) * 100) if prog2.get('exercices_totaux', 0) > 0 else 0
    print(f"{'Taux de réussite':<20} {taux1:.1f}%{'':<15} {taux2:.1f}%{'':<15}")
    
    print(f"{'Badges':<20} {len(prog1.get('badges', [])):<20} {len(prog2.get('badges', [])):<20}")
    print(f"{'Score':<20} {score1}/100{'':<12} {score2}/100{'':<12}")
    
    print("\n" + "-"*70)
    
    if score1 > score2:
        print(f"🏆 {nom1} est plus avancé (+{score1-score2} points)")
    elif score2 > score1:
        print(f"🏆 {nom2} est plus avancé (+{score2-score1} points)")
    else:
        print("⚖️  Niveau équivalent !")
    
    print("\n" + "="*70)


def menu_comparaison():
    """Menu de comparaison des domaines"""
    while True:
        print("\n" + "="*70)
        print("📊 COMPARAISON DES DOMAINES")
        print("="*70)
        print("\n1. Tableau comparatif complet")
        print("2. Graphique de compétences")
        print("3. Résumé global")
        print("4. Suggestion de domaine à travailler")
        print("5. Comparer deux domaines spécifiques")
        print("0. Retour")
        
        try:
            choix = int(input("\nVotre choix : "))
        except ValueError:
            print("Erreur: Entrez un numéro valide.")
            continue
        
        if choix == 0:
            break
        
        elif choix == 1:
            afficher_tableau_comparaison()
        
        elif choix == 2:
            afficher_graphique_radar_ascii()
        
        elif choix == 3:
            afficher_resume_global()
        
        elif choix == 4:
            suggerer_domaine_a_travailler()
        
        elif choix == 5:
            domaines_dict = charger_domaines()
            domaines_list = list(domaines_dict.keys())
            
            print("\n\nDomaines disponibles:")
            for i, dom_id in enumerate(domaines_list, 1):
                print(f"{i}. {obtenir_nom_domaine(dom_id)}")
            
            try:
                choix1 = int(input("\nPremier domaine (numéro) : "))
                choix2 = int(input("Deuxième domaine (numéro) : "))
                
                if 1 <= choix1 <= len(domaines_list) and 1 <= choix2 <= len(domaines_list):
                    dom1 = domaines_list[choix1 - 1]
                    dom2 = domaines_list[choix2 - 1]
                    comparer_deux_domaines(dom1, dom2)
                else:
                    print("Numéros invalides.")
            except ValueError:
                print("Erreur: Entrez des numéros valides.")
        
        else:
            print("Choix invalide.")
