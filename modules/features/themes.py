"""
Système de thèmes visuels
Permet de personnaliser l'apparence de l'interface
"""

import json
import os


FICHIER_THEMES = 'themes_config.json'

# Définition des thèmes
THEMES_DISPONIBLES = {
    'classique': {
        'nom': 'Classique',
        'description': 'Thème par défaut, sobre et professionnel',
        'couleurs': {
            'principal': 'bleu',
            'secondaire': 'gris',
            'succes': 'vert',
            'erreur': 'rouge',
            'avertissement': 'jaune'
        },
        'separateurs': {
            'principal': '=',
            'secondaire': '-'
        },
        'emojis': True
    },
    'sombre': {
        'nom': 'Sombre',
        'description': 'Thème dark mode, reposant pour les yeux',
        'couleurs': {
            'principal': 'cyan',
            'secondaire': 'gris_fonce',
            'succes': 'vert_fonce',
            'erreur': 'rouge_fonce',
            'avertissement': 'orange'
        },
        'separateurs': {
            'principal': '▬',
            'secondaire': '─'
        },
        'emojis': True
    },
    'minimal': {
        'nom': 'Minimal',
        'description': 'Interface épurée, sans emojis',
        'couleurs': {
            'principal': 'blanc',
            'secondaire': 'gris',
            'succes': 'blanc',
            'erreur': 'blanc',
            'avertissement': 'blanc'
        },
        'separateurs': {
            'principal': '-',
            'secondaire': '.'
        },
        'emojis': False
    },
    'arc_en_ciel': {
        'nom': 'Arc-en-ciel',
        'description': 'Coloré et joyeux',
        'couleurs': {
            'principal': 'multicolore',
            'secondaire': 'violet',
            'succes': 'vert',
            'erreur': 'rouge',
            'avertissement': 'orange'
        },
        'separateurs': {
            'principal': '✦',
            'secondaire': '•'
        },
        'emojis': True
    },
    'retro': {
        'nom': 'Rétro',
        'description': 'Style années 80, ASCII art',
        'couleurs': {
            'principal': 'vert_terminal',
            'secondaire': 'vert_terminal',
            'succes': 'vert_terminal',
            'erreur': 'vert_terminal',
            'avertissement': 'vert_terminal'
        },
        'separateurs': {
            'principal': '#',
            'secondaire': '*'
        },
        'emojis': False
    }
}


def obtenir_themes_disponibles():
    """Retourne la liste des thèmes disponibles"""
    return list(THEMES_DISPONIBLES.keys())


def charger_config_theme():
    """Charge la configuration complète des thèmes"""
    return {
        'theme_actif': charger_theme_actif(),
        'themes_disponibles': THEMES_DISPONIBLES
    }


