"""
Système de défis quotidiens
Génère des défis spécifiques par domaine avec récompenses bonus
"""

import json
import os
from datetime import datetime, timedelta
import random
from modules.core.progression import charger_progression, sauvegarder_progression, obtenir_domaine_actif, obtenir_progression_domaine
from modules.core.domaines import charger_domaines, obtenir_nom_domaine


FICHIER_DEFIS = 'defis_quotidiens.json'

# Types de défis
TYPES_DEFIS = {
    'serie_victoires': {
        'nom': 'Série de victoires',
        'description': 'Réussir {objectif} exercices d\'affilée',
        'xp_bonus': 100,
        'objectifs': [3, 5, 7]
    },
    'niveau_difficile': {
        'nom': 'Défi difficile',
        'description': 'Réussir {objectif} exercices de niveau 3',
        'xp_bonus': 150,
        'objectifs': [2, 3, 5]
    },
    'themes_varies': {
        'nom': 'Polyvalence',
        'description': 'Réussir des exercices dans {objectif} thèmes différents',
        'xp_bonus': 120,
        'objectifs': [3, 4, 5]
    },
    'perfectionniste': {
        'nom': 'Sans faute',
        'description': 'Réussir {objectif} exercices du premier coup',
        'xp_bonus': 130,
        'objectifs': [3, 5, 8]
    },
    'marathon': {
        'nom': 'Marathon',
        'description': 'Compléter {objectif} exercices dans la journée',
        'xp_bonus': 80,
        'objectifs': [10, 15, 20]
    }
}


def charger_defis():
    """Charge les défis depuis le fichier JSON"""
    if os.path.exists(FICHIER_DEFIS):
        try:
            with open(FICHIER_DEFIS, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}


def sauvegarder_defis(defis):
    """Sauvegarde les défis dans le fichier JSON"""
    with open(FICHIER_DEFIS, 'w', encoding='utf-8') as f:
        json.dump(defis, f, indent=4, ensure_ascii=False)


def obtenir_date_aujourdhui():
    """Retourne la date d'aujourd'hui au format YYYY-MM-DD"""
    return datetime.now().strftime('%Y-%m-%d')


def generer_defi_quotidien(domaine):
    """
    Génère un nouveau défi quotidien pour un domaine
    
    Args:
        domaine: ID du domaine
    
    Returns:
        dict: Défi généré
    """
    # Choisir un type de défi aléatoire
    type_defi = random.choice(list(TYPES_DEFIS.keys()))
    config = TYPES_DEFIS[type_defi]
    
    # Choisir un objectif aléatoire
    objectif = random.choice(config['objectifs'])
    
    # Créer le défi
    defi = {
        'type': type_defi,
        'nom': config['nom'],
        'description': config['description'].format(objectif=objectif),
        'objectif': objectif,
        'xp_bonus': config['xp_bonus'],
        'progression': 0,
        'complete': False,
        'date': obtenir_date_aujourdhui(),
        'domaine': domaine,
        'themes_completes': [] if type_defi == 'themes_varies' else None
    }
    
    return defi


def obtenir_defi_du_jour(domaine=None):
    """
    Obtient le défi du jour pour un domaine
    Génère un nouveau défi si nécessaire
    
    Args:
        domaine: ID du domaine (None = domaine actif)
    
    Returns:
        dict: Défi du jour ou None
    """
    if domaine is None:
        domaine = obtenir_domaine_actif()
    
    defis = charger_defis()
    date_aujourdhui = obtenir_date_aujourdhui()
    
    # Vérifier si un défi existe pour aujourd'hui
    cle_defi = f"{domaine}_{date_aujourdhui}"
    
    if cle_defi in defis:
        return defis[cle_defi]
    
    # Générer un nouveau défi
    nouveau_defi = generer_defi_quotidien(domaine)
    defis[cle_defi] = nouveau_defi
    sauvegarder_defis(defis)
    
    return nouveau_defi


