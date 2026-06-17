import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
});

export const dashboardApi = {
  getOverview: () => api.get("/dashboard/overview"),
};

export const usersApi = {
  getAll: (params?: {
    page?: number;
    limit?: number;
    search?: string;
    department?: string;
    risk_level?: string;
    anomaly_label?: string;
    security_status?: string;
  }) => api.get("/users/", { params }),
  getById: (id: string) => api.get(`/users/${id}`),
};

export const anomaliesApi = {
  getAll: () => api.get("/anomalies"),
  getHighRisk: () => api.get("/anomalies/high-risk"),
};

export const alertsApi = {
  getAll: (params?: {
    severity?: string;
    acknowledged?: boolean;
    search?: string;
  }) => api.get("/alerts/", { params }),
  acknowledge: (id: number) => api.put(`/alerts/${id}/acknowledge`),
};

export const analyticsApi = {
  loginTrends: () => api.get("/analytics/login-trends"),
  deviceTrends: () => api.get("/analytics/device-trends"),
  riskDistribution: () => api.get("/analytics/risk-distribution"),
  departmentSummary: () => api.get("/analytics/department-summary"),
};

export const predictionsApi = {
  run: () => api.post("/predictions/run"),
  getResults: () => api.get("/predictions/results"),
};

export const reportsApi = {
  getCsvUrl: (type: "profile" | "anomalies" | "risk") => `/api/reports/export/csv?type=${type}`,
  getPdfUrl: () => `/api/reports/export/pdf`,
};

export default api;
