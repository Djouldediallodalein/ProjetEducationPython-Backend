"""
Gestion des domaines d'apprentissage multi-sujets
Permet à l'utilisateur d'apprendre n'importe quel langage/sujet
"""

import json
import os
from modules.core.gestion_erreurs import sauvegarder_json_securise

FICHIER_DOMAINES = 'domaines.json'

def charger_domaines():
    """Charge les domaines disponibles"""
    if os.path.exists(FICHIER_DOMAINES):
        with open(FICHIER_DOMAINES, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return initialiser_domaines_par_defaut()

def initialiser_domaines_par_defaut():
    """Crée les domaines par défaut avec les langages les plus populaires"""
    domaines = {
        "python": {
            "nom": "Python",
            "emoji": "🐍",
            "type": "Langage de programmation",
            "description": "Langage polyvalent, idéal pour débuter",
            "popularite": 1,
            "themes": [
                "Variables et types de données",
                "Conditions (if/elif/else)",
                "Boucles (for/while)",
                "Fonctions",
                "Listes et tuples",
                "Dictionnaires",
                "Manipulation de strings",
                "Fichiers (lecture/écriture)",
                "Gestion des erreurs (try/except)",
                "Programmation orientée objet (classes)"
            ],
            "config_ia": {
                "role": "professeur expert en Python",
                "langage": "Python",
                "type_exercice": "code",
                "verification": "code Python"
            }
        },
        "javascript": {
            "nom": "JavaScript",
            "emoji": "⚡",
            "type": "Langage de programmation",
            "description": "Langage du web, interactif et dynamique",
            "popularite": 2,
            "themes": [
                "Variables (let, const, var)",
                "Types de données et opérateurs",
                "Conditions et ternaires",
                "Boucles (for, while, forEach)",
                "Fonctions et arrow functions",
                "Tableaux et méthodes (map, filter, reduce)",
                "Objets et JSON",
                "DOM et manipulation HTML",
                "Événements",
                "Promesses et async/await"
            ],
            "config_ia": {
                "role": "professeur expert en JavaScript",
                "langage": "JavaScript",
                "type_exercice": "code",
                "verification": "code JavaScript"
            }
        },
        "java": {
            "nom": "Java",
            "emoji": "☕",
            "type": "Langage de programmation",
            "description": "Langage orienté objet, puissant et universel",
            "popularite": 3,
            "themes": [
                "Types primitifs et String",
                "Conditions et boucles",
                "Tableaux (arrays)",
                "Méthodes et fonctions",
                "POO : Classes et objets",
                "Héritage et polymorphisme",
                "Interfaces et classes abstraites",
                "Collections (List, Map, Set)",
                "Gestion des exceptions",
                "Streams et expressions lambda"
            ],
            "config_ia": {
                "role": "professeur expert en Java",
                "langage": "Java",
                "type_exercice": "code",
                "verification": "code Java"
            }
        },
        "c": {
            "nom": "C",
            "emoji": "⚙️",
            "type": "Langage de programmation",
            "description": "Langage bas niveau, performance maximale",
            "popularite": 4,
            "themes": [
                "Variables et types (int, float, char)",
                "Opérateurs et expressions",
                "Conditions et boucles",
                "Fonctions",
                "Pointeurs et adresses mémoire",
                "Tableaux",
                "Chaînes de caractères",
                "Structures (struct)",
                "Allocation dynamique (malloc/free)",
                "Fichiers"
            ],
            "config_ia": {
                "role": "professeur expert en C",
                "langage": "C",
                "type_exercice": "code",
                "verification": "code C"
            }
        },
        "sql": {
            "nom": "SQL",
            "emoji": "🗄️",
            "type": "Langage de base de données",
            "description": "Gestion et requêtes de bases de données",
            "popularite": 5,
            "themes": [
                "SELECT : Requêtes simples",
                "WHERE : Filtrage de données",
                "ORDER BY et LIMIT",
                "Fonctions d'agrégation (COUNT, SUM, AVG)",
                "GROUP BY et HAVING",
                "JOINs (INNER, LEFT, RIGHT)",
                "Sous-requêtes",
                "INSERT, UPDATE, DELETE",
                "CREATE TABLE et contraintes",
                "Indexes et optimisation"
            ],
            "config_ia": {
                "role": "professeur expert en SQL",
                "langage": "SQL",
                "type_exercice": "code",
                "verification": "requête SQL"
            }
        },
        "html_css": {
            "nom": "HTML/CSS",
            "emoji": "🎨",
            "type": "Langages web",
            "description": "Structure et style des pages web",
            "popularite": 6,
            "themes": [
                "Structure HTML de base",
                "Balises de texte (h1-h6, p, span)",
                "Listes et tableaux",
                "Formulaires et inputs",
                "Sélecteurs CSS",
                "Couleurs et typographie",
                "Box model (margin, padding, border)",
                "Flexbox",
                "Grid Layout",
                "Responsive Design (media queries)"
            ],
            "config_ia": {
                "role": "professeur expert en HTML et CSS",
                "langage": "HTML/CSS",
                "type_exercice": "code",
                "verification": "code HTML/CSS"
            }
        },
        "mathematiques": {
            "nom": "Mathématiques",
            "emoji": "🔢",
            "type": "Matière académique",
            "description": "Algèbre, géométrie, analyse",
            "popularite": 7,
            "themes": [
                "Arithmétique et calculs",
                "Équations du premier degré",
                "Équations du second degré",
                "Fractions et pourcentages",
                "Puissances et racines",
                "Géométrie plane",
                "Trigonométrie",
                "Fonctions (affine, polynomiale)",
                "Dérivées",
                "Probabilités et statistiques"
            ],
            "config_ia": {
                "role": "professeur expert en mathématiques",
                "langage": "texte",
                "type_exercice": "calcul",
                "verification": "solution mathématique"
            }
        },
        "anglais": {
            "nom": "Anglais",
            "emoji": "🇬🇧",
            "type": "Langue étrangère",
            "description": "Grammaire, vocabulaire, conversation",
            "popularite": 8,
            "themes": [
                "Vocabulaire de base (200 mots essentiels)",
                "Present Simple",
                "Present Continuous",
                "Past Simple",
                "Future (will, going to)",
                "Questions et réponses",
                "Pronoms et possessifs",
                "Prépositions",
                "Adjectifs et comparatifs",
                "Conversation courante"
            ],
            "config_ia": {
                "role": "professeur expert en anglais",
                "langage": "anglais",
                "type_exercice": "texte",
                "verification": "réponse en anglais"
            }
        }
    }
    
    sauvegarder_domaines(domaines)
    return domaines

def sauvegarder_domaines(domaines):
    """Sauvegarde les domaines avec backup"""
    sauvegarder_json_securise(FICHIER_DOMAINES, domaines)

def choisir_domaine():
    """Permet à l'utilisateur de choisir un domaine d'apprentissage"""
    domaines = charger_domaines()
    
    print("\n" + "="*70)
    print("🌍 CHOIX DU DOMAINE D'APPRENTISSAGE".center(70))
    print("="*70)
    print("\nChoisissez ce que vous voulez apprendre :\n")
    
    # Trier par popularité
    domaines_tries = sorted(domaines.items(), key=lambda x: x[1].get('popularite', 99))
    
    for i, (id_domaine, info) in enumerate(domaines_tries, 1):
        emoji = info.get('emoji', '📚')
        nom = info['nom']
        type_dom = info.get('type', 'Divers')
        description = info.get('description', '')
        print(f"  {i}. {emoji} {nom:15} ({type_dom})")
        print(f"     → {description}")
        print()
    
    print(f"  {len(domaines_tries) + 1}. ➕ Créer un domaine personnalisé")
    print("  0. ↩️  Retour")
    print("="*70)
    
    choix = input("\n👉 Votre choix : ").strip()
    
    try:
        choix_int = int(choix)
        if choix_int == 0:
            return None, None
        elif 1 <= choix_int <= len(domaines_tries):
            id_domaine = domaines_tries[choix_int - 1][0]
            domaine_choisi = domaines[id_domaine]
            print(f"\n✅ Domaine sélectionné : {domaine_choisi.get('emoji', '')} {domaine_choisi['nom']}")
            return id_domaine, domaine_choisi
        elif choix_int == len(domaines_tries) + 1:
            return creer_domaine_personnalise()
    except:
        pass
    
    print("❌ Choix invalide")
    return None, None

def creer_domaine_personnalise():
    """Crée un domaine personnalisé par l'utilisateur"""
    print("\n" + "="*70)
    print("🎨 CRÉATION D'UN DOMAINE PERSONNALISÉ".center(70))
    print("="*70)
    
    nom = input("\n📝 Nom du domaine (ex: 'Électronique', 'Espagnol', 'VHDL') : ").strip()
    if not nom:
        print("❌ Annulé")
        return None, None
    
    description = input("📄 Description courte : ").strip()
    
    print("\n📂 Type de domaine :")
    print("  1. Langage de programmation")
    print("  2. Matière académique")
    print("  3. Langue étrangère")
    print("  4. Autre")
    
    type_choix = input("👉 Votre choix : ").strip()
    types = {
        "1": "Langage de programmation",
        "2": "Matière académique",
        "3": "Langue étrangère",
        "4": "Autre"
    }
    type_domaine = types.get(type_choix, "Autre")
    
    print("\n📚 Entrez les thèmes/chapitres (un par ligne, ligne vide pour terminer) :")
    themes = []
    i = 1
    while True:
        theme = input(f"  Thème {i} : ").strip()
        if not theme:
            break
        themes.append(theme)
        i += 1
    
    if not themes:
        themes = ["Concepts de base", "Niveau intermédiaire", "Niveau avancé"]
        print("⚠️  Aucun thème saisi, thèmes par défaut ajoutés")
    
    # Créer ID unique
    id_domaine = nom.lower().replace(" ", "_").replace("/", "_")
    
    # Déterminer le type d'exercice
    if type_domaine == "Langage de programmation":
        type_exercice = "code"
        langage = nom
    else:
        type_exercice = "texte"
        langage = "texte"
    
    nouveau_domaine = {
        "nom": nom,
        "emoji": "🎯",
        "type": type_domaine,
        "description": description,
        "popularite": 99,
        "themes": themes,
        "config_ia": {
            "role": f"professeur expert en {nom}",
            "langage": langage,
            "type_exercice": type_exercice,
            "verification": f"réponse sur {nom}"
        }
    }
    
    domaines = charger_domaines()
    domaines[id_domaine] = nouveau_domaine
    sauvegarder_domaines(domaines)
    
    print(f"\n✅ Domaine '{nom}' créé avec succès !")
    print(f"📊 {len(themes)} thèmes ajoutés")
    
    return id_domaine, nouveau_domaine

def obtenir_themes_domaine(id_domaine):
    """Obtient la liste des thèmes pour un domaine"""
    domaines = charger_domaines()
    if id_domaine in domaines:
        return domaines[id_domaine]["themes"]
    return []

def obtenir_config_ia(id_domaine):
    """Obtient la configuration IA pour un domaine"""
    domaines = charger_domaines()
    if id_domaine in domaines:
        return domaines[id_domaine]["config_ia"]
    return {
        "role": "professeur",
        "langage": "texte",
        "type_exercice": "texte",
        "verification": "réponse"
    }

def obtenir_nom_domaine(id_domaine):
    """Obtient le nom complet d'un domaine avec emoji"""
    domaines = charger_domaines()
    if id_domaine in domaines:
        info = domaines[id_domaine]
        emoji = info.get('emoji', '📚')
        nom = info['nom']
        return f"{emoji} {nom}"
    return "Domaine inconnu"
