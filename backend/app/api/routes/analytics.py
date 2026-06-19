from fastapi import APIRouter, Request, HTTPException
from typing import List, Dict
from backend.app.schemas.user import TrendPoint, DepartmentSummaryPoint

router = APIRouter()

@router.get("/risk-distribution", response_model=Dict[str, int])
def get_risk_distribution(request: Request):
    """
    Get user counts categorized by risk level.
    """
    try:
        data_service = request.app.state.data_service
        return data_service.get_risk_distribution()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch risk distribution: {e}")

@router.get("/login-trends", response_model=List[TrendPoint])
def get_login_trends(request: Request):
    """
    Get historical login frequency trend grouped by day.
    """
    try:
        data_service = request.app.state.data_service
        return data_service.get_login_trends()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch login trends: {e}")

@router.get("/device-trends", response_model=List[TrendPoint])
def get_device_trends(request: Request):
    """
    Get historical USB device connection trend grouped by day.
    """
    try:
        data_service = request.app.state.data_service
        return data_service.get_device_trends()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch device trends: {e}")

@router.get("/department-summary", response_model=List[DepartmentSummaryPoint])
def get_department_summary(request: Request):
    """
    Get total users and anomalous user counts grouped by department (LDAP).
    """
    try:
        data_service = request.app.state.data_service
        return data_service.get_department_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch department summaries: {e}")

@router.get("/top-risk-users")
def get_top_risk_users(request: Request):
    try:
        data_service = request.app.state.data_service
        return data_service.get_top_risk_users()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch top risk users: {e}")

@router.get("/department-risk-ranking")
def get_department_risk_ranking(request: Request):
    try:
        data_service = request.app.state.data_service
        return data_service.get_department_risk_ranking()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch department risk ranking: {e}")

@router.get("/anomaly-reason-breakdown")
def get_anomaly_reason_breakdown(request: Request):
    try:
        data_service = request.app.state.data_service
        return data_service.get_anomaly_reason_breakdown()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch anomaly reason breakdown: {e}")

@router.get("/threat-heatmap")
def get_threat_heatmap(request: Request):
    try:
        data_service = request.app.state.data_service
        return data_service.get_threat_heatmap()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch threat heatmap: {e}")

@router.get("/security-posture")
def get_security_posture(request: Request):
    try:
        data_service = request.app.state.data_service
        return data_service.get_security_posture_score()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch security posture score: {e}")

@router.get("/risk-matrix")
def get_risk_matrix(request: Request):
    try:
        data_service = request.app.state.data_service
        return data_service.get_user_activity_risk_matrix()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch risk matrix: {e}")

@router.get("/behavioral-indicators")
def get_behavioral_indicators(request: Request):
    try:
        data_service = request.app.state.data_service
        return data_service.get_behavioral_indicators_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch behavioral indicators: {e}")

@router.get("/watchlist")
def get_watchlist(request: Request):
    try:
        data_service = request.app.state.data_service
        return data_service.get_watchlist()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch watchlist: {e}")
