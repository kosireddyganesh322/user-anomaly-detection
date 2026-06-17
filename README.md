# User Anomaly Detection System (UADS) — Nuclear Fuel Complex (NFC)

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=flat&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![License: Protected](https://img.shields.io/badge/License-NFC%20Internal-red.svg)](https://www.nfc.gov.in)

> **Enterprise User Behavior Analytics (UBA) and Insider Threat Mitigation Gateway** developed for the **Nuclear Fuel Complex (NFC)**, a constituent unit of the **Department of Atomic Energy (DAE)**, Government of India.

---

## 1. Project Overview
The **User Anomaly Detection System (UADS)** is an advanced security intelligence platform designed to protect high-security nuclear fuel fabrication facilities and operational data registries. By continuously analyzing system access logs, directory services, and removable peripheral events, UADS proactively identifies insider threats, compromised accounts, and high-risk operational behaviors.

---

## 2. Problem Statement
High-security environments like the **Nuclear Fuel Complex (NFC)** face sophisticated security threats from within. Traditional rule-based endpoint detection mechanisms fail to intercept slow, low-intensity unauthorized actions, unauthorized physical workstation changes, or out-of-hours data copying because each action in isolation might appear legitimate. 

Security operators require an automated system to:
1. Aggregate multi-source activities (logons, USB mounts, LDAP details) at the user level.
2. Formulate dynamic behavioral baselines for each employee.
3. Automatically identify anomalous deviations using unsupervised Machine Learning.
4. Elevate threat alerts based on department-aware risk contexts before data exfiltration occurs.

---

## 3. Objectives
* **Behavioral Baselines**: Establish normalized access baselines using multi-source telemetry logs.
* **Unsupervised Anomaly Detection**: Detect outliers using Isolation Forest algorithms without requiring predefined threat signatures.
* **Risk Scoring & Categorization**: Compute user-specific threat risk values (0 to 100) using a weighted behavioral rules engine.
* **Role/Department Profiling**: Factor department structures into user risk contexts to prevent operational false positives.
* **Interactive Dashboard**: Provide security officers with a glassmorphism-themed command center for real-time risk investigation and certified report exports.

---

## 4. Key Features
* **Multi-Source Data Ingestion**: Processes login/logoff patterns, active directories (LDAP), and device mounts (USB events).
* **Isolation Forest Engine**: Fits multi-dimensional isolation trees to classify users into `Normal` or `Suspicious` categories.
* **Weighted Threat Scoring**: Appends risk scores based on weekend logons, out-of-hours system access, multiple workstation logons, and logins-to-USB ratios.
* **Real-time API Alerts**: Serves RESTful endpoints using FastAPI with request validation via Pydantic schemas.
* **Operational Command Center**: Features React + TypeScript tables, Interactive Recharts visual timelines, and user explorer profiles.
* **Certified Report Exporter**: Compiles Executive PDF Briefs and CSV records directly from the UI.

---

## 5. Dataset Information
This project utilizes the **CERT Insider Threat Dataset** (synthetic logs mimicking real organization networks):
* **`users.csv`**: Organization directory mapping employee IDs to names, email addresses, and roles.
* **`LDAP.csv`**: Temporal directory containing department and role hierarchy shifts for all users.
* **`logon.csv`**: Security logon/logoff activities containing timestamps, user IDs, workstations, and logon/logoff status.
* **`device.csv`**: USB drive insertion and removal activities recorded on workstation endpoints.

---

## 6. Tech Stack
* **Backend**: FastAPI (Python 3.11+), Uvicorn ASGI Server, SQLite DB (SQLAlchemy-ready).
* **Frontend**: React 18, TypeScript, Tailwind CSS, Recharts (visualizations), Lucide React (icons).
* **Machine Learning**: Pandas, NumPy, Scikit-learn (StandardScaler, Isolation Forest), Joblib/Pickle (serialization).

---

## 7. System Architecture
```
                                 [ RAW CERT DATASETS ]
                        (users.csv, LDAP.csv, logon.csv, device.csv)
                                           │
                                           ▼
                                 [ CLEANING PIPELINE ]
                        (ml/preprocessing/clean_*.py scripts)
                                           │
                                           ▼
                              [ FEATURE ENGINEERING & MERGE ]
                        (ml/feature_engineering/*_features.py)
                                           │
                        ┌──────────────────┴──────────────────┐
                        ▼                                     ▼
                [ RISK ENGINE ]                      [ ISOLATION FOREST ]
             (Weighted Rules Logic)                (Unsupervised Outliers)
                        │                                     │
                        └──────────────────┬──────────────────┘
                                           ▼
                            [ SECURITY PROFILE GENERATION ]
                           (data/reports/final_security_profile.csv)
                                           │
                                           ▼
                            [ FASTAPI SECURITY GATEWAY ]
                             (backend/app/api/routes/*)
                                           │
                                           ▼
                              [ REACT COMMAND CENTER ]
                             (Dashboard, User Explorer, Alerts)
```

---

## 8. Folder Structure
```text
user-anomaly-detection/
├── .env.example              # Template for environment variables
├── .gitignore                # Git ignore configuration
├── start_project.bat         # Batch script to launch both frontend and backend
├── README.md                 # Root documentation
│
├── backend/                  # FastAPI Backend API
│   ├── app/
│   │   ├── api/routes/       # API endpoints (users, alerts, analytics, reports)
│   │   ├── schemas/          # Pydantic validation models
│   │   ├── services/         # Business logic & Database connectors
│   │   ├── utils/            # Shared loggers and helper scripts
│   │   ├── config.py         # Backend configuration settings
│   │   └── main.py           # FastAPI entrypoint
│   └── requirements.txt      # Backend Python dependencies
│
├── frontend/                 # React + Vite Frontend UI
│   ├── src/
│   │   ├── components/       # Layout, charts, and reusable UI components
│   │   ├── pages/            # View pages (Dashboard, UserExplorer, Alerts, Analytics)
│   │   ├── services/         # Axios API connection endpoints
│   │   ├── App.tsx           # React main router config
│   │   └── main.tsx          # Frontend entrypoint
│   └── package.json          # Node scripts and UI dependencies
│
├── database/                 # SQLite database schema and init script
│   ├── init_db.py            # Database initializer
│   └── schema.sql            # Schema blueprints
│
├── ml/                       # Machine Learning and Scoring Modules
│   ├── preprocessing/        # Raw data cleaning scripts
│   ├── feature_engineering/  # Temporal and ratio feature aggregations
│   ├── training/             # Model fitting code (Isolation Forest)
│   ├── prediction/           # Anomaly scoring and Security Profile compiler
│   ├── risk_scoring/         # Weighted scoring engine & rules
│   └── models/               # Serialized model (.pkl) artifacts
│
├── data/                     # Internal data registry (Git ignored except structure)
│   ├── raw/                  # Source CSV files
│   ├── cleaned/              # Cleaned temporary data
│   ├── features/             # Generated feature tables
│   └── reports/              # Final scoring outputs
│
├── docs/                     # Documentation Assets
│   ├── SETUP.md              # Installation & troubleshooting guide
│   ├── architecture.md       # Data pipelines and architectural flow
│   ├── project_health_report.md # Quality and deployment readiness audit
│   └── results/              # Template guidelines for screenshot evidence
│
├── presentation/             # Presentation Assets
│   ├── README.md             # Demo structure & checklists
│   ├── screenshots/          # Captured UI illustrations
│   ├── demo_video/           # System screencasts
│   └── ppt/                  # Slide decks
│
└── tests/                    # Project Unit & Integration Tests
```

---

## 9. Installation Steps

### Prerequisites
* **Python**: `3.11.x` or higher
* **Node.js**: `20.x` or higher (with `npm` package manager)
* **OS**: Windows / Linux / macOS

### Initial Setup
1. Clone the repository and navigate into the folder:
   ```bash
   git clone https://github.com/nfc-dae/user-anomaly-detection.git
   cd user-anomaly-detection
   ```
2. Set up virtual environment and install packages:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate      # On Linux/macOS: source .venv/bin/activate
   pip install -r backend/requirements.txt
   ```
3. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

---

## 10. Running the Backend
1. Ensure the virtual environment is active.
2. Initialize the local database:
   ```bash
   python database/init_db.py
   ```
3. Run the backend development server using Uvicorn:
   ```bash
   python -m uvicorn backend.app.main:app --reload
   ```
   * The API Swagger UI will be available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 11. Running the Frontend
1. Open a new terminal instance and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Launch the Vite dev server:
   ```bash
   npm run dev
   ```
   * The frontend client will run at [http://localhost:5173](http://localhost:5173)

*Note: Alternatively, run `start_project.bat` from the root directory to launch both servers simultaneously in separate processes.*

---

## 12. ML Workflow
To train the Isolation Forest model and generate the final user profile from scratch, run the scripts in order:

```bash
# 1. Clean raw inputs
python ml/preprocessing/clean_users.py
python ml/preprocessing/clean_ldap.py
python ml/preprocessing/clean_logon.py
python ml/preprocessing/clean_device.py

# 2. Extract user features
python ml/feature_engineering/create_login_features.py
python ml/feature_engineering/create_device_features.py
python ml/feature_engineering/merge_features.py

# 3. Train model
python ml/training/train_model.py

# 4. Predict and score
python ml/risk_scoring/risk_engine.py
python ml/prediction/predict.py
python ml/prediction/generate_security_profile.py
```

---

## 13. Screenshots Section
Screenshots illustrating the system are categorized in the `presentation/screenshots/` directory. For descriptions of what each screenshot contains and instructions on how to take them, refer to:
* [Dashboard Screen Overview](docs/results/dashboard.md)
* [Threat Analytics Screen](docs/results/analytics.md)
* [System Security Alerts](docs/results/alerts.md)
* [Employee Profile Explorer](docs/results/users.md)
* [FastAPI Swagger Endpoint Interface](docs/results/swagger.md)

---

## 14. Future Scope
* **Real-time Stream Clustering**: Migrate from batch Isolation Forest to streaming isolation trees (e.g., Extended Isolation Forest or Half-Space Trees) via Kafka.
* **Email Sentiment Analysis**: Ingest employee email texts using local small language models (SLMs) to detect psychological threat indicators (disgruntlement, espionage language).
* **Active Directory Syncing**: Build real-time connectors directly into Active Directory (AD) servers for live employee directory updates.
* **Hardware USB Blocking**: Integrate agent-level endpoints to block unauthorized USB storage mounts when risk level escalates to `Critical`.

---

## 15. Contributors
* **Technical Engineering Team**, Nuclear Fuel Complex (NFC), Department of Atomic Energy (DAE).
