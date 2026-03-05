import os
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_predict():
    response = client.post("/predict", json={"text": "Hello, how are you?"})
    assert response.status_code == 200
    assert response.json() == {"message": "Hello to you too!"}

    response = client.post("/predict", json={"text": "Goodbye!"})
    assert response.status_code == 200
    assert response.json() == {"message": "I don't understand."}

def test_predict_validation_error():
    response = client.post("/predict", json={"text": 123})
    assert response.status_code == 422