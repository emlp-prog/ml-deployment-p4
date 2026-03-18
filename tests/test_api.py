class FakeModel:
    def predict(self, dataframe):
        return [1]

    def predict_proba(self, dataframe):
        return [[0.2, 0.8]]


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict(client, monkeypatch): # test de l'endpoint de prédiction
    fake_employee = {
        "id_employee": 1,
        "age": 41,
        "genre": "F",
        "revenu_mensuel": 5993,
        "statut_marital": "Celibataire",
        "departement": "Commercial",
        "poste": "Cadre Commercial",
        "nombre_experiences_precedentes": 8,
        "nombre_heures_travailless": 80,
        "annee_experience_totale": 8,
        "annees_dans_l_entreprise": 6,
        "annees_dans_le_poste_actuel": 4,
        "satisfaction_employee_environnement": 2,
        "note_evaluation_precedente": 3,
        "niveau_hierarchique_poste": 2,
        "satisfaction_employee_nature_travail": 4,
        "satisfaction_employee_equipe": 1,
        "satisfaction_employee_equilibre_pro_perso": 1,
        "note_evaluation_actuelle": 3,
        "heure_supplementaires": "Oui",
        "augementation_salaire_precedente": "11 %",
        "a_quitte_l_entreprise": "Oui",
        "nombre_participation_pee": 0,
        "nb_formations_suivies": 0,
        "nombre_employee_sous_responsabilite": 1,
        "distance_domicile_travail": 1,
        "niveau_education": 2,
        "domaine_etude": "Infra & Cloud",
        "ayant_enfants": "Y",
        "frequence_deplacement": "Occasionnel",
        "annees_depuis_la_derniere_promotion": 0,
        "annes_sous_responsable_actuel": 5,
    }

    monkeypatch.setattr("app.main.get_employee_by_id", lambda employee_id: fake_employee.copy())
    monkeypatch.setattr("app.main.insert_prediction_log", lambda **kwargs: None)
    monkeypatch.setattr("app.main.model", FakeModel())

    response = client.post("/predict", json={"employee_id": 1})

    assert response.status_code == 200
    assert response.json() == {"employee_id": 1, "prediction": 1}


def test_predict_proba(client, monkeypatch): # test de l'endpoint de prédiction de probabilité
    fake_employee = {
        "id_employee": 1,
        "age": 41,
        "genre": "F",
        "revenu_mensuel": 5993,
        "statut_marital": "Celibataire",
        "departement": "Commercial",
        "poste": "Cadre Commercial",
        "nombre_experiences_precedentes": 8,
        "nombre_heures_travailless": 80,
        "annee_experience_totale": 8,
        "annees_dans_l_entreprise": 6,
        "annees_dans_le_poste_actuel": 4,
        "satisfaction_employee_environnement": 2,
        "note_evaluation_precedente": 3,
        "niveau_hierarchique_poste": 2,
        "satisfaction_employee_nature_travail": 4,
        "satisfaction_employee_equipe": 1,
        "satisfaction_employee_equilibre_pro_perso": 1,
        "note_evaluation_actuelle": 3,
        "heure_supplementaires": "Oui",
        "augementation_salaire_precedente": "11 %",
        "a_quitte_l_entreprise": "Oui",
        "nombre_participation_pee": 0,
        "nb_formations_suivies": 0,
        "nombre_employee_sous_responsabilite": 1,
        "distance_domicile_travail": 1,
        "niveau_education": 2,
        "domaine_etude": "Infra & Cloud",
        "ayant_enfants": "Y",
        "frequence_deplacement": "Occasionnel",
        "annees_depuis_la_derniere_promotion": 0,
        "annes_sous_responsable_actuel": 5,
    }

    monkeypatch.setattr("app.main.get_employee_by_id", lambda employee_id: fake_employee.copy())
    monkeypatch.setattr("app.main.insert_prediction_log", lambda **kwargs: None)
    monkeypatch.setattr("app.main.model", FakeModel())

    response = client.post("/predict_proba", json={"employee_id": 1})

    assert response.status_code == 200
    assert response.json() == {"employee_id": 1, "prediction": 1, "probability": 0.8}


def test_employee_not_found(client, monkeypatch): # test du cas où l'employé n'est pas trouvé dans la base de données
    monkeypatch.setattr("app.main.get_employee_by_id", lambda employee_id: None)

    response = client.post("/predict", json={"employee_id": 9999})

    assert response.status_code == 404
    assert response.json() == {"detail": "Employee not found"}


def test_invalid_payload(client): # test du cas où le payload de la requête est invalide
    response = client.post("/predict", json={"employee_id": 0})

    assert response.status_code == 422


def test_log_is_called(client, monkeypatch): # test du cas où la fonction d'insertion de log est bien appelée lors d'une prédiction
    calls = []

    fake_employee = {
        "id_employee": 1,
        "age": 41,
        "genre": "F",
        "revenu_mensuel": 5993,
        "statut_marital": "Celibataire",
        "departement": "Commercial",
        "poste": "Cadre Commercial",
        "nombre_experiences_precedentes": 8,
        "nombre_heures_travailless": 80,
        "annee_experience_totale": 8,
        "annees_dans_l_entreprise": 6,
        "annees_dans_le_poste_actuel": 4,
        "satisfaction_employee_environnement": 2,
        "note_evaluation_precedente": 3,
        "niveau_hierarchique_poste": 2,
        "satisfaction_employee_nature_travail": 4,
        "satisfaction_employee_equipe": 1,
        "satisfaction_employee_equilibre_pro_perso": 1,
        "note_evaluation_actuelle": 3,
        "heure_supplementaires": "Oui",
        "augementation_salaire_precedente": "11 %",
        "a_quitte_l_entreprise": "Oui",
        "nombre_participation_pee": 0,
        "nb_formations_suivies": 0,
        "nombre_employee_sous_responsabilite": 1,
        "distance_domicile_travail": 1,
        "niveau_education": 2,
        "domaine_etude": "Infra & Cloud",
        "ayant_enfants": "Y",
        "frequence_deplacement": "Occasionnel",
        "annees_depuis_la_derniere_promotion": 0,
        "annes_sous_responsable_actuel": 5,
    }

    def fake_insert_prediction_log(**kwargs):
        calls.append(kwargs)

    monkeypatch.setattr("app.main.get_employee_by_id", lambda employee_id: fake_employee.copy())
    monkeypatch.setattr("app.main.insert_prediction_log", fake_insert_prediction_log)
    monkeypatch.setattr("app.main.model", FakeModel())

    response = client.post("/predict", json={"employee_id": 1})

    assert response.status_code == 200
    assert len(calls) == 1
    assert calls[0]["employee_id"] == 1
    assert calls[0]["endpoint"] == "predict"
