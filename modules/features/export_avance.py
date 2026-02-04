"""
Export avancé vers formats standards (CSV, TXT, Markdown)
Note: PDF nécessiterait la bibliothèque reportlab (non installée par défaut)
"""

import json
import os
import csv
from datetime import datetime
from modules.core.progression import charger_progression, obtenir_progression_domaine
from modules.core.domaines import charger_domaines, obtenir_nom_domaine


DOSSIER_EXPORTS = 'exports'


def initialiser_dossier_exports():
    """Crée le dossier d'exports s'il n'existe pas"""
    if not os.path.exists(DOSSIER_EXPORTS):
        os.makedirs(DOSSIER_EXPORTS)


def exporter_progression_csv():
    """Exporte la progression en format CSV"""
    initialiser_dossier_exports()
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nom_fichier = f"progression_{timestamp}.csv"
    chemin = os.path.join(DOSSIER_EXPORTS, nom_fichier)
    
    progression = charger_progression()
    domaines_dict = charger_domaines()
    
    with open(chemin, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        
        # En-têtes
        writer.writerow(['Domaine', 'Niveau', 'XP Total', 'Exercices Réussis', 'Exercices Totaux', 'Taux Réussite %', 'Badges'])
        
        # Données par domaine
        for dom_id in domaines_dict.keys():
            prog_dom = obtenir_progression_domaine(dom_id)
            nom = obtenir_nom_domaine(dom_id)
            niveau = prog_dom.get('niveau', 1)
            xp = prog_dom.get('xp_total', 0)
            reussis = prog_dom.get('exercices_reussis', 0)
            totaux = prog_dom.get('exercices_totaux', 0)
            taux = (reussis / totaux * 100) if totaux > 0 else 0
            badges = len(prog_dom.get('badges', []))
            
            writer.writerow([nom, niveau, xp, reussis, totaux, f"{taux:.1f}", badges])
    
    print(f"\n✅ Export CSV créé : {chemin}")
    return chemin


def exporter_themes_csv():
    """Exporte les statistiques par thème en CSV"""
    initialiser_dossier_exports()
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nom_fichier = f"themes_{timestamp}.csv"
    chemin = os.path.join(DOSSIER_EXPORTS, nom_fichier)
    
    domaines_dict = charger_domaines()
    
    with open(chemin, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        
        # En-têtes
        writer.writerow(['Domaine', 'Thème', 'Réussis', 'Totaux', 'Taux Réussite %'])
        
        # Données
        for dom_id in domaines_dict.keys():
            prog_dom = obtenir_progression_domaine(dom_id)
            nom_domaine = obtenir_nom_domaine(dom_id)
            
            for theme, stats in prog_dom.get('themes', {}).items():
                reussis = stats.get('reussis', 0)
                totaux = stats.get('totaux', 0)
                taux = (reussis / totaux * 100) if totaux > 0 else 0
                
                writer.writerow([nom_domaine, theme, reussis, totaux, f"{taux:.1f}"])
    
    print(f"\n✅ Export CSV thèmes créé : {chemin}")
    return chemin


def exporter_rapport_markdown():
    """Exporte un rapport complet en Markdown"""
    initialiser_dossier_exports()
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nom_fichier = f"rapport_{timestamp}.md"
    chemin = os.path.join(DOSSIER_EXPORTS, nom_fichier)
    
    progression = charger_progression()
    domaines_dict = charger_domaines()
    
    with open(chemin, 'w', encoding='utf-8') as f:
        f.write("# 📊 Rapport de Progression\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        # Statistiques globales
        f.write("## 🌟 Statistiques Globales\n\n")
        f.write(f"- **Streak actuel:** {progression.get('streak_actuel', 0)} jours\n")
        f.write(f"- **Record de streak:** {progression.get('streak_record', 0)} jours\n")
        
        # Total exercices
        total_reussis = 0
        total_exercices = 0
        total_badges = 0
        
        for dom_id in domaines_dict.keys():
            prog_dom = obtenir_progression_domaine(dom_id)
            total_reussis += prog_dom.get('exercices_reussis', 0)
            total_exercices += prog_dom.get('exercices_totaux', 0)
            total_badges += len(prog_dom.get('badges', []))
        
        taux_global = (total_reussis / total_exercices * 100) if total_exercices > 0 else 0
        
        f.write(f"- **Exercices réussis:** {total_reussis}/{total_exercices}\n")
        f.write(f"- **Taux de réussite global:** {taux_global:.1f}%\n")
        f.write(f"- **Badges totaux:** {total_badges}\n\n")
        
        f.write("---\n\n")
        
        # Par domaine
        f.write("## 📚 Progression par Domaine\n\n")
        
        for dom_id in domaines_dict.keys():
            prog_dom = obtenir_progression_domaine(dom_id)
            nom = obtenir_nom_domaine(dom_id)
            
            f.write(f"### {nom}\n\n")
            f.write(f"- **Niveau:** {prog_dom.get('niveau', 1)}\n")
            f.write(f"- **XP:** {prog_dom.get('xp_total', 0)}\n")
            
            reussis = prog_dom.get('exercices_reussis', 0)
            totaux = prog_dom.get('exercices_totaux', 0)
            taux = (reussis / totaux * 100) if totaux > 0 else 0
            
            f.write(f"- **Exercices:** {reussis}/{totaux} ({taux:.1f}%)\n")
            f.write(f"- **Badges:** {len(prog_dom.get('badges', []))}\n\n")
            
            # Thèmes
            themes = prog_dom.get('themes', {})
            if themes:
                f.write("**Thèmes:**\n\n")
                for theme, stats in themes.items():
                    t_reussis = stats.get('reussis', 0)
                    t_totaux = stats.get('totaux', 0)
                    t_taux = (t_reussis / t_totaux * 100) if t_totaux > 0 else 0
                    f.write(f"- {theme}: {t_reussis}/{t_totaux} ({t_taux:.0f}%)\n")
                f.write("\n")
        
        f.write("---\n\n")
        f.write("*Rapport généré automatiquement*\n")
    
    print(f"\n✅ Rapport Markdown créé : {chemin}")
    return chemin


def exporter_rapport_texte():
    """Exporte un rapport simple en texte brut"""
    initialiser_dossier_exports()
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nom_fichier = f"rapport_{timestamp}.txt"
    chemin = os.path.join(DOSSIER_EXPORTS, nom_fichier)
    
    progression = charger_progression()
    domaines_dict = charger_domaines()
    
    with open(chemin, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("RAPPORT DE PROGRESSION\n")
        f.write("="*70 + "\n")
        f.write(f"\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Stats globales
        f.write("STATISTIQUES GLOBALES\n")
        f.write("-"*70 + "\n")
        f.write(f"Streak actuel: {progression.get('streak_actuel', 0)} jours\n")
        f.write(f"Record de streak: {progression.get('streak_record', 0)} jours\n\n")
        
        # Par domaine
        f.write("\nPROGRESSION PAR DOMAINE\n")
        f.write("-"*70 + "\n\n")
        
        for dom_id in domaines_dict.keys():
            prog_dom = obtenir_progression_domaine(dom_id)
            nom = obtenir_nom_domaine(dom_id)
            
            f.write(f"{nom}\n")
            f.write(f"  Niveau: {prog_dom.get('niveau', 1)}\n")
            f.write(f"  XP: {prog_dom.get('xp_total', 0)}\n")
            
            reussis = prog_dom.get('exercices_reussis', 0)
            totaux = prog_dom.get('exercices_totaux', 0)
            taux = (reussis / totaux * 100) if totaux > 0 else 0
            
            f.write(f"  Exercices: {reussis}/{totaux} ({taux:.1f}%)\n")
            f.write(f"  Badges: {len(prog_dom.get('badges', []))}\n\n")
    
    print(f"\n✅ Rapport texte créé : {chemin}")
    return chemin


def exporter_historique_json():
    """Exporte l'historique complet en JSON"""
    initialiser_dossier_exports()
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nom_fichier = f"historique_{timestamp}.json"
    chemin = os.path.join(DOSSIER_EXPORTS, nom_fichier)
    
    progression = charger_progression()
    domaines_dict = charger_domaines()
    
    donnees_export = {
        'date_export': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'streak': {
            'actuel': progression.get('streak_actuel', 0),
            'record': progression.get('streak_record', 0)
        },
        'domaines': {}
    }
    
    for dom_id in domaines_dict.keys():
        prog_dom = obtenir_progression_domaine(dom_id)
        nom = obtenir_nom_domaine(dom_id)
        
        donnees_export['domaines'][nom] = {
            'niveau': prog_dom.get('niveau', 1),
            'xp_total': prog_dom.get('xp_total', 0),
            'exercices_reussis': prog_dom.get('exercices_reussis', 0),
            'exercices_totaux': prog_dom.get('exercices_totaux', 0),
            'badges': prog_dom.get('badges', []),
            'themes': prog_dom.get('themes', {}),
            'historique': prog_dom.get('historique', [])[-20:]  # 20 derniers
        }
    
    with open(chemin, 'w', encoding='utf-8') as f:
        json.dump(donnees_export, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Historique JSON créé : {chemin}")
    return chemin


def lister_exports():
    """Liste tous les fichiers exportés"""
    initialiser_dossier_exports()
    
    fichiers = os.listdir(DOSSIER_EXPORTS)
    
    if not fichiers:
        print("\nAucun export disponible.")
        return []
    
    print("\n" + "="*70)
    print("📂 EXPORTS DISPONIBLES")
    print("="*70)
    
    exports_tries = sorted(fichiers, reverse=True)
    
    for i, fichier in enumerate(exports_tries, 1):
        chemin = os.path.join(DOSSIER_EXPORTS, fichier)
        taille = os.path.getsize(chemin) / 1024
        date_modif = datetime.fromtimestamp(os.path.getmtime(chemin))
        
        print(f"\n{i}. {fichier}")
        print(f"   Taille: {taille:.2f} Ko")
        print(f"   Date: {date_modif.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n" + "="*70)
    return exports_tries


def menu_exports_avances():
    """Menu des exports avancés"""
    while True:
        print("\n" + "="*70)
        print("💾 EXPORTS AVANCÉS")
        print("="*70)
        print("\n1. Exporter progression (CSV)")
        print("2. Exporter thèmes (CSV)")
        print("3. Générer rapport (Markdown)")
        print("4. Générer rapport (Texte)")
        print("5. Exporter historique (JSON)")
        print("6. Lister les exports")
        print("7. Tout exporter")
        print("0. Retour")
        
        try:
            choix = int(input("\nVotre choix : "))
        except ValueError:
            print("Erreur: Entrez un numéro valide.")
            continue
        
        if choix == 0:
            break
        
        elif choix == 1:
            exporter_progression_csv()
        
        elif choix == 2:
            exporter_themes_csv()
        
        elif choix == 3:
            exporter_rapport_markdown()
        
        elif choix == 4:
            exporter_rapport_texte()
        
        elif choix == 5:
            exporter_historique_json()
        
        elif choix == 6:
            lister_exports()
        
        elif choix == 7:
            print("\nExport de tous les formats...")
            exporter_progression_csv()
            exporter_themes_csv()
            exporter_rapport_markdown()
            exporter_rapport_texte()
            exporter_historique_json()
            print("\n✅ Tous les exports sont terminés !")
        
        else:
            print("Choix invalide.")


# Alias pour la cohérence
menu_export_avance = menu_exports_avances
