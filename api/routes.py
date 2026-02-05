"""
Routes API Flask - ProjetEducationPython
Gestion complète et sécurisée de tous les endpoints
"""

from flask import request, jsonify
import sys
import os
from datetime import datetime, timedelta
import traceback

# Ajout du répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Imports de sécurité
from modules.core.security import (
    hash_password, verify_password, 
    create_access_token, create_refresh_token,
    require_auth, require_role,
    validate_password_strength
)

# Imports de validation
from modules.core.validation import (
    sanitize_string, validate_username, validate_email_address,
    validate_code_input, validate_integer, validate_json_keys,
    validate_domain
)

# Imports de logging
from modules.core.logging_config import (
    log_security_event, log_auth_attempt, log_code_execution, log_error
)

# Imports des modules métier
from modules.core.fonctions import (
    generer_exercice, verifier_reponse, analyser_verdict, 
    executer_code_securise, verifier_avec_tests, tester_fonction
)
from modules.core.progression import (
    charger_progression, mettre_a_jour_progression
)
from modules.core.domaines import (
    charger_domaines, obtenir_themes_domaine
)
from modules.core.utilisateurs import (
    lister_utilisateurs, creer_utilisateur, selectionner_utilisateur, 
    obtenir_utilisateur_actif, charger_utilisateurs
)
from modules.core.xp_systeme import (
    calculer_xp, calculer_niveau, xp_pour_prochain_niveau, SEUILS_NIVEAU
)
from modules.core.avancees import verifier_nouveaux_badges


