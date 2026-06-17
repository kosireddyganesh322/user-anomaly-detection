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
