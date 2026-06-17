from fastapi import APIRouter, Query, HTTPException, Request
from typing import Optional
from backend.app.schemas.user import PaginatedUsersResponse, UserResponse, DashboardOverviewResponse

router = APIRouter()

@router.get("/dashboard/overview", response_model=DashboardOverviewResponse)
def get_overview(request: Request):
    """
    Get dashboard summary overview counters.
    """
    try:
        data_service = request.app.state.data_service
        return data_service.get_dashboard_overview()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch overview metrics: {e}")

@router.get("/", response_model=PaginatedUsersResponse)
def get_users(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Page limit"),
    search: Optional[str] = Query(None, description="Search term matching ID, name, or role"),
    department: Optional[str] = Query(None, description="Filter by department"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level (Low, Medium, High, Critical)"),
    anomaly_label: Optional[str] = Query(None, description="Filter by anomaly label (Normal, Suspicious)"),
    security_status: Optional[str] = Query(None, description="Filter by security status")
):
    """
    Get a paginated list of users matching search and filter criteria.
    """
    try:
        data_service = request.app.state.data_service
        return data_service.get_users(
            page=page,
            limit=limit,
            search=search,
            department=department,
            risk_level=risk_level,
            anomaly_label=anomaly_label,
            security_status=security_status
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch users: {e}")

@router.get("/{user_id}", response_model=UserResponse)
def get_user_profile(user_id: str, request: Request):
    """
    Get single user's detailed profile, risk score, and anomaly score.
    """
    try:
        data_service = request.app.state.data_service
        user = data_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user profile: {e}")