def register_routes(app, limiter):
    """
    Enregistre toutes les routes de l'API avec sécurité et rate limiting
    
    Args:
        app: Instance Flask
        limiter: Instance Flask-Limiter
    """
    
    # ========================================================================
    # HEALTH CHECK
    # ========================================================================
    
    @app.route('/api/health', methods=['GET'])
    @limiter.limit("30 per minute")
    def health_check():
        """
        Endpoint de santé de l'API
        Rate limit: 30 requêtes par minute
        """
        try:
            return jsonify({
                'success': True,
                'data': {
                    'status': 'healthy',
                    'timestamp': datetime.now().isoformat(),
                    'version': '1.0.0'
                }
            }), 200
        except Exception as e:
            log_error(f"Health check failed: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Service unavailable'
            }), 503
    
    
    # ========================================================================
    # AUTHENTIFICATION
    # ========================================================================
    
    @app.route('/api/auth/register', methods=['POST'])
    @limiter.limit("5 per hour")
    def register():
        """
        Inscription d'un nouvel utilisateur
        Rate limit: 5 requêtes par heure
        
        Body: {username, email, password}
        Returns: {success, data: {user, access_token, refresh_token}}
        """
        try:
            # Validation du contenu
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Content-Type doit être application/json'
                }), 400
            
            data = request.get_json()
            
            # Validation des clés requises
            required_keys = ['username', 'email', 'password']
            if not validate_json_keys(data, required_keys):
                return jsonify({
                    'success': False,
                    'error': 'Champs requis: username, email, password'
                }), 400
            
            # Sanitization et validation des inputs
            username = sanitize_string(data.get('username', ''))
            email = sanitize_string(data.get('email', ''))
            password = data.get('password', '')
            
            # Validation du username
            if not validate_username(username):
                log_security_event('registration_failed', {
                    'reason': 'invalid_username',
                    'username': username
                })
                return jsonify({
                    'success': False,
                    'error': 'Username invalide (3-20 caractères alphanumériques)'
                }), 400
            
            # Validation de l'email
            if not validate_email_address(email):
                log_security_event('registration_failed', {
                    'reason': 'invalid_email',
                    'email': email
                })
                return jsonify({
                    'success': False,
                    'error': 'Adresse email invalide'
                }), 400
            
            # Validation de la force du mot de passe
            password_validation = validate_password_strength(password)
            if not password_validation['valid']:
                log_security_event('registration_failed', {
                    'reason': 'weak_password',
                    'username': username
                })
                return jsonify({
                    'success': False,
                    'error': 'Mot de passe trop faible',
                    'details': password_validation['errors']
                }), 400
            
            # Vérifier si l'utilisateur existe déjà
            utilisateurs = charger_utilisateurs()
            if username in utilisateurs:
                log_security_event('registration_failed', {
                    'reason': 'username_exists',
                    'username': username
                })
                return jsonify({
                    'success': False,
                    'error': 'Ce nom d\'utilisateur existe déjà'
                }), 409
            
            # Vérifier si l'email existe déjà
            for user_data in utilisateurs.values():
                if user_data.get('email') == email:
                    log_security_event('registration_failed', {
                        'reason': 'email_exists',
                        'email': email
                    })
                    return jsonify({
                        'success': False,
                        'error': 'Cet email est déjà utilisé'
                    }), 409
            
            # Hash du mot de passe
            password_hash = hash_password(password)
            
            # Création de l'utilisateur
            nouveau_utilisateur = {
                'username': username,
                'email': email,
                'password_hash': password_hash,
                'role': 'user',
                'created_at': datetime.now().isoformat(),
                'xp': 0,
                'niveau': 1,
                'badges': [],
                'statistiques': {
                    'exercices_total': 0,
                    'exercices_reussis': 0,
                    'streak': 0,
                    'derniere_connexion': None
                }
            }
            
            # Sauvegarder l'utilisateur
            utilisateurs[username] = nouveau_utilisateur
            creer_utilisateur(username, email=email, password_hash=password_hash, role='user')
            
            # Générer les tokens JWT
            access_token = create_access_token(username, username, 'user')
            refresh_token = create_refresh_token(username)
            
            # Log de l'événement
            log_security_event('user_registered', {
                'username': username,
                'email': email
            })
            
            # Retour sans le hash du mot de passe
            user_response = {k: v for k, v in nouveau_utilisateur.items() if k != 'password_hash'}
            
            return jsonify({
                'success': True,
                'data': {
                    'user': user_response,
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }
            }), 201
            
        except Exception as e:
            error_details = f"Erreur lors de l'inscription: {str(e)}\n{traceback.format_exc()}"
            log_error(error_details)
            print(f"\n🔴 ERREUR INSCRIPTION:\n{error_details}")  # Debug log
            return jsonify({
                'success': False,
                'error': 'Erreur interne du serveur',
                'details': str(e) if os.getenv('FLASK_ENV') == 'development' else None
            }), 500
    
    
    @app.route('/api/auth/login', methods=['POST'])
    @limiter.limit("10 per hour")
    def login():
        """
        Connexion d'un utilisateur
        Rate limit: 10 requêtes par heure
        
        Body: {username, password}
        Returns: {success, data: {user, access_token, refresh_token}}
        """
        try:
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Content-Type doit être application/json'
                }), 400
            
            data = request.get_json()
            
            # Validation des clés requises
            required_keys = ['username', 'password']
            if not validate_json_keys(data, required_keys):
                return jsonify({
                    'success': False,
                    'error': 'Champs requis: username, password'
                }), 400
            
            username = sanitize_string(data.get('username', ''))
            password = data.get('password', '')
            
            # Charger les utilisateurs
            utilisateurs = charger_utilisateurs()
            
            # Vérifier si l'utilisateur existe
            if username not in utilisateurs:
                log_auth_attempt(username, False, 'user_not_found')
                return jsonify({
                    'success': False,
                    'error': 'Identifiants invalides'
                }), 401
            
            user_data = utilisateurs[username]
            
            # Vérifier le mot de passe
            if not verify_password(password, user_data.get('password_hash', '')):
                log_auth_attempt(username, False, 'invalid_password')
                return jsonify({
                    'success': False,
                    'error': 'Identifiants invalides'
                }), 401
            
            # Mise à jour de la dernière connexion
            if 'statistiques' not in user_data:
                user_data['statistiques'] = {}
            user_data['statistiques']['derniere_connexion'] = datetime.now().isoformat()
            
            # Générer les tokens JWT
            user_role = user_data.get('role', 'user')
            access_token = create_access_token(username, username, user_role)
            refresh_token = create_refresh_token(username)
            
            # Log de l'événement
            log_auth_attempt(username, True, 'login_success')
            
            # Retour sans le hash du mot de passe
            user_response = {k: v for k, v in user_data.items() if k != 'password_hash'}
            
            return jsonify({
                'success': True,
                'data': {
                    'user': user_response,
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }
            }), 200
            
        except Exception as e:
            log_error(f"Erreur lors de la connexion: {str(e)}\n{traceback.format_exc()}")
            return jsonify({
                'success': False,
                'error': 'Erreur interne du serveur'
            }), 500
    
    
    @app.route('/api/auth/refresh', methods=['POST'])
    @limiter.limit("20 per hour")
    def refresh():
        """
        Rafraîchissement du token d'accès
        Rate limit: 20 requêtes par heure
        
        Body: {refresh_token}
        Returns: {success, data: {access_token}}
        """
        try:
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Content-Type doit être application/json'
                }), 400
            
            data = request.get_json()
            refresh_token = data.get('refresh_token')
            
            if not refresh_token:
                return jsonify({
                    'success': False,
                    'error': 'Refresh token requis'
                }), 400
            
            # Vérifier et décoder le refresh token
            try:
                import jwt
                from modules.core.security import JWT_SECRET_KEY, JWT_ALGORITHM
                
                payload = jwt.decode(refresh_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
                
                if payload.get('type') != 'refresh':
                    log_security_event('invalid_token_type', {
                        'expected': 'refresh',
                        'received': payload.get('type')
                    })
                    return jsonify({
                        'success': False,
                        'error': 'Token invalide'
                    }), 401
                
                user_id = payload.get('user_id')
                
                # Récupérer les infos utilisateur pour générer un nouveau token
                utilisateurs = charger_utilisateurs()
                if user_id not in utilisateurs:
                    return jsonify({
                        'success': False,
                        'error': 'Utilisateur non trouvé'
                    }), 404
                
                user_data = utilisateurs[user_id]
                user_role = user_data.get('role', 'user')
                
                # Générer un nouveau access token
                new_access_token = create_access_token(user_id, user_id, user_role)
                
                log_security_event('token_refreshed', {'username': user_id})
                
                return jsonify({
                    'success': True,
                    'data': {
                        'access_token': new_access_token
                    }
                }), 200
                
            except jwt.ExpiredSignatureError:
                log_security_event('refresh_token_expired', {})
                return jsonify({
                    'success': False,
                    'error': 'Refresh token expiré'
                }), 401
            except jwt.InvalidTokenError:
                log_security_event('invalid_refresh_token', {})
                return jsonify({
                    'success': False,
                    'error': 'Refresh token invalide'
                }), 401
            
        except Exception as e:
            log_error(f"Erreur lors du rafraîchissement: {str(e)}\n{traceback.format_exc()}")
            return jsonify({
                'success': False,
                'error': 'Erreur interne du serveur'
            }), 500
    
    
    @app.route('/api/auth/me', methods=['GET'])
    @require_auth
    def get_current_user():
        """
        Récupère les informations de l'utilisateur courant
        Authentification requise
        
        Returns: {success, data: {user}}
        """
        try:
            username = request.username
            
            utilisateurs = charger_utilisateurs()
            
            if username not in utilisateurs:
                return jsonify({
                    'success': False,
                    'error': 'Utilisateur non trouvé'
                }), 404
            
            user_data = utilisateurs[username]
            
            # Retour sans le hash du mot de passe
            user_response = {k: v for k, v in user_data.items() if k != 'password_hash'}
            
            return jsonify({
                'success': True,
                'data': {
                    'user': user_response
                }
            }), 200
            
        except Exception as e:
            log_error(f"Erreur lors de la récupération de l'utilisateur: {str(e)}\n{traceback.format_exc()}")
            return jsonify({
                'success': False,
                'error': 'Erreur interne du serveur'
            }), 500
    
    
    # ========================================================================
    # EXERCICES
    # ========================================================================
    
    @app.route('/api/exercices/generer', methods=['POST'])
    @limiter.limit("20 per hour")
    @require_auth
    def generer_exercice_endpoint():
        """
        Génère un nouvel exercice
        Rate limit: 20 requêtes par heure
        Authentification requise
        
        Body: {domaine, theme, difficulte}
        Returns: {success, data: {exercice}}
        """
        try:
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Content-Type doit être application/json'
                }), 400
            
            data = request.get_json()
            username = request.username
            
            # Validation des clés requises
            required_keys = ['domaine', 'theme']
            if not validate_json_keys(data, required_keys):
                return jsonify({
                    'success': False,
                    'error': 'Champs requis: domaine, theme'
                }), 400
            
            # Validation et sanitization
            domaine = sanitize_string(data.get('domaine', ''))
            theme = sanitize_string(data.get('theme', ''))
            difficulte = data.get('difficulte', 1)
            
            # Validation du domaine
            if not validate_domain(domaine):
                return jsonify({
                    'success': False,
                    'error': 'Domaine invalide'
                }), 400
            
            # Validation de la difficulté
            if not validate_integer(difficulte, 1, 5):
                return jsonify({
                    'success': False,
                    'error': 'Difficulté invalide (1-5)'
                }), 400
            
            # Génération de l'exercice
            exercice = generer_exercice(domaine, theme, difficulte)
            
            if not exercice:
                return jsonify({
                    'success': False,
                    'error': 'Impossible de générer un exercice pour ces paramètres'
                }), 404
            
            # Log de l'événement
            log_security_event('exercice_generated', {
                'username': username,
                'domaine': domaine,
                'theme': theme,
                'difficulte': difficulte
            })
            
            return jsonify({
                'success': True,
                'data': {
                    'exercice': exercice
                }
            }), 200
            
        except Exception as e:
            log_error(f"Erreur lors de la génération d'exercice: {str(e)}\n{traceback.format_exc()}")
            return jsonify({
                'success': False,
                'error': 'Erreur interne du serveur'
            }), 500
    
    
    @app.route('/api/exercices/verifier', methods=['POST'])
    @limiter.limit("30 per hour")
    @require_auth
    def verifier_reponse_endpoint():
        """
        Vérifie la réponse à un exercice
        Rate limit: 30 requêtes par heure
        Authentification requise
        
        Body: {exercice_id, reponse, exercice_data}
        Returns: {success, data: {correct, feedback, xp_gagne}}
        """
        try:
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Content-Type doit être application/json'
                }), 400
            
            data = request.get_json()
            username = request.username
            
            # Validation des clés requises
            required_keys = ['exercice_id', 'reponse', 'exercice_data']
            if not validate_json_keys(data, required_keys):
                return jsonify({
                    'success': False,
                    'error': 'Champs requis: exercice_id, reponse, exercice_data'
                }), 400
            
            exercice_id = sanitize_string(data.get('exercice_id', ''))
            reponse = data.get('reponse', '')
            exercice_data = data.get('exercice_data', {})
            
            # Vérification de la réponse
            resultat = verifier_reponse(exercice_data, reponse)
            
            # Calcul de l'XP
            xp_gagne = 0
            if resultat.get('correct', False):
                difficulte = exercice_data.get('difficulte', 1)
                xp_gagne = calculer_xp(difficulte, True)
                
                # Mise à jour de la progression
                progression = charger_progression(username)
                progression['xp'] = progression.get('xp', 0) + xp_gagne
                progression['exercices_reussis'] = progression.get('exercices_reussis', 0) + 1
                mettre_a_jour_progression(username, progression)
                
                # Vérification des nouveaux badges
                nouveaux_badges = verifier_nouveaux_badges(username)
                resultat['nouveaux_badges'] = nouveaux_badges
            
            # Log de l'événement
            log_security_event('exercice_verified', {
                'username': username,
                'exercice_id': exercice_id,
                'correct': resultat.get('correct', False),
                'xp_gagne': xp_gagne
            })
            
            return jsonify({
                'success': True,
                'data': {
                    'correct': resultat.get('correct', False),
                    'feedback': resultat.get('feedback', ''),
                    'xp_gagne': xp_gagne,
                    'nouveaux_badges': resultat.get('nouveaux_badges', [])
                }
            }), 200
            
        except Exception as e:
            log_error(f"Erreur lors de la vérification: {str(e)}\n{traceback.format_exc()}")
            return jsonify({
                'success': False,
                'error': 'Erreur interne du serveur'
            }), 500
    
    
    @app.route('/api/exercices/executer', methods=['POST'])
    @limiter.limit("15 per hour")
    @require_auth
    def executer_code_endpoint():
        """
        Exécute du code Python de manière sécurisée
        Rate limit: 15 requêtes par heure
        Authentification requise
        
        Body: {code, inputs}
        Returns: {success, data: {output, errors}}
        """
        try:
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Content-Type doit être application/json'
                }), 400
            
            data = request.get_json()
            username = request.username
            
            # Validation des clés requises
            required_keys = ['code']
            if not validate_json_keys(data, required_keys):
                return jsonify({
                    'success': False,
                    'error': 'Champ requis: code'
                }), 400
            
            code = data.get('code', '')
            inputs = data.get('inputs', [])
            
            # Validation du code
            if not validate_code_input(code):
                log_security_event('dangerous_code_attempt', {
                    'username': username,
                    'reason': 'Invalid code input',
                    'code_preview': code[:100]
                })
                return jsonify({
                    'success': False,
                    'error': 'Code refusé pour des raisons de sécurité'
                }), 400
            
            # Exécution sécurisée du code
            resultat = executer_code_securise(code, inputs)
            
            # Log de l'événement
            log_code_execution(username, code, resultat.get('success', False))
            
            return jsonify({
                'success': True,
                'data': {
                    'output': resultat.get('output', ''),
                    'errors': resultat.get('errors', ''),
                    'execution_time': resultat.get('execution_time', 0)
                }
            }), 200
            
        except Exception as e:
            log_error(f"Erreur lors de l'exécution: {str(e)}\n{traceback.format_exc()}")
            return jsonify({
                'success': False,
                'error': 'Erreur interne du serveur'
            }), 500
    
    
    @app.route('/api/exercices/tester', methods=['POST'])
    @limiter.limit("30 per hour")
    @require_auth
    def tester_fonction_endpoint():
        """
        Teste une fonction avec des cas de test
        Rate limit: 30 requêtes par heure
        Authentification requise
        
        Body: {code, tests}
        Returns: {success, data: {results, all_passed}}
        """
        try:
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Content-Type doit être application/json'
                }), 400
            
            data = request.get_json()
            username = request.username
            
            # Validation des clés requises
            required_keys = ['code', 'tests']
            if not validate_json_keys(data, required_keys):
                return jsonify({
                    'success': False,
                    'error': 'Champs requis: code, tests'
                }), 400
            
            code = data.get('code', '')
            tests = data.get('tests', [])
            
            # Validation du code
            if not validate_code_input(code):
                log_security_event('dangerous_code_attempt', {
                    'username': username,
                    'reason': 'Invalid code input',
                    'code_preview': code[:100]
                })
                return jsonify({
                    'success': False,
                    'error': 'Code refusé pour des raisons de sécurité'
                }), 400
            
            # Exécution des tests
            resultat = tester_fonction(code, tests)
            
            # Log de l'événement
            log_security_event('function_tested', {
                'username': username,
                'num_tests': len(tests),
                'all_passed': resultat.get('all_passed', False)
            })
            
            return jsonify({
                'success': True,
                'data': {
                    'results': resultat.get('results', []),
                    'all_passed': resultat.get('all_passed', False),
                    'passed_count': resultat.get('passed_count', 0),
                    'total_count': resultat.get('total_count', 0)
                }
            }), 200
            
        except Exception as e:
            log_error(f"Erreur lors du test: {str(e)}\n{traceback.format_exc()}")
            return jsonify({
                'success': False,
                'error': 'Erreur interne du serveur'
            }), 500
    
    
    # ========================================================================
    # PROGRESSION
    # ========================================================================
    
    @app.route('/api/progression', methods=['GET'])
    @require_auth
    def get_progression():
        """
        Récupère la progression de l'utilisateur courant
        Authentification requise
        
        Returns: {success, data: {progression}}
        """
        try:
            username = request.username
            
            progression = charger_progression(username)
            
            if not progression:
                return jsonify({
                    'success': False,
                    'error': 'Progression non trouvée'
                }), 404
            
            return jsonify({
                'success': True,
                'data': {
                    'progression': progression
                }
            }), 200
            
        except Exception as e:
            log_error(f"Erreur lors de la récupération de la progression: {str(e)}\n{traceback.format_exc()}")
            return jsonify({
                'success': False,
                'error': 'Erreur interne du serveur'
            }), 500
    
    
    @app.route('/api/progression/update', methods=['POST'])
    @require_auth
    def update_progression():
        """
        Met à jour la progression de l'utilisateur courant
        Authentification requise
        
        Body: {progression}
        Returns: {success, data: {progression}}
        """
        try:
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Content-Type doit être application/json'
                }), 400
            
            data = request.get_json()
            username = request.username
            
            # Validation des clés requises
            required_keys = ['progression']
            if not validate_json_keys(data, required_keys):
                return jsonify({
                    'success': False,
                    'error': 'Champ requis: progression'
                }), 400
            
            nouvelle_progression = data.get('progression', {})
            
            # Mise à jour de la progression
            mettre_a_jour_progression(username, nouvelle_progression)
            
            # Log de l'événement
            log_security_event('progression_updated', {
                'username': username
            })
            
            return jsonify({
                'success': True,
                'data': {
                    'progression': nouvelle_progression
                }
            }), 200
            
        except Exception as e:
            log_error(f"Erreur lors de la mise à jour de la progression: {str(e)}\n{traceback.format_exc()}")
            return jsonify({
                'success': False,
                'error': 'Erreur interne du serveur'
            }), 500
    
    
    @app.route('/api/progression/stats', methods=['GET'])
    @require_auth
    def get_progression_stats():
        """
        Récupère les statistiques de progression de l'utilisateur
        Authentification requise
        
        Returns: {success, data: {stats}}
        """
        try:
            username = request.username
            
            progression = charger_progression(username)
            
            if not progression:
                return jsonify({
                    'success': False,
                    'error': 'Progression non trouvée'
                }), 404
            
            # Calcul des statistiques
            xp_total = progression.get('xp', 0)
            niveau_actuel = calculer_niveau(xp_total)
            xp_prochain_niveau = xp_pour_prochain_niveau(xp_total)
            exercices_total = progression.get('exercices_total', 0)
            exercices_reussis = progression.get('exercices_reussis', 0)
            
            taux_reussite = 0
            if exercices_total > 0:
                taux_reussite = (exercices_reussis / exercices_total) * 100
            
            stats = {
                'xp_total': xp_total,
                'niveau_actuel': niveau_actuel,
                'xp_prochain_niveau': xp_prochain_niveau,
                'exercices_total': exercices_total,
                'exercices_reussis': exercices_reussis,
                'taux_reussite': round(taux_reussite, 2),
                'domaines': progression.get('domaines', {}),
                'badges': progression.get('badges', [])
            }
            
            return jsonify({
                'success': True,
                'data': {
                    'stats': stats
                }
            }), 200
            
        except Exception as e:
            log_error(f"Erreur lors de la récupération des stats: {str(e)}\n{traceback.format_exc()}")
            return jsonify({
                'success': False,
                'error': 'Erreur interne du serveur'
            }), 500
    
    
    # ========================================================================
    # DOMAINES
    # ========================================================================
    
    @app.route('/api/domaines', methods=['GET'])
    @limiter.limit("50 per hour")
    @require_auth
    def get_domaines():
        """
        Récupère la liste de tous les domaines
        Rate limit: 50 requêtes par heure
        Authentification requise
        
        Returns: {success, data: {domaines}}
        """
        try:
            domaines = charger_domaines()
            
            if not domaines:
                return jsonify({
                    'success': False,
                    'error': 'Aucun domaine trouvé'
                }), 404
            
            return jsonify({
                'success': True,
                'data': {
                    'domaines': domaines
                }
            }), 200
            
        except Exception as e:
            log_error(f"Erreur lors de la récupération des domaines: {str(e)}\n{traceback.format_exc()}")
            return jsonify({
                'success': False,
                'error': 'Erreur interne du serveur'
            }), 500
    
    
    @app.route('/api/domaines/<domaine_id>/themes', methods=['GET'])
    @require_auth
    def get_themes_domaine(domaine_id):
        """
        Récupère les thèmes d'un domaine spécifique
        Authentification requise
        
        Args:
            domaine_id: Identifiant du domaine
            
        Returns: {success, data: {themes}}
        """
        try:
            # Validation et sanitization du domaine_id
            domaine_id = sanitize_string(domaine_id)
            
            if not validate_domain(domaine_id):
                return jsonify({
                    'success': False,
                    'error': 'Domaine invalide'
                }), 400
            
            themes = obtenir_themes_domaine(domaine_id)
            
            if themes is None:
                return jsonify({
                    'success': False,
                    'error': 'Domaine non trouvé'
                }), 404
            
            return jsonify({
                'success': True,
                'data': {
                    'domaine': domaine_id,
                    'themes': themes
                }
            }), 200
            
        except Exception as e:
            log_error(f"Erreur lors de la récupération des thèmes: {str(e)}\n{traceback.format_exc()}")
            return jsonify({
                'success': False,
                'error': 'Erreur interne du serveur'
            }), 500
    
    
    # ========================================================================
    # UTILISATEURS
    # ========================================================================
    
    @app.route('/api/users/<username>/stats', methods=['GET'])
    @require_auth
    def get_user_stats(username):
        """
        Récupère les statistiques d'un utilisateur
        Authentification requise
        Ownership ou admin requis
        
        Args:
            username: Nom d'utilisateur
            
        Returns: {success, data: {stats}}
        """
        try:
            current_user = request.username
            
            # Sanitization
            username = sanitize_string(username)
            
            # Vérification des permissions
            utilisateurs = charger_utilisateurs()
            if username != current_user:
                # Vérifier si l'utilisateur actuel est admin
                if utilisateurs.get(current_user, {}).get('role') != 'admin':
                    log_security_event('unauthorized_stats_access', {
                        'requester': current_user,
                        'target': username
                    })
                    return jsonify({
                        'success': False,
                        'error': 'Accès non autorisé'
                    }), 403
            
            # Vérifier si l'utilisateur existe
            if username not in utilisateurs:
                return jsonify({
                    'success': False,
                    'error': 'Utilisateur non trouvé'
                }), 404
            
            # Récupérer la progression
            progression = charger_progression(username)
            user_data = utilisateurs[username]
            
            # Calcul des statistiques
            xp_total = progression.get('xp', 0)
            niveau_actuel = calculer_niveau(xp_total)
            
            stats = {
                'username': username,
                'niveau': niveau_actuel,
                'xp': xp_total,
                'badges': progression.get('badges', []),
                'exercices_total': progression.get('exercices_total', 0),
                'exercices_reussis': progression.get('exercices_reussis', 0),
                'statistiques': user_data.get('statistiques', {})
            }
            
            return jsonify({
                'success': True,
                'data': {
                    'stats': stats
                }
            }), 200
            
        except Exception as e:
            log_error(f"Erreur lors de la récupération des stats utilisateur: {str(e)}\n{traceback.format_exc()}")
            return jsonify({
                'success': False,
                'error': 'Erreur interne du serveur'
            }), 500
    
    
    @app.route('/api/users/<username>/profile', methods=['PUT'])
    @require_auth
    def update_user_profile(username):
        """
        Met à jour le profil d'un utilisateur
        Authentification requise
        Ownership ou admin requis
        
        Args:
            username: Nom d'utilisateur
            
        Body: {email, bio, preferences}
        Returns: {success, data: {user}}
        """
        try:
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Content-Type doit être application/json'
                }), 400
            
            current_user = request.username
            username = sanitize_string(username)
            
            # Vérification des permissions
            utilisateurs = charger_utilisateurs()
            if username != current_user:
                if utilisateurs.get(current_user, {}).get('role') != 'admin':
                    log_security_event('unauthorized_profile_update', {
                        'requester': current_user,
                        'target': username
                    })
                    return jsonify({
                        'success': False,
                        'error': 'Accès non autorisé'
                    }), 403
            
            # Vérifier si l'utilisateur existe
            if username not in utilisateurs:
                return jsonify({
                    'success': False,
                    'error': 'Utilisateur non trouvé'
                }), 404
            
            data = request.get_json()
            user_data = utilisateurs[username]
            
            # Mise à jour de l'email si fourni
            if 'email' in data:
                email = sanitize_string(data['email'])
                if not validate_email_address(email):
                    return jsonify({
                        'success': False,
                        'error': 'Email invalide'
                    }), 400
                user_data['email'] = email
            
            # Mise à jour de la bio si fournie
            if 'bio' in data:
                user_data['bio'] = sanitize_string(data['bio'])
            
            # Mise à jour des préférences si fournies
            if 'preferences' in data:
                if 'preferences' not in user_data:
                    user_data['preferences'] = {}
                user_data['preferences'].update(data['preferences'])
            
            # Sauvegarder les modifications
            utilisateurs[username] = user_data
            
            # Log de l'événement
            log_security_event('profile_updated', {
                'username': username,
                'updated_by': current_user
            })
            
            # Retour sans le hash du mot de passe
            user_response = {k: v for k, v in user_data.items() if k != 'password_hash'}
            
            return jsonify({
                'success': True,
                'data': {
                    'user': user_response
                }
            }), 200
            
        except Exception as e:
            log_error(f"Erreur lors de la mise à jour du profil: {str(e)}\n{traceback.format_exc()}")
            return jsonify({
                'success': False,
                'error': 'Erreur interne du serveur'
            }), 500
    
    
    # ========================================================================
    # XP ET BADGES
    # ========================================================================
    
    @app.route('/api/xp', methods=['GET'])
    @require_auth
    def get_xp():
        """
        Récupère les informations XP de l'utilisateur courant
        Authentification requise
        
        Returns: {success, data: {xp_info}}
        """
        try:
            username = request.username
            
            progression = charger_progression(username)
            xp_total = progression.get('xp', 0)
            niveau_actuel = calculer_niveau(xp_total)
            xp_prochain = xp_pour_prochain_niveau(xp_total)
            
            # Calcul de l'XP dans le niveau actuel
            xp_niveau_min = SEUILS_NIVEAU.get(niveau_actuel, 0)
            xp_niveau_max = SEUILS_NIVEAU.get(niveau_actuel + 1, xp_niveau_min + 1000)
            xp_dans_niveau = xp_total - xp_niveau_min
            xp_requis_niveau = xp_niveau_max - xp_niveau_min
            
            pourcentage = 0
            if xp_requis_niveau > 0:
                pourcentage = (xp_dans_niveau / xp_requis_niveau) * 100
            
            xp_info = {
                'xp_total': xp_total,
                'niveau_actuel': niveau_actuel,
                'xp_prochain_niveau': xp_prochain,
                'xp_dans_niveau': xp_dans_niveau,
                'xp_requis_niveau': xp_requis_niveau,
                'pourcentage_niveau': round(pourcentage, 2)
            }
            
            return jsonify({
                'success': True,
                'data': {
                    'xp_info': xp_info
                }
            }), 200
            
        except Exception as e:
            log_error(f"Erreur lors de la récupération de l'XP: {str(e)}\n{traceback.format_exc()}")
            return jsonify({
                'success': False,
                'error': 'Erreur interne du serveur'
            }), 500
    
    
    @app.route('/api/badges', methods=['GET'])
    @require_auth
    def get_badges():
        """
        Récupère les badges de l'utilisateur courant
        Authentification requise
        
        Returns: {success, data: {badges}}
        """
        try:
            username = request.username
            
            progression = charger_progression(username)
            badges = progression.get('badges', [])
            
            # Enrichir les badges avec des informations supplémentaires
            badges_enrichis = []
            for badge in badges:
                badge_info = {
                    'id': badge.get('id', ''),
                    'nom': badge.get('nom', ''),
                    'description': badge.get('description', ''),
                    'icone': badge.get('icone', ''),
                    'date_obtention': badge.get('date_obtention', ''),
                    'rarete': badge.get('rarete', 'commun')
                }
                badges_enrichis.append(badge_info)
            
            return jsonify({
                'success': True,
                'data': {
                    'badges': badges_enrichis,
                    'total': len(badges_enrichis)
                }
            }), 200
            
        except Exception as e:
            log_error(f"Erreur lors de la récupération des badges: {str(e)}\n{traceback.format_exc()}")
            return jsonify({
                'success': False,
                'error': 'Erreur interne du serveur'
            }), 500
    
    
    # ========================================================================
    # ADMINISTRATION
    # ========================================================================
    
    @app.route('/api/admin/users', methods=['GET'])
    @require_role('admin')
    def admin_get_users():
        """
        Liste tous les utilisateurs (admin seulement)
        Authentification et rôle admin requis
        
        Returns: {success, data: {users}}
        """
        try:
            utilisateurs = charger_utilisateurs()
            
            # Retourner les utilisateurs sans les hashes de mots de passe
            users_list = []
            for username, user_data in utilisateurs.items():
                user_info = {k: v for k, v in user_data.items() if k != 'password_hash'}
                user_info['username'] = username
                users_list.append(user_info)
            
            return jsonify({
                'success': True,
                'data': {
                    'users': users_list,
                    'total': len(users_list)
                }
            }), 200
            
        except Exception as e:
            log_error(f"Erreur lors de la liste des utilisateurs: {str(e)}\n{traceback.format_exc()}")
            return jsonify({
                'success': False,
                'error': 'Erreur interne du serveur'
            }), 500
    
    
    @app.route('/api/admin/users/<username>', methods=['DELETE'])
    @require_role('admin')
    def admin_delete_user(username):
        """
        Supprime un utilisateur (admin seulement)
        Authentification et rôle admin requis
        
        Args:
            username: Nom d'utilisateur à supprimer
            
        Returns: {success, message}
        """
        try:
            username = sanitize_string(username)
            current_user = request.username
            
            # Empêcher la suppression de soi-même
            if username == current_user:
                return jsonify({
                    'success': False,
                    'error': 'Vous ne pouvez pas supprimer votre propre compte'
                }), 400
            
            utilisateurs = charger_utilisateurs()
            
            # Vérifier si l'utilisateur existe
            if username not in utilisateurs:
                return jsonify({
                    'success': False,
                    'error': 'Utilisateur non trouvé'
                }), 404
            
            # Supprimer l'utilisateur
            del utilisateurs[username]
            
            # Log de l'événement
            log_security_event('user_deleted', {
                'username': username,
                'deleted_by': current_user
            })
            
            return jsonify({
                'success': True,
                'message': f'Utilisateur {username} supprimé avec succès'
            }), 200
            
        except Exception as e:
            log_error(f"Erreur lors de la suppression de l'utilisateur: {str(e)}\n{traceback.format_exc()}")
            return jsonify({
                'success': False,
                'error': 'Erreur interne du serveur'
            }), 500
    
    
    # ========================================================================
    # GESTION DES ERREURS
    # ========================================================================
    
    @app.errorhandler(404)
    def not_found(error):
        """Gestionnaire d'erreur 404"""
        return jsonify({
            'success': False,
            'error': 'Endpoint non trouvé'
        }), 404
    
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Gestionnaire d'erreur 405"""
        return jsonify({
            'success': False,
            'error': 'Méthode HTTP non autorisée'
        }), 405
    
    
    @app.errorhandler(429)
    def ratelimit_handler(error):
        """Gestionnaire d'erreur de rate limiting"""
        log_security_event('rate_limit_exceeded', {
            'ip': request.remote_addr,
            'endpoint': request.endpoint
        })
        return jsonify({
            'success': False,
            'error': 'Trop de requêtes. Veuillez réessayer plus tard.'
        }), 429
    
    
    @app.errorhandler(500)
    def internal_error(error):
        """Gestionnaire d'erreur 500"""
        log_error(f"Erreur interne du serveur: {str(error)}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': 'Erreur interne du serveur'
        }), 500


