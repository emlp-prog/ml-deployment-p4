---
title: ml-deployment-p4
sdk: docker
app_port: 7860
---

# ml-deployment-p4

Ce projet deploie un modele de machine learning capable d'estimer le risque de depart d'un employe.
L'application est exposee via une API FastAPI, les donnees employees sont lues depuis PostgreSQL, et chaque appel de prediction est historise dans une table de logs.

## Objectif

L'objectif du projet est de montrer un cycle simple de deploiement ML :
- stocker les donnees employees en base
- exposer un modele via une API
- predire a partir d'un `employee_id`
- tracer les appels de prediction
- tester et deployer automatiquement l'application

## Architecture du projet

- API REST developpee avec FastAPI
- Validation des entrees avec Pydantic
- Modele ML sauvegarde dans `ml_model/model.joblib`
- Base de donnees PostgreSQL
- Tests automatises avec Pytest
- Pipeline CI/CD avec GitHub Actions
- Deploiement cible vers Hugging Face Spaces

## Structure de la base de donnees

Le projet repose sur deux tables principales :

- `employees` : contient les donnees du dataset employees utilisees pour alimenter le modele
- `prediction_logs` : contient les logs des appels API

### Table `employees`

Cette table contient les caracteristiques utiles a la prediction, par exemple :
- `id_employee`
- `age`
- `genre`
- `revenu_mensuel`
- `departement`
- `poste`
- `distance_domicile_travail`
- `frequence_deplacement`

### Table `prediction_logs`

Cette table contient :
- `employee_id`
- `endpoint`
- `input_payload`
- `output_payload`
- `model_version`
- `created_at`

Le schema detaille est disponible dans [docs/schema_bdd.md](/c:/Users/Emile/Cours/python/projet-5/ml-deployment-p4/docs/schema_bdd.md).

## Installation

### 1. Cloner le projet

```bash
git clone <url-du-repository>
cd ml-deployment-p4
```

### 2. Creer l'environnement virtuel

Sous Windows :

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Installer les dependances

```bash
pip install -r requirements.txt
```

## Configuration

Le projet utilise un fichier `.env` local pour stocker les variables de configuration.
Creer ce fichier a partir de `.env.example`.

Exemple :

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/ml_api
MODEL_VERSION=xgb_pipeline_v1
API_KEY=change_me
HF_SPACE_ID=username/ml-deployment-p4
```

### Variables importantes

- `DATABASE_URL` : connexion PostgreSQL
- `MODEL_VERSION` : version du modele stockee dans les logs
- `API_KEY` : cle API optionnelle pour proteger les endpoints
- `HF_SPACE_ID` : identifiant du Space Hugging Face

## Initialisation de la base

Le script [scripts/init_db.py](/c:/Users/Emile/Cours/python/projet-5/ml-deployment-p4/scripts/init_db.py) :
- lit le fichier SQL
- cree les tables PostgreSQL
- charge le dataset CSV dans la table `employees`

Commande :

```bash
python scripts/init_db.py
```

Le script SQL utilise est [scripts/create_db.sql](/c:/Users/Emile/Cours/python/projet-5/ml-deployment-p4/scripts/create_db.sql).

## Lancer l'API

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 5050
```

Documentation interactive :

```text
http://127.0.0.1:5050/docs
```

## Endpoints disponibles

### `GET /health`

Permet de verifier que l'API fonctionne.

Reponse :

```json
{
  "status": "ok"
}
```

### `POST /predict`

Entree :

```json
{
  "employee_id": 1
}
```

Traitement :
- l'API lit l'employe dans `employees`
- elle transforme la ligne en `DataFrame`
- elle appelle le modele
- elle ecrit un log dans `prediction_logs`

Reponse :

```json
{
  "employee_id": 1,
  "prediction": 1
}
```

### `POST /predict_proba`

Entree :

```json
{
  "employee_id": 1
}
```

Reponse :

```json
{
  "employee_id": 1,
  "prediction": 1,
  "probability": 0.81
}
```

## Tests

Les tests Pytest couvrent :
- `/health`
- `/predict`
- `/predict_proba`
- le cas employe introuvable
- les erreurs de validation
- l'appel de la fonction de log

Commande :

```bash
python -m pytest -v --cov=app --cov-report=term-missing tests
```

## CI/CD

Le workflow GitHub Actions est dans [ci.yml](/c:/Users/Emile/Cours/python/projet-5/ml-deployment-p4/.github/workflows/ci.yml).

Il permet :
- d'executer les tests sur `push` et `pull_request`
- de deployer automatiquement vers Hugging Face Spaces sur `main`

## Deploiement vers Hugging Face

Le deploiement est gere par [deploy_to_hf.py](/c:/Users/Emile/Cours/python/projet-5/ml-deployment-p4/scripts/deploy_to_hf.py).

Pour que GitHub Actions puisse deployer, il faut ajouter dans GitHub :
- `HF_TOKEN`
- `HF_SPACE_ID`

Dans Hugging Face Spaces, il faut ensuite configurer les variables utiles a l'application, par exemple :
- `DATABASE_URL`
- `API_KEY`
- `MODEL_VERSION`

## Gestion des secrets et securite

Les informations sensibles ne sont pas stockees dans le code source.

Bonnes pratiques appliquees :
- le fichier `.env` local ne doit pas etre versionne
- les tokens de deploiement sont stockes dans GitHub Secrets
- la connexion a la base se fait via `DATABASE_URL`
- l'API peut etre protegee par une cle `API_KEY`

## Workflow Git recommande

Convention de branches :
- `develop`
- `feature/database`
- `feature/api`
- `feature/tests`
- `feature/docs`
- `feature/cicd`
- `main`

Flux recommande :
1. creer une branche feature depuis `develop`
2. developper la fonctionnalite
3. commit et push sur la branche
4. ouvrir une Pull Request vers `develop`
5. une fois les features validees, merger `develop` vers `main`

## Exploitation des donnees

La table `prediction_logs` permet ensuite :
- de suivre les requetes de prediction
- d'analyser l'usage de l'API
- d'identifier les predictions produites par version de modele
- d'alimenter un tableau de bord simple si besoin

## Fichiers principaux

- [app/main.py](/c:/Users/Emile/Cours/python/projet-5/ml-deployment-p4/app/main.py) : logique des endpoints FastAPI
- [app/db.py](/c:/Users/Emile/Cours/python/projet-5/ml-deployment-p4/app/db.py) : lecture et ecriture en base
- [scripts/init_db.py](/c:/Users/Emile/Cours/python/projet-5/ml-deployment-p4/scripts/init_db.py) : initialisation PostgreSQL
- [scripts/create_db.sql](/c:/Users/Emile/Cours/python/projet-5/ml-deployment-p4/scripts/create_db.sql) : schema SQL
- [tests/test_api.py](/c:/Users/Emile/Cours/python/projet-5/ml-deployment-p4/tests/test_api.py) : tests de l'API

## Resume

Ce projet fournit une architecture simple et pedagogique pour deployer un modele ML :
- des donnees employees en PostgreSQL
- une API FastAPI par `employee_id`
- des logs de prediction
- des tests automatises
- un pipeline CI/CD vers Hugging Face Spaces
