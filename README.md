---
title: ml-deployment-p4
sdk: docker
app_port: 7860
---

# ml-deployment-p4

Ce projet a pour objectif de déployer un modèle de machine learning capable d’estimer le risque de départ d’un employé. L’application est exposée via une API FastAPI. Les données utilisées pour la prédiction sont stockées dans PostgreSQL et chaque appel à l’API est historisé afin de conserver une trace des entrées, des sorties et de la version du modèle utilisée.

L’idée générale est simple : l’utilisateur envoie un `employee_id`, l’API lit les informations correspondantes dans la base de données, exécute le pipeline de prédiction puis renvoie soit une classe, soit une probabilité. En parallèle, l’appel est enregistré dans une table de logs pour permettre un suivi métier et technique de l’usage du modèle.

## Architecture du projet

Le projet repose sur une architecture volontairement lisible. L’API est développée avec FastAPI et valide les entrées avec Pydantic. Le modèle est chargé depuis le fichier `ml_model/model.joblib`. PostgreSQL sert à la fois de source de données pour les employés et de support de traçabilité pour les prédictions. Les tests sont écrits avec Pytest et le déploiement est automatisé avec GitHub Actions vers Hugging Face Spaces.

La base de données contient deux tables principales. La table `employees` rassemble les données nécessaires à la prédiction : informations RH, poste, département, ancienneté, évaluations, satisfaction et autres variables du dataset. La table `prediction_logs` conserve l’historique des appels à l’API : identifiant employé, point d’entrée utilisé, payload d’entrée, payload de sortie, version du modèle et horodatage. Le schéma détaillé est décrit dans [docs/schema_bdd.md](docs/schema_bdd.md).

## Installation

Commence par cloner le dépôt, puis crée un environnement virtuel. Sous Windows, les commandes suivantes suffisent :

```bash
git clone <url-du-repository>
cd ml-deployment-p4
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Une fois les dépendances installées, il faut créer un fichier `.env` à partir de `.env.example`. Ce fichier sert à déclarer les variables de configuration du projet, notamment l’URL de connexion à PostgreSQL et les paramètres de déploiement.

Exemple de configuration :

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/ml_api
MODEL_VERSION=xgb_pipeline_v1
API_KEY=change_me
HF_SPACE_ID=username/ml-deployment-p4
```

`DATABASE_URL` permet à l’application de se connecter à PostgreSQL. `MODEL_VERSION` est enregistrée dans les logs de prédiction. `API_KEY` permet, si on le souhaite, de protéger l’accès à l’API. Enfin, `HF_SPACE_ID` identifie le Space Hugging Face utilisé pour le déploiement.

## Initialisation de la base de données

L’initialisation de la base repose sur deux fichiers. Le fichier [scripts/create_db.sql](scripts/create_db.sql) décrit la structure SQL des tables. Le script [scripts/init_db.py](scripts/init_db.py) lit ce schéma, crée les tables dans PostgreSQL puis charge le contenu du fichier `data/employee_attrition_dataset.csv` dans la table `employees`.

Pour préparer la base, il suffit donc d’exécuter :

```bash
python scripts/init_db.py
```

À l’issue de cette étape, la base doit contenir les employés nécessaires aux prédictions ainsi que la table de logs qui recevra l’historique des appels.

## Utilisation de l’API

