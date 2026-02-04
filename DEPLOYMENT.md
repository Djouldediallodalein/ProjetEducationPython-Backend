# 🚀 Guide de Déploiement Production - PyQuest API

## Vue d'ensemble

Ce guide couvre le déploiement sécurisé de l'API PyQuest en production avec Gunicorn, Nginx, et toutes les meilleures pratiques de sécurité.

---

## 📋 Prérequis

- **OS** : Ubuntu 20.04+ ou Debian 11+ (recommandé)
- **Python** : 3.9+
- **RAM** : Minimum 2GB
- **Domaine** : Avec DNS configuré (ex: api.votredomaine.com)

---

## 1️⃣ Préparation du serveur

### Mise à jour système

```bash
sudo apt update
sudo apt upgrade -y
```

### Installation des dépendances

```bash
# Python et pip
sudo apt install python3 python3-pip python3-venv -y

# Nginx (reverse proxy)
sudo apt install nginx -y

# Certbot (SSL/HTTPS)
sudo apt install certbot python3-certbot-nginx -y

# Outils
sudo apt install git ufw -y
```

---

## 2️⃣ Configuration utilisateur

Créer un utilisateur dédié (sécurité) :

```bash
sudo adduser pyquest
sudo usermod -aG www-data pyquest
su - pyquest
```

---

## 3️⃣ Cloner le projet

```bash
cd /home/pyquest
git clone https://github.com/votre-username/ProjetEducationPython.git
cd ProjetEducationPython/backend
```

---

## 4️⃣ Environnement virtuel Python

```bash
# Créer venv
python3 -m venv venv

# Activer
source venv/bin/activate

# Installer dépendances
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 5️⃣ Variables d'environnement

Créer le fichier `.env` avec des secrets **UNIQUES** :

```bash
nano .env
```

**Contenu** :
```env
# ATTENTION : Générer des secrets UNIQUES pour la production !
JWT_SECRET_KEY=CHANGEZ_MOI_SECRET_PRODUCTION_JWT_ULTRA_SECURISE_12345
FLASK_SECRET_KEY=CHANGEZ_MOI_SECRET_PRODUCTION_FLASK_ULTRA_SECURISE_67890

# CORS - Ajouter votre domaine frontend
CORS_ORIGINS=https://votredomaine.com,https://www.votredomaine.com

# Rate limiting
RATE_LIMIT_DEFAULT=100 per hour
RATE_LIMIT_STORAGE_URL=memory://

# HTTPS (activer en production)
FORCE_HTTPS=True

# Flask
FLASK_ENV=production
```

**Générer des secrets sécurisés** :
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

**Permissions** :
```bash
chmod 600 .env  # Accessible uniquement par pyquest
```

---

## 6️⃣ Test local

```bash
# Tester que tout fonctionne
python3 -m pytest tests/test_security.py -v

# Tester Gunicorn
gunicorn -c gunicorn_config.py "api.app:app"
# Ctrl+C pour arrêter

# Vérifier que l'API répond
curl http://127.0.0.1:5000/api/domaines
```

---

## 7️⃣ Systemd Service (Gunicorn)

Créer un service systemd pour démarrer automatiquement :

```bash
sudo nano /etc/systemd/system/pyquest-api.service
```

**Contenu** :
```ini
[Unit]
Description=PyQuest API avec Gunicorn
After=network.target

[Service]
Type=notify
User=pyquest
Group=www-data
WorkingDirectory=/home/pyquest/ProjetEducationPython/backend
Environment="PATH=/home/pyquest/ProjetEducationPython/backend/venv/bin"
ExecStart=/home/pyquest/ProjetEducationPython/backend/venv/bin/gunicorn \
    -c gunicorn_config.py \
    "api.app:app"
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

**Activer et démarrer** :
```bash
sudo systemctl daemon-reload
sudo systemctl enable pyquest-api.service
sudo systemctl start pyquest-api.service

# Vérifier le statut
sudo systemctl status pyquest-api.service

# Logs
sudo journalctl -u pyquest-api.service -f
```

---

## 8️⃣ Configuration Nginx (Reverse Proxy)

### Créer la configuration

```bash
sudo nano /etc/nginx/sites-available/pyquest-api
```

