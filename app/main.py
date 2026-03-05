import os
from fastapi import FastAPI
from pydantic import BaseModel
import psycopg
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

class PredictRequest(BaseModel):
    text: str

class PredictResponse(BaseModel):
    message: str

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
    # Dummy prediction logic
    if "hello" in request.text.lower():
        response = PredictResponse(message="Hello to you too!")
    else:
        response = PredictResponse(message="I don't understand.")

# Enregistrer les prédictions dans la base de données
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO predictions (input_text, prediction) VALUES (%s, %s)",
                (request.text, response.message),
            )
    return response