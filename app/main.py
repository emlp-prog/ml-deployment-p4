from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class PredictRequest(BaseModel):
    text: str

class PredictResponse(BaseModel):
    message: str

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
        return PredictResponse(message="Hello to you too!")
    else:
        return PredictResponse(message="I don't understand.")