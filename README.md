---
title: ml-deployment-p4
sdk: docker
app_port: 7860
---

# ml-deployment-p4

Ce projet a pour objectif de déployer un modèle de machine learning capable d’estimer le risque de départ d’un employé. L’application est exposée via une API FastAPI. Les données utilisées par le modèle sont stockées dans PostgreSQL, et chaque appel de prédiction est enregistré afin de conserver une trace des entrées, des sorties et de la version du modèle utilisée.

L’idée générale est la suivante : un client envoie un `employee_id`, l’API récupère les informations correspondantes dans la base, exécute le pipeline de prédiction, renvoie un résultat, puis enregistre l’appel dans une table de logs. Le projet couvre donc toute une chaîne simple de déploiement ML : stockage des données, exposition du modèle, historisation, tests et déploiement automatisé.

## Architecture du projet

L’API est développée avec FastAPI et valide les entrées avec Pydantic. Le modèle est chargé depuis `ml_model/model.joblib`. PostgreSQL sert à la fois de source de données pour les employés et de support de traçabilité pour les prédictions. Les tests sont écrits avec Pytest et l’automatisation du projet repose sur GitHub Actions, avec un déploiement cible vers Hugging Face Spaces.

La base de données s’appuie sur deux tables principales. La table `employees` contient les informations RH utilisées pour la prédiction : âge, poste, département, ancienneté, évaluations, satisfaction, distance domicile-travail et autres variables métier. La table `prediction_logs` conserve l’historique des appels à l’API : identifiant de l’employé, endpoint utilisé, payload d’entrée, payload de sortie, version du modèle et date de création. Le détail du schéma est présenté dans [docs/schema_bdd.md](docs/schema_bdd.md).

## Installation

La première étape consiste à cloner le dépôt, puis à créer un environnement virtuel.

```bash
git clone <url-du-repository>
cd ml-deployment-p4
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Une fois les dépendances installées, il faut créer un fichier `.env` à partir de `.env.example`. Ce fichier sert à stocker les variables de configuration du projet.

Exemple :

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/ml_api
MODEL_VERSION=xgb_pipeline_v1
API_KEY=change_me
HF_SPACE_ID=username/ml-deployment-p4
```

`DATABASE_URL` permet à l’application de se connecter à PostgreSQL. `MODEL_VERSION` est enregistrée dans les logs. `API_KEY` peut être utilisée pour restreindre l’accès aux endpoints, et `HF_SPACE_ID` identifie le Space Hugging Face utilisé pour le déploiement.

## Initialisation de la base de données

L’initialisation de la base repose sur deux fichiers complémentaires. Le fichier [scripts/create_db.sql](scripts/create_db.sql) définit la structure SQL des tables. Le script [scripts/init_db.py](scripts/init_db.py) lit ce schéma, crée les tables dans PostgreSQL, puis charge le contenu du fichier `data/employee_attrition_dataset.csv` dans la table `employees`.

La commande à lancer est :

```bash
python scripts/init_db.py
```

À l’issue de cette étape, la base doit contenir les données nécessaires à la prédiction ainsi que la table de logs qui enregistrera les appels de l’API.

## Utilisation de l’API

