from fastapi import APIRouter, Request, HTTPException, Path, Query
from typing import List, Dict, Any, Optional

router = APIRouter()

@router.get("/", response_model=List[Dict[str, Any]])
def get_alerts(
    request: Request,
    severity: Optional[str] = Query(None, description="Filter by severity (Info, Warning, High, Critical)"),
    acknowledged: Optional[bool] = Query(None, description="Filter by acknowledgment status"),
    search: Optional[str] = Query(None, description="Search query")
):
    """
    Get a list of active alerts representing flagged anomalous/suspicious user behavior.
    """
    try:
        data_service = request.app.state.data_service
        return data_service.get_alerts(severity=severity, acknowledged=acknowledged, search=search)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch alerts: {e}")

@router.put("/{alert_id}/acknowledge")
def acknowledge_alert(request: Request, alert_id: int = Path(..., description="ID of the alert to acknowledge")):
    """
    Mark a specific alert as acknowledged.
    """
    try:
        data_service = request.app.state.data_service
        success = data_service.acknowledge_alert(alert_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Alert with ID {alert_id} not found")
        return {"alert_id": alert_id, "status": "acknowledged", "success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to acknowledge alert: {e}")

@router.put("/acknowledge-all")
def acknowledge_all_alerts(request: Request):
    """
    Mark all alerts as acknowledged.
    """
    try:
        data_service = request.app.state.data_service
        count = data_service.acknowledge_all_alerts()
        return {"status": "acknowledged", "count": count, "success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to acknowledge all alerts: {e}")
