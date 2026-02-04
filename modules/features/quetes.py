"""
Système de quêtes à long terme
Objectifs qui se débloquent progressivement
"""

import json
import os
from datetime import datetime
from modules.core.progression import charger_progression, sauvegarder_progression, obtenir_domaine_actif, obtenir_progression_domaine
from modules.core.domaines import charger_domaines, obtenir_nom_domaine


FICHIER_QUETES = 'quetes.json'

# Définition des quêtes
QUETES_DISPONIBLES = {
    'premier_pas': {
        'titre': '🌱 Premiers Pas',
        'description': 'Compléter votre premier exercice',
        'objectif': 1,
        'type': 'exercices_reussis',
        'recompense_xp': 50,
        'recompense_titre': 'Débutant',
        'difficulte': 'facile'
    },
    'apprenti_assidu': {
        'titre': '📚 Apprenti Assidu',
        'description': 'Réussir 50 exercices',
        'objectif': 50,
        'type': 'exercices_reussis',
        'recompense_xp': 500,
        'recompense_titre': 'Apprenti Assidu',
        'difficulte': 'moyen'
    },
    'centenaire': {
        'titre': '💯 Centenaire',
        'description': 'Réussir 100 exercices',
        'objectif': 100,
        'type': 'exercices_reussis',
        'recompense_xp': 1000,
        'recompense_titre': 'Centenaire',
        'difficulte': 'difficile'
    },
    'niveau_5_domaine': {
        'titre': '⭐ Compétent',
        'description': 'Atteindre le niveau 5 dans un domaine',
        'objectif': 5,
        'type': 'niveau_max',
        'recompense_xp': 750,
        'recompense_titre': 'Compétent',
        'difficulte': 'moyen'
    },
    'niveau_10_domaine': {
        'titre': '🏆 Expert',
        'description': 'Atteindre le niveau 10 dans un domaine',
        'objectif': 10,
        'type': 'niveau_max',
        'recompense_xp': 2000,
        'recompense_titre': 'Expert',
        'difficulte': 'difficile'
    },
    'polyglotte': {
        'titre': '🌍 Polyglotte',
        'description': 'Atteindre le niveau 3 dans 3 domaines différents',
        'objectif': 3,
        'type': 'domaines_niveau3',
        'recompense_xp': 1500,
        'recompense_titre': 'Polyglotte',
        'difficulte': 'difficile'
    },
    'collectionneur_badges': {
        'titre': '🎖️  Collectionneur',
        'description': 'Obtenir 10 badges',
        'objectif': 10,
        'type': 'badges_total',
        'recompense_xp': 800,
        'recompense_titre': 'Collectionneur',
        'difficulte': 'moyen'
    },
    'streak_warrior': {
        'titre': '🔥 Guerrier du Streak',
        'description': 'Maintenir un streak de 30 jours',
        'objectif': 30,
        'type': 'streak_max',
        'recompense_xp': 2500,
        'recompense_titre': 'Guerrier du Streak',
        'difficulte': 'difficile'
    },
    'perfectionniste': {
        'titre': '💎 Perfectionniste',
        'description': 'Atteindre 90% de taux de réussite global (min 50 exercices)',
        'objectif': 90,
        'type': 'taux_reussite',
        'recompense_xp': 1200,
        'recompense_titre': 'Perfectionniste',
        'difficulte': 'difficile'
    },
    'maitre_themes': {
        'titre': '🎯 Maître des Thèmes',
        'description': 'Réussir au moins un exercice dans tous les thèmes d\'un domaine',
        'objectif': 10,
        'type': 'themes_complets',
        'recompense_xp': 600,
        'recompense_titre': 'Maître des Thèmes',
        'difficulte': 'moyen'
    },
    'marathonien': {
        'titre': '🏃 Marathonien',
        'description': 'Compléter 20 exercices en une seule journée',
        'objectif': 20,
        'type': 'exercices_quotidiens',
        'recompense_xp': 1000,
        'recompense_titre': 'Marathonien',
        'difficulte': 'difficile'
    },
    'touche_a_tout': {
        'titre': '🎨 Touche-à-tout',
        'description': 'Essayer au moins 5 domaines différents',
        'objectif': 5,
        'type': 'domaines_essayes',
        'recompense_xp': 500,
        'recompense_titre': 'Touche-à-tout',
        'difficulte': 'facile'
    }
}


