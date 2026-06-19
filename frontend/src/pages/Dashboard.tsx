import { useEffect, useState } from "react";
import axios from "axios";
import { Users, AlertTriangle, ShieldAlert, Zap, Loader2, FileDown, FileText, TableProperties } from "lucide-react";
import api, { dashboardApi, reportsApi } from "../services/api";

interface DashboardStats {
  total_users: number;
  anomalies_detected: number;
  high_risk_users: number;
  critical_users: number;
  total_alerts: number;
  pending_alerts: number;
  critical_alerts: number;
  high_alerts: number;
  warning_alerts: number;
  info_alerts: number;
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [generatingPdf, setGeneratingPdf] = useState(false);
  const [generatingCsv, setGeneratingCsv] = useState<Record<string, boolean>>({});

  const fetchOverview = () => {
    setLoading(true);
    setError(null);
    dashboardApi
      .getOverview()
      .then((res) => {
        setStats(res.data);
      })
      .catch((err) => {
        console.error("Error loading dashboard metrics:", err);
        setError("Unable to retrieve dashboard metrics from security gateway.");
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const downloadPdfReport = async () => {
    setGeneratingPdf(true);
    try {
      const response = await axios.get(reportsApi.getPdfUrl(), { responseType: "blob" });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "nfc_insider_threat_report.pdf");
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      console.error("Failed to compile PDF report:", err);
      let errorMsg = "Unable to compile executive PDF report.";
      if (err.response) {
        if (err.response.status === 404) {
          errorMsg = "PDF compilation failed: Source logs or database records not found on the security vault (404).";
        } else if (err.response.status === 500) {
          errorMsg = "PDF compilation failed: Backend server encountered an error (500).";
        } else {
          errorMsg = `PDF compilation failed with status code ${err.response.status}.`;
        }
      } else if (err.request) {
        errorMsg = "Network request failed: Secure security gateway is unreachable.";
      }
      alert(errorMsg);
    } finally {
      setGeneratingPdf(false);
    }
  };

  const downloadCsvReport = async (type: "profile" | "anomalies" | "risk", filename: string) => {
    setGeneratingCsv((prev) => ({ ...prev, [type]: true }));
    try {
      const response = await axios.get(reportsApi.getCsvUrl(type), { responseType: "blob" });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      console.error(`Failed to export ${type} CSV:`, err);
      let errorMsg = `Unable to export ${type} CSV log file.`;
      if (err.response) {
        if (err.response.status === 404) {
          errorMsg = `CSV export failed: Source file for '${type}' not found on the security vault (404).`;
        } else if (err.response.status === 500) {
          errorMsg = `CSV export failed: Backend server encountered an error (500).`;
        } else {
          errorMsg = `CSV export failed with status code ${err.response.status}.`;
        }
      } else if (err.request) {
        errorMsg = "Network request failed: Secure security gateway is unreachable.";
      }
      alert(errorMsg);
    } finally {
      setGeneratingCsv((prev) => ({ ...prev, [type]: false }));
    }
  };

  useEffect(() => {
    fetchOverview();
    window.addEventListener("refresh-data", fetchOverview);
    return () => window.removeEventListener("refresh-data", fetchOverview);
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] gap-3">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-brand-500"></div>
        <p className="text-gray-400 text-sm">Loading security summary...</p>
      </div>
    );
  }

  if (error || !stats) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] text-center max-w-md mx-auto">
        <AlertTriangle className="text-danger mb-4" size={48} />
        <h2 className="text-lg font-semibold text-white mb-2">Security Data Offline</h2>
        <p className="text-gray-400 text-sm mb-6">{error || "Data service is currently unavailable."}</p>
        <button
          onClick={fetchOverview}
          className="px-4 py-2 bg-brand-500 hover:bg-brand-700 text-white rounded-lg text-sm font-medium transition-colors"
        >
          Retry Connection
        </button>
      </div>
    );
  }

  const cards = [
    {
      title: "Total Users",
      value: stats.total_users,
      description: "Monitored employee profiles",
      icon: Users,
      bgColor: "bg-blue-500/10",
      textColor: "text-blue-400",
      borderColor: "border-blue-500/20",
    },
    {
      title: "Anomalies Detected",
      value: stats.anomalies_detected,
      description: "Flagged Suspicious by Isolation Forest",
      icon: AlertTriangle,
      bgColor: "bg-purple-500/10",
      textColor: "text-purple-400",
      borderColor: "border-purple-500/20",
    },
    {
      title: "High Risk Users",
      value: stats.high_risk_users,
      description: "Severe behavioral scoring outliers",
      icon: ShieldAlert,
      bgColor: "bg-warning/10",
      textColor: "text-warning",
      borderColor: "border-warning/20",
    },
    {
      title: "Critical Users",
      value: stats.critical_users,
      description: "Immediate action required cases",
      icon: Zap,
      bgColor: "bg-danger/10",
      textColor: "text-danger",
      borderColor: "border-danger/20",
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Security Command Center</h1>
        <p className="text-gray-400 text-sm">Real-time threat telemetry dashboard for Nuclear Fuel Complex assets.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {cards.map((card) => {
          const Icon = card.icon;
          return (
            <div
              key={card.title}
              className={`p-6 bg-gray-900 border ${card.borderColor} rounded-xl flex items-center justify-between transition-transform duration-200 hover:-translate-y-1`}
            >
              <div className="space-y-2">
                <p className="text-gray-400 text-xs font-medium uppercase tracking-wider">{card.title}</p>
                <p className="text-3xl font-extrabold text-white">{card.value.toLocaleString()}</p>
                <p className="text-gray-500 text-xs">{card.description}</p>
              </div>
              <div className={`p-4 rounded-lg ${card.bgColor} ${card.textColor}`}>
                <Icon size={24} />
              </div>
            </div>
          );
        })}
      </div>

      {/* Overview Context Panel */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-2">System Health & Threat Level</h2>
        <p className="text-gray-400 text-sm leading-relaxed max-w-3xl">
          The threat detection scanner is actively monitoring {stats.total_users} users. A total of{" "}
          {stats.anomalies_detected} anomalies have been identified by the Isolation Forest engine based on abnormal after-hours logins, excessive USB usage, and high logins-to-device ratio profiles.
        </p>
        <div className="mt-4 flex flex-wrap gap-4 items-center">
          <span className="flex items-center gap-2 text-xs font-semibold text-safe bg-safe/10 border border-safe/25 px-2.5 py-1 rounded-full">
            <span className="h-1.5 w-1.5 rounded-full bg-safe animate-pulse"></span>
            Telemetry Online
          </span>
          <span className="flex items-center gap-2 text-xs font-semibold text-brand-400 bg-brand-500/10 border border-brand-500/25 px-2.5 py-1 rounded-full">
            Isolation Forest Active
          </span>
        </div>
      </div>

      {/* Alert Severity Telemetry */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-4">
        <div className="flex justify-between items-center">
          <h2 className="text-lg font-semibold text-white">Active System Security Alerts</h2>
          <span className="text-xs bg-brand-500/20 text-brand-400 font-bold px-2.5 py-1 rounded-full border border-brand-500/20">
            {stats.pending_alerts} Pending Action
          </span>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="bg-gray-950 border border-gray-850 p-4 rounded-xl text-center space-y-1">
            <p className="text-gray-500 text-xs uppercase tracking-wider font-semibold">Total Alerts</p>
            <p className="text-2xl font-extrabold text-white">{stats.total_alerts}</p>
          </div>
          <div className="bg-gray-950 border border-danger/10 p-4 rounded-xl text-center space-y-1">
            <p className="text-danger text-xs uppercase tracking-wider font-semibold">Critical</p>
            <p className="text-2xl font-extrabold text-danger">{stats.critical_alerts}</p>
          </div>
          <div className="bg-gray-950 border border-warning/10 p-4 rounded-xl text-center space-y-1">
            <p className="text-warning text-xs uppercase tracking-wider font-semibold">High</p>
            <p className="text-2xl font-extrabold text-warning">{stats.high_alerts}</p>
          </div>
          <div className="bg-gray-950 border border-amber-500/10 p-4 rounded-xl text-center space-y-1">
            <p className="text-amber-400 text-xs uppercase tracking-wider font-semibold">Warning</p>
            <p className="text-2xl font-extrabold text-amber-400">{stats.warning_alerts}</p>
          </div>
          <div className="bg-gray-950 border border-slate-700/20 p-4 rounded-xl text-center space-y-1 col-span-2 md:col-span-1">
            <p className="text-slate-400 text-xs uppercase tracking-wider font-semibold">Info</p>
            <p className="text-2xl font-extrabold text-slate-400">{stats.info_alerts}</p>
          </div>
        </div>
      </div>

      {/* Export & Reports Center */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-6">
        <div>
          <h2 className="text-lg font-semibold text-white">Report & Intelligence Export Center</h2>
          <p className="text-gray-400 text-sm">Download certified executive briefs and underlying model metrics data registers.</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* PDF Card */}
          <div className="lg:col-span-4 p-5 bg-gray-950/60 border border-gray-800 rounded-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="space-y-1">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <FileText className="text-brand-400" size={18} /> Executive Security Audit Brief (PDF)
              </h3>
              <p className="text-xs text-gray-500 leading-relaxed max-w-2xl">
                Certified audit brief for presentations. Contains formal NFC government header decorations, executive summaries, risk distribution figures, department-level anomaly bars, and tabular records of Critical Threat outliers.
              </p>
            </div>
            <button
              onClick={downloadPdfReport}
              disabled={generatingPdf}
              className="flex items-center justify-center gap-2 bg-brand-500 hover:bg-brand-700 text-white font-medium px-5 py-2.5 rounded-lg text-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
            >
              {generatingPdf ? (
                <>
                  <Loader2 size={16} className="animate-spin" /> Compiling PDF...
                </>
              ) : (
                <>
                  <FileDown size={16} /> Export PDF Report
                </>
              )}
            </button>
          </div>

          {/* CSV Grid */}
          <div className="lg:col-span-4 grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* CSV 1 */}
            <div className="p-4 bg-gray-950/40 border border-gray-800/60 rounded-xl flex flex-col justify-between space-y-4">
              <div className="space-y-1">
                <h4 className="text-xs font-semibold text-white uppercase tracking-wider flex items-center gap-1.5">
                  <TableProperties className="text-purple-400" size={14} /> Final Security Profiles
                </h4>
                <p className="text-xs text-gray-500">Merged directory registry columns, risk scores, and anomaly predictions.</p>
              </div>
              <button
                onClick={() => downloadCsvReport("profile", "final_security_profile.csv")}
                disabled={generatingCsv["profile"]}
                className="w-full py-2 bg-gray-800 hover:bg-gray-700 text-gray-200 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors disabled:opacity-50"
              >
                {generatingCsv["profile"] ? (
                  <Loader2 size={13} className="animate-spin" />
                ) : (
                  <>
                    <FileDown size={13} /> Export Profile CSV
                  </>
                )}
              </button>
            </div>

            {/* CSV 2 */}
            <div className="p-4 bg-gray-950/40 border border-gray-800/60 rounded-xl flex flex-col justify-between space-y-4">
              <div className="space-y-1">
                <h4 className="text-xs font-semibold text-white uppercase tracking-wider flex items-center gap-1.5">
                  <TableProperties className="text-danger" size={14} /> Anomaly Prediction Logs
                </h4>
                <p className="text-xs text-gray-500">Isolation Forest classification outputs, index values, and labels.</p>
              </div>
              <button
                onClick={() => downloadCsvReport("anomalies", "anomaly_report.csv")}
                disabled={generatingCsv["anomalies"]}
                className="w-full py-2 bg-gray-800 hover:bg-gray-700 text-gray-200 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors disabled:opacity-50"
              >
                {generatingCsv["anomalies"] ? (
                  <Loader2 size={13} className="animate-spin" />
                ) : (
                  <>
                    <FileDown size={13} /> Export Anomalies CSV
                  </>
                )}
              </button>
            </div>

            {/* CSV 3 */}
            <div className="p-4 bg-gray-950/40 border border-gray-800/60 rounded-xl flex flex-col justify-between space-y-4">
              <div className="space-y-1">
                <h4 className="text-xs font-semibold text-white uppercase tracking-wider flex items-center gap-1.5">
                  <TableProperties className="text-warning" size={14} /> Risk Scoring Register
                </h4>
                <p className="text-xs text-gray-500">Numerical weighted scoring registries and categorizations.</p>
              </div>
              <button
                onClick={() => downloadCsvReport("risk", "risk_scores.csv")}
                disabled={generatingCsv["risk"]}
                className="w-full py-2 bg-gray-800 hover:bg-gray-700 text-gray-200 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors disabled:opacity-50"
              >
                {generatingCsv["risk"] ? (
                  <Loader2 size={13} className="animate-spin" />
                ) : (
                  <>
                    <FileDown size={13} /> Export Risk CSV
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