def mettre_a_jour_defi(type_defi, domaine=None, theme=None, niveau=None, reussi=True, tentatives=1):
    """
    Met à jour la progression du défi quotidien
    
    Args:
        type_defi: Type d'action (exercice, niveau3, theme, premier_coup, etc.)
        domaine: ID du domaine
        theme: Thème de l'exercice
        niveau: Niveau de l'exercice
        reussi: Si l'exercice a été réussi
        tentatives: Nombre de tentatives
    """
    if domaine is None:
        domaine = obtenir_domaine_actif()
    
    defi = obtenir_defi_du_jour(domaine)
    
    if not defi or defi['complete']:
        return False
    
    # Mettre à jour selon le type de défi
    if defi['type'] == 'serie_victoires':
        if reussi:
            defi['progression'] += 1
        else:
            defi['progression'] = 0  # Reset si échec
    
    elif defi['type'] == 'niveau_difficile':
        if reussi and niveau == 3:
            defi['progression'] += 1
    
    elif defi['type'] == 'themes_varies':
        if reussi and theme:
            if theme not in defi['themes_completes']:
                defi['themes_completes'].append(theme)
                defi['progression'] = len(defi['themes_completes'])
    
    elif defi['type'] == 'perfectionniste':
        if reussi and tentatives == 1:
            defi['progression'] += 1
    
    elif defi['type'] == 'marathon':
        if reussi:
            defi['progression'] += 1
    
    # Vérifier si le défi est complété
    if defi['progression'] >= defi['objectif']:
        defi['complete'] = True
        
        # Ajouter XP bonus
        from xp_systeme import ajouter_xp
        ajouter_xp(defi['xp_bonus'], domaine)
        
        print(f"\n🎉 DÉFI QUOTIDIEN COMPLÉTÉ ! 🎉")
        print(f"   {defi['nom']}: {defi['description']}")
        print(f"   +{defi['xp_bonus']} XP BONUS !")
    
    # Sauvegarder
    defis = charger_defis()
    date_aujourdhui = obtenir_date_aujourdhui()
    cle_defi = f"{domaine}_{date_aujourdhui}"
    defis[cle_defi] = defi
    sauvegarder_defis(defis)
    
    return defi['complete']


def afficher_defi_du_jour(domaine=None):
    """Affiche le défi quotidien actuel"""
    if domaine is None:
        domaine = obtenir_domaine_actif()
    
    defi = obtenir_defi_du_jour(domaine)
    nom_domaine = obtenir_nom_domaine(domaine)
    
    print("\n" + "="*70)
    print("🎯 DÉFI QUOTIDIEN")
    print("="*70)
    print(f"\nDomaine: {nom_domaine}")
    print(f"Défi: {defi['nom']}")
    print(f"Objectif: {defi['description']}")
    
    if defi['complete']:
        print(f"\n✅ COMPLÉTÉ ! +{defi['xp_bonus']} XP")
    else:
        print(f"\nProgression: {defi['progression']}/{defi['objectif']}")
        
        # Barre de progression
        pct = (defi['progression'] / defi['objectif']) * 100
        barre_longueur = 30
        barre_rempli = int((pct / 100) * barre_longueur)
        barre = "█" * barre_rempli + "░" * (barre_longueur - barre_rempli)
        print(f"[{barre}] {pct:.0f}%")
        print(f"\nRécompense: +{defi['xp_bonus']} XP BONUS")
    
    print("="*70)


def afficher_historique_defis(domaine=None, limite=7):
    """Affiche l'historique des défis complétés"""
    if domaine is None:
        domaine = obtenir_domaine_actif()
    
    defis = charger_defis()
    nom_domaine = obtenir_nom_domaine(domaine)
    
    # Filtrer les défis du domaine
    defis_domaine = {k: v for k, v in defis.items() if v['domaine'] == domaine}
    
    # Trier par date (plus récent en premier)
    defis_tries = sorted(defis_domaine.items(), key=lambda x: x[1]['date'], reverse=True)
    
    print("\n" + "="*70)
    print(f"📜 HISTORIQUE DES DÉFIS - {nom_domaine}")
    print("="*70)
    
    if not defis_tries:
        print("\nAucun défi complété pour ce domaine.")
        return
    
    compteur = 0
    total_xp_bonus = 0
    defis_completes = 0
    
    for cle, defi in defis_tries[:limite]:
        compteur += 1
        statut = "✅ COMPLÉTÉ" if defi['complete'] else "⏳ En cours"
        
        print(f"\n{compteur}. [{defi['date']}] {defi['nom']}")
        print(f"   {defi['description']}")
        print(f"   Progression: {defi['progression']}/{defi['objectif']}")
        print(f"   Statut: {statut}")
        
        if defi['complete']:
            print(f"   XP gagné: +{defi['xp_bonus']}")
            total_xp_bonus += defi['xp_bonus']
            defis_completes += 1
    
    print("\n" + "-"*70)
    print(f"Défis complétés: {defis_completes}/{compteur}")
    if total_xp_bonus > 0:
        print(f"XP bonus total: {total_xp_bonus}")
    print("="*70)


