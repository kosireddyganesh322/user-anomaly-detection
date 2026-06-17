import { useEffect, useState } from "react";
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
} from "recharts";
import { AlertCircle, BarChart3, LineChart as LineIcon, Activity, TrendingUp } from "lucide-react";

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

interface DeptSummary {
  department: string;
  total_users: number;
  anomalies: number;
}

export default function Analytics() {
  const [riskDist, setRiskDist] = useState<RiskDist | null>(null);
  const [loginTrends, setLoginTrends] = useState<TrendPoint[]>([]);
  const [deviceTrends, setDeviceTrends] = useState<TrendPoint[]>([]);
  const [deptSummary, setDeptSummary] = useState<DeptSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalytics = () => {
    setLoading(true);
    setError(null);
    Promise.all([
      analyticsApi.riskDistribution(),
      analyticsApi.loginTrends(),
      analyticsApi.deviceTrends(),
      analyticsApi.departmentSummary(),
    ])
      .then(([riskRes, loginRes, deviceRes, deptRes]) => {
        setRiskDist(riskRes.data);
        setLoginTrends(loginRes.data || []);
        setDeviceTrends(deviceRes.data || []);
        setDeptSummary(deptRes.data || []);
      })
      .catch((err) => {
        console.error("Error loading analytics:", err);
        setError("Failed to fetch interactive analytical graphs.");
      })
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] gap-3">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-500"></div>
        <p className="text-gray-400 text-xs">Assembling visual charts...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-gray-900 border border-danger/20 p-6 rounded-xl text-center max-w-md mx-auto min-h-[200px] flex flex-col justify-center items-center">
        <AlertCircle className="text-danger mb-3" size={36} />
        <h3 className="text-white font-medium mb-1">Analytics Error</h3>
        <p className="text-gray-400 text-xs">{error}</p>
        <button
          onClick={fetchAnalytics}
          className="mt-4 px-3 py-1.5 bg-brand-500 hover:bg-brand-700 text-white rounded-lg text-xs font-semibold"
        >
          Try Again
        </button>
      </div>
    );
  }

  // Formatting risk data for Recharts
  const riskData = riskDist
    ? [
        { name: "Low", value: riskDist.Low, color: "#22c55e" },
        { name: "Medium", value: riskDist.Medium, color: "#f59e0b" },
        { name: "High", value: riskDist.High, color: "#ea580c" },
        { name: "Critical", value: riskDist.Critical, color: "#ef4444" },
      ]
    : [];

  return (
    <div className="space-y-6 pb-12">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">System Threat Analytics</h1>
        <p className="text-gray-400 text-sm">Visual statistical breakdowns, temporal logon spikes, and departmental indicators.</p>
      </div>

      {/* Analytics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Risk Distribution Chart */}
        <div className="bg-gray-900 border border-gray-800 p-5 rounded-xl flex flex-col space-y-4">
          <h2 className="text-sm font-semibold text-white uppercase tracking-wider flex items-center gap-2">
            <BarChart3 size={16} className="text-brand-400" /> User Risk Class Distribution
          </h2>
          <div className="h-64 flex justify-center items-center">
            {riskDist && (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={riskData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {riskData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: "#111827", borderColor: "#374151", color: "#fff" }}
                    itemStyle={{ color: "#fff" }}
                  />
                  <Legend iconType="circle" wrapperStyle={{ fontSize: "12px", color: "#9ca3af" }} />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Department Summary Chart */}
        <div className="bg-gray-900 border border-gray-800 p-5 rounded-xl flex flex-col space-y-4">
          <h2 className="text-sm font-semibold text-white uppercase tracking-wider flex items-center gap-2">
            <TrendingUp size={16} className="text-brand-400" /> Anomalies vs Total Users by Department
          </h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={deptSummary} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
                <XAxis dataKey="department" stroke="#9ca3af" tickLine={false} style={{ fontSize: "10px" }} />
                <YAxis stroke="#9ca3af" tickLine={false} style={{ fontSize: "10px" }} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#111827", borderColor: "#374151" }}
                  labelStyle={{ color: "#fff", fontWeight: "bold" }}
                />
                <Legend wrapperStyle={{ fontSize: "12px" }} />
                <Bar dataKey="total_users" name="Total Users" fill="#475569" radius={[4, 4, 0, 0]} />
                <Bar dataKey="anomalies" name="Anomalies Flagged" fill="#ef4444" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Login Trends Chart */}
        <div className="bg-gray-900 border border-gray-800 p-5 rounded-xl flex flex-col space-y-4 lg:col-span-2">
          <h2 className="text-sm font-semibold text-white uppercase tracking-wider flex items-center gap-2">
            <LineIcon size={16} className="text-brand-400" /> Daily User Logon Events Timeline (516 Days)
          </h2>
          <div className="h-72">
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
        <div className="bg-gray-900 border border-gray-800 p-5 rounded-xl flex flex-col space-y-4 lg:col-span-2">
          <h2 className="text-sm font-semibold text-white uppercase tracking-wider flex items-center gap-2">
            <Activity size={16} className="text-brand-400" /> Daily USB Device Connect Events Timeline (515 Days)
          </h2>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={deviceTrends} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorDevice" x1="0" y1="0" x2="0" y2="1">
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
                  fill="url(#colorDevice)"
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
