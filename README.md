# ML Deployment - Projet 4

## Description
API de classification automatique basée sur un modèle de Machine Learning, déployée avec FastAPI.

## Prérequis
- Python 3.12+
- pip

## Installation
```bash
git clone https://github.com/ton-username/ml-deployment-p4.git
cd ml-deployment-p4
pip install -r requirements.txt
```

## Utilisation
Lancer l'API :
```bash
uvicorn app.main:app --reload
```
L'API est accessible sur : http://localhost:8000
La documentation Swagger est accessible sur : http://localhost:8000/docs

## Structure du projet
```
ml-deployment-p4/
├── app/          # Code source de l'API
├── models/       # Modèle ML
├── data/         # Données
├── tests/        # Tests unitaires et fonctionnels
└── requirements.txt
```

## Tests
```bash
pytest tests/
```

## Déploiement
(à compléter)

## Auteur
Ton nom