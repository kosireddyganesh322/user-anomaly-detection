from pydantic import BaseModel
from typing import Optional, List

class UserBase(BaseModel):
    user_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None
    team: Optional[str] = None
    manager: Optional[str] = None

class UserResponse(UserBase):
    risk_score: Optional[float] = 0.0
    risk_level: Optional[str] = "Low"
    anomaly_score: Optional[float] = 0.0
    anomaly_label: Optional[str] = "Normal"
    security_status: Optional[str] = "Normal"

    class Config:
        from_attributes = True

class DashboardOverviewResponse(BaseModel):
    total_users: int
    anomalies_detected: int
    high_risk_users: int
    critical_users: int

class PaginatedUsersResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    limit: int

class TrendPoint(BaseModel):
    day: str
    count: int

class DepartmentSummaryPoint(BaseModel):
    department: str
    total_users: int
    anomalies: int
