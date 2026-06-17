# System Documentation & QA Telemetry Report

## 1. Metadata & Execution Details

* **Timestamp**: `2026-06-17T23:16:30+05:30` (IST)
* **Organization**: Nuclear Fuel Complex (NFC), Department of Atomic Energy (DAE)
* **QA Auditor**: Cyber Telemetry Verification Agent
* **Target Environment**:
  * **Frontend Client**: `http://localhost:5173`
  * **Backend Swagger Gateway**: `http://127.0.0.1:8000/docs`

---

## 2. Screenshot Capture Inventory

A total of $12$ full-screen high-resolution PNG screenshots have been captured, verified for layout correctness, and saved to the `presentation/screenshots/` directory:

| Index | Screenshot Filename | Target Element / View | Verification Status |
| :--- | :--- | :--- | :--- |
| 1 | **`dashboard.png`** | Dashboard Home (Command Center Overview) | `✓ Verified - OK` |
| 2 | **`dashboard_metrics.png`** | Active Alerts Status and Report Export Panel | `✓ Verified - OK` |
| 3 | **`user_explorer.png`** | Employee Registry Table list | `✓ Verified - OK` |
| 4 | **`user_profile.png`** | Individual Security Audit Profile details modal | `✓ Verified - OK` |
| 5 | **`alerts.png`** | Alerts Incident Center list and filters | `✓ Verified - OK` |
| 6 | **`analytics.png`** | Analytics Home page displaying top-half graphs | `✓ Verified - OK` |
| 7 | **`risk_distribution.png`** | User Risk Class Distribution pie chart with active hover tooltip | `✓ Verified - OK` |
| 8 | **`login_trends.png`** | Daily Logon Events Timeline line chart with active hover tooltip | `✓ Verified - OK` |
| 9 | **`device_trends.png`** | Daily USB Device Connect Timeline area chart with hover tooltip | `✓ Verified - OK` |
| 10 | **`csv_export.png`** | CSV Export button section highlights | `✓ Verified - OK` |
| 11 | **`pdf_export.png`** | PDF Export button compile feedback state | `✓ Verified - OK` |
| 12 | **`swagger_docs.png`** | FastAPI Swagger documentation endpoints overview | `✓ Verified - OK` |

---

## 3. Demo Walkthrough Video

* **Video Filename**: `presentation/demo_video/project_demo.mp4`
* **Format**: `H.264 Video (MP4), 1920x924 resolution`
* **Frame Rate**: `5 fps` (optimized to show transitions clearly)
* **Walkthrough Flow Demonstrated**:
  1. Open application dashboard, loading system telemetry indicators.
  2. Inspect primary statistics cards (monitored users, anomaly rate, critical flags).
  3. Navigate to User Explorer and filter by risk levels.
  4. Expand user row to display details modal with features scoring indicators.
  5. Go to Alerts and toggle severities filter options.
  6. Open Analytics and trigger hover tooltips on Recharts risk pie and timeline curves.
  7. Return to Dashboard and trigger 'Export Profile CSV' download.
  8. Click 'Export PDF Report' to compile the executive audit brief.
  9. Redirect to FastAPI Swagger UI docs interface `/docs`.

---

## 4. QA Validation & Health Audit

* **Failures Encountered**:
  * *Vite Proxy / host connection issues*: None. The proxy target has been updated to `127.0.0.1:8000` to prevent localhost lookup errors on IPv6-configured machines.
  * *FFmpeg compile limitation*: Local system `ffmpeg` was compiled without a WebP animation decoder (skipping ANIM/ANMF chunks).
    * *Workaround*: Built a Python Pillow frame extractor script to convert the subagent walkthrough WebP recording into individual PNG frames, then compiled the image series into an MP4 container using ffmpeg image sequence decoder. Works perfectly.
* **Missing Pages**: None. All core requirements (Dashboard, User Explorer, Alerts, Analytics, Swagger) are fully verified and present.
* **Missing Assets**: None. All requested files exist and have non-zero file sizes.
