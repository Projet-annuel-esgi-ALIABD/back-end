# Smart City - Backend

Ce projet est le backend d'une application Smart City. Il fournit une API RESTful pour accéder aux données et aux prédictions relatives à la qualité de l'air et à la météo, ainsi qu'un système d'alerte automatisé. L'application est entièrement conteneurisée avec Docker pour une installation et un déploiement simplifiés.

-----

## 📋 Features

  * **API RESTful complète** : Construite avec Django et Django REST Framework.
  * [cite\_start]**Authentification JWT** : Système d'inscription, de connexion, de déconnexion et de rafraîchissement de token sécurisé[cite: 30, 177, 178].
  * **Qualité de l'Air** :
      * [cite\_start]Intégration avec l'API OpenWeatherMap pour récupérer les données de qualité de l'air actuelles et historiques[cite: 32, 38, 45].
      * [cite\_start]Prédiction de l'indice de qualité de l'air (AQI) à l'aide d'un modèle **LSTM (Long Short-Term Memory)** entraîné avec PyTorch[cite: 4, 81, 184].
      * [cite\_start]Endpoints pour consulter les données de qualité de l'air récentes[cite: 31, 173, 174].
  * **Prédictions Météo** :
      * [cite\_start]Intégration avec l'API Météo France pour obtenir des données climatologiques historiques[cite: 138].
      * [cite\_start]Entraînement de modèles de prédiction météo (**XGBoost**) pour diverses caractéristiques (température max/min, précipitations, etc.)[cite: 5, 54, 114].
      * [cite\_start]API pour obtenir des prédictions météo à plusieurs jours[cite: 6, 186].
  * **Système d'Alertes Automatisé** :
      * [cite\_start]Tâches planifiées (cron jobs) pour vérifier en continu si les seuils de polluants atmosphériques sont dépassés[cite: 32, 35, 52].
      * [cite\_start]Création automatique d'alertes en base de données lorsque les seuils sont atteints[cite: 24, 35].
  * [cite\_start]**Tâches Asynchrones** : Utilisation d'APScheduler pour exécuter des tâches en arrière-plan, comme la récupération de données et la vérification des alertes, sans bloquer le serveur web[cite: 9, 52].
  * [cite\_start]**Containerisation** : Configuration complète avec `Dockerfile` et `docker-compose.yml` pour un déploiement facile et reproductible[cite: 8, 9, 10].
  * [cite\_start]**Documentation d'API** : Génération automatique de la documentation interactive avec Swagger (OpenAPI) et ReDoc[cite: 220].

-----

## 🏗️ Architecture

Le projet est conçu autour d'une architecture de microservices gérée par Docker Compose, comprenant :

1.  **`web`** : Le service principal qui exécute l'application Django avec un serveur Gunicorn. [cite\_start]Il expose l'API RESTful pour les interactions avec les clients[cite: 8, 11].
2.  **`scheduler`** : Un service dédié qui exécute les tâches planifiées (via `APScheduler`) pour la récupération de données et le système d'alerte. [cite\_start]Il garantit que les tâches de fond n'impactent pas les performances de l'API[cite: 9, 52].
3.  **Base de données** : Le système est configuré pour se connecter à une base de données PostgreSQL, qui doit être fournie en tant que service distinct (non incluse dans ce `docker-compose.yml`).

Les modèles de Machine Learning sont pré-entraînés ou peuvent être entraînés via des commandes de gestion Django et sont ensuite chargés en mémoire par les services pour effectuer des prédictions en temps réel.

-----

## 🛠️ Technologies Utilisées

  * **Backend** : Django, Django REST Framework
  * **Base de Données** : PostgreSQL
  * **Machine Learning** : PyTorch, Scikit-learn, XGBoost, Pandas, NumPy
  * **Containerisation** : Docker, Docker Compose
  * [cite\_start]**Serveur WSGI** : Gunicorn [cite: 11]
  * **Planification de Tâches** : APScheduler
  * **Documentation API** : drf-yasg (Swagger/OpenAPI)
  * [cite\_start]**Authentification** : djangorestframework-simplejwt [cite: 213]

-----

## 🚀 Installation et Lancement

### Prérequis

  * Docker
  * Docker Compose

### 1\. Cloner le Dépôt

```bash
git clone <URL_DU_DEPOT>
cd projet-annuel-esgi-aliabd-back-end
```

### 2\. Configurer les Variables d'Environnement

Créez un fichier `.env` à la racine du projet en copiant le modèle `env.example` (s'il existe) ou en le créant manuellement. Remplissez les variables nécessaires :

```env
# Clé secrète de Django (générez une chaîne aléatoire forte)
SECRET_KEY=votre_super_cle_secrete

# Configuration de la base de données PostgreSQL
DB_NAME=postgres
DB_USER=votre_user
DB_PASSWORD=votre_mot_de_passe
DB_HOST=host.docker.internal # ou l'IP de votre service de base de données
DB_PORT=5432

# Mode Debug (mettre à False en production)
DEBUG=True

# Clés d'API externes
OPENWEATHERMAP_API_KEY=votre_cle_api_openweathermap
METEOFRANCE_API_KEY=votre_cle_api_meteofrance
```

### 3\. Lancer l'Application

Utilisez Docker Compose pour construire et démarrer les conteneurs en arrière-plan.

```bash
docker-compose up --build -d
```

[cite\_start]L'API sera alors accessible sur `http://localhost:3000`. [cite: 8]

-----

## 💡 Utilisation du Projet

### Documentation de l'API

Une fois l'application lancée, vous pouvez accéder à la documentation interactive de l'API pour voir tous les endpoints disponibles et les tester directement depuis votre navigateur :

  * [cite\_start]**Swagger UI** : `http://localhost:3000/swagger/` [cite: 220]
  * [cite\_start]**ReDoc** : `http://localhost:3000/redoc/` [cite: 220]

### Commandes de Gestion

Plusieurs commandes sont disponibles pour gérer l'application et les modèles d'IA. Exécutez-les à l'intérieur du conteneur `web`.

  * [cite\_start]**Appliquer les migrations de la base de données** (normalement fait au démarrage [cite: 8]) :

    ```bash
    docker-compose exec web python manage.py migrate
    ```

  * **Importer les données historiques de qualité de l'air** (pour les 6 derniers mois) :

    ```bash
    [cite_start]docker-compose exec web python manage.py import_aq [cite: 3]
    ```

  * **Entraîner les modèles de prédiction météo** :

    ```bash
    # Entraîner les modèles par défaut (TX, TN, RR, TM, TAMPLI)
    [cite_start]docker-compose exec web python manage.py train_weather_models [cite: 54]

    # Entraîner pour une caractéristique spécifique (ex: température maximale 'TX')
    [cite_start]docker-compose exec web python manage.py train_weather_models --features TX [cite: 54]
    ```

### Tâches Planifiées

[cite\_start]Le service `scheduler` exécute automatiquement les tâches suivantes toutes les heures[cite: 52]:

  * `fetch_latest_air` : Récupère la dernière heure de données sur la qualité de l'air.
  * `check_alerts` : Vérifie les données actuelles de qualité de l'air par rapport aux seuils d'alerte définis.