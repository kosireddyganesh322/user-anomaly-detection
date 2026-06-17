# Result Screenshot Guide — FastAPI Swagger Documentation Gateway

This document describes the screenshot that should be placed here to demonstrate the automatic Swagger interactive API playground.

---

## 1. Screenshot Placeholder

> **Screenshot Filename**: `presentation/screenshots/swagger.png`
> Insert the screenshot below:
> ![FastAPI Swagger documentation](../../presentation/screenshots/swagger.png)

---

## 2. Key Components Demonstrated in this Screenshot

1. **FastAPI OpenAPI Document Header**:
   * Displays the title "User Anomaly Detection — NFC", version, and system description.

2. **Grouped Router Endpoints (Tags)**:
   * **Users**: `/api/users/`, `/api/users/{user_id}`.
   * **Alerts**: `/api/alerts/`, `/api/alerts/{alert_id}`.
   * **Analytics**: `/api/analytics/risk-distribution`, `/api/analytics/login-trends`.
   * **Dashboard**: `/api/dashboard/overview`.
   * **Reports**: `/api/reports/export/{type}`, `/api/reports/pdf`.

3. **Interactive "Try it out" Execution UI**:
   * Shows request parameters, payload JSON schemas, curl command generation, response headers, and return statuses (200, 404, 500).

---

## 3. How to Capture this Screenshot

1. Ensure the FastAPI server is running.
2. Navigate your browser to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).
3. Expand one of the endpoints (e.g., `/api/dashboard/overview`), click **Try it out**, and then click **Execute** to show the sample JSON response.
4. Capture a clean screenshot of the browser showing the endpoint and JSON response. Save it as `swagger.png` inside the `presentation/screenshots/` folder.
