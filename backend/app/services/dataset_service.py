import os
import re
import json
import uuid
import shutil
import logging
import threading
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import UploadFile, HTTPException

logger = logging.getLogger(__name__)

# In-memory store for active background jobs
processing_jobs: Dict[str, Dict[str, Any]] = {}

class DatasetService:
    def __init__(self, data_service_state=None):
        self.data_service = data_service_state
        self.base_dir = "data/datasets"
        os.makedirs(self.base_dir, exist_ok=True)
        self.init_cert_metadata()

    def init_cert_metadata(self):
        """Pre-populate the CERT metadata if it doesn't exist, to ensure uniform listing."""
        cert_meta_dir = os.path.join(self.base_dir, "CERT")
        os.makedirs(cert_meta_dir, exist_ok=True)
        meta_path = os.path.join(cert_meta_dir, "metadata.json")
        if not os.path.exists(meta_path):
            cert_meta = {
                "name": "CERT",
                "upload_date": "2026-06-17 00:00:00",
                "total_users": 4000,
                "total_records": 3534287,
                "status": "Success",
                "departments": 12,
                "date_range": "2010-01-02 to 2011-06-01",
                "records_processed": 3534287,
                "missing_values_count": 0,
                "data_quality_score": 100
            }
            with open(meta_path, "w") as f:
                json.dump(cert_meta, f, indent=4)

    def list_datasets(self) -> List[Dict[str, Any]]:
        """List all datasets in data/datasets/."""
        datasets = []
        # Ensure CERT is always initialized
        self.init_cert_metadata()

        if not os.path.exists(self.base_dir):
            return []

        for name in os.listdir(self.base_dir):
            dir_path = os.path.join(self.base_dir, name)
            if not os.path.isdir(dir_path):
                continue

            meta_path = os.path.join(dir_path, "metadata.json")
            if os.path.exists(meta_path):
                try:
                    with open(meta_path, "r") as f:
                        meta = json.load(f)
                    # If there's an active in-memory job, update status and progress
                    if name in processing_jobs:
                        meta["status"] = processing_jobs[name]["status"]
                        meta["progress"] = processing_jobs[name]["progress"]
                        meta["current_step"] = processing_jobs[name]["current_step"]
                    datasets.append(meta)
                except Exception as e:
                    logger.error(f"Failed to read metadata for dataset {name}: {e}")
            else:
                # Missing metadata.json, generate a draft entry
                status = "Processing" if name in processing_jobs else "Draft"
                progress = processing_jobs[name]["progress"] if name in processing_jobs else 0
                datasets.append({
                    "name": name,
                    "upload_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "total_users": 0,
                    "total_records": 0,
                    "status": status,
                    "progress": progress,
                    "departments": 0,
                    "data_quality_score": 0
                })
        return datasets

    def get_dataset_metadata(self, name: str) -> Optional[Dict[str, Any]]:
        """Fetch metadata for a specific dataset."""
        self.sanitize_dataset_name(name)
        dir_path = os.path.join(self.base_dir, name)
        meta_path = os.path.join(dir_path, "metadata.json")
        if os.path.exists(meta_path):
            with open(meta_path, "r") as f:
                meta = json.load(f)
            if name in processing_jobs:
                meta["status"] = processing_jobs[name]["status"]
                meta["progress"] = processing_jobs[name]["progress"]
                meta["current_step"] = processing_jobs[name]["current_step"]
                meta["error"] = processing_jobs[name].get("error")
            return meta
        return None

    def sanitize_dataset_name(self, name: str) -> str:
        """Sanitize name to prevent path traversal."""
        if not re.match(r"^[a-zA-Z0-9_\-]+$", name):
            raise HTTPException(
                status_code=400,
                detail="Invalid dataset name. Only alphanumeric characters, hyphens, and underscores are allowed."
            )
        return name

    def validate_file_schema(self, file_path: str, required_cols: List[str], mapping: Dict[str, str] = {}) -> Dict[str, Any]:
        """Read the header of a file and check columns, including case-insensitive and mapping checks."""
        try:
            df_header = pd.read_csv(file_path, nrows=5)
            cols = [str(c).strip().lower() for c in df_header.columns]
            
            missing = []
            for col in required_cols:
                alt_names = [col.lower()]
                # Include any alias mappings (e.g. employee_name for name, user for user_id)
                for k, v in mapping.items():
                    if v == col:
                        alt_names.append(k.lower())
                
                # Check if any alias is present in the actual columns
                if not any(alt in cols for alt in alt_names):
                    missing.append(col)

            return {
                "valid": len(missing) == 0,
                "missing_columns": missing,
                "total_records": 0, # computed later in standardisation
                "columns_found": list(df_header.columns)
            }
        except Exception as e:
            return {
                "valid": False,
                "error": f"Failed to parse CSV: {str(e)}",
                "missing_columns": required_cols
            }

    async def save_uploaded_file(self, upload_file: UploadFile, dest_path: str):
        """Save a FastAPI UploadFile to disk safely."""
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        with open(dest_path, "wb") as f:
            while chunk := await upload_file.read(8192):
                f.write(chunk)

    async def process_dataset_upload(
        self,
        name: str,
        users_file: UploadFile,
        logon_file: UploadFile,
        device_file: UploadFile,
        ldap_file: UploadFile
    ) -> Dict[str, Any]:
        """Upload, validate, and launch background thread for reprocessing."""
        name = self.sanitize_dataset_name(name)

        if name.upper() == "CERT":
            raise HTTPException(status_code=400, detail="Cannot overwrite or upload to the default CERT dataset.")

        # Create raw directory
        raw_dir = os.path.join(self.base_dir, name, "raw")
        os.makedirs(raw_dir, exist_ok=True)

        # File paths on disk
        users_path = os.path.join(raw_dir, "users.csv")
        logon_path = os.path.join(raw_dir, "logon.csv")
        device_path = os.path.join(raw_dir, "device.csv")
        ldap_path = os.path.join(raw_dir, "ldap.csv")

        # Save files
        await self.save_uploaded_file(users_file, users_path)
        await self.save_uploaded_file(logon_file, logon_path)
        await self.save_uploaded_file(device_file, device_path)
        await self.save_uploaded_file(ldap_file, ldap_path)

        # Run validation
        validation_result = self.validate_dataset(name)
        if not validation_result["valid"]:
            # Clean up directories
            shutil.rmtree(os.path.join(self.base_dir, name), ignore_errors=True)
            return {
                "success": False,
                "message": "Dataset validation failed.",
                "details": validation_result
            }

        # Initialize background job state
        processing_jobs[name] = {
            "status": "Processing",
            "progress": 0,
            "current_step": "Data Normalization",
            "error": None
        }

        # Save initial metadata
        meta = {
            "name": name,
            "upload_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_users": 0,
            "total_records": 0,
            "status": "Processing",
            "progress": 0,
            "departments": 0,
            "date_range": "Calculating...",
            "records_processed": 0,
            "missing_values_count": 0,
            "data_quality_score": 100
        }
        with open(os.path.join(self.base_dir, name, "metadata.json"), "w") as f:
            json.dump(meta, f, indent=4)

        # Launch thread
        thread = threading.Thread(target=self.run_pipeline, args=(name,))
        thread.start()

        return {
            "success": True,
            "message": "Dataset uploaded successfully. Background processing started.",
            "details": validation_result
        }

    def validate_dataset(self, name: str) -> Dict[str, Any]:
        """Validate files and columns inside the raw folder."""
        name = self.sanitize_dataset_name(name)
        raw_dir = os.path.join(self.base_dir, name, "raw")

        users_path = os.path.join(raw_dir, "users.csv")
        logon_path = os.path.join(raw_dir, "logon.csv")
        device_path = os.path.join(raw_dir, "device.csv")
        ldap_path = os.path.join(raw_dir, "ldap.csv")

        errors = {
            "missing_files": [],
            "missing_columns": {},
            "incorrect_formats": []
        }

        # Check files exist
        if not os.path.exists(users_path): errors["missing_files"].append("users.csv")
        if not os.path.exists(logon_path): errors["missing_files"].append("logon.csv")
        if not os.path.exists(device_path): errors["missing_files"].append("device.csv")
        if not os.path.exists(ldap_path): errors["missing_files"].append("ldap.csv")

        if errors["missing_files"]:
            return {"valid": False, "errors": errors}

        # Validate columns
        # users
        u_res = self.validate_file_schema(users_path, ["user_id", "name", "department", "role"], {"employee_name": "name"})
        if not u_res["valid"]: errors["missing_columns"]["users.csv"] = u_res["missing_columns"]

        # logon
        lo_res = self.validate_file_schema(logon_path, ["user_id", "date", "activity", "pc"], {"user": "user_id"})
        if not lo_res["valid"]: errors["missing_columns"]["logon.csv"] = lo_res["missing_columns"]

        # device
        d_res = self.validate_file_schema(device_path, ["user_id", "date", "activity", "device"], {"user": "user_id", "pc": "device"})
        if not d_res["valid"]: errors["missing_columns"]["device.csv"] = d_res["missing_columns"]

        # LDAP
        ld_res = self.validate_file_schema(ldap_path, ["user_id", "manager", "team"], {"supervisor": "manager"})
        if not ld_res["valid"]: errors["missing_columns"]["ldap.csv"] = ld_res["missing_columns"]

        valid = len(errors["missing_columns"]) == 0
        return {
            "valid": valid,
            "errors": errors
        }

    def standardize_and_normalize_raw_files(self, name: str) -> Dict[str, Any]:
        """Convert any custom uploaded CSV files into the exact column layouts expected by legacy CERT scripts."""
        raw_dir = os.path.join(self.base_dir, name, "raw")
        users_path = os.path.join(raw_dir, "users.csv")
        logon_path = os.path.join(raw_dir, "logon.csv")
        device_path = os.path.join(raw_dir, "device.csv")
        ldap_path = os.path.join(raw_dir, "ldap.csv")

        # 1. users.csv
        u_df = pd.read_csv(users_path)
        u_df.columns = [c.strip() for c in u_df.columns]
        
        # If 'employee_name' is missing but 'name' is present, rename 'name' to 'employee_name'
        # so clean_users.py can safely rename it back to 'name' without creating duplicate columns.
        if "name" in u_df.columns and "employee_name" not in u_df.columns:
            u_df = u_df.rename(columns={"name": "employee_name"})

        # Add missing fields
        if "email" not in u_df.columns:
            u_df["email"] = u_df["user_id"].astype(str) + "@company.com"
        if "start_date" not in u_df.columns:
            u_df["start_date"] = "2010-01-01 00:00:00"
            
        # Map 'team' from ldap.csv if missing in users.csv
        if "team" not in u_df.columns and os.path.exists(ldap_path):
            try:
                ld_df_temp = pd.read_csv(ldap_path)
                ld_df_temp.columns = [c.strip() for c in ld_df_temp.columns]
                # Normalize user_id keys for mapping
                ld_df_temp['user_id'] = ld_df_temp['user_id'].astype(str).str.strip().str.upper()
                u_df_temp_id = u_df['user_id'].astype(str).str.strip().str.upper()
                
                team_map = ld_df_temp.set_index("user_id")["team"].to_dict()
                u_df["team"] = u_df_temp_id.map(team_map)
            except Exception as e:
                logger.warning(f"Failed to map team from ldap.csv: {e}")
                u_df["team"] = "Unknown"
        elif "team" not in u_df.columns:
            u_df["team"] = "Unknown"
        
        u_df.to_csv(users_path, index=False)
        total_users = int(u_df["user_id"].nunique())
        departments_count = int(u_df["department"].nunique()) if "department" in u_df.columns else 0

        # Calculate missing values
        nulls = int(u_df.isnull().sum().sum())

        # 2. logon.csv
        lo_df = pd.read_csv(logon_path)
        lo_df.columns = [c.strip() for c in lo_df.columns]
        
        if "user_id" in lo_df.columns and "user" not in lo_df.columns:
            lo_df = lo_df.rename(columns={"user_id": "user"})
        
        if "id" not in lo_df.columns:
            lo_df["id"] = [f"L_{i}" for i in range(len(lo_df))]

        lo_df.to_csv(logon_path, index=False)
        nulls += int(lo_df.isnull().sum().sum())
        total_records = len(lo_df)

        # Calculate date range
        min_date, max_date = "N/A", "N/A"
        if "date" in lo_df.columns:
            try:
                dates = pd.to_datetime(lo_df["date"], errors="coerce")
                min_date = dates.min().strftime("%Y-%m-%d")
                max_date = dates.max().strftime("%Y-%m-%d")
            except Exception:
                pass

        # 3. device.csv
        d_df = pd.read_csv(device_path)
        d_df.columns = [c.strip() for c in d_df.columns]
        
        if "user_id" in d_df.columns and "user" not in d_df.columns:
            d_df = d_df.rename(columns={"user_id": "user"})
        if "device" in d_df.columns and "pc" not in d_df.columns:
            d_df = d_df.rename(columns={"device": "pc"})
        
        if "id" not in d_df.columns:
            d_df["id"] = [f"D_{i}" for i in range(len(d_df))]
        if "file_tree" not in d_df.columns:
            d_df["file_tree"] = ""

        d_df.to_csv(device_path, index=False)
        nulls += int(d_df.isnull().sum().sum())
        total_records += len(d_df)

        # 4. ldap.csv
        ld_df = pd.read_csv(ldap_path)
        ld_df.columns = [c.strip() for c in ld_df.columns]
        
        if "manager" in ld_df.columns and "supervisor" not in ld_df.columns:
            ld_df = ld_df.rename(columns={"manager": "supervisor"})

        # Add missing departments/role from users if missing
        if "department" not in ld_df.columns and "department" in u_df.columns:
            dept_map = u_df.set_index("user_id")["department"].to_dict()
            ld_df["department"] = ld_df["user_id"].map(dept_map)
        if "role" not in ld_df.columns and "role" in u_df.columns:
            role_map = u_df.set_index("user_id")["role"].to_dict()
            ld_df["role"] = ld_df["role"] = ld_df["user_id"].map(role_map)

        # Add standard business units/functional units to prevent failures in clean_ldap.py
        if "business_unit" not in ld_df.columns:
            ld_df["business_unit"] = "1"
        if "functional_unit" not in ld_df.columns:
            ld_df["functional_unit"] = "1"

        ld_df.to_csv(ldap_path, index=False)
        nulls += int(ld_df.isnull().sum().sum())

        # Quality Score Calculation
        total_elements = (len(u_df) * len(u_df.columns) + 
                          len(lo_df) * len(lo_df.columns) + 
                          len(d_df) * len(d_df.columns) + 
                          len(ld_df) * len(ld_df.columns))
        quality_score = round(max(0.0, 100.0 - (nulls / max(1, total_elements) * 100.0)), 2)

        return {
            "total_users": total_users,
            "total_records": total_records,
            "departments": departments_count,
            "date_range": f"{min_date} to {max_date}",
            "missing_values_count": nulls,
            "data_quality_score": quality_score
        }

    def run_pipeline(self, name: str):
        """Sequential background runner for cleaning, features, model training, prediction, risk and profiles."""
        dataset_dir = os.path.join(self.base_dir, name)
        meta_path = os.path.join(dataset_dir, "metadata.json")

        try:
            # 1. Standardise Columns (0% -> 10%)
            logger.info(f"[{name}] Starting column standardisation...")
            processing_jobs[name]["progress"] = 5
            processing_jobs[name]["current_step"] = "Normalizing Files"
            stats = self.standardize_and_normalize_raw_files(name)
            
            # 2. Data Cleaning (10% -> 30%)
            logger.info(f"[{name}] Step 1: Cleaning raw datasets...")
            processing_jobs[name]["progress"] = 15
            processing_jobs[name]["current_step"] = "Data Preprocessing & Cleaning"

            from ml.preprocessing.clean_users import clean_users
            from ml.preprocessing.clean_logon import clean_logon
            from ml.preprocessing.clean_device import clean_device
            from ml.preprocessing.clean_ldap import clean_ldap

            clean_users(os.path.join(dataset_dir, "raw/users.csv"), os.path.join(dataset_dir, "cleaned/users_clean.csv"))
            processing_jobs[name]["progress"] = 20
            clean_logon(os.path.join(dataset_dir, "raw/logon.csv"), os.path.join(dataset_dir, "cleaned/logon_clean.csv"))
            processing_jobs[name]["progress"] = 25
            clean_device(os.path.join(dataset_dir, "raw/device.csv"), os.path.join(dataset_dir, "cleaned/device_clean.csv"))
            processing_jobs[name]["progress"] = 28
            clean_ldap(os.path.join(dataset_dir, "raw/ldap.csv"), os.path.join(dataset_dir, "cleaned/ldap_clean.csv"))

            # 3. Feature Engineering (30% -> 60%)
            logger.info(f"[{name}] Step 2: Extracting user behavior features...")
            processing_jobs[name]["progress"] = 35
            processing_jobs[name]["current_step"] = "Feature Extraction"

            from ml.feature_engineering.create_login_features import create_login_features
            from ml.feature_engineering.create_device_features import create_device_features
            from ml.feature_engineering.merge_features import merge_features

            create_login_features(
                os.path.join(dataset_dir, "cleaned/logon_clean.csv"),
                os.path.join(dataset_dir, "features/login_features.csv")
            )
            processing_jobs[name]["progress"] = 45
            create_device_features(
                os.path.join(dataset_dir, "cleaned/device_clean.csv"),
                os.path.join(dataset_dir, "features/device_features.csv")
            )
            processing_jobs[name]["progress"] = 50
            merge_features(
                output_path=os.path.join(dataset_dir, "features/user_features.csv"),
                users_clean_path=os.path.join(dataset_dir, "cleaned/users_clean.csv"),
                ldap_clean_path=os.path.join(dataset_dir, "cleaned/ldap_clean.csv"),
                login_features_path=os.path.join(dataset_dir, "features/login_features.csv"),
                device_features_path=os.path.join(dataset_dir, "features/device_features.csv"),
                raw_users_path=os.path.join(dataset_dir, "raw/users.csv")
            )

            # 4. Model Training (60% -> 75%)
            logger.info(f"[{name}] Fitting Isolation Forest model...")
            processing_jobs[name]["progress"] = 65
            processing_jobs[name]["current_step"] = "Model Training"

            from ml.training.train_model import train
            train(
                features_path=os.path.join(dataset_dir, "features/user_features.csv"),
                model_path=os.path.join(dataset_dir, "models/isolation_forest.pkl"),
                scaler_path=os.path.join(dataset_dir, "models/scaler.pkl")
            )

            # 5. Risk Scoring & Anomaly Detection (75% -> 90%)
            logger.info(f"[{name}] Step 3-4: Scoring risks and predicting anomalies...")
            processing_jobs[name]["progress"] = 78
            processing_jobs[name]["current_step"] = "Risk Scoring & Anomaly Detection"

            from ml.risk_scoring.risk_engine import run_risk_scoring
            from ml.prediction.predict import predict

            run_risk_scoring(
                os.path.join(dataset_dir, "features/user_features.csv"),
                os.path.join(dataset_dir, "reports/risk_scores.csv")
            )
            processing_jobs[name]["progress"] = 83
            predict(
                features_path=os.path.join(dataset_dir, "features/user_features.csv"),
                model_path=os.path.join(dataset_dir, "models/isolation_forest.pkl"),
                scaler_path=os.path.join(dataset_dir, "models/scaler.pkl"),
                output_path=os.path.join(dataset_dir, "reports/anomaly_report.csv")
            )

            # 6. Profile Generation (90% -> 98%)
            logger.info(f"[{name}] Step 5: Generating final security profiles...")
            processing_jobs[name]["progress"] = 92
            processing_jobs[name]["current_step"] = "Compiling Security Profiles"

            from ml.prediction.generate_security_profile import generate_profile
            generate_profile(
                features_path=os.path.join(dataset_dir, "features/user_features.csv"),
                risk_path=os.path.join(dataset_dir, "reports/risk_scores.csv"),
                anomaly_path=os.path.join(dataset_dir, "reports/anomaly_report.csv"),
                output_path=os.path.join(dataset_dir, "reports/final_security_profile.csv")
            )

            # 7. Finalize and Save Stats (98% -> 100%)
            logger.info(f"[{name}] Pipeline completed successfully!")
            processing_jobs[name]["progress"] = 100
            processing_jobs[name]["status"] = "Success"
            processing_jobs[name]["current_step"] = "Completed"

            # Update final metadata
            meta = {
                "name": name,
                "upload_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_users": stats["total_users"],
                "total_records": stats["total_records"],
                "status": "Success",
                "departments": stats["departments"],
                "date_range": stats["date_range"],
                "records_processed": stats["total_records"],
                "missing_values_count": stats["missing_values_count"],
                "data_quality_score": stats["data_quality_score"]
            }
            with open(meta_path, "w") as f:
                json.dump(meta, f, indent=4)

            # If this is the active dataset, refresh in-memory state of data service
            if self.data_service and self.data_service.current_dataset == name:
                logger.info(f"Refreshing active data_service state with newly compiled dataset: {name}")
                self.data_service.load_data()

        except Exception as e:
            logger.error(f"[{name}] Processing failed: {str(e)}", exc_info=True)
            processing_jobs[name]["status"] = "Failed"
            processing_jobs[name]["error"] = str(e)
            
            # Save failed metadata
            meta = {
                "name": name,
                "upload_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_users": 0,
                "total_records": 0,
                "status": "Failed",
                "departments": 0,
                "error": str(e)
            }
            with open(meta_path, "w") as f:
                json.dump(meta, f, indent=4)

    def delete_dataset(self, name: str):
        """Delete custom dataset directory and entries."""
        name = self.sanitize_dataset_name(name)
        if name.upper() == "CERT":
            raise HTTPException(status_code=400, detail="Cannot delete the default CERT dataset.")

        # If it is currently active, switch back to CERT first
        if self.data_service and self.data_service.current_dataset == name:
            self.data_service.switch_dataset("CERT")

        dataset_dir = os.path.join(self.base_dir, name)
        if os.path.exists(dataset_dir):
            shutil.rmtree(dataset_dir, ignore_errors=True)

        if name in processing_jobs:
            del processing_jobs[name]

        logger.info(f"Dataset {name} deleted successfully.")

    def trigger_reprocess(self, name: str) -> Dict[str, Any]:
        """Manually trigger reprocessing of an existing dataset."""
        name = self.sanitize_dataset_name(name)
        raw_dir = os.path.join(self.base_dir, name, "raw")
        if not os.path.exists(raw_dir):
            raise HTTPException(status_code=404, detail=f"Source raw files for dataset '{name}' not found.")

        # Re-initialize background job
        processing_jobs[name] = {
            "status": "Processing",
            "progress": 0,
            "current_step": "Data Normalization",
            "error": None
        }

        # Launch background reprocessing thread
        thread = threading.Thread(target=self.run_pipeline, args=(name,))
        thread.start()

        return {
            "success": True,
            "message": f"Reprocessing triggered for dataset '{name}'."
        }
