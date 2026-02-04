"""
Mode hors ligne
Cache d'exercices pour fonctionner sans Ollama
"""

import json
import os
import random
from modules.core.domaines import charger_domaines, obtenir_themes_domaine


FICHIER_CACHE = 'cache_exercices.json'
FICHIER_CONFIG_OFFLINE = 'config_offline.json'


def charger_cache():
    """Charge le cache d'exercices"""
    if os.path.exists(FICHIER_CACHE):
        try:
            with open(FICHIER_CACHE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {'exercices': []}
    return {'exercices': []}


def sauvegarder_cache(cache):
    """Sauvegarde le cache d'exercices"""
    with open(FICHIER_CACHE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=4, ensure_ascii=False)


def charger_config_offline():
    """Charge la configuration du mode hors ligne"""
    if os.path.exists(FICHIER_CONFIG_OFFLINE):
        try:
            with open(FICHIER_CONFIG_OFFLINE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {'mode_hors_ligne': False}
    return {'mode_hors_ligne': False}


def est_mode_hors_ligne():
    """Vérifie si le mode hors ligne est activé"""
    if os.path.exists(FICHIER_CONFIG_OFFLINE):
        try:
            with open(FICHIER_CONFIG_OFFLINE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('mode_hors_ligne', False)
        except:
            return False
    return False


def activer_mode_hors_ligne():
    """Active le mode hors ligne"""
    config = {'mode_hors_ligne': True}
    with open(FICHIER_CONFIG_OFFLINE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    print("\n✅ Mode hors ligne activé.")


def desactiver_mode_hors_ligne():
    """Désactive le mode hors ligne"""
    config = {'mode_hors_ligne': False}
    with open(FICHIER_CONFIG_OFFLINE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    print("\n✅ Mode hors ligne désactivé.")


def ajouter_au_cache(exercice, domaine, theme, niveau):
    """Ajoute un exercice au cache"""
    cache = charger_cache()
    
    exercice_cache = {
        'id': len(cache['exercices']) + 1,
        'domaine': domaine,
        'theme': theme,
        'niveau': niveau,
        'exercice': exercice,
        'date_ajout': __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    cache['exercices'].append(exercice_cache)
    sauvegarder_cache(cache)


def obtenir_exercice_cache(domaine, theme, niveau):
    """Obtient un exercice du cache"""
    cache = charger_cache()
    
    # Filtrer par domaine, thème et niveau
    exercices_disponibles = [
        e for e in cache['exercices']
        if e['domaine'] == domaine and e['theme'] == theme and e['niveau'] == niveau
    ]
    
    if not exercices_disponibles:
        # Essayer sans le thème spécifique
        exercices_disponibles = [
            e for e in cache['exercices']
            if e['domaine'] == domaine and e['niveau'] == niveau
        ]
    
    if not exercices_disponibles:
        # Essayer juste le domaine
        exercices_disponibles = [
            e for e in cache['exercices']
            if e['domaine'] == domaine
        ]
    
    if exercices_disponibles:
        return random.choice(exercices_disponibles)['exercice']
    
    return None


def generer_exercice_basique(domaine, theme, niveau):
    """Génère un exercice basique sans IA (fallback)"""
    from domaines import obtenir_nom_domaine
    
    nom_domaine = obtenir_nom_domaine(domaine)
    
    # Exercices basiques prédéfinis
    exercices_basiques = {
        'python': {
            1: [
                {'type': 'qcm', 'question': 'Quel est le résultat de 2 + 2 * 2 en Python?', 
                 'choix': ['6', '8', '4', 'Erreur'], 'reponse': '6'},
                {'type': 'qcm', 'question': 'Comment déclarer une variable en Python?',
                 'choix': ['var x = 5', 'int x = 5', 'x = 5', 'let x = 5'], 'reponse': 'x = 5'},
            ],
            2: [
                {'type': 'qcm', 'question': 'Quelle méthode ajoute un élément à la fin d\'une liste?',
                 'choix': ['add()', 'append()', 'insert()', 'push()'], 'reponse': 'append()'},
            ],
            3: [
                {'type': 'qcm', 'question': 'Qu\'est-ce qu\'une list comprehension en Python?',
                 'choix': ['Une boucle for', 'Une manière concise de créer des listes', 'Une fonction', 'Un module'], 
                 'reponse': 'Une manière concise de créer des listes'},
            ]
        },
        'java': {
            1: [
                {'type': 'qcm', 'question': 'Quel mot-clé est utilisé pour créer une classe en Java?',
                 'choix': ['class', 'Class', 'new', 'object'], 'reponse': 'class'},
            ],
            2: [
                {'type': 'qcm', 'question': 'Quelle est la méthode principale en Java?',
                 'choix': ['start()', 'main()', 'run()', 'begin()'], 'reponse': 'main()'},
            ]
        },
        'javascript': {
            1: [
                {'type': 'qcm', 'question': 'Comment déclarer une variable constante en JavaScript?',
                 'choix': ['var x', 'let x', 'const x', 'constant x'], 'reponse': 'const x'},
            ]
        }
    }
    
    # Essayer d'obtenir un exercice prédéfini
    if domaine in exercices_basiques and niveau in exercices_basiques[domaine]:
        return random.choice(exercices_basiques[domaine][niveau])
    
    # Exercice générique
    return {
        'type': 'qcm',
        'question': f'Question de niveau {niveau} sur {theme} en {nom_domaine}',
        'choix': ['Réponse A', 'Réponse B', 'Réponse C', 'Réponse D'],
        'reponse': 'Réponse A',
        'note': 'Exercice généré en mode hors ligne basique'
    }


def peupler_cache_automatique(nb_exercices_par_domaine=10):
    """Génère automatiquement des exercices pour le cache"""
    from fonctions import generer_exercice
    import ollama
    
    domaines_dict = charger_domaines()
    cache = charger_cache()
    
    print(f"\n🔄 Génération de {nb_exercices_par_domaine} exercices par domaine...")
    print("Cela peut prendre quelques minutes.\n")
    
    total_generes = 0
    
    try:
        for domaine_id in list(domaines_dict.keys())[:3]:  # Limiter à 3 domaines principaux
            themes = obtenir_themes_domaine(domaine_id)
            
            for niveau in [1, 2, 3]:
                for theme in themes[:3]:  # 3 thèmes par domaine
                    try:
                        print(f"Génération: {domaine_id} - {theme} - Niveau {niveau}...")
                        exercice = generer_exercice(niveau, theme, domaine_id)
                        ajouter_au_cache(exercice, domaine_id, theme, niveau)
                        total_generes += 1
                        
                        if total_generes >= nb_exercices_par_domaine:
                            break
                    except Exception as e:
                        print(f"  Erreur: {e}")
                        continue
                
                if total_generes >= nb_exercices_par_domaine:
                    break
            
            if total_generes >= nb_exercices_par_domaine:
                break
        
        print(f"\n✅ {total_generes} exercices ajoutés au cache.")
        
    except Exception as e:
        print(f"\n⚠️  Erreur lors de la génération: {e}")
        print("Le mode hors ligne fonctionnera avec des exercices basiques.")


def afficher_statistiques_cache():
    """Affiche les statistiques du cache"""
    cache = charger_cache()
    exercices = cache['exercices']
    
    print("\n" + "="*70)
    print("📦 STATISTIQUES DU CACHE")
    print("="*70)
    
    print(f"\nTotal d'exercices en cache: {len(exercices)}")
    
    if not exercices:
        print("\nLe cache est vide. Utilisez l'option 3 pour le peupler.")
        return
    
    # Par domaine
    domaines_count = {}
    for ex in exercices:
        dom = ex['domaine']
        domaines_count[dom] = domaines_count.get(dom, 0) + 1
    
    print("\nExercices par domaine:")
    for dom, count in sorted(domaines_count.items(), key=lambda x: x[1], reverse=True):
        from domaines import obtenir_nom_domaine
        nom = obtenir_nom_domaine(dom)
        print(f"  • {nom}: {count}")
    
    # Par niveau
    niveaux_count = {}
    for ex in exercices:
        niv = ex['niveau']
        niveaux_count[niv] = niveaux_count.get(niv, 0) + 1
    
    print("\nExercices par niveau:")
    for niv in sorted(niveaux_count.keys()):
        print(f"  • Niveau {niv}: {niveaux_count[niv]}")
    
    print("\n" + "="*70)


def vider_cache():
    """Vide complètement le cache"""
    confirmation = input("\n⚠️  Êtes-vous sûr de vouloir vider le cache? (oui/non): ")
    if confirmation.lower() in ['oui', 'o', 'yes', 'y']:
        sauvegarder_cache({'exercices': []})
        print("\n✅ Cache vidé.")
    else:
        print("\n❌ Annulé.")


def menu_mode_hors_ligne():
    """Menu du mode hors ligne"""
    while True:
        mode_actif = est_mode_hors_ligne()
        statut = "✅ ACTIVÉ" if mode_actif else "❌ DÉSACTIVÉ"
        
        print("\n" + "="*70)
        print(f"📴 MODE HORS LIGNE - {statut}")
        print("="*70)
        print("\n1. Activer/Désactiver le mode hors ligne")
        print("2. Statistiques du cache")
        print("3. Peupler le cache automatiquement")
        print("4. Vider le cache")
        print("5. Tester un exercice du cache")
        print("0. Retour")
        
        try:
            choix = int(input("\nVotre choix : "))
        except ValueError:
            print("Erreur: Entrez un numéro valide.")
            continue
        
        if choix == 0:
            break
        
        elif choix == 1:
            if mode_actif:
                desactiver_mode_hors_ligne()
            else:
                activer_mode_hors_ligne()
        
        elif choix == 2:
            afficher_statistiques_cache()
        
        elif choix == 3:
            try:
                nb = int(input("\nNombre d'exercices à générer (10-50): "))
                peupler_cache_automatique(nb)
            except ValueError:
                print("Nombre invalide.")
        
        elif choix == 4:
            vider_cache()
        
        elif choix == 5:
            from domaines import charger_domaines
            domaines_dict = charger_domaines()
            print("\nTest d'exercice du cache:")
            print(f"Domaines disponibles: {', '.join(list(domaines_dict.keys())[:3])}")
            
            domaine = input("Domaine (ex: python): ")
            if domaine in domaines_dict:
                exercice = obtenir_exercice_cache(domaine, 'Variables', 1)
                if exercice:
                    print(f"\n✅ Exercice trouvé:")
                    print(json.dumps(exercice, indent=2, ensure_ascii=False))
                else:
                    print("\n❌ Aucun exercice disponible pour ces critères.")
            else:
                print("Domaine invalide.")
        
        else:
            print("Choix invalide.")
