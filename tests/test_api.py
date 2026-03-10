import os
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

sample_payload = {
    "id_employee": 1226,
    "age": 20,
    "genre": "M",
    "revenu_mensuel": 2678,
    "statut_marital": "Célibataire",
    "departement": "Commercial",
    "poste": "Représentant Commercial",
    "nombre_experiences_precedentes": 1,
    "nombre_heures_travailless": 80,
    "annee_experience_totale": 2,
    "annees_dans_l_entreprise": 2,
    "annees_dans_le_poste_actuel": 1,
    "satisfaction_employee_environnement": 3,
    "note_evaluation_precedente": 4,
    "niveau_hierarchique_poste": 1,
    "satisfaction_employee_nature_travail": 4,
    "satisfaction_employee_equipe": 4,
    "satisfaction_employee_equilibre_pro_perso": 3,
    "note_evaluation_actuelle": 3,
    "heure_supplementaires": "Non",
    "augementation_salaire_precedente": "17 %",
    "nombre_participation_pee": 0,
    "nb_formations_suivies": 2,
    "nombre_employee_sous_responsabilite": 1,
    "distance_domicile_travail": 21,
    "niveau_education": 3,
    "domaine_etude": "Marketing",
    "ayant_enfants": "Y",
    "frequence_deplacement": "Occasionnel",
    "annees_depuis_la_derniere_promotion": 2,
    "annes_sous_responsable_actuel": 2
  }

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_predict():
    response = client.post("/predict", json=sample_payload)
    assert response.status_code == 200
    assert "prediction" in response.json()

def test_predict_invalid_payload():
    invalid_payload = sample_payload.copy()
    invalid_payload.pop("age")

    response = client.post("/predict", json=invalid_payload)
    assert response.status_code == 422

def test_predict_invalid_value():
    invalid_payload = sample_payload.copy()
    invalid_payload["age"] = -5

    response = client.post("/predict", json=invalid_payload)
    assert response.status_code == 422

def test_predict_invalid_enum():
    invalid_payload = sample_payload.copy()
    invalid_payload["genre"] = "X"

    response = client.post("/predict", json=invalid_payload)
    assert response.status_code == 422

def test_predict_missing_optional_fields():
    optional_fields = ["nombre_heures_travailless", "nombre_employee_sous_responsabilite", "ayant_enfants"]
    for field in optional_fields:
        payload = sample_payload.copy()
        payload.pop(field)

        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        assert "prediction" in response.json()

def test_predict_invalid_percentage_format():
    invalid_payload = sample_payload.copy()
    invalid_payload["augementation_salaire_precedente"] = "17 percent"

    response = client.post("/predict", json=invalid_payload)
    assert response.status_code == 422