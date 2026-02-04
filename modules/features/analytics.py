"""
Analytics avancées
Graphiques, statistiques et analyses détaillées de la progression
"""

import json
from datetime import datetime, timedelta
from modules.core.progression import charger_progression, obtenir_progression_domaine
from modules.core.domaines import charger_domaines, obtenir_nom_domaine


def calculer_temps_moyen_par_exercice():
    """Calcule le temps moyen estimé par exercice (basé sur historique)"""
    # Estimation basique car on ne track pas encore le temps réel
    progression = charger_progression()
    domaines_dict = charger_domaines()
    
    total_exercices = 0
    for dom_id in domaines_dict.keys():
        prog_dom = obtenir_progression_domaine(dom_id)
        total_exercices += prog_dom.get('exercices_totaux', 0)
    
    # Estimation: 5 min par exercice niveau 1, 10 min niveau 2, 15 min niveau 3
    temps_estime = total_exercices * 8  # Moyenne de 8 minutes
    
    return temps_estime


def generer_graphique_progression_ascii(domaine):
    """Génère un graphique ASCII de la progression"""
    prog_dom = obtenir_progression_domaine(domaine)
    nom_domaine = obtenir_nom_domaine(domaine)
    historique = prog_dom.get('historique', [])
    
    if not historique:
        print("\nPas assez de données pour générer un graphique.")
        return
    
    # Prendre les 30 derniers exercices
    historique_recent = historique[-30:]
    
    print("\n" + "="*70)
    print(f"📈 GRAPHIQUE DE PROGRESSION - {nom_domaine}")
    print("="*70)
    print("\nTaux de réussite sur les 30 derniers exercices:\n")
    
    # Calculer le taux de réussite par tranche de 5
    tranches = []
    for i in range(0, len(historique_recent), 5):
        tranche = historique_recent[i:i+5]
        reussis = sum(1 for e in tranche if e.get('reussi', False))
        taux = (reussis / len(tranche)) * 100 if tranche else 0
        tranches.append(taux)
    
    # Afficher le graphique
    max_hauteur = 10
    for hauteur in range(max_hauteur, 0, -1):
        ligne = ""
        for taux in tranches:
            if (taux / 100 * max_hauteur) >= hauteur:
                ligne += " ██"
            else:
                ligne += "   "
        
        seuil = hauteur * 10
        print(f"{seuil:3d}%|{ligne}")
    
    print("    " + "─" * (len(tranches) * 3))
    print("    " + "".join([f" {i+1:2d}" for i in range(len(tranches))]))
    print("\n    (Tranches de 5 exercices)")
    print("="*70)


def afficher_heatmap_activite():
    """Affiche une heatmap de l'activité (style GitHub)"""
    progression = charger_progression()
    domaines_dict = charger_domaines()
    
    # Collecter toutes les dates d'historique
    dates_activite = {}
    
    for dom_id in domaines_dict.keys():
        prog_dom = obtenir_progression_domaine(dom_id)
        for entree in prog_dom.get('historique', []):
            date = entree.get('date', '').split()[0]  # Garder seulement la date
            if date:
                dates_activite[date] = dates_activite.get(date, 0) + 1
    
    print("\n" + "="*70)
    print("🔥 HEATMAP D'ACTIVITÉ (7 dernières semaines)")
    print("="*70)
    print()
    
    # Générer les 49 derniers jours (7 semaines)
    aujourd_hui = datetime.now().date()
    jours = []
    
    for i in range(48, -1, -1):
        date = aujourd_hui - timedelta(days=i)
        jours.append(date)
    
    # Afficher par semaine
    semaines = [jours[i:i+7] for i in range(0, len(jours), 7)]
    
    jours_noms = ['L', 'M', 'M', 'J', 'V', 'S', 'D']
    
    for idx, jour_nom in enumerate(jours_noms):
        ligne = f"{jour_nom} "
        for semaine in semaines:
            if idx < len(semaine):
                date_str = semaine[idx].strftime('%Y-%m-%d')
                count = dates_activite.get(date_str, 0)
                
                if count == 0:
                    ligne += "░"
                elif count <= 2:
                    ligne += "▒"
                elif count <= 5:
                    ligne += "▓"
                else:
                    ligne += "█"
                ligne += " "
            else:
                ligne += "  "
        print(ligne)
    
    print("\n  ░ Aucun  ▒ Peu  ▓ Moyen  █ Beaucoup")
    print("="*70)


