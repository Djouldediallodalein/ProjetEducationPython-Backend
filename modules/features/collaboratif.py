"""
Mode collaboratif (simulation locale)
Partage de progression anonyme et défis entre utilisateurs
Note: Version simulée pour fonctionnement local sans serveur
"""

import json
import os
import random
from datetime import datetime
from modules.core.progression import charger_progression, obtenir_progression_domaine
from modules.core.domaines import charger_domaines, obtenir_nom_domaine


FICHIER_COMMUNAUTE = 'communaute.json'


def charger_donnees_communaute():
    """Charge les données de la communauté (simulées)"""
    if os.path.exists(FICHIER_COMMUNAUTE):
        try:
            with open(FICHIER_COMMUNAUTE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return generer_donnees_initiales()
    return generer_donnees_initiales()


def generer_donnees_initiales():
    """Génère des données initiales simulées de la communauté"""
    return {
        'utilisateurs': [
            {'pseudo': 'CodeMaster', 'niveau_moyen': 8, 'total_xp': 5420, 'specialite': 'Python'},
            {'pseudo': 'JavaNinja', 'niveau_moyen': 7, 'total_xp': 4230, 'specialite': 'Java'},
            {'pseudo': 'WebWizard', 'niveau_moyen': 6, 'total_xp': 3890, 'specialite': 'JavaScript'},
            {'pseudo': 'DataScientist', 'niveau_moyen': 9, 'total_xp': 6100, 'specialite': 'Python'},
            {'pseudo': 'FrontendPro', 'niveau_moyen': 5, 'total_xp': 2750, 'specialite': 'HTML/CSS'},
            {'pseudo': 'BackendDev', 'niveau_moyen': 7, 'total_xp': 4500, 'specialite': 'Java'},
            {'pseudo': 'FullStack', 'niveau_moyen': 6, 'total_xp': 3950, 'specialite': 'JavaScript'},
            {'pseudo': 'AlgoExpert', 'niveau_moyen': 10, 'total_xp': 7200, 'specialite': 'C'},
        ],
        'defis_communautaires': [
            {
                'id': 1,
                'titre': '🏃 Marathon Python',
                'description': 'Complétez 20 exercices Python en une semaine',
                'participants': 156,
                'objectif': 20,
                'recompense_xp': 500
            },
            {
                'id': 2,
                'titre': '🎯 Perfectionniste',
                'description': 'Obtenez 100% de réussite sur 10 exercices',
                'participants': 89,
                'objectif': 10,
                'recompense_xp': 400
            },
            {
                'id': 3,
                'titre': '🌍 Polyglotte',
                'description': 'Pratiquez 5 langages différents cette semaine',
                'participants': 234,
                'objectif': 5,
                'recompense_xp': 600
            }
        ],
        'statistiques_globales': {
            'total_utilisateurs': 1547,
            'total_exercices': 89432,
            'exercices_cette_semaine': 8934,
            'domaine_populaire': 'Python',
            'niveau_moyen_global': 5.2
        }
    }


def sauvegarder_donnees_communaute(donnees):
    """Sauvegarde les données de la communauté"""
    with open(FICHIER_COMMUNAUTE, 'w', encoding='utf-8') as f:
        json.dump(donnees, f, indent=4, ensure_ascii=False)


def obtenir_classement_global(domaine=None):
    """Obtient le classement global (simulé avec données locales + aléatoires)"""
    communaute = charger_donnees_communaute()
    progression = charger_progression()
    
    # Calculer le score de l'utilisateur
    if domaine:
        prog_dom = obtenir_progression_domaine(domaine)
        score_utilisateur = prog_dom.get('xp_total', 0)
        niveau_utilisateur = prog_dom.get('niveau', 1)
    else:
        # Score global
        domaines_dict = charger_domaines()
        score_utilisateur = 0
        niveaux_sum = 0
        for dom_id in domaines_dict.keys():
            prog_dom = obtenir_progression_domaine(dom_id)
            score_utilisateur += prog_dom.get('xp_total', 0)
            niveaux_sum += prog_dom.get('niveau', 1)
        niveau_utilisateur = niveaux_sum / len(domaines_dict) if domaines_dict else 1
    
    # Créer le classement avec l'utilisateur
    classement = []
    
    # Ajouter les utilisateurs simulés
    for user in communaute['utilisateurs']:
        if not domaine or user.get('specialite') == domaine:
            classement.append({
                'pseudo': user['pseudo'],
                'score': user['total_xp'],
                'niveau': user['niveau_moyen'],
                'est_vous': False
            })
    
    # Ajouter l'utilisateur actuel
    classement.append({
        'pseudo': 'Vous',
        'score': score_utilisateur,
        'niveau': niveau_utilisateur,
        'est_vous': True
    })
    
    # Trier par score
    classement.sort(key=lambda x: x['score'], reverse=True)
    
    # Ajouter les positions
    for i, user in enumerate(classement, 1):
        user['position'] = i
    
    return classement


def afficher_classement_global():
    """Affiche le classement global"""
    classement = obtenir_classement_global()
    
    print("\n" + "="*70)
    print("🏆 CLASSEMENT GLOBAL DE LA COMMUNAUTÉ")
    print("="*70)
    
    communaute = charger_donnees_communaute()
    stats = communaute['statistiques_globales']
    
    print(f"\n👥 Utilisateurs actifs: {stats['total_utilisateurs']}")
    print(f"📚 Exercices complétés: {stats['total_exercices']:,}")
    print(f"🌟 Niveau moyen: {stats['niveau_moyen_global']:.1f}")
    print(f"🔥 Domaine populaire: {stats['domaine_populaire']}")
    
    print(f"\n\nTOP 10:")
    print("-"*70)
    print(f"{'#':<5} {'Pseudo':<20} {'Score':<15} {'Niveau':<10}")
    print("-"*70)
    
    for user in classement[:10]:
        emoji = "👑" if user['position'] == 1 else "🥈" if user['position'] == 2 else "🥉" if user['position'] == 3 else "  "
        marqueur = " ← " if user['est_vous'] else ""
        
        print(f"{user['position']:<5} {emoji} {user['pseudo']:<17} {user['score']:<15,} {user['niveau']:<10.1f}{marqueur}")
    
    # Afficher la position de l'utilisateur s'il n'est pas dans le top 10
    user_position = next((u for u in classement if u['est_vous']), None)
    if user_position and user_position['position'] > 10:
        print("\n...")
        print(f"{user_position['position']:<5}    {'Vous':<17} {user_position['score']:<15,} {user_position['niveau']:<10.1f} ←")
    
    print("\n" + "="*70)


def afficher_defis_communautaires():
    """Affiche les défis de la communauté"""
    communaute = charger_donnees_communaute()
    defis = communaute['defis_communautaires']
    
    print("\n" + "="*70)
    print("🌟 DÉFIS COMMUNAUTAIRES")
    print("="*70)
    
    for defi in defis:
        print(f"\n{defi['titre']}")
        print(f"   {defi['description']}")
        print(f"   👥 {defi['participants']} participants")
        print(f"   🎁 Récompense: +{defi['recompense_xp']} XP")
        print(f"   Objectif: {defi['objectif']}")
    
    print("\n💡 Note: Les défis communautaires sont synchronisés chaque semaine.")
    print("="*70)


def partager_progression_anonyme():
    """Partage anonyme de la progression à la communauté"""
    progression = charger_progression()
    domaines_dict = charger_domaines()
    
    # Calculer les statistiques à partager
    total_xp = 0
    niveau_moyen = 0
    domaine_favori = None
    max_xp_domaine = 0
    
    for dom_id in domaines_dict.keys():
        prog_dom = obtenir_progression_domaine(dom_id)
        xp = prog_dom.get('xp_total', 0)
        total_xp += xp
        niveau_moyen += prog_dom.get('niveau', 1)
        
        if xp > max_xp_domaine:
            max_xp_domaine = xp
            domaine_favori = obtenir_nom_domaine(dom_id)
    
    niveau_moyen = niveau_moyen / len(domaines_dict) if domaines_dict else 0
    
    print("\n" + "="*70)
    print("🌍 PARTAGE ANONYME DE PROGRESSION")
    print("="*70)
    
    print("\nVos données anonymisées:")
    print(f"  • Niveau moyen: {niveau_moyen:.1f}")
    print(f"  • XP total: {total_xp:,}")
    print(f"  • Spécialité: {domaine_favori}")
    
    confirmation = input("\nPartager ces données avec la communauté? (oui/non): ")
    
    if confirmation.lower() in ['oui', 'o', 'yes', 'y']:
        # Simuler l'ajout à la communauté
        communaute = charger_donnees_communaute()
        
        # Générer un pseudo anonyme
        pseudo_anonyme = f"User{random.randint(1000, 9999)}"
        
        communaute['utilisateurs'].append({
            'pseudo': pseudo_anonyme,
            'niveau_moyen': niveau_moyen,
            'total_xp': total_xp,
            'specialite': domaine_favori
        })
        
        # Mettre à jour les stats globales
        communaute['statistiques_globales']['total_utilisateurs'] += 1
        
        sauvegarder_donnees_communaute(communaute)
        
        print(f"\n✅ Progression partagée sous le pseudo: {pseudo_anonyme}")
        print("Merci de contribuer à la communauté !")
    else:
        print("\n❌ Partage annulé.")
    
    print("="*70)


def comparer_avec_communaute():
    """Compare les performances avec la moyenne de la communauté"""
    progression = charger_progression()
    communaute = charger_donnees_communaute()
    domaines_dict = charger_domaines()
    
    # Calculer les stats utilisateur
    total_exercices = 0
    total_reussis = 0
    niveau_moyen_user = 0
    
    for dom_id in domaines_dict.keys():
        prog_dom = obtenir_progression_domaine(dom_id)
        total_exercices += prog_dom.get('exercices_totaux', 0)
        total_reussis += prog_dom.get('exercices_reussis', 0)
        niveau_moyen_user += prog_dom.get('niveau', 1)
    
    niveau_moyen_user = niveau_moyen_user / len(domaines_dict) if domaines_dict else 0
    taux_reussite = (total_reussis / total_exercices * 100) if total_exercices > 0 else 0
    
    # Stats communauté
    niveau_moyen_communaute = communaute['statistiques_globales']['niveau_moyen_global']
    
    print("\n" + "="*70)
    print("📊 COMPARAISON AVEC LA COMMUNAUTÉ")
    print("="*70)
    
    print(f"\n{'Métrique':<30} {'Vous':<20} {'Communauté':<20}")
    print("-"*70)
    
    print(f"{'Niveau moyen':<30} {niveau_moyen_user:<20.1f} {niveau_moyen_communaute:<20.1f}")
    print(f"{'Exercices complétés':<30} {total_exercices:<20} ~{int(communaute['statistiques_globales']['total_exercices'] / communaute['statistiques_globales']['total_utilisateurs']):<20}")
    print(f"{'Taux de réussite':<30} {taux_reussite:.1f}%{'':<15} ~75.0%{'':<15}")
    
    print("\n\n💡 ANALYSE:")
    
    if niveau_moyen_user > niveau_moyen_communaute:
        diff = niveau_moyen_user - niveau_moyen_communaute
        print(f"   🎉 Vous êtes {diff:.1f} niveaux au-dessus de la moyenne !")
    elif niveau_moyen_user < niveau_moyen_communaute:
        diff = niveau_moyen_communaute - niveau_moyen_user
        print(f"   📈 Continuez ! Vous êtes {diff:.1f} niveaux en dessous de la moyenne.")
    else:
        print("   ⚖️  Vous êtes dans la moyenne de la communauté.")
    
    print("\n" + "="*70)


def afficher_contributions_communautaires():
    """Affiche des exemples de contributions de la communauté"""
    print("\n" + "="*70)
    print("💡 CONTRIBUTIONS DE LA COMMUNAUTÉ")
    print("="*70)
    
    contributions = [
        {
            'auteur': 'CodeMaster',
            'type': 'Exercice',
            'titre': 'Algorithme de tri avancé',
            'votes': 45,
            'domaine': 'Python'
        },
        {
            'auteur': 'WebWizard',
            'type': 'Astuce',
            'titre': 'Optimisation CSS Grid',
            'votes': 32,
            'domaine': 'HTML/CSS'
        },
        {
            'auteur': 'AlgoExpert',
            'type': 'Tutoriel',
            'titre': 'Structures de données en C',
            'votes': 67,
            'domaine': 'C'
        }
    ]
    
    print("\nContributions populaires:")
    
    for contrib in contributions:
        print(f"\n📝 {contrib['type']}: {contrib['titre']}")
        print(f"   Par: {contrib['auteur']} | {contrib['domaine']}")
        print(f"   👍 {contrib['votes']} votes")
    
    print("\n\n💡 Vous aussi, contribuez ! (fonctionnalité à venir)")
    print("="*70)


def menu_collaboratif():
    """Menu du mode collaboratif"""
    while True:
        print("\n" + "="*70)
        print("🌍 MODE COLLABORATIF")
        print("="*70)
        print("\n1. Classement global")
        print("2. Défis communautaires")
        print("3. Partager ma progression (anonyme)")
        print("4. Comparer avec la communauté")
        print("5. Contributions populaires")
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
            afficher_defis_communautaires()
        
        elif choix == 3:
            partager_progression_anonyme()
        
        elif choix == 4:
            comparer_avec_communaute()
        
        elif choix == 5:
            afficher_contributions_communautaires()
        
        else:
            print("Choix invalide.")
