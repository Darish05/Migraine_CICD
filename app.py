# app.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any
import uvicorn
from migraine_models_enhanced import EnhancedMigrainePredictor
import json

app = FastAPI(
    title="Migraine Prediction API",
    description="ML-powered migraine prediction with top 2 models",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize predictor
predictor = EnhancedMigrainePredictor()

class PatientInput(BaseModel):
    age: int = Field(..., ge=10, le=100, description="Age of patient")
    gender: int = Field(..., ge=0, le=1, description="Gender (0: Male, 1: Female)")
    sleep_hours: float = Field(..., ge=0, le=24, description="Hours of sleep")
    sleep_quality: int = Field(..., ge=1, le=10, description="Sleep quality (1-10)")
    stress_level: int = Field(..., ge=1, le=10, description="Stress level (1-10)")
    hydration: int = Field(..., ge=0, le=10, description="Hydration level (0-10)")
    exercise: int = Field(..., ge=0, le=7, description="Exercise days per week")
    screen_time: float = Field(..., ge=0, le=24, description="Screen time hours")
    caffeine_intake: int = Field(..., ge=0, le=10, description="Caffeine intake")
    alcohol_intake: int = Field(..., ge=0, le=10, description="Alcohol intake")
    weather_changes: int = Field(..., ge=0, le=1, description="Weather changes (0/1)")
    menstrual_cycle: int = Field(..., ge=0, le=1, description="Menstrual cycle (0/1)")
    dehydration: int = Field(..., ge=0, le=1, description="Dehydration (0/1)")
    bright_light: int = Field(..., ge=0, le=1, description="Bright light exposure (0/1)")
    loud_noises: int = Field(..., ge=0, le=1, description="Loud noises (0/1)")
    strong_smells: int = Field(..., ge=0, le=1, description="Strong smells (0/1)")
    missed_meals: int = Field(..., ge=0, le=1, description="Missed meals (0/1)")
    specific_foods: int = Field(..., ge=0, le=1, description="Specific foods (0/1)")
    physical_activity: int = Field(..., ge=0, le=1, description="Physical activity (0/1)")
    neck_pain: int = Field(..., ge=0, le=1, description="Neck pain (0/1)")
    weather_pressure: float = Field(..., description="Weather pressure")
    humidity: float = Field(..., ge=0, le=100, description="Humidity percentage")
    temperature_change: float = Field(..., description="Temperature change")

@app.on_event("startup")
async def startup_event():
    """Load models on startup"""
    success = predictor.load_models()
    if not success:
        print("⚠️ Models not found. Training new models...")
        predictor.train_models()

@app.get("/")
async def root():
    return {
        "message": "Migraine Prediction API",
        "version": "2.0.0",
        "endpoints": ["/predict", "/models-info", "/health"]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "models_loaded": len(predictor.top_classification_models) > 0}

@app.get("/models-info")
async def get_models_info():
    """Get information about top 2 models"""
    try:
        with open('models_info.json', 'r') as f:
            models_info = json.load(f)
        return models_info
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Models info not found")

@app.post("/predict")
async def predict(patient: PatientInput):
    """Make predictions using both top models"""
    try:
        input_data = patient.dict()
        predictions = predictor.predict(input_data)
        
        if predictions is None:
            raise HTTPException(status_code=500, detail="Prediction failed")
        
        return {
            "success": True,
            "predictions": predictions,
            "input_data": input_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/retrain")
async def retrain_models():
    """Retrain all models (admin endpoint)"""
    try:
        class_results, reg_results = predictor.train_models()
        return {
            "success": True,
            "message": "Models retrained successfully",
            "classification_results": [
                {k: v for k, v in r.items() if k != 'model'} 
                for r in class_results
            ],
            "regression_results": [
                {k: v for k, v in r.items() if k != 'model'} 
                for r in reg_results
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)