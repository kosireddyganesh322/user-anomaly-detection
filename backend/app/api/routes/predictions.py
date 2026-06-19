import os
from fastapi import APIRouter, Request, HTTPException
from ml.risk_scoring.risk_engine import run_risk_scoring
from ml.prediction.predict import predict
from ml.prediction.generate_security_profile import generate_profile

router = APIRouter()

@router.post("/run")
def run_predictions(request: Request):
    """
    Trigger the Isolation Forest prediction and Risk Scoring pipeline.
    Recomputes user risk levels, anomaly scores, and updates final profiles.
    """
    try:
        # Resolve path offsets based on presence of data folder
        base_dir = ""
        if not os.path.exists("data"):
            base_dir = "../"

        features_path = os.path.join(base_dir, "data/features/user_features.csv")
        risk_path = os.path.join(base_dir, "data/reports/risk_scores.csv")
        anomaly_path = os.path.join(base_dir, "data/reports/anomaly_report.csv")
        profile_path = os.path.join(base_dir, "data/reports/final_security_profile.csv")
        model_path = os.path.join(base_dir, "ml/models/isolation_forest.pkl")
        scaler_path = os.path.join(base_dir, "ml/models/scaler.pkl")

        # Verify raw feature inputs are present
        if not os.path.exists(features_path):
            raise FileNotFoundError(f"Feature table not found at: {features_path}. Run features extraction first.")

        # 1. Run rule-based risk calculations
        run_risk_scoring(features_path, risk_path)

        # 2. Run Isolation Forest inference
        predict(features_path, model_path, scaler_path, anomaly_path)

        # 3. Consolidate final profile
        generate_profile(features_path, risk_path, anomaly_path, profile_path)

        # 4. Invalidate and reload backend in-memory state
        data_service = request.app.state.data_service
        data_service.load_data()

        return {
            "status": "success",
            "message": "Security profile updated and reloaded successfully."
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Inference pipeline execution failed: {str(e)}"
        )

@router.get("/results")
def get_results(request: Request):
    """
    Retrieve latest anomaly predictions and security statuses from memory.
    """
    try:
        data_service = request.app.state.data_service
        return data_service.get_anomalies()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch prediction results: {str(e)}"
        )

