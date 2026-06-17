import { useEffect, useState, useCallback } from "react";
import { alertsApi, anomaliesApi } from "../services/api";

export function useAlerts() {
  const [alerts, setAlerts] = useState<any[]>([]);
  const [anomalies, setAnomalies] = useState<any[]>([]);
  const [highRiskAnomalies, setHighRiskAnomalies] = useState<any[]>([]);
  
  // Filters state
  const [severity, setSeverity] = useState<string>("");
  const [acknowledgedFilter, setAcknowledgedFilter] = useState<string>("active"); // "all" | "active" | "acknowledged"
  const [search, setSearch] = useState<string>("");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAlertData = useCallback(() => {
    setLoading(true);
    setError(null);
    
    // Map filter state to API parameter
    let ackParam: boolean | undefined = undefined;
    if (acknowledgedFilter === "active") ackParam = false;
    else if (acknowledgedFilter === "acknowledged") ackParam = true;

    Promise.all([
      alertsApi.getAll({
        severity: severity || undefined,
        acknowledged: ackParam,
        search: search || undefined
      }),
      anomaliesApi.getAll(),
      anomaliesApi.getHighRisk()
    ])
      .then(([alertsRes, anomaliesRes, highRiskRes]) => {
        // Both alerts and anomalies endpoints return JSON arrays directly
        setAlerts(alertsRes.data || []);
        setAnomalies(anomaliesRes.data || []);
        setHighRiskAnomalies(highRiskRes.data || []);
      })
      .catch((err) => {
        console.error("Error fetching alerts:", err);
        setError("Failed to load alerts & anomalies data");
      })
      .finally(() => {
        setLoading(false);
      });
  }, [severity, acknowledgedFilter, search]);

  const acknowledgeAlert = useCallback((alertId: number) => {
    return alertsApi.acknowledge(alertId)
      .then(() => {
        setAlerts(prev => prev.map(a => a.id === alertId ? { ...a, acknowledged: true } : a));
      })
      .catch((err) => {
        console.error("Failed to acknowledge alert:", err);
        throw err;
      });
  }, []);

  useEffect(() => {
    fetchAlertData();
  }, [fetchAlertData]);

  return {
    alerts,
    anomalies,
    highRiskAnomalies,
    severity,
    acknowledgedFilter,
    search,
    loading,
    error,
    setSeverity,
    setAcknowledgedFilter,
    setSearch,
    acknowledgeAlert,
    refresh: fetchAlertData
  };
}