**Contenu** :
```nginx
# Rate limiting zone
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/m;

# Upstream Gunicorn
upstream pyquest_backend {
    server 127.0.0.1:5000 fail_timeout=0;
}

server {
    listen 80;
    server_name api.votredomaine.com;

    # Logs
    access_log /var/log/nginx/pyquest-api-access.log;
    error_log /var/log/nginx/pyquest-api-error.log;

    # Taille maximale upload (16MB)
    client_max_body_size 16M;

    # Security headers
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Proxy vers Gunicorn
    location / {
        # Rate limiting
        limit_req zone=api_limit burst=20 nodelay;
        limit_req_status 429;

        proxy_pass http://pyquest_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;

        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

**Activer la configuration** :
```bash
sudo ln -s /etc/nginx/sites-available/pyquest-api /etc/nginx/sites-enabled/
sudo nginx -t  # Tester la config
sudo systemctl restart nginx
```

---

## 9️⃣ SSL/HTTPS avec Let's Encrypt

### Obtenir certificat SSL

```bash
sudo certbot --nginx -d api.votredomaine.com
```

Certbot va automatiquement :
- Générer un certificat SSL gratuit
- Configurer Nginx pour HTTPS
- Rediriger HTTP → HTTPS

### Renouvellement automatique

```bash
# Tester le renouvellement
sudo certbot renew --dry-run

# Certbot configure automatiquement un cron job
```

### Configuration HTTPS finale

Nginx sera automatiquement mis à jour par Certbot avec :

```nginx
server {
    listen 443 ssl http2;
    server_name api.votredomaine.com;

    ssl_certificate /etc/letsencrypt/live/api.votredomaine.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.votredomaine.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # ... reste de la config
}

server {
    listen 80;
    server_name api.votredomaine.com;
    return 301 https://$server_name$request_uri;
}
```

---

## 🔟 Firewall (UFW)

Configurer le firewall :

```bash
# Désactiver tous les ports par défaut
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Autoriser SSH
sudo ufw allow 22/tcp

# Autoriser HTTP et HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Bloquer accès direct à Gunicorn (port 5000)
sudo ufw deny 5000/tcp

# Activer le firewall
sudo ufw enable

# Vérifier les règles
sudo ufw status verbose
```

---

## 1️⃣1️⃣ Monitoring et Logs

### Logs Gunicorn

```bash
# Logs de l'application
tail -f /home/pyquest/ProjetEducationPython/backend/logs/access.log
tail -f /home/pyquest/ProjetEducationPython/backend/logs/error.log

# Logs systemd
sudo journalctl -u pyquest-api.service -f
```

### Logs Nginx

```bash
tail -f /var/log/nginx/pyquest-api-access.log
tail -f /var/log/nginx/pyquest-api-error.log
```

### Logs de sécurité

```bash
tail -f /home/pyquest/ProjetEducationPython/backend/logs/security.log
tail -f /home/pyquest/ProjetEducationPython/backend/logs/auth.log
```

### Rotation des logs

Créer `/etc/logrotate.d/pyquest-api` :

```bash
sudo nano /etc/logrotate.d/pyquest-api
```

```
/home/pyquest/ProjetEducationPython/backend/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    missingok
    copytruncate
}
```

---

## 1️⃣2️⃣ Backup automatique

### Script de backup

```bash
nano /home/pyquest/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/home/pyquest/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup des données utilisateurs
cp -r /home/pyquest/ProjetEducationPython/backend/utilisateurs "$BACKUP_DIR/utilisateurs_$DATE"
cp -r /home/pyquest/ProjetEducationPython/backend/progressions "$BACKUP_DIR/progressions_$DATE"

# Garder seulement 7 derniers backups
ls -t $BACKUP_DIR/utilisateurs_* | tail -n +8 | xargs -r rm -rf
ls -t $BACKUP_DIR/progressions_* | tail -n +8 | xargs -r rm -rf

echo "Backup completed: $DATE"
```

```bash
chmod +x /home/pyquest/backup.sh
```

### Cron job (backup quotidien)

```bash
crontab -e
```

```
# Backup tous les jours à 3h du matin
0 3 * * * /home/pyquest/backup.sh >> /home/pyquest/backup.log 2>&1
```

---

## 1️⃣3️⃣ Mise à jour de l'application

```bash
cd /home/pyquest/ProjetEducationPython/backend

