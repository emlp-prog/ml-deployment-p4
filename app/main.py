import os
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Literal
import pandas as pd
import psycopg
from dotenv import load_dotenv
import joblib
from ml_model.feature_engineering import AttritionFeatureEngineer
from psycopg.types.json import Jsonb

load_dotenv()

app = FastAPI()
model = joblib.load("ml_model/model.joblib")

class PredictRequest(BaseModel):
    id_employee: int
    age: int = Field(..., ge=0, le=150)
    genre: Literal["M", "F"]
    revenu_mensuel: float = Field(..., ge=0)
    statut_marital: Literal['Célibataire', 'Marié(e)', 'Divorcé(e)']
    departement: Literal['Commercial', 'Consulting', 'Ressources Humaines']
    poste: Literal['Cadre Commercial', 'Assistant de Direction', 'Consultant', 'Tech Lead', 'Manager',
                   'Senior Manager', 'Représentant Commercial','Directeur Technique','Ressources Humaines']
    nombre_experiences_precedentes: int = Field(..., ge=0)
    nombre_heures_travailless: int = Field(ge=0)                                    # Pas obligatoire pour la prédiction
    annee_experience_totale: int = Field(..., ge=0)
    annees_dans_l_entreprise: int = Field(..., ge=0)
    annees_dans_le_poste_actuel: int = Field(..., ge=0)
    satisfaction_employee_environnement: int = Field(..., ge=1, le=5)
    note_evaluation_precedente: int = Field(..., ge=1, le=5)
    niveau_hierarchique_poste: int = Field(..., ge=1)
    satisfaction_employee_nature_travail: int = Field(..., ge=1, le=5)
    satisfaction_employee_equipe: int = Field(..., ge=1, le=5)
    satisfaction_employee_equilibre_pro_perso: int = Field(..., ge=1, le=5)
    note_evaluation_actuelle: int = Field(..., ge=1, le=5)
    heure_supplementaires: Literal["Oui", "Non"]
    augementation_salaire_precedente: str = Field(..., pattern=r"^\d+(\.\d+)?\s%$")
    nombre_participation_pee: int = Field(..., ge=0)
    nb_formations_suivies: int = Field(..., ge=0)
    nombre_employee_sous_responsabilite: int = Field(..., ge=0)                     # Pas obligatoire pour la prédiction
    distance_domicile_travail: float = Field(..., ge=0)
    niveau_education: int = Field(..., ge=0)
    domaine_etude: Literal['Infra & Cloud', 'Autre', 'Transformation Digitale', 'Marketing', 'Entrepreunariat', 'Ressources Humaines']
    ayant_enfants: Literal["Y", "N"]                                                # Pas obligatoire pour la prédiction
    frequence_deplacement: Literal["Frequent", "Occasionnel", "Aucun"]
    annees_depuis_la_derniere_promotion: int = Field(..., ge=0)
    annes_sous_responsable_actuel: int = Field(..., ge=0)

class PredictResponse(BaseModel):
    prediction: int

def get_conn():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL pas défini")
    return psycopg.connect(db_url)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/health")
def health_check():
    return {"status": "ok"} 

@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    df = pd.DataFrame([request.model_dump()])
    prediction = int(model.predict(df)[0])
    response = PredictResponse(prediction=prediction)

# Enregistrer les prédictions dans la base de données
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO predictions (input_payload, output_payload, model_version)
                VALUES (%s, %s, %s)
                """,
                (
                    Jsonb(request.model_dump()),
                    Jsonb(response.model_dump()),
                    "xgb_pipeline_v1",
                ),
            )
    return response