def calculer_statistiques_avancees():
    """Calcule des statistiques avancées"""
    progression = charger_progression()
    domaines_dict = charger_domaines()
    
    stats = {
        'total_exercices': 0,
        'total_reussis': 0,
        'total_xp': 0,
        'niveau_moyen': 0,
        'meilleur_domaine': None,
        'meilleur_score': 0,
        'domaines_actifs': 0,
        'jours_actifs': set(),
        'meilleure_serie': 0
    }
    
    niveaux_sum = 0
    
    for dom_id in domaines_dict.keys():
        prog_dom = obtenir_progression_domaine(dom_id)
        
        exercices_totaux = prog_dom.get('exercices_totaux', 0)
        exercices_reussis = prog_dom.get('exercices_reussis', 0)
        
        stats['total_exercices'] += exercices_totaux
        stats['total_reussis'] += exercices_reussis
        stats['total_xp'] += prog_dom.get('xp_total', 0)
        niveaux_sum += prog_dom.get('niveau', 1)
        
        if exercices_totaux > 0:
            stats['domaines_actifs'] += 1
            taux = exercices_reussis / exercices_totaux
            if taux > stats['meilleur_score']:
                stats['meilleur_score'] = taux
                stats['meilleur_domaine'] = obtenir_nom_domaine(dom_id)
        
        # Collecter les jours actifs
        for entree in prog_dom.get('historique', []):
            date = entree.get('date', '').split()[0]
            if date:
                stats['jours_actifs'].add(date)
    
    stats['niveau_moyen'] = niveaux_sum / len(domaines_dict) if domaines_dict else 0
    stats['jours_actifs_count'] = len(stats['jours_actifs'])
    
    # Calculer meilleure série de jours consécutifs
    if stats['jours_actifs']:
        dates_triees = sorted([datetime.strptime(d, '%Y-%m-%d').date() for d in stats['jours_actifs']])
        serie_actuelle = 1
        meilleure_serie = 1
        
        for i in range(1, len(dates_triees)):
            if (dates_triees[i] - dates_triees[i-1]).days == 1:
                serie_actuelle += 1
                meilleure_serie = max(meilleure_serie, serie_actuelle)
            else:
                serie_actuelle = 1
        
        stats['meilleure_serie'] = meilleure_serie
    
    return stats


def afficher_rapport_analytique():
    """Affiche un rapport analytique complet"""
    stats = calculer_statistiques_avancees()
    progression = charger_progression()
    
    print("\n" + "="*70)
    print("📊 RAPPORT ANALYTIQUE COMPLET")
    print("="*70)
    
    # Vue d'ensemble
    print("\n🌟 VUE D'ENSEMBLE")
    print("-"*70)
    print(f"Total d'exercices: {stats['total_exercices']}")
    print(f"Exercices réussis: {stats['total_reussis']}")
    
    if stats['total_exercices'] > 0:
        taux_global = (stats['total_reussis'] / stats['total_exercices']) * 100
        print(f"Taux de réussite global: {taux_global:.1f}%")
    
    print(f"XP total: {stats['total_xp']:,}")
    print(f"Niveau moyen: {stats['niveau_moyen']:.1f}")
    
    # Engagement
    print("\n\n📅 ENGAGEMENT")
    print("-"*70)
    print(f"Jours actifs: {stats['jours_actifs_count']}")
    print(f"Meilleure série: {stats['meilleure_serie']} jours consécutifs")
    print(f"Streak actuel: {progression.get('streak_actuel', 0)} jours")
    print(f"Record de streak: {progression.get('streak_record', 0)} jours")
    
    # Performance
    print("\n\n🎯 PERFORMANCE")
    print("-"*70)
    print(f"Domaines actifs: {stats['domaines_actifs']}")
    if stats['meilleur_domaine']:
        print(f"Meilleur domaine: {stats['meilleur_domaine']} ({stats['meilleur_score']*100:.1f}%)")
    
    # Temps estimé
    temps_total = calculer_temps_moyen_par_exercice()
    heures = temps_total // 60
    minutes = temps_total % 60
    print(f"Temps total estimé: {heures}h {minutes}min")
    
    # Projections
    print("\n\n🔮 PROJECTIONS")
    print("-"*70)
    
    if stats['jours_actifs_count'] > 0:
        exercices_par_jour = stats['total_exercices'] / stats['jours_actifs_count']
        print(f"Moyenne: {exercices_par_jour:.1f} exercices par jour actif")
        
        # Projection pour atteindre 1000 exercices
        if stats['total_exercices'] < 1000:
            restant = 1000 - stats['total_exercices']
            jours_necessaires = int(restant / exercices_par_jour) if exercices_par_jour > 0 else 0
            print(f"Pour atteindre 1000 exercices: ~{jours_necessaires} jours actifs")
    
    print("\n" + "="*70)


