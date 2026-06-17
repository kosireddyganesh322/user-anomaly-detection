# NFC User Anomaly Detection System — Installation & Setup Guide

This document outlines the detailed system prerequisites, environment setup, database configuration, model training execution, and frontend deployment instructions for the User Anomaly Detection System (UADS) in the Nuclear Fuel Complex (NFC) environment.

---

## 1. System Prerequisites

Before initiating setup, ensure your development target environment meets the following specifications:

| Resource | Minimum Version | Notes |
| :--- | :--- | :--- |
| **Python** | 3.11.x | Python 3.12 is also supported. |
| **Node.js** | 20.x | Includes `npm` package manager (v10+). |
| **RAM** | 8 GB | 16 GB recommended for feature engineering processing. |
| **OS** | Windows 10/11 | Linux (RHEL/Ubuntu) or macOS are also compatible. |
| **Disk Space** | 5 GB | Required for raw datasets and generated reports. |

---

## 2. Environment Setup

### Step A: Clone the Repository
Download and enter the workspace directory:
```bash
git clone https://github.com/nfc-dae/user-anomaly-detection.git
cd user-anomaly-detection
```

### Step B: Setup Python Virtual Environment
We isolate dependencies using a virtual environment to prevent global package conflicts:
```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows Powershell:
.\.venv\Scripts\Activate.ps1
# Windows Command Prompt:
.\.venv\Scripts\activate.bat
# Linux / macOS Terminal:
source .venv/bin/activate
```

---

## 3. Backend Setup & Dependency Installation

1. Verify Python path resolves to your virtual environment:
   ```bash
   python -c "import sys; print(sys.executable)"
   ```
2. Install dependencies listed in `backend/requirements.txt`:
   ```bash
   pip install --upgrade pip
   pip install -r backend/requirements.txt
   ```
3. Create the backend configuration environment file:
   * Copy the example file:
     ```bash
     copy .env.example .env
     ```
   * Open `.env` and verify key configurations:
     ```env
     DATABASE_URL=sqlite:///./sql_app.db
     SECRET_KEY=NFC_SECRET_KEY_PLACEHOLDER_4A9B8D
     ACCESS_TOKEN_EXPIRE_MINUTES=30
     ENVIRONMENT=development
     ```

---

## 4. SQLite Database Initialization

Initialize the database schema for alert management and incident resolution metadata. From the root directory:
```bash
python database/init_db.py
```
*Expected Output:*
```text
2026-06-17 13:54:10 - INFO - Database initialization script started.
2026-06-17 13:54:10 - INFO - Executing schema blueprint setup...
2026-06-17 13:54:11 - INFO - SQLite database initialized successfully!
```

---

## 5. Machine Learning Pipeline Execution

Before launching the web services, you must process the raw datasets, execute the risk engine, train the Isolation Forest model, and compile the final security profile. Run the following modules sequentially from the root directory:

```bash
# -------------------------------------------------------------
# PHASE A: RAW DATA CLEANING
# -------------------------------------------------------------
# Clean employee registry
python ml/preprocessing/clean_users.py

# Clean Department and Role shifts
python ml/preprocessing/clean_ldap.py

# Clean login/logoff timestamps
python ml/preprocessing/clean_logon.py

# Clean USB insert/eject actions
python ml/preprocessing/clean_device.py

# -------------------------------------------------------------
# PHASE B: FEATURE ENGINEERING
# -------------------------------------------------------------
# Extract login counts, off-hours frequencies, active days
python ml/feature_engineering/create_login_features.py

# Extract device mounts, off-hours USB connects
python ml/feature_engineering/create_device_features.py

# Merge login and device features with LDAP profiles
python ml/feature_engineering/merge_features.py

# -------------------------------------------------------------
# PHASE C: MODEL TRAINING
# -------------------------------------------------------------
# Scale features and fit Isolation Forest algorithm
python ml/training/train_model.py

# -------------------------------------------------------------
# PHASE D: SCORING & SECURITY PROFILE COMPILATION
# -------------------------------------------------------------
# Calculate weighted numerical risk scores
python ml/risk_scoring/risk_engine.py

# Perform model outlier inference
python ml/prediction/predict.py

# Consolidate outlier outputs & risk scores into final security profile
python ml/prediction/generate_security_profile.py
```

*Verification:* Confirm that `ml/models/isolation_forest.pkl` and `data/reports/final_security_profile.csv` have been successfully generated.

---

## 6. Running the Project

### Start Services via Batch Script (Windows)
To start both the FastAPI backend and React frontend concurrently in separate terminal shells, execute the root batch script:
```cmd
start_project.bat
```

### Start Services Individually

#### A. Running the FastAPI Backend
Launch the API gateway via Uvicorn:
```bash
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```
* Uvicorn will monitor source files for automatic reloading.
* Swagger API Documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

#### B. Running the React Frontend
Navigate to the frontend folder, install packages, and launch Vite dev server:
```bash
cd frontend
npm install
npm run dev
```
* Vite Dev Server URL: [http://localhost:5173](http://localhost:5173)

---

## 7. Troubleshooting Guide

### Issue 1: `ModuleNotFoundError` during script run
* **Cause**: Your python executable is pointing to the global machine scope rather than your virtual environment, or the packages were not installed in the active shell context.
* **Solution**: Ensure your shell prompts with `(.venv)`. Re-run `pip install -r backend/requirements.txt`.

### Issue 2: `sqlite3.OperationalError: no such table`
* **Cause**: The SQLite database (`sql_app.db`) was not initialized, or the service ran from a working directory where the database file wasn't found.
* **Solution**: Re-run the initialization script: `python database/init_db.py`. Ensure that you execute this from the root directory.

### Issue 3: Frontend cannot load stats / "Security Data Offline"
* **Cause**: The React client cannot establish a network connection with FastAPI at port `8000`.
* **Solution**:
  1. Verify FastAPI is running by accessing [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.
  2. Verify that CORS middleware configs in `backend/app/main.py` allow requests from `http://localhost:5173` or `http://127.0.0.1:5173`.

### Issue 4: `isolation_forest.pkl` file missing
* **Cause**: Model training was skipped, or failed due to missing inputs in `data/features/user_features.csv`.
* **Solution**: Execute the ML Pipeline scripts sequentially as shown in Section 5. Ensure that your raw CERT datasets are present under `data/raw/`.

---

## 8. Clean up Commands

To clean compiled Python files and temporary development files:
```bash
# Windows:
del /s /q *.pyc
del /s /q __pycache__
# Linux / macOS:
find . -type f -name '*.pyc' -delete
find . -type d -name '__pycache__' -delete
```
