import os

import joblib
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from app.db import DatabaseError, get_employee_by_id, insert_prediction_log

load_dotenv()

app = FastAPI(
    title="Employee Attrition API",
    description="API de prediction du risque de depart d'un employe.",
    version="1.0.0",
)

model = joblib.load("ml_model/model.joblib")


class EmployeeRequest(BaseModel):
    employee_id: int = Field(..., gt=0, description="Identifiant de l'employe")


class PredictResponse(BaseModel):
    employee_id: int
    prediction: int


class PredictProbaResponse(BaseModel):
    employee_id: int
    prediction: int
    probability: float


def check_api_key(x_api_key: str | None = Header(default=None)) -> None:
    expected_api_key = os.getenv("API_KEY")

    if expected_api_key and x_api_key != expected_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.get("/")
def read_root():
    return {"message": "Employee Attrition API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict(request: EmployeeRequest, x_api_key: str | None = Header(default=None)):
    check_api_key(x_api_key)

    try:
        employee = get_employee_by_id(request.employee_id)
    except DatabaseError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    employee.pop("a_quitte_l_entreprise", None)
    employee_df = pd.DataFrame([employee])

    prediction = int(model.predict(employee_df)[0])

    response = PredictResponse(
        employee_id=request.employee_id,
        prediction=prediction,
    )

    try:
        insert_prediction_log(
            employee_id=request.employee_id,
            endpoint="predict",
            input_payload=request.model_dump(),
            output_payload=response.model_dump(),
        )
    except DatabaseError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return response


@app.post("/predict_proba", response_model=PredictProbaResponse)
def predict_proba(request: EmployeeRequest, x_api_key: str | None = Header(default=None)):
    check_api_key(x_api_key)

    try:
        employee = get_employee_by_id(request.employee_id)
    except DatabaseError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    employee.pop("a_quitte_l_entreprise", None)
    employee_df = pd.DataFrame([employee])

    prediction = int(model.predict(employee_df)[0])
    probability = float(model.predict_proba(employee_df)[0][1])

    response = PredictProbaResponse(
        employee_id=request.employee_id,
        prediction=prediction,
        probability=probability,
    )

    try:
        insert_prediction_log(
            employee_id=request.employee_id,
            endpoint="predict_proba",
            input_payload=request.model_dump(),
            output_payload=response.model_dump(),
        )
    except DatabaseError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return response
