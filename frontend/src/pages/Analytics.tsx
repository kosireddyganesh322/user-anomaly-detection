import { useEffect, useState, useMemo } from "react";
import { analyticsApi } from "../services/api";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ScatterChart,
  Scatter
} from "recharts";
import {
  AlertCircle,
  BarChart3,
  LineChart as LineIcon,
  Activity,
  TrendingUp,
  ShieldCheck,
  Search,
  Flame,
  LayoutGrid,
  AlertTriangle,
  Zap,
  FolderLock,
  Layers,
  Award
} from "lucide-react";

interface RiskDist {
  Low: number;
  Medium: number;
  High: number;
  Critical: number;
}

interface TrendPoint {
  day: string;
  count: number;
}

interface DeptRiskRank {
  department: string;
  avg_risk_score: number;
  suspicious_users: number;
  high_risk_users: number;
  critical_users: number;
}

interface TopRiskUser {
  user_id: string;
  name: string;
  department: string;
  risk_score: number;
  risk_level: string;
  anomaly_reason: string;
}

interface HeatmapRow {
  department: string;
  Low: number;
  Medium: number;
  High: number;
  Critical: number;
}

interface PostureScore {
  score: number;
  status: string;
  critical_users: number;
  high_risk_users: number;
  suspicious_users: number;
  avg_risk_score: number;
}

interface MatrixUser {
  user_id: string;
  name: string;
  department: string;
  risk_score: number;
  risk_level: string;
  anomaly_score: number;
  anomaly_reason: string;
}

interface IndicatorsSummary {
  avg_after_hours_ratio: number;
  avg_weekend_ratio: number;
  avg_usb_connections: number;
  avg_unique_endpoints: number;
  avg_risk_score: number;
}

interface WatchlistUser {
  user_id: string;
  name: string;
  department: string;
  risk_score: number;
  security_status: string;
  anomaly_reason: string;
}