def comparer_periodes():
    """Compare les performances entre deux périodes"""
    progression = charger_progression()
    domaines_dict = charger_domaines()
    
    print("\n" + "="*70)
    print("📊 COMPARAISON DE PÉRIODES")
    print("="*70)
    
    # Collecter les données de cette semaine vs semaine dernière
    aujourd_hui = datetime.now().date()
    debut_semaine_actuelle = aujourd_hui - timedelta(days=7)
    debut_semaine_precedente = aujourd_hui - timedelta(days=14)
    
    stats_actuelle = {'exercices': 0, 'reussis': 0}
    stats_precedente = {'exercices': 0, 'reussis': 0}
    
    for dom_id in domaines_dict.keys():
        prog_dom = obtenir_progression_domaine(dom_id)
        
        for entree in prog_dom.get('historique', []):
            date_str = entree.get('date', '').split()[0]
            if date_str:
                try:
                    date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    
                    if date >= debut_semaine_actuelle:
                        stats_actuelle['exercices'] += 1
                        if entree.get('reussi', False):
                            stats_actuelle['reussis'] += 1
                    
                    elif date >= debut_semaine_precedente:
                        stats_precedente['exercices'] += 1
                        if entree.get('reussi', False):
                            stats_precedente['reussis'] += 1
                except:
                    pass
    
    print("\n7 derniers jours vs 7 jours précédents:\n")
    print(f"{'Métrique':<30} {'Cette semaine':<20} {'Semaine dernière':<20}")
    print("-"*70)
    
    print(f"{'Exercices totaux':<30} {stats_actuelle['exercices']:<20} {stats_precedente['exercices']:<20}")
    print(f"{'Exercices réussis':<30} {stats_actuelle['reussis']:<20} {stats_precedente['reussis']:<20}")
    
    if stats_actuelle['exercices'] > 0:
        taux_actuel = (stats_actuelle['reussis'] / stats_actuelle['exercices']) * 100
    else:
        taux_actuel = 0
    
    if stats_precedente['exercices'] > 0:
        taux_precedent = (stats_precedente['reussis'] / stats_precedente['exercices']) * 100
    else:
        taux_precedent = 0
    
    print(f"{'Taux de réussite':<30} {taux_actuel:.1f}%{'':<15} {taux_precedent:.1f}%{'':<15}")
    
    # Tendance
    print("\n\n💡 TENDANCE:")
    if stats_actuelle['exercices'] > stats_precedente['exercices']:
        print(f"   📈 +{stats_actuelle['exercices'] - stats_precedente['exercices']} exercices cette semaine")
    elif stats_actuelle['exercices'] < stats_precedente['exercices']:
        print(f"   📉 -{stats_precedente['exercices'] - stats_actuelle['exercices']} exercices cette semaine")
    else:
        print("   ➡️  Activité stable")
    
    print("\n" + "="*70)


def menu_analytics():
    """Menu des analytics avancées"""
    while True:
        print("\n" + "="*70)
        print("📊 ANALYTICS AVANCÉES")
        print("="*70)
        print("\n1. Rapport analytique complet")
        print("2. Graphique de progression (ASCII)")
        print("3. Heatmap d'activité")
        print("4. Comparaison de périodes")
        print("5. Statistiques détaillées")
        print("0. Retour")
        
        try:
            choix = int(input("\nVotre choix : "))
        except ValueError:
            print("Erreur: Entrez un numéro valide.")
            continue
        
        if choix == 0:
            break
        
        elif choix == 1:
            afficher_rapport_analytique()
        
        elif choix == 2:
            from domaines import charger_domaines
            domaines_dict = charger_domaines()
            print("\nDomaines disponibles:")
            for i, (dom_id, dom_info) in enumerate(domaines_dict.items(), 1):
                print(f"{i}. {dom_info['nom']}")
            
            try:
                choix_dom = int(input("\nChoisir un domaine (numéro) : "))
                domaines_list = list(domaines_dict.keys())
                if 1 <= choix_dom <= len(domaines_list):
                    generer_graphique_progression_ascii(domaines_list[choix_dom - 1])
                else:
                    print("Numéro invalide.")
            except ValueError:
                print("Erreur: Entrez un numéro valide.")
        
        elif choix == 3:
            afficher_heatmap_activite()
        
        elif choix == 4:
            comparer_periodes()
        
        elif choix == 5:
            stats = calculer_statistiques_avancees()
            print("\n" + "="*70)
            print("📊 STATISTIQUES DÉTAILLÉES")
            print("="*70)
            print(json.dumps(stats, indent=2, ensure_ascii=False, default=str))
            print("="*70)
        
        else:
            print("Choix invalide.")