# Backup avant mise à jour
/home/pyquest/backup.sh

# Pull dernières modifications
git pull origin main

# Activer venv
source venv/bin/activate

# Mise à jour dépendances
pip install -r requirements.txt --upgrade

# Tests
python3 -m pytest tests/ -v

# Redémarrer l'app
sudo systemctl restart pyquest-api.service

# Vérifier
sudo systemctl status pyquest-api.service
```

---

## 1️⃣4️⃣ Monitoring avancé (optionnel)

### Prometheus + Grafana

Installation pour monitoring des performances :

```bash
# Prometheus
sudo apt install prometheus -y

# Grafana
sudo apt install grafana -y
sudo systemctl enable grafana-server
sudo systemctl start grafana-server
```

Configuration Prometheus pour scraper l'API :

```yaml
# /etc/prometheus/prometheus.yml
scrape_configs:
  - job_name: 'pyquest-api'
    static_configs:
      - targets: ['localhost:5000']
```

---

## 🔒 Checklist Sécurité Production

Avant de mettre en production, vérifier :

- [ ] ✅ `.env` avec secrets UNIQUES et sécurisés
- [ ] ✅ `.env` avec permissions 600 (chmod 600 .env)
- [ ] ✅ HTTPS activé avec certificat SSL valide
- [ ] ✅ `FORCE_HTTPS=True` dans `.env`
- [ ] ✅ CORS configuré avec domaines spécifiques (pas "*")
- [ ] ✅ Firewall UFW activé avec règles restrictives
- [ ] ✅ Port 5000 bloqué en externe (accessible uniquement via Nginx)
- [ ] ✅ Service systemd activé et démarré
- [ ] ✅ Logs configurés et rotatifs
- [ ] ✅ Backup automatique configuré
- [ ] ✅ Utilisateur dédié (pas root)
- [ ] ✅ Tests de sécurité passés (pytest)
- [ ] ✅ Rate limiting Nginx + Flask configuré
- [ ] ✅ Headers de sécurité ajoutés
- [ ] ✅ Monitoring en place

---

## 🧪 Tests post-déploiement

### Test API

```bash
# Health check
curl https://api.votredomaine.com/health

# Liste domaines
curl https://api.votredomaine.com/api/domaines

# Login
curl -X POST https://api.votredomaine.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "SecurePass123!"}'
```

### Test HTTPS

```bash
# Vérifier le certificat SSL
openssl s_client -connect api.votredomaine.com:443 -servername api.votredomaine.com

# Tester la redirection HTTP → HTTPS
curl -I http://api.votredomaine.com
# Doit retourner 301 redirect vers https://
```

### Test Rate Limiting

```bash
# Envoyer 110 requêtes rapidement (devrait bloquer après 100)
for i in {1..110}; do
  curl -I https://api.votredomaine.com/api/domaines
done
# Les dernières devraient retourner 429 Too Many Requests
```

---

## 🆘 Troubleshooting

### L'API ne démarre pas

```bash
# Vérifier les logs
sudo journalctl -u pyquest-api.service -n 50

# Vérifier Gunicorn manuellement
cd /home/pyquest/ProjetEducationPython/backend
source venv/bin/activate
gunicorn -c gunicorn_config.py "api.app:app"
```

### Nginx ne fonctionne pas

```bash
# Tester la config
sudo nginx -t

# Vérifier les logs
sudo tail -f /var/log/nginx/error.log

# Redémarrer
sudo systemctl restart nginx
```

### Certificat SSL expiré

```bash
# Renouveler manuellement
sudo certbot renew

# Redémarrer Nginx
sudo systemctl restart nginx
```

### Erreur 502 Bad Gateway

- Vérifier que Gunicorn est démarré : `sudo systemctl status pyquest-api.service`
- Vérifier que Gunicorn écoute sur 127.0.0.1:5000
- Vérifier les logs Nginx et Gunicorn

---

## 📞 Support

Pour toute question sur le déploiement : support@votredomaine.com

---

**Félicitations ! Votre API PyQuest est maintenant en production avec un niveau de sécurité professionnel. 🎉**
