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
  getDepartments: () => api.get<string[]>("/users/departments"),
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
  acknowledgeAll: () => api.put("/alerts/acknowledge-all"),
};

export const analyticsApi = {
  loginTrends: () => api.get("/analytics/login-trends"),
  deviceTrends: () => api.get("/analytics/device-trends"),
  riskDistribution: () => api.get("/analytics/risk-distribution"),
  departmentSummary: () => api.get("/analytics/department-summary"),
  topRiskUsers: () => api.get("/analytics/top-risk-users"),
  departmentRiskRanking: () => api.get("/analytics/department-risk-ranking"),
  anomalyReasonBreakdown: () => api.get("/analytics/anomaly-reason-breakdown"),
  threatHeatmap: () => api.get("/analytics/threat-heatmap"),
  securityPosture: () => api.get("/analytics/security-posture"),
  riskMatrix: () => api.get("/analytics/risk-matrix"),
  behavioralIndicators: () => api.get("/analytics/behavioral-indicators"),
  watchlist: () => api.get("/analytics/watchlist"),
};

export const predictionsApi = {
  run: () => api.post("/predictions/run"),
  getResults: () => api.get("/predictions/results"),
};

export const datasetsApi = {
  list: () => api.get("/datasets"),
  upload: (formData: FormData) => api.post("/datasets/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" }
  }),
  validate: (formData: FormData) => api.post("/datasets/validate", formData, {
    headers: { "Content-Type": "multipart/form-data" }
  }),
  switch: (name: string) => api.post("/datasets/switch", { name }),
  getActive: () => api.get("/datasets/active"),
  getStatus: (name: string) => api.get(`/datasets/${name}/status`),
  reprocess: (name: string) => api.post(`/datasets/${name}/reprocess`),
  delete: (name: string) => api.delete(`/datasets/${name}`),
};

export const reportsApi = {
  getCsvUrl: (type: "profile" | "anomalies" | "risk") => `/api/reports/export/csv?type=${type}`,
  getPdfUrl: () => `/api/reports/export/pdf`,
};

export default api;
