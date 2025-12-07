# src/api.py
# Minimal FastAPI app exposing a health-check and a simple predict endpoint (loads model if available)
from fastapi import FastAPI
import joblib, os, pandas as pd
from pydantic import BaseModel

app = FastAPI(title='SmartAQI API')

class PredictRequest(BaseModel):
    features: dict

MODEL_PATH = "models/lgb_baseline.pkl"
model = None
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)

@app.get('/health')
def health():
    return {"status":"ok"}

@app.post('/predict')
def predict(req: PredictRequest):
    if model is None:
        return {"error":"No model available. Train a model and place it at models/lgb_baseline.pkl"}
    df = pd.DataFrame([req.features])
    preds = model.predict(df)
    return {"predictions": preds.tolist()}