L’API peut ensuite être lancée localement avec :

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 5050
```

La documentation interactive est disponible à l’adresse suivante :

```text
http://127.0.0.1:5050/docs
```

L’endpoint `GET /health` permet simplement de vérifier que l’API répond correctement. Les deux endpoints métier sont `POST /predict` et `POST /predict_proba`. Dans les deux cas, l’entrée attendue est un identifiant employé.

Exemple de payload :

```json
{
  "employee_id": 1
}
```

Quand un appel est envoyé à `POST /predict`, l’API récupère l’employé correspondant dans la table `employees`, transforme les données dans le format attendu par le modèle, exécute la prédiction puis renvoie une réponse de ce type :

```json
{
  "employee_id": 1,
  "prediction": 1
}
```

L’endpoint `POST /predict_proba` suit la même logique mais renvoie également une probabilité :

```json
{
  "employee_id": 1,
  "prediction": 1,
  "probability": 0.81
}
```

Chaque appel réussi est enregistré dans `prediction_logs`, ce qui permet de conserver une traçabilité complète des échanges entre l’API, la base et le modèle.

## Authentification, accès et sécurité

Le projet prévoit une protection simple de l’API par clé d’accès. Si la variable `API_KEY` est définie dans l’environnement, le client doit envoyer l’en-tête HTTP suivant :

```text
x-api-key: valeur_de_la_cle
```

Si cette clé est absente ou invalide, l’API renvoie une erreur `401`. À ce stade, le projet ne met pas en œuvre de comptes utilisateurs, de rôles, ni d’authentification par JWT. La gestion des accès repose donc principalement sur les variables d’environnement, sur la protection de la base PostgreSQL et sur l’usage éventuel de cette clé API.

Les informations sensibles ne sont jamais écrites en dur dans le code source. Le fichier `.env` local ne doit pas être versionné, les secrets de déploiement doivent être stockés dans GitHub Secrets, et les variables du Space Hugging Face doivent être définies dans `Variables and secrets`. Il n’existe pas encore de mots de passe applicatifs gérés par l’application elle-même. En conséquence, il n’y a pas encore de mécanisme de hachage à appliquer dans le code. Si une authentification par comptes utilisateurs était ajoutée plus tard, les mots de passe devraient alors être stockés sous forme hachée, avec un algorithme adapté comme `bcrypt` ou `argon2`.

## Tests

Les tests automatisés sont regroupés dans [tests/test_api.py](tests/test_api.py). Ils vérifient le fonctionnement de l’endpoint de santé, le comportement de `POST /predict` et `POST /predict_proba`, le cas d’un employé introuvable, la validation des entrées ainsi que l’appel du mécanisme de log.

La commande suivante permet de lancer les tests et d’obtenir un rapport de couverture :

```bash
python -m pytest -v --cov=app --cov-report=term-missing tests
```

## CI/CD et déploiement

Le pipeline GitHub Actions est défini dans [.github/workflows/ci.yml](.github/workflows/ci.yml). Il exécute les tests sur les branches de travail et sur les pull requests, puis déploie automatiquement le projet sur Hugging Face Spaces lorsqu’un push est effectué sur `main`.

Le déploiement vers Hugging Face est piloté par [scripts/deploy_to_hf.py](scripts/deploy_to_hf.py). Pour que cette étape fonctionne, il faut définir dans GitHub les secrets `HF_TOKEN` et `HF_SPACE_ID`. Côté Hugging Face, il faut ensuite renseigner les variables d’environnement nécessaires à l’exécution de l’application, en particulier `DATABASE_URL`, `API_KEY` et `MODEL_VERSION`.

Le déroulement recommandé est le suivant : créer un Space Hugging Face en mode Docker, configurer les secrets GitHub, renseigner les variables du Space, vérifier que `DATABASE_URL` pointe bien vers une base PostgreSQL distante accessible depuis Internet, puis pousser le code sur `main`. Une fois le workflow terminé, il reste à vérifier que le Space s’est bien construit et que l’endpoint `/docs` est accessible.

## Workflow Git

Le projet a été organisé autour d’un workflow simple avec une branche `develop`, plusieurs branches `feature/...` et une branche `main` réservée à l’intégration finale. L’idée est de développer chaque bloc fonctionnel séparément, de le pousser sur GitHub, puis d’ouvrir une pull request vers `develop`. Une fois les fonctionnalités validées, `develop` peut être fusionnée dans `main`.

Ce découpage permet de distinguer clairement les évolutions de la base de données, de l’API, des tests, de la documentation et du pipeline CI/CD. Il rend aussi l’historique Git plus lisible.

## Exploitation des données et besoin analytique

La table `prediction_logs` n’a pas seulement un intérêt technique. Elle peut aussi être exploitée dans une logique analytique. Elle permet, par exemple, de suivre le nombre de prédictions réalisées par jour, de comparer l’usage de `predict` et `predict_proba`, d’identifier les réponses les plus fréquentes, de suivre les probabilités produites par le modèle et de repérer les erreurs métier comme les employés introuvables.

À partir de cette table, il est possible de construire un tableau de bord simple pour répondre à plusieurs besoins : mesurer l’activité de l’API dans le temps, observer la répartition des prédictions, suivre les versions de modèle utilisées et disposer d’un début de traçabilité pour l’analyse des performances métier.

## Fichiers principaux

Les fichiers les plus importants du projet sont [app/main.py](app/main.py), qui contient la logique des endpoints FastAPI, [app/db.py](app/db.py), qui gère les interactions avec PostgreSQL, [scripts/init_db.py](scripts/init_db.py), qui initialise la base, [scripts/create_db.sql](scripts/create_db.sql), qui définit le schéma SQL, et [tests/test_api.py](tests/test_api.py), qui regroupe les tests de l’API.

## Conclusion

Ce projet propose une architecture simple et pédagogique pour déployer un modèle de machine learning dans un cadre proche d’un usage réel. Il combine une API FastAPI, une base PostgreSQL, un système de logs, une stratégie de tests, une documentation d’exploitation et un pipeline CI/CD vers Hugging Face Spaces.