L’API peut être lancée localement avec la commande suivante :

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 5050
```

La documentation interactive Swagger est ensuite disponible à l’adresse :

```text
http://127.0.0.1:5050/docs
```

L’endpoint `GET /health` permet de vérifier rapidement que l’API fonctionne correctement.

Les deux endpoints métier sont `POST /predict` et `POST /predict_proba`. Dans les deux cas, l’entrée attendue est un identifiant employé.

Exemple de payload :

```json
{
  "employee_id": 1
}
```

Quand une requête est envoyée sur `POST /predict`, l’API lit l’employé dans la table `employees`, transforme les données dans le format attendu par le modèle, exécute la prédiction, puis enregistre l’appel dans `prediction_logs`.

Réponse possible :

```json
{
  "employee_id": 1,
  "prediction": 1
}
```

L’endpoint `POST /predict_proba` suit la même logique, mais renvoie en plus la probabilité associée à la prédiction.

```json
{
  "employee_id": 1,
  "prediction": 1,
  "probability": 0.81
}
```

## Authentification, gestion des accès et sécurité

Le projet prévoit une protection simple de l’API par clé d’accès. Si la variable `API_KEY` est définie dans l’environnement, le client doit envoyer l’en-tête HTTP suivant :

```text
x-api-key: valeur_de_la_cle
```

Si la clé est absente ou invalide, l’API renvoie une erreur `401`. À ce stade, le projet ne met pas en place de comptes utilisateurs, de gestion de rôles ni d’authentification par JWT. Le contrôle d’accès repose donc principalement sur l’usage d’une clé API optionnelle et sur la protection de l’accès à la base.

Les informations sensibles ne sont jamais écrites en dur dans le code source. Le fichier `.env` local ne doit pas être versionné. Les secrets de déploiement doivent être stockés dans GitHub Secrets, et les variables nécessaires au Space Hugging Face doivent être définies dans `Variables and secrets`.

Le projet ne gère pas encore de mots de passe applicatifs. Il n’y a donc pas de mécanisme de hachage utilisé dans le code à ce stade. Si une authentification par utilisateurs était ajoutée plus tard, les mots de passe ne devraient évidemment jamais être stockés en clair : ils devraient être hachés avec un algorithme adapté comme `bcrypt` ou `argon2`.

## Tests

Les tests automatisés sont regroupés dans [tests/test_api.py](tests/test_api.py). Ils vérifient le fonctionnement de l’endpoint de santé, le comportement de `POST /predict` et `POST /predict_proba`, le cas d’un employé introuvable, la validation des entrées ainsi que l’appel du mécanisme de log.

La commande suivante permet de lancer les tests avec un rapport de couverture :

```bash
python -m pytest -v --cov=app --cov-report=term-missing tests
```

## CI/CD et déploiement

Le pipeline GitHub Actions est défini dans [.github/workflows/ci.yml](.github/workflows/ci.yml). Il exécute les tests sur les branches de travail et sur les pull requests, puis déploie automatiquement le projet sur Hugging Face Spaces lorsqu’un push est effectué sur `main`.

Le déploiement vers Hugging Face est piloté par [scripts/deploy_to_hf.py](scripts/deploy_to_hf.py). Pour que cette étape fonctionne, il faut définir dans GitHub les secrets `HF_TOKEN` et `HF_SPACE_ID`. Côté Hugging Face, il faut ensuite configurer les variables d’environnement nécessaires à l’exécution de l’application, en particulier `DATABASE_URL`, `API_KEY` et `MODEL_VERSION`.

Le déroulement recommandé est le suivant : créer un Space Hugging Face en mode Docker, configurer les secrets GitHub, renseigner les variables du Space, vérifier que `DATABASE_URL` pointe vers une base PostgreSQL distante accessible depuis Internet, puis pousser le code sur `main`. Une fois le workflow terminé, il reste à vérifier que le Space s’est bien construit et que l’endpoint `/docs` est accessible.

## Workflow Git

Le projet a été organisé autour d’un workflow simple avec une branche `develop`, plusieurs branches `feature/...` et une branche `main` réservée à l’intégration finale. Chaque bloc fonctionnel a été développé séparément, poussé sur GitHub, puis intégré progressivement.

Ce découpage permet de distinguer clairement les évolutions liées à la base de données, à l’API, aux tests, à la documentation et au pipeline CI/CD. Il rend aussi l’historique Git plus lisible et plus facile à justifier.

## Exploitation des données et besoins analytiques

La table `prediction_logs` n’a pas seulement un intérêt technique. Elle peut aussi être exploitée d’un point de vue analytique. Elle permet, par exemple, de suivre le nombre de prédictions réalisées par jour, de comparer l’usage de `predict` et `predict_proba`, d’identifier les réponses les plus fréquentes, de suivre les probabilités produites par le modèle et de repérer les erreurs métier comme les employés introuvables.

À partir de cette table, il est possible de construire un tableau de bord simple pour répondre à plusieurs besoins : mesurer l’activité de l’API dans le temps, observer la répartition des prédictions, suivre les versions de modèle utilisées et disposer d’une première base de traçabilité pour l’analyse des performances métier.

## Fichiers principaux

Les fichiers les plus importants du projet sont [app/main.py](app/main.py), qui contient la logique des endpoints FastAPI, [app/db.py](app/db.py), qui gère les interactions avec PostgreSQL, [scripts/init_db.py](scripts/init_db.py), qui initialise la base, [scripts/create_db.sql](scripts/create_db.sql), qui définit le schéma SQL, et [tests/test_api.py](tests/test_api.py), qui regroupe les tests de l’API.

## Conclusion

Ce projet propose une architecture simple et pédagogique pour déployer un modèle de machine learning dans un cadre proche d’un usage réel. Il combine une API FastAPI, une base PostgreSQL, un système de logs, une stratégie de tests, une documentation d’exploitation et un pipeline CI/CD vers Hugging Face Spaces.
