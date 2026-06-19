import { useEffect, useState, useCallback } from "react";
import { usersApi } from "../services/api";

export function useUsers() {
  const [users, setUsers] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(10);
  const [search, setSearch] = useState("");
  const [department, setDepartment] = useState("");
  const [riskLevel, setRiskLevel] = useState("");
  const [anomalyLabel, setAnomalyLabel] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchUsers = useCallback(() => {
    setLoading(true);
    setError(null);
    usersApi
      .getAll({
        page,
        limit,
        search: search || undefined,
        department: department || undefined,
        risk_level: riskLevel || undefined,
        anomaly_label: anomalyLabel || undefined,
      })
      .then((res) => {
        setUsers(res.data.users || []);
        setTotal(res.data.total || 0);
      })
      .catch((err) => {
        console.error("Error fetching users:", err);
        setError("Failed to fetch users");
      })
      .finally(() => {
        setLoading(false);
      });
  }, [page, limit, search, department, riskLevel, anomalyLabel]);

  useEffect(() => {
    // Reset page to 1 when filters or search change
    setPage(1);
  }, [search, department, riskLevel, anomalyLabel]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  useEffect(() => {
    const handleRefresh = () => fetchUsers();
    window.addEventListener("refresh-data", handleRefresh);
    return () => window.removeEventListener("refresh-data", handleRefresh);
  }, [fetchUsers]);

  return {
    users,
    total,
    page,
    limit,
    search,
    department,
    riskLevel,
    anomalyLabel,
    loading,
    error,
    setPage,
    setLimit,
    setSearch,
    setDepartment,
    setRiskLevel,
    setAnomalyLabel,
    refresh: fetchUsers,
  };
}