export default function Analytics() {
  const [riskDist, setRiskDist] = useState<RiskDist | null>(null);
  const [loginTrends, setLoginTrends] = useState<TrendPoint[]>([]);
  const [deviceTrends, setDeviceTrends] = useState<TrendPoint[]>([]);
  
  // Phase 4 New states
  const [topRiskUsers, setTopRiskUsers] = useState<TopRiskUser[]>([]);
  const [deptRanking, setDeptRanking] = useState<DeptRiskRank[]>([]);
  const [reasonBreakdown, setReasonBreakdown] = useState<Record<string, number>>({});
  const [heatmap, setHeatmap] = useState<HeatmapRow[]>([]);
  const [posture, setPosture] = useState<PostureScore | null>(null);
  const [riskMatrix, setRiskMatrix] = useState<MatrixUser[]>([]);
  const [indicators, setIndicators] = useState<IndicatorsSummary | null>(null);
  const [watchlist, setWatchlist] = useState<WatchlistUser[]>([]);
  const [watchlistSearch, setWatchlistSearch] = useState("");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalytics = () => {
    setLoading(true);
    setError(null);
    Promise.all([
      analyticsApi.riskDistribution(),
      analyticsApi.loginTrends(),
      analyticsApi.deviceTrends(),
      analyticsApi.topRiskUsers(),
      analyticsApi.departmentRiskRanking(),
      analyticsApi.anomalyReasonBreakdown(),
      analyticsApi.threatHeatmap(),
      analyticsApi.securityPosture(),
      analyticsApi.riskMatrix(),
      analyticsApi.behavioralIndicators(),
      analyticsApi.watchlist(),
    ])
      .then(([
        riskRes, loginRes, deviceRes,
        topRes, deptRankRes, breakdownRes,
        heatmapRes, postureRes, matrixRes,
        indicatorsRes, watchlistRes
      ]) => {
        setRiskDist(riskRes.data);
        setLoginTrends(loginRes.data || []);
        setDeviceTrends(deviceRes.data || []);
        setTopRiskUsers(topRes.data || []);
        setDeptRanking(deptRankRes.data || []);
        setReasonBreakdown(breakdownRes.data || {});
        setHeatmap(heatmapRes.data || []);
        setPosture(postureRes.data || null);
        setRiskMatrix(matrixRes.data || []);
        setIndicators(indicatorsRes.data || null);
        setWatchlist(watchlistRes.data || []);
      })
      .catch((err) => {
        console.error("Error loading SOC analytics:", err);
        setError("Failed to fetch interactive SOC command center analytical data.");
      })
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchAnalytics();
    window.addEventListener("refresh-data", fetchAnalytics);
    return () => window.removeEventListener("refresh-data", fetchAnalytics);
  }, []);

  // Filter watchlist locally by user id, name or department
  const filteredWatchlist = useMemo(() => {
    if (!watchlistSearch.trim()) return watchlist;
    const term = watchlistSearch.toLowerCase();
    return watchlist.filter(
      (w) =>
        w.user_id.toLowerCase().includes(term) ||
        w.name.toLowerCase().includes(term) ||
        w.department.toLowerCase().includes(term)
    );
  }, [watchlist, watchlistSearch]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[500px] gap-3">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-500"></div>
        <p className="text-gray-400 text-xs tracking-wider font-mono">ASSEMBLING SOC COMMAND CENTER ANALYTICS...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-gray-900 border border-danger/20 p-8 rounded-xl text-center max-w-md mx-auto min-h-[250px] flex flex-col justify-center items-center">
        <AlertCircle className="text-danger mb-3" size={40} />
        <h3 className="text-white font-medium mb-2 text-lg">SOC Dashboard Load Failure</h3>
        <p className="text-gray-400 text-xs leading-relaxed">{error}</p>
        <button
          onClick={fetchAnalytics}
          className="mt-5 px-4 py-2 bg-brand-500 hover:bg-brand-700 text-white rounded-lg text-xs font-semibold transition-colors"
        >
          Try Again
        </button>
      </div>
    );
  }

  // Formatting risk data for Donut Chart (Threat Severity Distribution)
  const donutData = riskDist
    ? [
        { name: "Low", value: riskDist.Low, color: "#22c55e" },
        { name: "Medium", value: riskDist.Medium, color: "#f59e0b" },
        { name: "High", value: riskDist.High, color: "#ea580c" },
        { name: "Critical", value: riskDist.Critical, color: "#ef4444" },
      ]
    : [];
  const totalSeverityCount = donutData.reduce((acc, curr) => acc + curr.value, 0) || 1;

  // Formatting anomaly breakdown data for Pie Chart
  const pieData = Object.entries(reasonBreakdown).map(([name, value]) => ({
    name,
    value,
  }));
  const totalReasonsCount = pieData.reduce((acc, curr) => acc + curr.value, 0) || 1;
  const PIE_COLORS = ["#ef4444", "#ea580c", "#f59e0b", "#3b82f6", "#8b5cf6", "#10b981"];

  // Helper classes for badge colors
  const getRiskLevelBadge = (level: string) => {
    switch (level) {
      case "Critical":
        return "bg-danger/10 text-danger border border-danger/25 font-bold";
      case "High":
        return "bg-warning/10 text-warning border border-warning/25 font-semibold";
      case "Medium":
        return "bg-amber-500/10 text-amber-400 border border-amber-500/25";
      default:
        return "bg-safe/10 text-safe border border-safe/25";
    }
  };

  const getSecurityStatusBadge = (status: string) => {
    if (status.includes("Threat") || status.includes("Critical")) {
      return "bg-danger/10 text-danger border border-danger/20 font-bold";
    }
    if (status.includes("Medium")) {
      return "bg-amber-500/10 text-amber-400 border border-amber-500/20";
    }
    return "bg-gray-850 text-gray-400 border border-gray-800";
  };

  const getPostureScoreColor = (score: number) => {
    if (score >= 90) return "text-safe";
    if (score >= 75) return "text-warning";
    if (score >= 50) return "text-amber-400";
    return "text-danger";
  };

  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-gray-850 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <ShieldCheck className="text-brand-500" size={26} /> SOC Command Center Dashboard
          </h1>
          <p className="text-gray-400 text-sm">Advanced real-time risk scores, department threat matrix, anomalies, and watchlist controls.</p>
        </div>
        <div className="text-xs text-gray-500 bg-gray-900 border border-gray-800 px-3 py-1.5 rounded-lg flex items-center gap-1.5 font-mono">
          <span className="h-2 w-2 rounded-full bg-brand-500 animate-ping"></span>
          LIVE MONITORING ACTIVE
        </div>
      </div>

      {/* Row 1: KPI Summary Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-5">
        {/* Security Health Score */}
        {posture && (
          <div className="bg-gray-950 border border-gray-800 p-5 rounded-xl flex flex-col justify-between col-span-1 lg:col-span-2 min-h-[140px] relative overflow-hidden group">
            <div className="absolute right-[-10px] top-[-10px] opacity-5 text-white group-hover:scale-110 transition-transform">
              <ShieldCheck size={120} />
            </div>
            <div>
              <span className="text-gray-500 text-[10px] font-bold uppercase tracking-wider block">Security Posture Health</span>
              <div className="flex items-baseline gap-2 mt-1">
                <span className={`text-4xl font-extrabold font-mono tracking-tight ${getPostureScoreColor(posture.score)}`}>
                  {posture.score}
                </span>
                <span className="text-gray-500 text-sm">/ 100</span>
              </div>
            </div>
            <div className="flex justify-between items-center mt-3 pt-3 border-t border-gray-900">
              <span className="text-xs text-gray-400">Status Label</span>
              <span className={`text-xs font-bold uppercase px-2.5 py-0.5 rounded-full border ${
                posture.status === "Excellent" ? "bg-safe/10 text-safe border-safe/25" :
                posture.status === "Good" ? "bg-warning/10 text-warning border-warning/25" :
                posture.status === "Moderate" ? "bg-amber-500/10 text-amber-400 border-amber-500/25" :
                "bg-danger/10 text-danger border-danger/25"
              }`}>
                {posture.status}
              </span>
            </div>
          </div>
        )}

        {/* Behavioral Indicators KPI cards */}
        {indicators && (
          <>
            <div className="bg-gray-900 border border-gray-800 p-4 rounded-xl flex flex-col justify-between">
              <div>
                <span className="text-gray-500 text-[10px] font-bold uppercase tracking-wider block">Avg Off-Hours Ratio</span>
                <span className="text-2xl font-bold font-mono text-white mt-1.5 block">
                  {(indicators.avg_after_hours_ratio * 100).toFixed(1)}%
                </span>
              </div>
              <span className="text-[10px] text-gray-500 mt-2 block">After-hours logins ratio</span>
            </div>

            <div className="bg-gray-900 border border-gray-800 p-4 rounded-xl flex flex-col justify-between">
              <div>
                <span className="text-gray-500 text-[10px] font-bold uppercase tracking-wider block">Avg Weekend Ratio</span>
                <span className="text-2xl font-bold font-mono text-white mt-1.5 block">
                  {(indicators.avg_weekend_ratio * 100).toFixed(1)}%
                </span>
              </div>
              <span className="text-[10px] text-gray-500 mt-2 block">Weekend access ratio</span>
            </div>

            <div className="bg-gray-900 border border-gray-800 p-4 rounded-xl flex flex-col justify-between">
              <div>
                <span className="text-gray-500 text-[10px] font-bold uppercase tracking-wider block">Avg USB Connections</span>
                <span className="text-2xl font-bold font-mono text-white mt-1.5 block">
                  {indicators.avg_usb_connections.toFixed(1)}
                </span>
              </div>
              <span className="text-[10px] text-gray-500 mt-2 block">Mounts per profile</span>
            </div>

            <div className="bg-gray-900 border border-gray-800 p-4 rounded-xl flex flex-col justify-between">
              <div>
                <span className="text-gray-500 text-[10px] font-bold uppercase tracking-wider block">Avg Endpoint Count</span>
                <span className="text-2xl font-bold font-mono text-white mt-1.5 block">
                  {indicators.avg_unique_endpoints.toFixed(1)}
                </span>
              </div>
              <span className="text-[10px] text-gray-500 mt-2 block">Unique PCs logged on</span>
            </div>
          </>
        )}
      </div>

      {/* Row 2: Top 10 High-Risk Users & Critical Watchlist */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top 10 High Risk Users */}
        <div className="bg-gray-900 border border-gray-800 p-5 rounded-xl flex flex-col space-y-4">
          <h2 className="text-sm font-semibold text-white uppercase tracking-wider flex items-center gap-2">
            <Flame size={16} className="text-danger" /> Top 10 Highest Risk Users
          </h2>
          <div className="overflow-x-auto min-h-[300px]">
            <table className="w-full text-left border-collapse whitespace-nowrap text-xs">
              <thead>
                <tr className="border-b border-gray-800 bg-gray-950 text-gray-400 uppercase tracking-wider font-semibold">
                  <th className="py-2.5 px-3">User ID</th>
                  <th className="py-2.5 px-3">Name</th>
                  <th className="py-2.5 px-3">Department</th>
                  <th className="py-2.5 px-3 text-center">Risk Score</th>
                  <th className="py-2.5 px-3 text-center">Risk Level</th>
                  <th className="py-2.5 px-3">Primary Anomaly</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800 text-gray-300">
                {topRiskUsers.map((u) => (
                  <tr key={u.user_id} className="hover:bg-gray-800/40 transition-colors">
                    <td className="py-2 px-3 font-mono font-bold text-brand-400">{u.user_id}</td>
                    <td className="py-2 px-3 text-white font-medium">{u.name}</td>
                    <td className="py-2 px-3 text-gray-400">{u.department}</td>
                    <td className="py-2 px-3 text-center font-bold">{u.risk_score.toFixed(1)}</td>
                    <td className="py-2 px-3 text-center">
                      <span className={`px-2 py-0.5 rounded text-[10px] ${getRiskLevelBadge(u.risk_level)}`}>
                        {u.risk_level}
                      </span>
                    </td>
                    <td className="py-2 px-3 max-w-[150px] truncate" title={u.anomaly_reason}>
                      {u.anomaly_reason}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Critical Watchlist with local search */}
        <div className="bg-gray-900 border border-gray-800 p-5 rounded-xl flex flex-col space-y-4">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
            <h2 className="text-sm font-semibold text-white uppercase tracking-wider flex items-center gap-2">
              <FolderLock size={16} className="text-warning" /> Critical User Watchlist (Top 20)
            </h2>
            <div className="relative w-full sm:w-48">
              <Search className="absolute left-2.5 top-2 text-gray-500" size={13} />
              <input
                type="text"
                placeholder="Search watchlist..."
                value={watchlistSearch}
                onChange={(e) => setWatchlistSearch(e.target.value)}
                className="w-full bg-gray-950 border border-gray-800 rounded-lg pl-8 pr-3 py-1 text-xs text-white focus:outline-none focus:border-brand-500 transition-colors"
              />
            </div>
          </div>
          <div className="overflow-x-auto min-h-[300px] max-h-[310px] overflow-y-auto">
            <table className="w-full text-left border-collapse whitespace-nowrap text-xs">
              <thead>
                <tr className="border-b border-gray-800 bg-gray-950 text-gray-400 uppercase tracking-wider font-semibold sticky top-0 z-10">
                  <th className="py-2.5 px-3 bg-gray-950">User ID</th>
                  <th className="py-2.5 px-3 bg-gray-950">Name</th>
                  <th className="py-2.5 px-3 bg-gray-950">Department</th>
                  <th className="py-2.5 px-3 bg-gray-950 text-center">Score</th>
                  <th className="py-2.5 px-3 bg-gray-950 text-center">Clearance Status</th>
                  <th className="py-2.5 px-3 bg-gray-950">Reason</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800 text-gray-300">
                {filteredWatchlist.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="text-center py-8 text-gray-500">
                      No matching watchlist profiles.
                    </td>
                  </tr>
                ) : (
                  filteredWatchlist.map((u) => (
                    <tr key={u.user_id} className="hover:bg-gray-800/40 transition-colors">
                      <td className="py-2 px-3 font-mono font-bold text-brand-400">{u.user_id}</td>
                      <td className="py-2 px-3 text-white font-medium">{u.name}</td>
                      <td className="py-2 px-3 text-gray-400">{u.department}</td>
                      <td className="py-2 px-3 text-center font-bold">{u.risk_score.toFixed(1)}</td>
                      <td className="py-2 px-3 text-center">
                        <span className={`px-2 py-0.5 rounded text-[10px] ${getSecurityStatusBadge(u.security_status)}`}>
                          {u.security_status}
                        </span>
                      </td>
                      <td className="py-2 px-3 max-w-[150px] truncate" title={u.anomaly_reason}>
                        {u.anomaly_reason}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Row 3: Department Risk Ranking & Threat Severity Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Department Risk Ranking */}
        <div className="bg-gray-900 border border-gray-800 p-5 rounded-xl flex flex-col space-y-4">
          <h2 className="text-sm font-semibold text-white uppercase tracking-wider flex items-center gap-2">
            <TrendingUp size={16} className="text-brand-400" /> Department Risk Ranking
          </h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                layout="vertical"
                data={deptRanking}
                margin={{ top: 10, right: 10, left: 30, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" horizontal={false} />
                <XAxis type="number" stroke="#9ca3af" tickLine={false} style={{ fontSize: "10px" }} />
                <YAxis dataKey="department" type="category" stroke="#9ca3af" tickLine={false} style={{ fontSize: "9px" }} width={110} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#111827", borderColor: "#374151", color: "#fff" }}
                  labelStyle={{ color: "#fff", fontWeight: "bold" }}
                  itemStyle={{ color: "#fff" }}
                />
                <Bar dataKey="avg_risk_score" name="Avg Risk Score" fill="#ea580c" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          {/* Ranking Table below chart */}
          <div className="overflow-x-auto pt-2 border-t border-gray-800">
            <table className="w-full text-left border-collapse text-xs whitespace-nowrap">
              <thead>
                <tr className="text-gray-500 border-b border-gray-800 font-semibold">
                  <th className="py-1 px-2">Rank</th>
                  <th className="py-1 px-2">Department</th>
                  <th className="py-1 px-2 text-center">Avg Risk Score</th>
                  <th className="py-1 px-2 text-center">Suspicious Users</th>
                  <th className="py-1 px-2 text-center">High Risk</th>
                  <th className="py-1 px-2 text-center">Critical</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800 text-gray-300">
                {deptRanking.map((d, i) => (
                  <tr key={d.department} className="hover:bg-gray-800/20">
                    <td className="py-1.5 px-2 font-bold font-mono text-gray-400">{i + 1}</td>
                    <td className="py-1.5 px-2 text-white font-medium">{d.department}</td>
                    <td className="py-1.5 px-2 text-center font-bold text-amber-400">{d.avg_risk_score.toFixed(1)}</td>
                    <td className="py-1.5 px-2 text-center">{d.suspicious_users}</td>
                    <td className="py-1.5 px-2 text-center text-warning">{d.high_risk_users}</td>
                    <td className="py-1.5 px-2 text-center text-danger">{d.critical_users}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Threat Severity Distribution (Donut Chart) */}
        <div className="bg-gray-900 border border-gray-800 p-5 rounded-xl flex flex-col space-y-4">
          <h2 className="text-sm font-semibold text-white uppercase tracking-wider flex items-center gap-2">
            <Award size={16} className="text-brand-400" /> Threat Severity Distribution
          </h2>
          <div className="h-64 flex justify-center items-center relative">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={donutData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={85}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {donutData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: "#111827", borderColor: "#374151", color: "#fff" }}
                  itemStyle={{ color: "#fff" }}
                  formatter={(value: number) => [`${value} users (${((value / totalSeverityCount) * 100).toFixed(1)}%)`, "Count"]}
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="absolute flex flex-col items-center justify-center">
              <span className="text-2xl font-bold font-mono text-white">{totalSeverityCount}</span>
              <span className="text-[10px] text-gray-500 uppercase tracking-wider font-bold">Total Users</span>
            </div>
          </div>
          {/* Custom stats breakdown block below chart */}
          <div className="grid grid-cols-4 gap-2 pt-2 border-t border-gray-800 text-center text-xs">
            {donutData.map((d) => (
              <div key={d.name} className="p-2 bg-gray-950 rounded-lg border border-gray-850">
                <span className="text-gray-500 block mb-0.5 text-[10px] uppercase font-bold">{d.name}</span>
                <span className="font-mono text-sm font-extrabold text-white block">{d.value}</span>
                <span className="text-[10px] text-gray-400 block">{((d.value / totalSeverityCount) * 100).toFixed(1)}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Row 4: Anomaly Reason Breakdown & Threat Heatmap */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Anomaly Reason Breakdown */}
        <div className="bg-gray-900 border border-gray-800 p-5 rounded-xl flex flex-col space-y-4">
          <h2 className="text-sm font-semibold text-white uppercase tracking-wider flex items-center gap-2">
            <Layers size={16} className="text-brand-400" /> Anomaly Reason Breakdown
          </h2>
          <div className="h-64 flex justify-center items-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  dataKey="value"
                  label={({ name, percent }) => `${(percent * 100).toFixed(0)}%`}
                  labelLine={false}
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: "#111827", borderColor: "#374151", color: "#fff" }}
                  itemStyle={{ color: "#fff" }}
                  formatter={(value: number) => [`${value} flags (${((value / totalReasonsCount) * 100).toFixed(1)}%)`, "Counts"]}
                />
                <Legend layout="horizontal" verticalAlign="bottom" iconType="circle" wrapperStyle={{ fontSize: "10px", color: "#9ca3af" }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Threat Heatmap Grid */}
        <div className="bg-gray-900 border border-gray-800 p-5 rounded-xl flex flex-col space-y-4">
          <h2 className="text-sm font-semibold text-white uppercase tracking-wider flex items-center gap-2">
            <LayoutGrid size={16} className="text-brand-400" /> Department vs Risk Level Threat Heatmap
          </h2>
          <div className="overflow-x-auto">
            <div className="min-w-[450px] space-y-2 text-xs">
              {/* Heatmap header */}
              <div className="grid grid-cols-5 gap-2 font-bold text-gray-500 uppercase tracking-wider py-1.5 border-b border-gray-800">
                <div>Department</div>
                <div className="text-center">Low</div>
                <div className="text-center">Medium</div>
                <div className="text-center">High</div>
                <div className="text-center">Critical</div>
              </div>
              {/* Heatmap rows */}
              {heatmap.map((row) => {
                const getHeatmapColor = (count: number, type: "Low" | "Medium" | "High" | "Critical") => {
                  if (count === 0) return "bg-gray-950 text-gray-600 border border-gray-900";
                  if (type === "Low") return "bg-safe/25 text-safe border border-safe/30 font-semibold";
                  if (type === "Medium") return "bg-amber-500/25 text-amber-400 border border-amber-500/30 font-semibold";
                  if (type === "High") return "bg-warning/25 text-warning border border-warning/30 font-semibold";
                  return "bg-danger/25 text-danger border border-danger/30 font-bold animate-pulse";
                };

                return (
                  <div key={row.department} className="grid grid-cols-5 gap-2 items-center hover:bg-gray-850/30 p-1.5 rounded-lg transition-colors">
                    <div className="font-semibold text-white truncate pr-2" title={row.department}>
                      {row.department}
                    </div>
                    <div className={`p-2 rounded text-center font-mono ${getHeatmapColor(row.Low, "Low")}`}>
                      {row.Low}
                    </div>
                    <div className={`p-2 rounded text-center font-mono ${getHeatmapColor(row.Medium, "Medium")}`}>
                      {row.Medium}
                    </div>
                    <div className={`p-2 rounded text-center font-mono ${getHeatmapColor(row.High, "High")}`}>
                      {row.High}
                    </div>
                    <div className={`p-2 rounded text-center font-mono ${getHeatmapColor(row.Critical, "Critical")}`}>
                      {row.Critical}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Row 5: User Activity Risk Matrix (Scatter Plot) */}
      <div className="bg-gray-900 border border-gray-800 p-5 rounded-xl flex flex-col space-y-4">
        <h2 className="text-sm font-semibold text-white uppercase tracking-wider flex items-center gap-2">
          <Activity size={16} className="text-brand-400" /> User Activity Anomaly Risk Matrix
        </h2>
        <div className="h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: -20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
              <XAxis type="number" dataKey="risk_score" name="Risk Score" stroke="#9ca3af" style={{ fontSize: "11px" }} />
              <YAxis type="number" dataKey="anomaly_score" name="Anomaly Score" stroke="#9ca3af" style={{ fontSize: "11px" }} />
              <Tooltip
                cursor={{ strokeDasharray: '3 3' }}
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload;
                    return (
                      <div className="bg-gray-950 border border-gray-800 p-3 rounded-lg text-xs space-y-1.5 shadow-2xl">
                        <p className="font-bold text-white font-mono text-sm border-b border-gray-800 pb-1 flex justify-between items-center gap-2">
                          <span>{data.user_id}</span>
                          <span className={`px-1.5 py-0.5 rounded text-[10px] ${getRiskLevelBadge(data.risk_level)}`}>
                            {data.risk_level}
                          </span>
                        </p>
                        <p className="text-gray-400">Name: <span className="text-white font-medium">{data.name}</span></p>
                        <p className="text-gray-400">Department: <span className="text-white">{data.department}</span></p>
                        <p className="text-gray-400">Risk Score: <span className="text-white font-bold">{data.risk_score.toFixed(1)}</span></p>
                        <p className="text-gray-400">Anomaly Score: <span className="text-white font-mono">{data.anomaly_score.toFixed(4)}</span></p>
                        <p className="text-gray-400 max-w-[250px] leading-relaxed">
                          Explanation: <span className="text-brand-400 font-medium">{data.anomaly_reason}</span>
                        </p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Scatter name="Users" data={riskMatrix}>
                {riskMatrix.map((entry, index) => {
                  let color = "#22c55e"; // Low = Green
                  if (entry.risk_level === "Critical") color = "#ef4444"; // Critical = Red
                  else if (entry.risk_level === "High") color = "#ea580c"; // High = Orange
                  else if (entry.risk_level === "Medium") color = "#f59e0b"; // Medium = Yellow
                  return <Cell key={`cell-${index}`} fill={color} fillOpacity={0.75} r={5} />;
                })}
              </Scatter>
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Row 6: Timelines (Retained from previous layout) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Login Trends Chart */}
        <div className="bg-gray-900 border border-gray-800 p-5 rounded-xl flex flex-col space-y-4">
          <h2 className="text-sm font-semibold text-white uppercase tracking-wider flex items-center gap-2">
            <LineIcon size={16} className="text-brand-400" /> Daily User Logon Events Timeline
          </h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={loginTrends} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
                <XAxis dataKey="day" stroke="#9ca3af" tickLine={false} tick={false} />
                <YAxis stroke="#9ca3af" tickLine={false} style={{ fontSize: "11px" }} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#111827", borderColor: "#374151" }}
                  labelStyle={{ color: "#fff", fontWeight: "bold" }}
                  itemStyle={{ color: "#3b5bdb" }}
                />
                <Line
                  type="monotone"
                  dataKey="count"
                  name="Logons"
                  stroke="#3b5bdb"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Device Trends Chart */}
        <div className="bg-gray-900 border border-gray-800 p-5 rounded-xl flex flex-col space-y-4">
          <h2 className="text-sm font-semibold text-white uppercase tracking-wider flex items-center gap-2">
            <Activity size={16} className="text-brand-400" /> Daily USB Device Connect Events Timeline
          </h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={deviceTrends} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorDeviceSoc" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
                <XAxis dataKey="day" stroke="#9ca3af" tickLine={false} tick={false} />
                <YAxis stroke="#9ca3af" tickLine={false} style={{ fontSize: "11px" }} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#111827", borderColor: "#374151" }}
                  labelStyle={{ color: "#fff", fontWeight: "bold" }}
                  itemStyle={{ color: "#8b5cf6" }}
                />
                <Area
                  type="monotone"
                  dataKey="count"
                  name="USB Connections"
                  stroke="#8b5cf6"
                  fillOpacity={1}
                  fill="url(#colorDeviceSoc)"
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
