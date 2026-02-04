"""
Routes API - Tous les endpoints REST
"""
from flask import request, jsonify
import sys
import os

# Ajouter le dossier parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Imports des modules backend
from modules.core.fonctions import (
    generer_exercice, 
    verifier_reponse, 
    analyser_verdict,
    executer_code_securise,
    verifier_avec_tests,
    tester_fonction
)
from modules.core.progression import (
    charger_progression, 
    mettre_a_jour_progression, 
    afficher_progression
)
from modules.core.domaines import charger_domaines, obtenir_themes_domaine
from modules.core.utilisateurs import (
    lister_utilisateurs, 
    creer_utilisateur, 
    selectionner_utilisateur,
    obtenir_utilisateur_actif
)
from modules.core.xp_systeme import (
    afficher_info_xp,
    calculer_xp,
    calculer_niveau,
    xp_pour_prochain_niveau
)
from modules.core.avancees import verifier_nouveaux_badges

def register_routes(app):
    """Enregistre toutes les routes de l'API sur l'app Flask"""

    # ==================== SANTÉ API ====================

    @app.route('/api/health', methods=['GET'])
    def api_health():
        """Vérifie que l'API fonctionne"""
        return jsonify({
            'success': True,
            'message': 'API fonctionnelle',
            'version': '1.0.0',
            'endpoints': 10
        }), 200

    # ==================== AUTHENTIFICATION ====================

    @app.route('/api/auth/register', methods=['POST'])
    def api_register():
        """
        Inscription d'un nouvel utilisateur
        
        Body JSON:
        {
            "username": "Djoulde",
            "email": "d.djoulde.d@gmail.com",
            "password": "motdepasse123"
        }
        """
        try:
            data = request.json or {}
            username = data.get('username', '')
            email = data.get('email', '')
            password = data.get('password', '')
            
            if not username or not email or not password:
                return jsonify({
                    'success': False,
                    'error': 'Nom d\'utilisateur, email et mot de passe requis'
                }), 400
            
            # Vérifier si l'utilisateur existe déjà
            utilisateurs = lister_utilisateurs()
            for user in utilisateurs:
                if user.get('nom') == username or user.get('email') == email:
                    return jsonify({
                        'success': False,
                        'error': 'Cet utilisateur existe déjà'
                    }), 400
            
            # Créer l'utilisateur
            user = creer_utilisateur(username, niveau=1, email=email)
            
            # Sélectionner automatiquement l'utilisateur
            selectionner_utilisateur(username)
            
            return jsonify({
                'success': True,
                'message': 'Utilisateur créé avec succès',
                'user': {
                    'id': user.get('nom'),
                    'username': user.get('nom'),
                    'email': user.get('email', email),
                    'niveau': user.get('niveau', 1)
                }
            }), 201
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de la création du compte'
            }), 500

    @app.route('/api/auth/login', methods=['POST'])
    def api_login():
        """
        Connexion d'un utilisateur existant
        
        Body JSON:
        {
            "username": "Djoulde",
            "password": "motdepasse123"
        }
        """
        try:
            data = request.json or {}
            username = data.get('username', '')
            password = data.get('password', '')
            
            if not username:
                return jsonify({
                    'success': False,
                    'error': 'Nom d\'utilisateur requis'
                }), 400
            
            # Vérifier si l'utilisateur existe
            utilisateurs = lister_utilisateurs()
            user_found = None
            for user in utilisateurs:
                if user.get('nom') == username:
                    user_found = user
                    break
            
            if not user_found:
                return jsonify({
                    'success': False,
                    'error': 'Utilisateur non trouvé'
                }), 404
            
            # Sélectionner l'utilisateur
            selectionner_utilisateur(username)
            
            return jsonify({
                'success': True,
                'message': 'Connexion réussie',
                'user': {
                    'id': user_found.get('nom'),
                    'username': user_found.get('nom'),
                    'email': user_found.get('email', ''),
                    'niveau': user_found.get('niveau', 1)
                }
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de la connexion'
            }), 500

    # ==================== EXERCICES ====================

    @app.route('/api/exercices/generer', methods=['POST'])
    def api_generer_exercice():
        """
        Génère un exercice avec l'IA
        
        Body JSON:
        {
            "niveau": 2,
            "theme": "Boucles",
            "domaine": "python"
        }
        
        Returns:
        {
            "success": true,
            "exercice": "...",
            "niveau": 2,
            "theme": "Boucles"
        }
        """
        try:
            data = request.json or {}
            niveau = data.get('niveau', 1)
            theme = data.get('theme', 'Variables')
            domaine = data.get('domaine', 'python')
            
            # Générer l'exercice
            exercice = generer_exercice(niveau, theme, domaine)
            
            return jsonify({
                'success': True,
                'exercice': exercice,
                'niveau': niveau,
                'theme': theme,
                'domaine': domaine
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de la generation de l\'exercice'
                }), 500

    @app.route('/api/exercices/verifier', methods=['POST'])
    def api_verifier_exercice():
        """
        Vérifie une solution avec l'IA
        
        Body JSON:
        {
            "exercice": "Créez une fonction...",
            "solution": "def ma_fonction():\\n    return 42"
        }
        
        Returns:
        {
            "success": true,
            "verification": "...",
            "reussi": true/false
        }
        """
        try:
            data = request.json or {}
            exercice = data.get('exercice', '')
            solution = data.get('solution', '')
            
            if not exercice or not solution:
                return jsonify({
                    'success': False,
                    'error': 'Exercice et solution requis'
                }), 400
            
            # Vérifier avec l'IA
            verification = verifier_reponse(exercice, solution)
            reussi = analyser_verdict(verification)
            
            return jsonify({
                'success': True,
                'verification': verification,
                'reussi': reussi,
                'solution': solution
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de la verification'
                }), 500

    @app.route('/api/exercices/executer', methods=['POST'])
    def api_executer_code():
        """
        Exécute du code Python de manière sécurisée
        
        Body JSON:
        {
            "code": "print('Hello')",
            "timeout": 5
        }
        
        Returns:
        {
            "success": true,
            "output": "Hello\\n",
            "error": "",
            "timeout": false
        }
        """
        try:
            data = request.json or {}
            code = data.get('code', '')
            timeout = data.get('timeout', 5)
            
            if not code:
                return jsonify({
                    'success': False,
                    'error': 'Code requis'
                }), 400
            
            # Exécuter le code de manière sécurisée
            resultat = executer_code_securise(code, timeout)
            
            # Retirer l'environnement (non sérialisable en JSON)
            if 'environnement' in resultat:
                del resultat['environnement']
            
            return jsonify(resultat), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de l\'execution'
                }), 500

    @app.route('/api/exercices/tester', methods=['POST'])
    def api_tester_code():
        """
        Teste du code avec plusieurs cas de test
        
        Body JSON:
        {
            "code": "def fonction(x):\\n    return x * 2",
            "tests": [["fonction(5)", 10], ["fonction(3)", 6]]
        }
        
        Returns:
        {
            "success": true,
            "tests_reussis": 2,
            "tests_total": 2,
            "details": [...]
        }
        """
        try:
            data = request.json or {}
            code = data.get('code', '')
            tests = data.get('tests', [])
            
            if not code or not tests:
                return jsonify({
                    'success': False,
                    'error': 'Code et tests requis'
                }), 400
            
            # Vérifier avec les tests
            resultat = verifier_avec_tests(code, tests)
            
            return jsonify(resultat), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Erreur lors des tests'
            }), 500

        # ==================== PROGRESSION ====================

    @app.route('/api/progression', methods=['GET'])
    def api_obtenir_progression():
        """
        Récupère la progression de l'utilisateur actuel
        
        Returns:
        {
            "success": true,
            "progression": {...}
        }
        """
        try:
            progression = charger_progression()
            
            return jsonify({
                'success': True,
                'progression': progression
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Erreur lors du chargement de la progression'
                }), 500

    @app.route('/api/progression/update', methods=['POST'])
    def api_update_progression():
        """
        Met à jour la progression après un exercice
        
        Body JSON:
        {
            "theme": "Boucles",
            "reussi": true,
            "domaine": "python"
        }
        
        Returns:
        {
            "success": true,
            "message": "Progression mise à jour"
        }
        """
        try:
            data = request.json or {}
            theme = data.get('theme')
            reussi = data.get('reussi', False)
            domaine = data.get('domaine', 'python')
            
            if not theme:
                return jsonify({
                    'success': False,
                    'error': 'Theme requis'
                }), 400
            
            # Mettre à jour la progression
            mettre_a_jour_progression(theme, reussi, domaine)
            
            return jsonify({
                'success': True,
                'message': 'Progression mise a jour',
                'theme': theme,
                'reussi': reussi
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de la mise a jour'
                }), 500

    @app.route('/api/progression/stats', methods=['GET'])
    def api_stats_progression():
        """
        Récupère les statistiques de progression
        
        Returns:
        {
            "success": true,
            "stats": {
                "total_exercices": 50,
                "reussis": 40,
                "taux_reussite": 80.0
            }
        }
        """
        try:
            progression = charger_progression()
            
            # Calculer les stats
            total = 0
            reussis = 0
            
            for domaine, data in progression.get('domaines', {}).items():
                for theme, stats in data.items():
                    if isinstance(stats, dict):
                        total += stats.get('tentatives', 0)
                        reussis += stats.get('reussites', 0)
            
            taux = (reussis / total * 100) if total > 0 else 0
            
            return jsonify({
                'success': True,
                'stats': {
                    'total_exercices': total,
                    'reussis': reussis,
                    'taux_reussite': round(taux, 2),
                    'niveau': progression.get('niveau_global', 1),
                    'xp': progression.get('xp', 0)
                }
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

        # ==================== DOMAINES ====================

    @app.route('/api/domaines', methods=['GET'])
    def api_lister_domaines():
        """
        Liste tous les domaines disponibles
        
        Returns:
        {
            "success": true,
            "domaines": {...}
        }
        """
        try:
            domaines = charger_domaines()
            
            return jsonify({
                'success': True,
                'domaines': domaines,
                'count': len(domaines)
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Erreur lors du chargement des domaines'
                }), 500

    @app.route('/api/domaines/<domaine_id>/themes', methods=['GET'])
    def api_themes_domaine(domaine_id):
        """
        Liste les thèmes d'un domaine spécifique
        
        Returns:
        {
            "success": true,
            "themes": [...]
        }
        """
        try:
            themes = obtenir_themes_domaine(domaine_id)
            
            if not themes:
                return jsonify({
                    'success': False,
                    'error': f'Domaine {domaine_id} introuvable'
                }), 404
            
            return jsonify({
                'success': True,
                'domaine': domaine_id,
                'themes': themes,
                'count': len(themes)
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'message': f'Erreur lors du chargement des themes du domaine {domaine_id}'
            }), 500

        # ==================== UTILISATEURS ====================

    @app.route('/api/utilisateurs', methods=['GET'])
    def api_lister_utilisateurs():
        """
        Liste tous les utilisateurs
        
        Returns:
        {
            "success": true,
            "utilisateurs": [...],
            "actuel": "nom_utilisateur"
        }
        """
        try:
            utilisateurs = lister_utilisateurs()
            actuel = obtenir_utilisateur_actif()
            
            return jsonify({
                'success': True,
                'utilisateurs': utilisateurs,
                'actuel': actuel,
                'count': len(utilisateurs)
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Erreur lors du chargement des utilisateurs'
                }), 500

    @app.route('/api/utilisateurs/creer', methods=['POST'])
    def api_creer_utilisateur():
        """
        Crée un nouvel utilisateur
        
        Body JSON:
        {
            "nom": "Mamad"
        }
        
        Returns:
        {
            "success": true,
            "message": "Utilisateur créé",
            "nom": "Mamad"
        }
        """
        try:
            data = request.json or {}
            nom = data.get('nom', '').strip()
            
            if not nom:
                return jsonify({
                    'success': False,
                    'error': 'Nom d\'utilisateur requis'
                }), 400
            
            # Créer l'utilisateur
            resultat = creer_utilisateur(nom)
            
            if resultat:
                return jsonify({
                    'success': True,
                    'message': f'Utilisateur {nom} cree avec succes',
                    'nom': nom
                }), 201
            else:
                return jsonify({
                    'success': False,
                    'error': 'Erreur lors de la creation (nom deja utilise ?)'
                }), 400
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de la creation de l\'utilisateur'
                }), 500

    @app.route('/api/utilisateurs/selectionner', methods=['POST'])
    def api_selectionner_utilisateur():
        """
        Sélectionne un utilisateur actif
        
        Body JSON:
        {
            "nom": "Mamad"
        }
        
        Returns:
        {
            "success": true,
            "message": "Utilisateur sélectionné",
            "nom": "Mamad"
        }
        """
        try:
            data = request.json or {}
            nom = data.get('nom', '').strip()
            
            if not nom:
                return jsonify({
                    'success': False,
                    'error': 'Nom d\'utilisateur requis'
                }), 400
            
            # Sélectionner l'utilisateur
            resultat = selectionner_utilisateur(nom)
            
            if resultat:
                return jsonify({
                    'success': True,
                    'message': f'Utilisateur {nom} selectionne',
                    'nom': nom
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': f'Utilisateur {nom} introuvable'
                }), 404
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de la selection'
            }), 500

        # ==================== BADGES & XP ====================

    @app.route('/api/badges', methods=['GET'])
    def api_obtenir_badges():
        """
        Liste les badges de l'utilisateur
        
        Returns:
        {
            "success": true,
            "badges": [...],
            "nouveaux": [...]
        }
        """
        try:
            # Vérifier les nouveaux badges
            nouveaux = verifier_nouveaux_badges()
            
            # Charger la progression pour obtenir tous les badges
            progression = charger_progression()
            badges = progression.get('badges_obtenus', [])
            
            return jsonify({
                'success': True,
                'badges': badges,
                'nouveaux': nouveaux,
                'count': len(badges)
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Erreur lors du chargement des badges'
                }), 500

    @app.route('/api/xp', methods=['GET'])
    def api_info_xp():
        """
        Récupère les informations XP de l'utilisateur
        
        Returns:
        {
            "success": true,
            "xp": 1250,
            "niveau": 5,
            "xp_prochain_niveau": 1500
        }
        """
        try:
            progression = charger_progression()
            xp_actuel = progression.get('xp', 0)
            niveau_actuel = calculer_niveau(xp_actuel)
            
            # Calculer l'XP nécessaire pour le prochain niveau
            xp_manquant = xp_pour_prochain_niveau(xp_actuel)
            
            # Si niveau max atteint
            if xp_manquant == 0:
                return jsonify({
                    'success': True,
                    'xp': xp_actuel,
                    'niveau': niveau_actuel,
                    'niveau_max': True,
                    'xp_prochain_niveau': 0,
                    'progression_niveau': 100,
                    'xp_requis_niveau': 0
                }), 200
            
            # Calculer le seuil du prochain niveau
            from modules.core.xp_systeme import SEUILS_NIVEAU
            prochain_niveau = niveau_actuel + 1
            seuil_prochain = SEUILS_NIVEAU.get(prochain_niveau, 0)
            xp_debut_niveau = SEUILS_NIVEAU.get(niveau_actuel, 0)
            
            # Calculer la progression dans le niveau actuel (en %)
            xp_dans_niveau = xp_actuel - xp_debut_niveau
            xp_total_niveau = seuil_prochain - xp_debut_niveau
            progression_pct = int((xp_dans_niveau / xp_total_niveau) * 100) if xp_total_niveau > 0 else 0
            
            return jsonify({
                'success': True,
                'xp': xp_actuel,
                'niveau': niveau_actuel,
                'niveau_max': False,
                'xp_prochain_niveau': seuil_prochain,
                'progression_niveau': progression_pct,
                'xp_requis_niveau': xp_manquant
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Erreur lors du calcul XP'
            }), 500

    # ==================== GESTION D'ERREURS ====================

    @app.errorhandler(404)
    def not_found(error):
        """Gestion des erreurs 404"""
        return jsonify({
            'success': False,
            'error': 'Endpoint introuvable',
            'code': 404
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Gestion des erreurs 500"""
        return jsonify({
            'success': False,
            'error': 'Erreur interne du serveur',
            'code': 500
        }), 500

    @app.errorhandler(405)
    def method_not_allowed(error):
        """Gestion des erreurs 405 (méthode HTTP non autorisée)"""
        return jsonify({
            'success': False,
            'error': 'Methode HTTP non autorisee',
            'code': 405
        }), 405

