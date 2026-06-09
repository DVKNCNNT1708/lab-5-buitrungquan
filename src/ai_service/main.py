"""
FastAPI AI Mock Service
Lab 05: Docker Compose Readiness
Provides mock predictions for IoT readings
"""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Any
import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Service",
    description="Lab 05: Docker Compose Readiness - Mock AI Predictions",
    version="1.0.0"
)

SERVICE_NAME = "ai-service"
MODEL_VERSION = "mock-v1"


class HealthResponse(BaseModel):
    status: str
    service: str
    model: str


class PredictionResponse(BaseModel):
    label: str
    confidence: float


class PredictionRequest(BaseModel):
    device_id: Optional[str] = None
    metric: Optional[str] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    timestamp: Optional[str] = None


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """
    Health check endpoint
    Returns service status, name, and model version
    """
    return HealthResponse(
        status="ok",
        service=SERVICE_NAME,
        model=MODEL_VERSION
    )


@app.post("/predict", response_model=PredictionResponse, tags=["Predictions"])
async def predict(request: PredictionRequest) -> PredictionResponse:
    """
    Make a prediction on IoT data
    Returns mock prediction result with label and confidence
    """
    try:
        logger.info(f"Received prediction request for device: {request.device_id}, metric: {request.metric}")
        
        # Mock prediction logic
        # In real world, this would use actual ML model
        labels = ["normal", "anomaly", "warning"]
        
        # Simple heuristic: if value > 100, mark as anomaly
        if request.value and request.value > 100:
            label = "anomaly"
            confidence = 0.95
        elif request.value and request.value > 50:
            label = "warning"
            confidence = 0.75
        else:
            label = "normal"
            confidence = 0.98
        
        result = PredictionResponse(label=label, confidence=confidence)
        logger.info(f"Prediction result: {result}")
        
        return result
    
    except Exception as e:
        logger.error(f"Error in prediction: {str(e)}")
        return PredictionResponse(label="error", confidence=0.0)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "AI Service Lab 05",
        "service": SERVICE_NAME,
        "model": MODEL_VERSION,
        "endpoints": [
            "GET /health",
            "POST /predict"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9000,
        log_level="info"
    )