def charger_quetes():
    """Charge l'état des quêtes"""
    if os.path.exists(FICHIER_QUETES):
        try:
            with open(FICHIER_QUETES, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}


def sauvegarder_quetes(quetes):
    """Sauvegarde l'état des quêtes"""
    with open(FICHIER_QUETES, 'w', encoding='utf-8') as f:
        json.dump(quetes, f, indent=4, ensure_ascii=False)


def initialiser_quetes():
    """Initialise toutes les quêtes si nécessaire"""
    quetes = charger_quetes()
    
    modifie = False
    for quete_id, config in QUETES_DISPONIBLES.items():
        if quete_id not in quetes:
            quetes[quete_id] = {
                'complete': False,
                'progression': 0,
                'date_debut': datetime.now().strftime('%Y-%m-%d'),
                'date_completion': None
            }
            modifie = True
    
    if modifie:
        sauvegarder_quetes(quetes)
    
    return quetes


def verifier_progression_quetes():
    """Vérifie et met à jour la progression de toutes les quêtes"""
    quetes = initialiser_quetes()
    progression = charger_progression()
    domaines_dict = charger_domaines()
    
    nouvelles_completions = []
    
    for quete_id, config in QUETES_DISPONIBLES.items():
        if quetes[quete_id]['complete']:
            continue  # Déjà complétée
        
        progression_actuelle = 0
        complete = False
        
        # Calculer la progression selon le type
        if config['type'] == 'exercices_reussis':
            # Total d'exercices réussis sur tous les domaines
            total_reussis = 0
            for dom_id in domaines_dict.keys():
                prog_dom = obtenir_progression_domaine(dom_id)
                total_reussis += prog_dom.get('exercices_reussis', 0)
            progression_actuelle = total_reussis
            complete = total_reussis >= config['objectif']
        
        elif config['type'] == 'niveau_max':
            # Niveau maximum atteint dans un domaine
            niveau_max = 0
            for dom_id in domaines_dict.keys():
                prog_dom = obtenir_progression_domaine(dom_id)
                niveau_max = max(niveau_max, prog_dom.get('niveau', 1))
            progression_actuelle = niveau_max
            complete = niveau_max >= config['objectif']
        
        elif config['type'] == 'domaines_niveau3':
            # Nombre de domaines avec niveau 3+
            count = 0
            for dom_id in domaines_dict.keys():
                prog_dom = obtenir_progression_domaine(dom_id)
                if prog_dom.get('niveau', 1) >= 3:
                    count += 1
            progression_actuelle = count
            complete = count >= config['objectif']
        
        elif config['type'] == 'badges_total':
            # Total de badges sur tous les domaines
            total_badges = 0
            for dom_id in domaines_dict.keys():
                prog_dom = obtenir_progression_domaine(dom_id)
                total_badges += len(prog_dom.get('badges', []))
            progression_actuelle = total_badges
            complete = total_badges >= config['objectif']
        
        elif config['type'] == 'streak_max':
            # Streak record
            streak_record = progression.get('streak_record', 0)
            progression_actuelle = streak_record
            complete = streak_record >= config['objectif']
        
        elif config['type'] == 'taux_reussite':
            # Taux de réussite global
            total_reussis = 0
            total_exercices = 0
            for dom_id in domaines_dict.keys():
                prog_dom = obtenir_progression_domaine(dom_id)
                total_reussis += prog_dom.get('exercices_reussis', 0)
                total_exercices += prog_dom.get('exercices_totaux', 0)
            
            if total_exercices >= 50:
                taux = (total_reussis / total_exercices * 100) if total_exercices > 0 else 0
                progression_actuelle = int(taux)
                complete = taux >= config['objectif']
            else:
                progression_actuelle = 0
        
        elif config['type'] == 'themes_complets':
            # Tous les thèmes d'un domaine complétés
            for dom_id in domaines_dict.keys():
                prog_dom = obtenir_progression_domaine(dom_id)
                themes_avec_reussite = len([t for t, stats in prog_dom.get('themes', {}).items() if stats.get('reussis', 0) > 0])
                if themes_avec_reussite >= config['objectif']:
                    progression_actuelle = themes_avec_reussite
                    complete = True
                    break
        
        elif config['type'] == 'domaines_essayes':
            # Nombre de domaines essayés (au moins 1 exercice)
            count = 0
            for dom_id in domaines_dict.keys():
                prog_dom = obtenir_progression_domaine(dom_id)
                if prog_dom.get('exercices_totaux', 0) > 0:
                    count += 1
            progression_actuelle = count
            complete = count >= config['objectif']
        
        # Mettre à jour
        quetes[quete_id]['progression'] = progression_actuelle
        
        if complete and not quetes[quete_id]['complete']:
            quetes[quete_id]['complete'] = True
            quetes[quete_id]['date_completion'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            nouvelles_completions.append(quete_id)
            
            # Ajouter XP
            from xp_systeme import ajouter_xp
            ajouter_xp(config['recompense_xp'])
    
    sauvegarder_quetes(quetes)
    
    # Afficher les nouvelles complétions
    for quete_id in nouvelles_completions:
        config = QUETES_DISPONIBLES[quete_id]
        print(f"\n✨ QUÊTE COMPLÉTÉE ! ✨")
        print(f"   {config['titre']}")
        print(f"   {config['description']}")
        print(f"   Récompense: +{config['recompense_xp']} XP")
        print(f"   Titre débloqué: {config['recompense_titre']}")
    
    return nouvelles_completions


def afficher_quetes():
    """Affiche toutes les quêtes avec leur progression"""
    quetes = initialiser_quetes()
    
    print("\n" + "="*80)
    print("✨ QUÊTES")
    print("="*80)
    
    # Séparer par statut
    completes = []
    en_cours = []
    
    for quete_id, etat in quetes.items():
        config = QUETES_DISPONIBLES[quete_id]
        if etat['complete']:
            completes.append((quete_id, config, etat))
        else:
            en_cours.append((quete_id, config, etat))
    
    # Afficher quêtes en cours
    print(f"\n📋 EN COURS ({len(en_cours)}):")
    print("-"*80)
    
    if not en_cours:
        print("Toutes les quêtes sont complétées ! Bravo !")
    else:
        # Trier par difficulté
        en_cours.sort(key=lambda x: {'facile': 0, 'moyen': 1, 'difficile': 2}[x[1]['difficulte']])
        
        for quete_id, config, etat in en_cours:
            pct = (etat['progression'] / config['objectif'] * 100) if config['objectif'] > 0 else 0
            
            # Barre de progression
            barre_longueur = 20
            barre_rempli = int((pct / 100) * barre_longueur)
            barre = "█" * barre_rempli + "░" * (barre_longueur - barre_rempli)
            
            difficulte_emoji = {"facile": "⭐", "moyen": "⭐⭐", "difficile": "⭐⭐⭐"}[config['difficulte']]
            
            print(f"\n{config['titre']} {difficulte_emoji}")
            print(f"  {config['description']}")
            print(f"  Progression: {etat['progression']}/{config['objectif']} [{barre}] {pct:.0f}%")
            print(f"  Récompense: +{config['recompense_xp']} XP | Titre: {config['recompense_titre']}")
    
    # Afficher quêtes complétées
    print(f"\n\n✅ COMPLÉTÉES ({len(completes)}):")
    print("-"*80)
    
    if completes:
        for quete_id, config, etat in completes:
            print(f"\n{config['titre']}")
            print(f"  {config['description']}")
            print(f"  ✓ Complétée le {etat['date_completion']}")
            print(f"  Titre obtenu: {config['recompense_titre']}")
    else:
        print("Aucune quête complétée pour le moment.")
    
    print("\n" + "="*80)


def afficher_titres_obtenus():
    """Affiche tous les titres obtenus via les quêtes"""
    quetes = initialiser_quetes()
    
    titres_obtenus = []
    
    for quete_id, etat in quetes.items():
        if etat['complete']:
            config = QUETES_DISPONIBLES[quete_id]
            titres_obtenus.append({
                'titre': config['recompense_titre'],
                'quete': config['titre'],
                'date': etat['date_completion']
            })
    
    print("\n" + "="*70)
    print("🏅 MES TITRES")
    print("="*70)
    
    if not titres_obtenus:
        print("\nAucun titre obtenu pour le moment.")
        print("Complétez des quêtes pour débloquer des titres !")
    else:
        print(f"\nVous avez {len(titres_obtenus)} titre(s):")
        print()
        
        for item in titres_obtenus:
            print(f"🏆 {item['titre']}")
            print(f"   Débloqué via: {item['quete']}")
            print(f"   Date: {item['date']}")
            print()
    
    print("="*70)


def obtenir_prochaine_quete_recommandee():
    """Recommande la prochaine quête à compléter"""
    quetes = initialiser_quetes()
    
    # Trouver les quêtes en cours les plus proches de la completion
    quetes_proches = []
    
    for quete_id, etat in quetes.items():
        if not etat['complete']:
            config = QUETES_DISPONIBLES[quete_id]
            pct = (etat['progression'] / config['objectif'] * 100) if config['objectif'] > 0 else 0
            quetes_proches.append((quete_id, config, etat, pct))
    
    if not quetes_proches:
        return None
    
    # Trier par pourcentage de completion décroissant
    quetes_proches.sort(key=lambda x: x[3], reverse=True)
    
    return quetes_proches[0]


def afficher_recommandation_quete():
    """Affiche une recommandation de quête"""
    recommandation = obtenir_prochaine_quete_recommandee()
    
    print("\n" + "="*70)
    print("💡 QUÊTE RECOMMANDÉE")
    print("="*70)
    
    if not recommandation:
        print("\nToutes les quêtes sont complétées ! Félicitations !")
    else:
        quete_id, config, etat, pct = recommandation
        restant = config['objectif'] - etat['progression']
        
        print(f"\n{config['titre']}")
        print(f"{config['description']}")
        print(f"\nProgression: {etat['progression']}/{config['objectif']} ({pct:.0f}%)")
        print(f"Restant: {restant}")
        print(f"\nRécompense: +{config['recompense_xp']} XP")
        print(f"Titre à débloquer: {config['recompense_titre']}")
    
    print("\n" + "="*70)


def menu_quetes():
    """Menu des quêtes"""
    while True:
        print("\n" + "="*70)
        print("✨ QUÊTES")
        print("="*70)
        print("\n1. Voir toutes les quêtes")
        print("2. Mes titres")
        print("3. Quête recommandée")
        print("4. Vérifier progression")
        print("0. Retour")
        
        try:
            choix = int(input("\nVotre choix : "))
        except ValueError:
            print("Erreur: Entrez un numéro valide.")
            continue
        
        if choix == 0:
            break
        
        elif choix == 1:
            afficher_quetes()
        
        elif choix == 2:
            afficher_titres_obtenus()
        
        elif choix == 3:
            afficher_recommandation_quete()
        
        elif choix == 4:
            print("\nVérification de la progression...")
            nouvelles = verifier_progression_quetes()
            if not nouvelles:
                print("Aucune nouvelle quête complétée.")
            else:
                print(f"\n🎉 {len(nouvelles)} quête(s) complétée(s) !")
        
        else:
            print("Choix invalide.")
