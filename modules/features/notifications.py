"""
Système de notifications et rappels
Gère les alertes pour streak, révisions SRS, défis, etc.
"""

import json
import os
from datetime import datetime, timedelta
from modules.core.progression import charger_progression


FICHIER_NOTIFICATIONS = 'notifications.json'


def charger_notifications():
    """Charge les notifications"""
    if os.path.exists(FICHIER_NOTIFICATIONS):
        try:
            with open(FICHIER_NOTIFICATIONS, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {'notifications': [], 'dernier_check': None}
    return {'notifications': [], 'dernier_check': None}


def sauvegarder_notifications(notifs):
    """Sauvegarde les notifications"""
    with open(FICHIER_NOTIFICATIONS, 'w', encoding='utf-8') as f:
        json.dump(notifs, f, indent=4, ensure_ascii=False)


def ajouter_notification(type_notif, titre, message, priorite='normale'):
    """
    Ajoute une nouvelle notification
    
    Args:
        type_notif: Type (streak, srs, defi, badge, quete)
        titre: Titre de la notification
        message: Message détaillé
        priorite: 'faible', 'normale', 'haute', 'urgente'
    """
    notifs = charger_notifications()
    
    nouvelle_notif = {
        'id': datetime.now().strftime('%Y%m%d%H%M%S%f'),
        'type': type_notif,
        'titre': titre,
        'message': message,
        'priorite': priorite,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'lue': False
    }
    
    notifs['notifications'].append(nouvelle_notif)
    sauvegarder_notifications(notifs)


def verifier_notifications_automatiques():
    """Vérifie et génère les notifications automatiques"""
    progression = charger_progression()
    nouvelles_notifs = []
    
    # 1. Vérifier le streak
    streak_actuel = progression.get('streak_actuel', 0)
    derniere_pratique = progression.get('derniere_pratique')
    
    if derniere_pratique:
        derniere_date = datetime.strptime(derniere_pratique, '%Y-%m-%d').date()
        aujourd_hui = datetime.now().date()
        jours_depuis = (aujourd_hui - derniere_date).days
        
        if jours_depuis == 1:
            # Rappel quotidien
            ajouter_notification(
                'streak',
                '🔥 Maintiens ton streak !',
                f'Continue ta série de {streak_actuel} jours ! Ne la laisse pas s\'éteindre.',
                'normale'
            )
            nouvelles_notifs.append('streak_rappel')
        
        elif jours_depuis > 1 and streak_actuel > 0:
            # Streak en danger
            ajouter_notification(
                'streak',
                '⚠️  Streak en danger !',
                f'Attention ! Ton streak de {streak_actuel} jours est sur le point de se terminer. Fais un exercice aujourd\'hui !',
                'urgente'
            )
            nouvelles_notifs.append('streak_danger')
    
    # 2. Vérifier les révisions SRS
    try:
        from repetition_espacee import obtenir_exercices_a_reviser
        exercices_srs = obtenir_exercices_a_reviser()
        
        if len(exercices_srs) >= 5:
            ajouter_notification(
                'srs',
                '📚 Révisions en attente',
                f'Tu as {len(exercices_srs)} exercices à réviser. C\'est le moment parfait pour consolider tes connaissances !',
                'normale'
            )
            nouvelles_notifs.append('srs_revisions')
    except:
        pass
    
    # 3. Vérifier les défis quotidiens
    try:
        from defis_quotidiens import obtenir_defi_du_jour
        defi = obtenir_defi_du_jour()
        
        if defi and not defi['complete']:
            if defi['progression'] == 0:
                ajouter_notification(
                    'defi',
                    '🎯 Défi du jour disponible',
                    f'{defi["nom"]}: {defi["description"]}. Récompense: +{defi["xp_bonus"]} XP',
                    'normale'
                )
                nouvelles_notifs.append('defi_nouveau')
            elif defi['progression'] >= defi['objectif'] * 0.75:
                ajouter_notification(
                    'defi',
                    '🏁 Défi presque terminé !',
                    f'Tu es à {defi["progression"]}/{defi["objectif"]} pour "{defi["nom"]}". Encore un petit effort !',
                    'haute'
                )
                nouvelles_notifs.append('defi_proche')
    except:
        pass
    
    # 4. Milestones de streak
    if streak_actuel in [7, 30, 50, 100]:
        ajouter_notification(
            'streak',
            f'🎉 Milestone: {streak_actuel} jours !',
            f'Félicitations ! Tu as atteint {streak_actuel} jours consécutifs. Continue comme ça !',
            'haute'
        )
        nouvelles_notifs.append(f'streak_{streak_actuel}')
    
    return nouvelles_notifs


def obtenir_notifications_non_lues():
    """Retourne les notifications non lues"""
    notifs = charger_notifications()
    return [n for n in notifs['notifications'] if not n['lue']]


def marquer_notification_lue(notif_id):
    """Marque une notification comme lue"""
    notifs = charger_notifications()
    
    for notif in notifs['notifications']:
        if notif['id'] == notif_id:
            notif['lue'] = True
            break
    
    sauvegarder_notifications(notifs)


def marquer_toutes_lues():
    """Marque toutes les notifications comme lues"""
    notifs = charger_notifications()
    
    for notif in notifs['notifications']:
        notif['lue'] = True
    
    sauvegarder_notifications(notifs)


def supprimer_notification(notif_id):
    """Supprime une notification"""
    notifs = charger_notifications()
    notifs['notifications'] = [n for n in notifs['notifications'] if n['id'] != notif_id]
    sauvegarder_notifications(notifs)


def supprimer_anciennes_notifications(jours=7):
    """Supprime les notifications de plus de X jours"""
    notifs = charger_notifications()
    date_limite = (datetime.now() - timedelta(days=jours)).strftime('%Y-%m-%d')
    
    notifs['notifications'] = [
        n for n in notifs['notifications']
        if n['date'].split()[0] >= date_limite
    ]
    
    sauvegarder_notifications(notifs)


def afficher_notifications():
    """Affiche toutes les notifications"""
    notifs_data = charger_notifications()
    toutes_notifs = notifs_data['notifications']
    
    # Trier par date (plus récentes en premier)
    toutes_notifs.sort(key=lambda x: x['date'], reverse=True)
    
    non_lues = [n for n in toutes_notifs if not n['lue']]
    
    print("\n" + "="*70)
    print(f"🔔 NOTIFICATIONS ({len(non_lues)} non lues)")
    print("="*70)
    
    if not toutes_notifs:
        print("\nAucune notification.")
        return
    
    # Afficher les non lues en premier
    if non_lues:
        print("\n📬 NON LUES:")
        print("-"*70)
        
        for notif in non_lues:
            emoji_priorite = {
                'faible': '🔵',
                'normale': '🟢',
                'haute': '🟠',
                'urgente': '🔴'
            }.get(notif['priorite'], '⚪')
            
            print(f"\n{emoji_priorite} {notif['titre']}")
            print(f"   {notif['message']}")
            print(f"   📅 {notif['date']}")
    
    # Afficher les lues
    lues = [n for n in toutes_notifs if n['lue']]
    
    if lues:
        print(f"\n\n✅ LUES ({len(lues)}):")
        print("-"*70)
        
        for notif in lues[:5]:  # Afficher seulement les 5 dernières
            print(f"\n{notif['titre']}")
            print(f"   📅 {notif['date']}")
    
    print("\n" + "="*70)


def afficher_resume_notifications():
    """Affiche un résumé rapide des notifications"""
    non_lues = obtenir_notifications_non_lues()
    
    if not non_lues:
        return
    
    # Grouper par priorité
    urgentes = [n for n in non_lues if n['priorite'] == 'urgente']
    hautes = [n for n in non_lues if n['priorite'] == 'haute']
    normales = [n for n in non_lues if n['priorite'] == 'normale']
    
    print("\n" + "="*70)
    print("🔔 NOTIFICATIONS")
    print("="*70)
    
    if urgentes:
        print(f"\n🔴 URGENTES ({len(urgentes)}):")
        for notif in urgentes:
            print(f"   • {notif['titre']}")
    
    if hautes:
        print(f"\n🟠 IMPORTANTES ({len(hautes)}):")
        for notif in hautes:
            print(f"   • {notif['titre']}")
    
    if normales and len(normales) <= 3:
        print(f"\n🟢 AUTRES ({len(normales)}):")
        for notif in normales:
            print(f"   • {notif['titre']}")
    elif normales:
        print(f"\n🟢 AUTRES: {len(normales)} notification(s)")
    
    print("\n" + "="*70)


def configurer_notifications():
    """Configure les préférences de notifications"""
    print("\n" + "="*70)
    print("⚙️  CONFIGURATION DES NOTIFICATIONS")
    print("="*70)
    
    print("\nTypes de notifications:")
    print("1. Rappels de streak ✓")
    print("2. Révisions SRS ✓")
    print("3. Défis quotidiens ✓")
    print("4. Nouveaux badges ✓")
    print("5. Quêtes complétées ✓")
    
    print("\nToutes les notifications sont activées par défaut.")
    print("(Configuration avancée disponible dans une future version)")


def menu_notifications():
    """Menu de gestion des notifications"""
    while True:
        # Vérifier les nouvelles notifications
        verifier_notifications_automatiques()
        
        non_lues = obtenir_notifications_non_lues()
        
        print("\n" + "="*70)
        print(f"🔔 NOTIFICATIONS ({len(non_lues)} non lues)")
        print("="*70)
        print("\n1. Voir toutes les notifications")
        print("2. Résumé rapide")
        print("3. Marquer toutes comme lues")
        print("4. Supprimer anciennes notifications")
        print("5. Configuration")
        print("0. Retour")
        
        try:
            choix = int(input("\nVotre choix : "))
        except ValueError:
            print("Erreur: Entrez un numéro valide.")
            continue
        
        if choix == 0:
            break
        
        elif choix == 1:
            afficher_notifications()
        
        elif choix == 2:
            afficher_resume_notifications()
        
        elif choix == 3:
            marquer_toutes_lues()
            print("\n✅ Toutes les notifications marquées comme lues.")
        
        elif choix == 4:
            supprimees = supprimer_anciennes_notifications(7)
            print(f"\n✅ Notifications de plus de 7 jours supprimées.")
        
        elif choix == 5:
            configurer_notifications()
        
        else:
            print("Choix invalide.")
