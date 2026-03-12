---
title: ml-deployment-p4
sdk: docker
app_port: 7860
---
# ML Deployment

Ce projet déploie un modèle de machine learning permettant de prédire le départ potentiel d'un employé.  
Le modèle est exposé via une API FastAPI et les prédictions sont enregistrées dans une base PostgreSQL afin d'assurer la traçabilité.

## Architecture du projet

- API REST développée avec **FastAPI**
- Validation des données avec **Pydantic**
- Modèle ML : **XGBoost pipeline**
- Base de données : **PostgreSQL**
- Tests : **Pytest**
- CI : **GitHub Actions**

## Installation

### Cloner le repository :

```bash
git clone https://github.com/emlp-prog/ml-deployment-p4.git
cd ml-deployment-p4
```

### Créer un environnement virtuel :
Linux / Mac :
```bash
python -m venv venv
source venv/bin/activate
```
Windows :
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Installer les dépendances :

```bash
pip install -r requirements.txt
```

### Configuration

Le projet utilise une variable d'environnement pour la base PostgreSQL :

```text
DATABASE_URL=postgresql://postgres:mot_de_passe@localhost:5432/ml_api
```
Créer un fichier .env à la racine du projet à partir de .env.example.

## Lancer l'API

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 5050
```
### Documentation de l'API

Une fois l'API lancée, la documentation interactive Swagger est accessible à l'adresse :

```text
http://127.0.0.1:5050/docs
```

## Endpoints principaux

### POST /predict

Cet endpoint reçoit les données brutes d'un employé au format JSON, exécute le pipeline de prédiction et retourne le résultat.
Des exemples de données peuvent être trouvés dans data/example_data.json.

Le payload envoyé à l'API est validé avec Pydantic avant la prédiction.

Exemple de réponse :
```json
{
  "prediction": 0
}
```
### GET /health

Endpoint simple de vérification de santé de l'API.
Réponse :
```json
{
  "status": "ok"
}
```

## Base de données

Le projet utilise une base PostgreSQL locale nommée ml_api.

La base sert à deux usages :

- stocker le dataset complet

- enregistrer les prédictions générées par l'API

### Initialiser la base

Créer les tables :

```bash
psql -U postgres -d ml_api -f scripts/create_db.sql
```

Importer le dataset :

```bash
\copy employee_attrition_dataset
FROM 'data/employee_attrition_dataset.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',');
```
Vérifier l'import :
```bash
SELECT COUNT(*) FROM employee_attrition_dataset;
```
Schéma de la base de données :
Visible dans docs/schema_bdd.md

Traçabilité :

Chaque appel valide à l'endpoint /predict peut être enregistré dans la table predictions avec :
- les données d'entrée envoyées au modèle
- la réponse produite par le modèle
- la version du modèle utilisée
- la date de création
Cela permet d'assurer une traçabilité complète des échanges entre l'API, le modèle et la base de données.

Le fichier `scripts/query_predictions.sql` contient des requêtes SQL permettant de consulter les prédictions enregistrées dans la base.

## Modèle de machine learning

Le modèle utilisé est un pipeline sauvegardé dans :

```text
ml_model/model.joblib
```
Ce pipeline inclut :
- le feature engineering métier
- le modèle XGBoost
- la logique de transformation nécessaire avant prédiction

Le fichier ```text ml_model/feature_engineering.py ``` contient la classe AttritionFeatureEngineer utilisée par le pipeline.

## Tests

Les tests sont réalisés avec Pytest.
Les tests couvrent le endpoint /health, le endpoint /predict, les cas d'erreur de validation, les valeurs invalides, les catégories interdites, les champs optionnels
Exécuter les tests :
```bash
pytest -v
```
Rapport :
```bash
pytest --cov=app --cov-report=term-missing
```
## CI / CD
Le projet utilise GitHub Actions pour exécuter automatiquement les tests à chaque push.
Le pipeline CI vérifie l'installation des dépendances et l'exécution des tests Pytest.

## Jeu de données

Le dataset utilisé dans ce projet provient du projet de classification RH et contient 1470 observations.
Le dataset fusionné complet est stocké dans PostgreSQL dans la table employee_attrition_dataset

## Gestion des secrets et sécurité

Le projet utilise des variables d'environnement pour gérer les informations sensibles, notamment la connexion à PostgreSQL via `DATABASE_URL`.

Le fichier `.env` ne doit pas être versionné dans le dépôt Git.  
Un fichier `.env.example` est fourni comme exemple de configuration.

Aucun secret n'est stocké directement dans le code source.

À ce stade, l'API ne met pas en place de mécanisme d'authentification applicative (JWT, API key, login/mot de passe).  
Le projet est présenté comme un POC technique centré sur le déploiement du modèle, l'API, les tests et la traçabilité des prédictions.

## Déploiement

L'API a vocation à être déployée sur une plateforme cloud telle que **Hugging Face Spaces**.

Le déploiement permet de rendre l'API accessible via une URL publique et de démontrer l'utilisation du modèle en dehors de l'environnement local.

Une fois le déploiement effectué, la documentation interactive reste accessible via l'endpoint `/docs`.

## Gestion et exploitation des données

Le stockage des données repose sur deux tables principales :

- `employee_attrition_dataset` : contient le dataset complet utilisé dans le projet
- `predictions` : contient les entrées et sorties des prédictions effectuées via l'API

## Versions

Le projet utilise Git pour le versionnage du code.
Un tag v1.0 a été créé pour marquer une première version fonctionnelle du projet.

## Conclusion

Ce projet fournit une API de prédiction fonctionnelle, testée et intégrée à une base PostgreSQL locale, avec une logique de traçabilité complète des entrées et sorties du modèle.