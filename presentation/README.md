# NFC User Anomaly Detection System — Presentation & Demonstration Guide

This guide is designed for security officers, system administrators, and evaluation committees. It structures the system demonstration flow, slide deck creation (PPT), and screenshot cataloging.

---

## 1. System Demonstration Flow (Screencast Outline)

To conduct a live system evaluation or compile a demo video, follow this sequential flow:

```
[ STEP 1: REST API Gateway Check ]
  └─ Navigate to http://127.0.0.1:8000/docs
  └─ Execute the /api/dashboard/overview endpoint to show raw model JSON metrics.

[ STEP 2: Dashboard System Health Auditing ]
  └─ Open client interface at http://localhost:5173/
  └─ Point out the telemetry health indicator badges.
  └─ Audit the high-level cards showing anomalous, high, and critical risk user counts.

[ STEP 3: Statistical Analytics Review ]
  └─ Click on "Analytics" in the sidebar.
  └─ Highlight the Risk Pie Chart, showing percentage breakdowns.
  └─ Show the logon & device time series charts, explaining historical spikes.

[ STEP 4: Incident Response Alerts Management ]
  └─ Go to "Alerts".
  └─ Filter by "Critical" severity alerts.
  └─ Update an alert status from "Pending" to "Investigating", demonstrating DB persistence.

[ STEP 5: Employee Profile Deep Dive Explorer ]
  └─ Select "User Explorer".
  └─ Search for a user marked as "Critical Threat".
  └─ Click on their profile row to display their multi-dimensional feature audit modal.

[ STEP 6: Certified Report Exports ]
  └─ Go back to the Dashboard page.
  └─ Trigger "Export PDF Report" to download the executive audit brief.
  └─ Download final profile logs CSV.
```

---

## 2. Screenshot Checklist (for PowerPoint & Reports)

Capture and place the following images in the `presentation/screenshots/` directory:

- [ ] **`dashboard.png`**: The main Security Command Center overview dashboard.
- [ ] **`analytics.png`**: The Recharts-powered graphs page with an active hover tooltip.
- [ ] **`alerts.png`**: The Incident Alerts table showing filtered list states.
- [ ] **`users.png`**: The User Explorer table with an open detail modal auditing a Critical Threat user.
- [ ] **`swagger.png`**: The interactive FastAPI Swagger schema with an executed API response payload.

---

## 3. Slide Deck Structure (PowerPoint Outline)

Use this outline to build your presentation (`presentation/ppt/user_anomaly_detection.pptx`):

* **Slide 1: Title & Organization**
  * Project Title: *User Anomaly Detection System (UADS)*.
  * Organization: *Nuclear Fuel Complex (NFC)*, *Department of Atomic Energy (DAE)*.
* **Slide 2: Problem Statement & Context**
  * Protecting high-security nuclear fuel fabrication environments from insider threat models.
  * Limitations of rule-based firewalls; need for behavioral anomalies identification.
* **Slide 3: System Architecture & Data Flow**
  * Raw data logs $\rightarrow$ Preprocessing $\rightarrow$ Feature Engineering $\rightarrow$ Scoring Engine $\rightarrow$ Model Inference $\rightarrow$ API Gateway $\rightarrow$ UI Command Center.
* **Slide 4: Machine Learning Core (Isolation Forest)**
  * Preprocessing with `StandardScaler`.
  * Multi-tree isolation principles ($n\_estimators=100$, $contamination=0.05$).
* **Slide 5: Rules-Based Risk Engine**
  * Weighted threat calculation logic ($S_{risk}$) using out-of-hours logons, USB connects, workstation counts, and login-to-device ratios.
* **Slide 6: Threat Classification Matrix**
  * Mapping risk levels and machine learning outlier labels to consolidated security levels (`Critical Threat`, `High Threat`, `Medium Threat`, `Normal`).
* **Slide 7: UI Command Center (Dashboard & Analytics)**
  * Introduce the dark-theme glassmorphism UI, interactive Recharts timelines, and PDF reporting features.
* **Slide 8: Future Scope & Roadmap**
  * real-time event streaming via Kafka, email NLP parsing, active directory synchronization, and endpoint agent lockouts.

---

## 9. Evaluation Checklist (System Readiness Audit)

Before showing the system, verify the following checklist items are complete:

- [ ] FastAPI backend is running on port `8000` with CORS configured.
- [ ] React frontend is running on port `5173` without errors.
- [ ] SQLite database is initialized and contains default resolved alerts.
- [ ] `final_security_profile.csv` contains active rows (verify file size > 100 KB).
- [ ] `isolation_forest.pkl` and `scaler.pkl` are present in `ml/models/`.
- [ ] Report generation endpoints (PDF/CSV) work successfully (test PDF export from frontend).
