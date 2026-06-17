# Result Screenshot Guide — Employee Profile Explorer

This document describes the screenshot that should be placed here to demonstrate the profile explorer panel and risk auditor.

---

## 1. Screenshot Placeholder

> **Screenshot Filename**: `presentation/screenshots/users.png`
> Insert the screenshot below:
> ![Employee Profile Explorer](../../presentation/screenshots/users.png)

---

## 2. Key Components Demonstrated in this Screenshot

1. **Monitored Directory Grid**:
   * Layout showing all employee records, including employee ID (`user_id`), Department, Role, and dynamic **Risk Score** and **Security Status** fields.

2. **Unified Search & Security Filters**:
   * Text input bar to search profiles by ID or Name.
   * Quick filter dropdowns to isolate users by **Threat Classification** (`Critical Threat`, `High Threat`, `Medium Threat`, `Normal`).

3. **Interactive Security Audit Detail Modal**:
   * Triggered by clicking on a user row. Shows a deep dive audit of the user's features:
     * Numerical feature values (total logins, USB mounts, after-hours ratios).
     * Computed weighted risk breakdown.
     * Decision score output from the Isolation Forest model.
     * Recommendations for security action based on threat levels.

---

## 3. How to Capture this Screenshot

1. Open your browser and navigate to [http://localhost:5173/users](http://localhost:5173/users) (or click **User Explorer** in the navigation sidebar).
2. Type an anomalous user ID (e.g. search for a user flagged as `Critical Threat`) and click on their row to open the details modal.
3. Capture a screenshot displaying the modal overlay showing detailed features. Save it as `users.png` inside the `presentation/screenshots/` folder.
