"""
FastAPI IoT Ingestion Service
Lab 05: Docker Compose Readiness
"""
import uuid
import os
import requests
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel, Field
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="IoT Ingestion Service",
    description="Lab 05: Docker Compose Readiness",
    version="1.0.0"
)

# Configuration
SERVICE_NAME = "iot-service"
SERVICE_VERSION = "1.0.0"
API_SECRET_TOKEN = os.getenv("API_SECRET_TOKEN", "lab05-secret-token")
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://ai-service:9000")

# Models
class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class ReadingRequest(BaseModel):
    device_id: str = Field(..., description="Device identifier")
    metric: str = Field(..., description="Metric name")
    value: float = Field(..., description="Metric value")
    unit: str = Field(default="", description="Unit of measurement")


class ReadingResponse(BaseModel):
    reading_id: str
    status: str
    ai_result: Optional[dict] = None


# Helper function to verify token
def verify_token(authorization: Optional[str] = Header(None)) -> str:
    """Verify Bearer token from Authorization header"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization token")
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = parts[1]
    if token != API_SECRET_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return token


# Endpoints
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """
    Health check endpoint
    Returns service status, name, and version
    """
    return HealthResponse(
        status="ok",
        service=SERVICE_NAME,
        version=SERVICE_VERSION
    )


@app.post("/readings", response_model=ReadingResponse, tags=["Readings"])
async def create_reading(
    reading: ReadingRequest,
    token: str = Depends(verify_token)
) -> ReadingResponse:
    """
    Create a new reading from IoT device
    Requires Bearer token in Authorization header
    
    Steps:
    1. Validate reading request
    2. Call AI service /predict endpoint
    3. Return reading_id, status, and AI result
    """
    try:
        # Generate reading ID
        reading_id = str(uuid.uuid4())
        
        logger.info(f"Processing reading: device={reading.device_id}, metric={reading.metric}, value={reading.value}")
        
        # Call AI service for prediction
        ai_payload = {
            "device_id": reading.device_id,
            "metric": reading.metric,
            "value": reading.value,
            "unit": reading.unit,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Calling AI service at {AI_SERVICE_URL}/predict")
        response = requests.post(
            f"{AI_SERVICE_URL}/predict",
            json=ai_payload,
            timeout=5
        )
        
        if response.status_code != 200:
            logger.warning(f"AI service returned {response.status_code}: {response.text}")
            ai_result = {"label": "unknown", "confidence": 0.0}
        else:
            ai_result = response.json()
        
        logger.info(f"AI prediction result: {ai_result}")
        
        return ReadingResponse(
            reading_id=reading_id,
            status="success",
            ai_result=ai_result
        )
    
    except requests.RequestException as e:
        logger.error(f"Error calling AI service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="AI service unavailable"
        )
    except Exception as e:
        logger.error(f"Error processing reading: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "IoT Ingestion Service Lab 05",
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "endpoints": [
            "GET /health",
            "POST /readings (requires Bearer token)"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
