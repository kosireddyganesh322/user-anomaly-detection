import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.routes import users, alerts, analytics, predictions, reports
from backend.app.services.data_service import DataService

# Set up logging format
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set up lifespan for loading data once on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize service and store it in app state
    service = DataService()
    app.state.data_service = service
    logger.info("Lifespan setup completed: DataService state loaded.")
    yield
    # Cleanup on shutdown
    logger.info("Lifespan shutdown: Cleaning state.")

app = FastAPI(
    title="User Anomaly Detection — NFC",
    description="Insider Threat & Anomaly Detection System for Nuclear Fuel Complex",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include standard prefixed routers
app.include_router(users.router,       prefix="/api/users",       tags=["Users"])
app.include_router(alerts.router,      prefix="/api/alerts",      tags=["Alerts"])
app.include_router(analytics.router,   prefix="/api/analytics",   tags=["Analytics"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["Predictions"])
app.include_router(reports.router,     prefix="/api/reports",     tags=["Reports"])

# Mount extra endpoints requested by the user
@app.get("/api/dashboard/overview", tags=["Dashboard"])
@app.get("/dashboard/overview", tags=["Dashboard"])
def get_dashboard_overview(request: Request):
    """
    Get dashboard overview metrics containing total counts, anomalies, and risk breakdowns.
    """
    try:
        return request.app.state.data_service.get_dashboard_overview()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch overview: {e}")

@app.get("/api/anomalies", tags=["Anomalies"])
@app.get("/anomalies", tags=["Anomalies"])
def get_anomalies(request: Request):
    """
    Get a list of all users flagged as suspicious anomalies.
    """
    try:
        return request.app.state.data_service.get_anomalies()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch anomalies: {e}")

@app.get("/api/anomalies/high-risk", tags=["Anomalies"])
@app.get("/anomalies/high-risk", tags=["Anomalies"])
def get_high_risk_anomalies(request: Request):
    """
    Get a list of high-risk / critical users flagged as suspicious anomalies.
    """
    try:
        return request.app.state.data_service.get_high_risk_anomalies()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch high risk anomalies: {e}")

@app.get("/")
@app.get("/api")
def health_check():
    return {"status": "ok", "service": "anomaly-detection-api"}