def obtenir_statistiques_defis(domaine=None):
    """Obtient les statistiques des défis pour un domaine"""
    if domaine is None:
        domaine = obtenir_domaine_actif()
    
    defis = charger_defis()
    
    # Filtrer les défis du domaine
    defis_domaine = [v for k, v in defis.items() if v['domaine'] == domaine]
    
    total_defis = len(defis_domaine)
    defis_completes = sum(1 for d in defis_domaine if d['complete'])
    xp_total_bonus = sum(d['xp_bonus'] for d in defis_domaine if d['complete'])
    
    # Taux de réussite par type
    types_stats = {}
    for defi in defis_domaine:
        type_d = defi['type']
        if type_d not in types_stats:
            types_stats[type_d] = {'total': 0, 'completes': 0}
        types_stats[type_d]['total'] += 1
        if defi['complete']:
            types_stats[type_d]['completes'] += 1
    
    return {
        'total_defis': total_defis,
        'defis_completes': defis_completes,
        'xp_total_bonus': xp_total_bonus,
        'taux_reussite': (defis_completes / total_defis * 100) if total_defis > 0 else 0,
        'types_stats': types_stats
    }


def afficher_statistiques_defis(domaine=None):
    """Affiche les statistiques des défis"""
    if domaine is None:
        domaine = obtenir_domaine_actif()
    
    stats = obtenir_statistiques_defis(domaine)
    nom_domaine = obtenir_nom_domaine(domaine)
    
    print("\n" + "="*70)
    print(f"📊 STATISTIQUES DES DÉFIS - {nom_domaine}")
    print("="*70)
    
    print(f"\nDéfis complétés: {stats['defis_completes']}/{stats['total_defis']}")
    print(f"Taux de réussite: {stats['taux_reussite']:.1f}%")
    print(f"XP bonus total gagné: {stats['xp_total_bonus']}")
    
    if stats['types_stats']:
        print("\n\nRéussite par type de défi:")
        print("-"*70)
        
        for type_defi, type_stats in stats['types_stats'].items():
            config = TYPES_DEFIS.get(type_defi, {})
            nom = config.get('nom', type_defi)
            taux = (type_stats['completes'] / type_stats['total'] * 100) if type_stats['total'] > 0 else 0
            
            print(f"\n{nom}:")
            print(f"  Complétés: {type_stats['completes']}/{type_stats['total']} ({taux:.0f}%)")
    
    print("\n" + "="*70)


def nettoyer_vieux_defis(jours=30):
    """Supprime les défis de plus de X jours"""
    defis = charger_defis()
    date_limite = (datetime.now() - timedelta(days=jours)).strftime('%Y-%m-%d')
    
    defis_filtres = {k: v for k, v in defis.items() if v['date'] >= date_limite}
    
    if len(defis_filtres) < len(defis):
        sauvegarder_defis(defis_filtres)
        print(f"\n{len(defis) - len(defis_filtres)} vieux défis supprimés.")
    
    return len(defis) - len(defis_filtres)


def menu_defis():
    """Menu de gestion des défis quotidiens"""
    while True:
        print("\n" + "="*70)
        print("🎯 DÉFIS QUOTIDIENS")
        print("="*70)
        print("\n1. Voir le défi du jour")
        print("2. Historique des défis")
        print("3. Statistiques des défis")
        print("4. Défis des autres domaines")
        print("0. Retour")
        
        try:
            choix = int(input("\nVotre choix : "))
        except ValueError:
            print("Erreur: Entrez un numéro valide.")
            continue
        
        if choix == 0:
            break
        
        elif choix == 1:
            afficher_defi_du_jour()
        
        elif choix == 2:
            afficher_historique_defis()
        
        elif choix == 3:
            afficher_statistiques_defis()
        
        elif choix == 4:
            domaines_dict = charger_domaines()
            print("\n\nDomaines disponibles:")
            for i, (dom_id, dom_info) in enumerate(domaines_dict.items(), 1):
                print(f"{i}. {dom_info['nom']}")
            
            try:
                choix_dom = int(input("\nChoisir un domaine (numéro) : "))
                domaines_list = list(domaines_dict.keys())
                if 1 <= choix_dom <= len(domaines_list):
                    dom_id = domaines_list[choix_dom - 1]
                    afficher_defi_du_jour(dom_id)
                else:
                    print("Numéro invalide.")
            except ValueError:
                print("Erreur: Entrez un numéro valide.")
        
        else:
            print("Choix invalide.")
