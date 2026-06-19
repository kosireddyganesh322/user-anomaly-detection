import logging
from typing import List, Optional
from fastapi import APIRouter, File, UploadFile, Form, Request, HTTPException
from backend.app.services.dataset_service import DatasetService, processing_jobs

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/upload")
async def upload_dataset(
    request: Request,
    name: str = Form(...),
    users: UploadFile = File(...),
    logon: UploadFile = File(...),
    device: UploadFile = File(...),
    ldap: UploadFile = File(...)
):
    """
    Upload a new organizational dataset. Automatically validates columns
    and launches background processing pipeline.
    """
    # Verify file extensions are strictly CSV
    for file_obj, filename in [(users, "users.csv"), (logon, "logon.csv"), (device, "device.csv"), (ldap, "ldap.csv")]:
        if not file_obj.filename.lower().endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file format for {filename}. Only CSV files are allowed."
            )

    try:
        service = DatasetService(request.app.state.data_service)
        result = await service.process_dataset_upload(name, users, logon, device, ldap)
        return result
    except Exception as e:
        logger.error(f"Upload failed for dataset {name}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate")
async def validate_dataset(
    request: Request,
    users: UploadFile = File(...),
    logon: UploadFile = File(...),
    device: UploadFile = File(...),
    ldap: UploadFile = File(...)
):
    """
    Validate dataset CSV columns before committing to upload.
    """
    # Temporary saving and validation
    import tempfile
    import os
    
    temp_dir = tempfile.mkdtemp()
    try:
        users_path = os.path.join(temp_dir, "users.csv")
        logon_path = os.path.join(temp_dir, "logon.csv")
        device_path = os.path.join(temp_dir, "device.csv")
        ldap_path = os.path.join(temp_dir, "ldap.csv")
        
        # Save uploaded files to temp
        with open(users_path, "wb") as f: f.write(await users.read())
        with open(logon_path, "wb") as f: f.write(await logon.read())
        with open(device_path, "wb") as f: f.write(await device.read())
        with open(ldap_path, "wb") as f: f.write(await ldap.read())
        
        service = DatasetService(request.app.state.data_service)
        
        # Check schemas
        errors = {
            "missing_files": [],
            "missing_columns": {},
            "incorrect_formats": []
        }
        
        u_res = service.validate_file_schema(users_path, ["user_id", "name", "department", "role"], {"employee_name": "name"})
        if not u_res["valid"]: errors["missing_columns"]["users.csv"] = u_res["missing_columns"]

        lo_res = service.validate_file_schema(logon_path, ["user_id", "date", "activity", "pc"], {"user": "user_id"})
        if not lo_res["valid"]: errors["missing_columns"]["logon.csv"] = lo_res["missing_columns"]

        d_res = service.validate_file_schema(device_path, ["user_id", "date", "activity", "device"], {"user": "user_id", "pc": "device"})
        if not d_res["valid"]: errors["missing_columns"]["device.csv"] = d_res["missing_columns"]

        ld_res = service.validate_file_schema(ldap_path, ["user_id", "manager", "team"], {"supervisor": "manager"})
        if not ld_res["valid"]: errors["missing_columns"]["ldap.csv"] = ld_res["missing_columns"]

        # Clean up temp
        for path in [users_path, logon_path, device_path, ldap_path]:
            if os.path.exists(path):
                os.remove(path)
        os.rmdir(temp_dir)
        
        valid = len(errors["missing_columns"]) == 0
        return {
            "valid": valid,
            "errors": errors
        }
    except Exception as e:
        logger.error(f"Pre-validation failed: {e}", exc_info=True)
        # Clean up temp if folder exists
        if os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"Pre-validation engine failed: {str(e)}")


@router.get("")
def list_datasets(request: Request):
    """
    List all available datasets and their statuses.
    """
    try:
        service = DatasetService(request.app.state.data_service)
        return service.list_datasets()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/switch")
def switch_dataset(request: Request, payload: dict):
    """
    Switch active platform dataset. Reloads dashboard, charts, alerts, and report telemetry.
    """
    name = payload.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="Dataset name is required.")
    
    try:
        service = DatasetService(request.app.state.data_service)
        sanitized_name = service.sanitize_dataset_name(name)
        
        # Verify metadata exists / dataset is processed successfully
        meta = service.get_dataset_metadata(sanitized_name)
        if not meta:
            raise HTTPException(status_code=404, detail=f"Dataset '{sanitized_name}' not found.")
        if meta["status"] != "Success":
            raise HTTPException(status_code=400, detail=f"Dataset '{sanitized_name}' cannot be switched as its status is: {meta['status']}.")
        
        request.app.state.data_service.switch_dataset(sanitized_name)
        return {
            "success": True,
            "message": f"Active dataset switched to '{sanitized_name}' successfully.",
            "current_dataset": sanitized_name
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/active")
def get_active_dataset(request: Request):
    """
    Get active dataset metadata.
    """
    try:
        data_service = request.app.state.data_service
        active_name = data_service.current_dataset
        
        service = DatasetService(data_service)
        meta = service.get_dataset_metadata(active_name)
        if not meta:
            return {
                "name": active_name,
                "status": "Success",
                "total_users": len(data_service.users_df),
                "total_records": 0
            }
        return meta
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{name}/metadata")
def get_dataset_metadata(request: Request, name: str):
    """
    Get metadata for a specific dataset.
    """
    try:
        service = DatasetService(request.app.state.data_service)
        meta = service.get_dataset_metadata(name)
        if not meta:
            raise HTTPException(status_code=404, detail=f"Dataset '{name}' metadata not found.")
        return meta
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{name}/status")
def get_dataset_status(request: Request, name: str):
    """
    Get status/progress details for a running background reprocessing job.
    """
    service = DatasetService(request.app.state.data_service)
    sanitized_name = service.sanitize_dataset_name(name)
    
    if sanitized_name in processing_jobs:
        return processing_jobs[sanitized_name]
        
    meta = service.get_dataset_metadata(sanitized_name)
    if meta:
        return {
            "status": meta.get("status", "Draft"),
            "progress": 100 if meta.get("status") == "Success" else 0,
            "current_step": "Completed" if meta.get("status") == "Success" else "Idle",
            "error": meta.get("error")
        }
        
    return {
        "status": "NotFound",
        "progress": 0,
        "current_step": "Idle",
        "error": "No record of this dataset exists."
    }


@router.delete("/{name}")
def delete_dataset(request: Request, name: str):
    """
    Delete a custom dataset.
    """
    try:
        service = DatasetService(request.app.state.data_service)
        service.delete_dataset(name)
        return {
            "success": True,
            "message": f"Dataset '{name}' deleted successfully."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{name}/reprocess")
def reprocess_dataset(request: Request, name: str):
    """
    Trigger manual reprocessing of raw files for a dataset.
    """
    try:
        service = DatasetService(request.app.state.data_service)
        result = service.trigger_reprocess(name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