def charger_theme_actif():
    """Charge la configuration du thème actif"""
    if os.path.exists(FICHIER_THEMES):
        try:
            with open(FICHIER_THEMES, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('theme_actif', 'classique')
        except:
            return 'classique'
    return 'classique'


def sauvegarder_theme(theme_id):
    """Sauvegarde le thème actif"""
    config = {'theme_actif': theme_id}
    with open(FICHIER_THEMES, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


def obtenir_config_theme(theme_id=None):
    """Obtient la configuration du thème"""
    if theme_id is None:
        theme_id = charger_theme_actif()
    
    return THEMES_DISPONIBLES.get(theme_id, THEMES_DISPONIBLES['classique'])


def afficher_separateur(type_sep='principal', longueur=70):
    """Affiche un séparateur selon le thème actif"""
    config = obtenir_config_theme()
    char = config['separateurs'].get(type_sep, '=')
    return char * longueur


def afficher_titre(texte, avec_separateurs=True):
    """Affiche un titre stylisé selon le thème"""
    config = obtenir_config_theme()
    
    if avec_separateurs:
        print("\n" + afficher_separateur('principal'))
    print(texte)
    if avec_separateurs:
        print(afficher_separateur('principal'))


def formatter_texte_succes(texte):
    """Formate un texte de succès"""
    config = obtenir_config_theme()
    emoji = "✅ " if config['emojis'] else ""
    return f"{emoji}{texte}"


def formatter_texte_erreur(texte):
    """Formate un texte d'erreur"""
    config = obtenir_config_theme()
    emoji = "❌ " if config['emojis'] else ""
    return f"{emoji}{texte}"


def formatter_texte_avertissement(texte):
    """Formate un texte d'avertissement"""
    config = obtenir_config_theme()
    emoji = "⚠️  " if config['emojis'] else ""
    return f"{emoji}{texte}"


def formatter_texte_info(texte):
    """Formate un texte informatif"""
    config = obtenir_config_theme()
    emoji = "ℹ️  " if config['emojis'] else ""
    return f"{emoji}{texte}"


def afficher_tous_themes():
    """Affiche tous les thèmes disponibles"""
    theme_actif = charger_theme_actif()
    
    print("\n" + "="*70)
    print("🎨 THÈMES DISPONIBLES")
    print("="*70)
    
    for i, (theme_id, config) in enumerate(THEMES_DISPONIBLES.items(), 1):
        actif = " [ACTIF]" if theme_id == theme_actif else ""
        print(f"\n{i}. {config['nom']}{actif}")
        print(f"   {config['description']}")
        print(f"   Séparateurs: '{config['separateurs']['principal']}' et '{config['separateurs']['secondaire']}'")
        print(f"   Emojis: {'Oui' if config['emojis'] else 'Non'}")
    
    print("\n" + "="*70)


def changer_theme():
    """Interface pour changer de thème"""
    afficher_tous_themes()
    
    print("\nChoisir un thème:")
    themes_list = list(THEMES_DISPONIBLES.keys())
    
    for i, theme_id in enumerate(themes_list, 1):
        print(f"{i}. {THEMES_DISPONIBLES[theme_id]['nom']}")
    
    try:
        choix = int(input("\nNuméro du thème : "))
        if 1 <= choix <= len(themes_list):
            theme_id = themes_list[choix - 1]
            sauvegarder_theme(theme_id)
            print(f"\n✅ Thème '{THEMES_DISPONIBLES[theme_id]['nom']}' activé !")
            
            # Aperçu
            print("\nAperçu:")
            config = obtenir_config_theme(theme_id)
            print(afficher_separateur('principal'))
            print("EXEMPLE DE TITRE")
            print(afficher_separateur('principal'))
            print(formatter_texte_succes("Message de succès"))
            print(formatter_texte_erreur("Message d'erreur"))
            print(formatter_texte_avertissement("Message d'avertissement"))
            print(formatter_texte_info("Message informatif"))
            print(afficher_separateur('secondaire'))
        else:
            print("Numéro invalide.")
    except ValueError:
        print("Erreur: Entrez un numéro valide.")


def obtenir_emoji_selon_theme(emoji_si_active, texte_alternatif=""):
    """Retourne un emoji si le thème le permet, sinon du texte"""
    config = obtenir_config_theme()
    if config['emojis']:
        return emoji_si_active
    return texte_alternatif


def menu_themes():
    """Menu de gestion des thèmes"""
    while True:
        print("\n" + afficher_separateur('principal'))
        print("🎨 THÈMES VISUELS")
        print(afficher_separateur('principal'))
        print("\n1. Voir tous les thèmes")
        print("2. Changer de thème")
        print("3. Thème actif")
        print("0. Retour")
        
        try:
            choix = int(input("\nVotre choix : "))
        except ValueError:
            print("Erreur: Entrez un numéro valide.")
            continue
        
        if choix == 0:
            break
        
        elif choix == 1:
            afficher_tous_themes()
        
        elif choix == 2:
            changer_theme()
        
        elif choix == 3:
            theme_id = charger_theme_actif()
            config = obtenir_config_theme(theme_id)
            print(f"\nThème actif: {config['nom']}")
            print(f"Description: {config['description']}")
        
        else:
            print("Choix invalide.")
