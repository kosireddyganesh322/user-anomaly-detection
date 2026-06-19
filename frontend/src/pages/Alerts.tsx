import { useState, useEffect } from "react";
import { useAlerts } from "../hooks/useAlerts";
import { BellRing, ShieldAlert, CheckCircle, AlertOctagon, User, Clock, Terminal, Search, X } from "lucide-react";

export default function Alerts() {
  const {
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
    acknowledgeAllAlerts,
    refresh,
  } = useAlerts();

  useEffect(() => {
    const handleRefresh = () => refresh();
    window.addEventListener("refresh-data", handleRefresh);
    return () => window.removeEventListener("refresh-data", handleRefresh);
  }, [refresh]);


  const [activeTab, setActiveTab] = useState<"alerts" | "suspicious" | "high-risk">("alerts");
  const [ackProgressId, setAckProgressId] = useState<number | null>(null);

  // Debounced search term
  const [searchInput, setSearchInput] = useState(search);

  useEffect(() => {
    const handler = setTimeout(() => {
      setSearch(searchInput);
    }, 400);
    return () => clearTimeout(handler);
  }, [searchInput, setSearch]);

  // Sync search input when search state is cleared/updated externally
  useEffect(() => {
    setSearchInput(search);
  }, [search]);

  const handleAcknowledge = (id: number) => {
    setAckProgressId(id);
    acknowledgeAlert(id)
      .catch((err) => {
        alert("Failed to acknowledge alert. Please try again.");
      })
      .finally(() => {
        setAckProgressId(null);
      });
  };

  const handleAcknowledgeAll = () => {
    if (!window.confirm("Are you sure you want to acknowledge all active alerts?")) return;
    setAckProgressId(-1); // -1 represents bulk acknowledgment progress
    acknowledgeAllAlerts()
      .then(() => {
        // Refresh unread count globally
        window.dispatchEvent(new Event("refresh-data"));
      })
      .catch((err) => {
        alert("Failed to acknowledge all alerts. Please try again.");
      })
      .finally(() => {
        setAckProgressId(null);
      });
  };

  const getSeverityColor = (severity?: string) => {
    switch (severity) {
      case "Critical":
        return "text-danger border-danger/25 bg-danger/10";
      case "High":
        return "text-warning border-warning/25 bg-warning/10";
      case "Warning":
        return "text-amber-500 border-amber-500/25 bg-amber-500/10";
      case "Info":
        return "text-slate-400 border-slate-700/20 bg-slate-800/10";
      default:
        return "text-slate-400 border-slate-700/20 bg-slate-800/10";
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] gap-3">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-500"></div>
        <p className="text-gray-400 text-xs">Loading active warning logs...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-gray-900 border border-danger/20 p-6 rounded-xl text-center max-w-md mx-auto min-h-[200px] flex flex-col justify-center items-center">
        <AlertOctagon className="text-danger mb-3" size={36} />
        <h3 className="text-white font-medium mb-1">Alert Data Offline</h3>
        <p className="text-gray-400 text-xs">{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Security Incident Center</h1>
        <p className="text-gray-400 text-sm">Review real-time threat notifications, anomaly classifications, and alert states.</p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-800">
        <button
          onClick={() => setActiveTab("alerts")}
          className={`px-4 py-2.5 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${
            activeTab === "alerts"
              ? "border-brand-500 text-brand-400"
              : "border-transparent text-gray-400 hover:text-gray-200"
          }`}
        >
          <BellRing size={16} />
          Active Incident Notifications
          <span className="ml-1 px-2 py-0.5 rounded-full text-xs bg-gray-800 text-white font-semibold">
            {alerts.filter(a => !a.acknowledged).length}
          </span>
        </button>

        <button
          onClick={() => setActiveTab("suspicious")}
          className={`px-4 py-2.5 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${
            activeTab === "suspicious"
              ? "border-brand-500 text-brand-400"
              : "border-transparent text-gray-400 hover:text-gray-200"
          }`}
        >
          <User size={16} />
          Suspicious Anomalies Queue
          <span className="ml-1 px-2 py-0.5 rounded-full text-xs bg-gray-850 text-gray-400 font-semibold">
            {anomalies.length}
          </span>
        </button>

        <button
          onClick={() => setActiveTab("high-risk")}
          className={`px-4 py-2.5 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${
            activeTab === "high-risk"
              ? "border-brand-500 text-brand-400"
              : "border-transparent text-gray-400 hover:text-gray-200"
          }`}
        >
          <ShieldAlert size={16} />
          High-RiskThreat Queue
          <span className="ml-1 px-2 py-0.5 rounded-full text-xs bg-gray-850 text-gray-400 font-semibold">
            {highRiskAnomalies.length}
          </span>
        </button>
      </div>

      {/* Tab Panels */}
      <div className="space-y-4">
        {activeTab === "alerts" && (
          <div className="space-y-4">
            {/* Filter Toolbar */}
            <div className="bg-gray-900 border border-gray-800 p-4 rounded-xl flex flex-col md:flex-row gap-4 items-center">
              {/* Search */}
              <div className="relative w-full md:w-80">
                <Search className="absolute left-3 top-2.5 text-gray-500" size={17} />
                <input
                  type="text"
                  placeholder="Search alerts by ID, name, or type..."
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value)}
                  className="w-full bg-gray-950 border border-gray-800 rounded-lg pl-10 pr-4 py-2 text-sm text-white focus:outline-none focus:border-brand-500 transition-colors"
                />
                {searchInput && (
                  <button
                    onClick={() => setSearchInput("")}
                    className="absolute right-3 top-3 text-gray-500 hover:text-white"
                  >
                    <X size={14} />
                  </button>
                )}
              </div>

              {/* Filters */}
              <div className="grid grid-cols-2 md:flex md:flex-row gap-4 w-full md:w-auto md:ml-auto">
                {/* Severity Filter */}
                <select
                  value={severity}
                  onChange={(e) => setSeverity(e.target.value)}
                  className="bg-gray-950 border border-gray-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-brand-500"
                >
                  <option value="">All Severities</option>
                  <option value="Critical">Critical</option>
                  <option value="High">High</option>
                  <option value="Warning">Warning</option>
                  <option value="Info">Info</option>
                </select>

                {/* Acknowledgment Filter */}
                <select
                  value={acknowledgedFilter}
                  onChange={(e) => setAcknowledgedFilter(e.target.value)}
                  className="bg-gray-950 border border-gray-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-brand-500"
                >
                  <option value="active">Active Alerts</option>
                  <option value="acknowledged">Acknowledged Alerts</option>
                  <option value="all">All Alerts</option>
                </select>

                {alerts.some((a) => !a.acknowledged) && (
                  <button
                    onClick={handleAcknowledgeAll}
                    disabled={ackProgressId !== null}
                    className="bg-brand-500 hover:bg-brand-600 text-white rounded-lg px-4 py-2 text-sm font-semibold transition-colors disabled:opacity-50 flex items-center justify-center whitespace-nowrap"
                  >
                    {ackProgressId === -1 ? "Acknowledging..." : "Acknowledge All"}
                  </button>
                )}
              </div>
            </div>

            {alerts.length === 0 ? (
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-8 text-center text-gray-400">
                <CheckCircle className="text-safe mx-auto mb-3" size={32} />
                <p className="font-semibold text-white mb-1">No Active Incidents</p>
                <p className="text-xs">All detected alerts have been investigated or cleared.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-4">
                {alerts.map((alert) => (
                  <div
                    key={alert.id}
                    className={`p-5 bg-gray-900 border rounded-xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4 transition-all duration-200 ${
                      alert.acknowledged
                        ? "border-gray-800/50 opacity-60 bg-gray-950/20"
                        : "border-gray-800 hover:border-gray-700"
                    }`}
                  >
                    <div className="space-y-2 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="text-xs font-mono font-bold text-brand-400 uppercase tracking-wide bg-brand-500/10 px-2 py-0.5 rounded">
                          {alert.user_id}
                        </span>
                        <span className={`text-xs px-2 py-0.5 rounded font-semibold border ${getSeverityColor(alert.severity)}`}>
                          {alert.severity} Risk
                        </span>
                        {alert.acknowledged && (
                          <span className="text-xs bg-safe/10 text-safe border border-safe/20 px-2 py-0.5 rounded font-medium flex items-center gap-1">
                            <CheckCircle size={12} /> Acknowledged
                          </span>
                        )}
                      </div>
                      <h3 className="text-sm font-semibold text-white">{alert.description}</h3>
                      <div className="flex items-center gap-4 text-xs text-gray-500">
                        <span className="flex items-center gap-1">
                          <User size={13} /> {alert.name}
                        </span>
                        <span className="flex items-center gap-1">
                          <Clock size={13} /> {alert.created_at || "Just now"}
                        </span>
                      </div>
                    </div>

                    {!alert.acknowledged && (
                      <button
                        onClick={() => handleAcknowledge(alert.id)}
                        disabled={ackProgressId === alert.id}
                        className="px-3 py-1.5 bg-gray-800 hover:bg-brand-500/20 border border-gray-700 hover:border-brand-500/30 text-gray-300 hover:text-brand-400 rounded-lg text-xs font-semibold transition-all duration-150 disabled:opacity-50"
                      >
                        {ackProgressId === alert.id ? "Processing..." : "Acknowledge Alert"}
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === "suspicious" && (
          <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
            <div className="p-4 bg-gray-950 border-b border-gray-850 flex items-center justify-between">
              <span className="text-xs text-gray-400">Flagged Users (Contamination Limit: 5%)</span>
              <span className="text-xs font-mono bg-danger/10 text-danger border border-danger/20 px-2 py-0.5 rounded">
                Isolation Forest Outliers
              </span>
            </div>
            <div className="divide-y divide-gray-800/60 max-h-[500px] overflow-y-auto">
              {anomalies.map((user) => (
                <div key={user.user_id} className="p-4 hover:bg-gray-800/20 transition-colors flex items-center justify-between text-sm">
                  <div>
                    <p className="font-semibold text-white">{user.name}</p>
                    <p className="text-xs font-mono text-brand-400 mt-0.5">{user.user_id} • {user.role}</p>
                  </div>
                  <div className="text-right">
                    <span className="px-2.5 py-0.5 rounded bg-warning/10 text-warning border border-warning/20 text-xs font-semibold">
                      Risk Score: {user.risk_score?.toFixed(1)}
                    </span>
                    <p className="text-xs text-gray-500 mt-1">{user.department}</p>
                  </div>

                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === "high-risk" && (
          <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
            <div className="p-4 bg-gray-950 border-b border-gray-850 flex items-center justify-between">
              <span className="text-xs text-gray-400">Severe Threat Profiles (Score &gt;= 50)</span>
              <span className="text-xs font-mono bg-danger/10 text-danger border border-danger/20 px-2 py-0.5 rounded">
                High / Critical Alerts
              </span>
            </div>
            <div className="divide-y divide-gray-800/60 max-h-[500px] overflow-y-auto">
              {highRiskAnomalies.length === 0 ? (
                <div className="p-8 text-center text-gray-500 text-xs">No high risk anomalies detected.</div>
              ) : (
                highRiskAnomalies.map((user) => (
                  <div key={user.user_id} className="p-4 hover:bg-gray-800/20 transition-colors flex items-center justify-between text-sm">
                    <div>
                      <p className="font-semibold text-white">{user.name}</p>
                      <p className="text-xs font-mono text-danger mt-0.5">{user.user_id} • {user.role}</p>
                    </div>
                    <div className="text-right space-y-1">
                      <span className="px-2.5 py-0.5 rounded bg-danger/10 text-danger border border-danger/25 text-xs font-bold">
                        {user.risk_level} ({user.risk_score?.toFixed(1)})
                      </span>
                      <p className="text-xs text-gray-400">{user.security_status}</p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
