import { useState, useEffect } from "react";
import { useUsers } from "../hooks/useUsers";
import { usersApi } from "../services/api";
import { Search, ChevronLeft, ChevronRight, X, AlertTriangle, Eye, ShieldAlert, ArrowUpDown } from "lucide-react";

interface UserProfile {
  user_id: string;
  name?: string;
  email?: string;
  role?: string;
  department?: string;
  team?: string;
  manager?: string;
  risk_score?: number;
  risk_level?: string;
  anomaly_score?: number;
  anomaly_label?: string;
  security_status?: string;
}

export default function UserExplorer() {
  const {
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
    setSearch,
    setDepartment,
    setRiskLevel,
    setAnomalyLabel,
  } = useUsers();

  const [selectedUserId, setSelectedUserId] = useState<string | null>(null);
  const [selectedUser, setSelectedUser] = useState<UserProfile | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState<string | null>(null);

  // Debounced search term
  const [searchInput, setSearchInput] = useState(search);

  useEffect(() => {
    const handler = setTimeout(() => {
      setSearch(searchInput);
    }, 400);
    return () => clearTimeout(handler);
  }, [searchInput, setSearch]);

  // Load detailed user profile
  useEffect(() => {
    if (!selectedUserId) {
      setSelectedUser(null);
      return;
    }

    setDetailLoading(true);
    setDetailError(null);
    usersApi
      .getById(selectedUserId)
      .then((res) => {
        setSelectedUser(res.data);
      })
      .catch((err) => {
        console.error("Error fetching user profile:", err);
        setDetailError("Failed to fetch detailed profile statistics.");
      })
      .finally(() => {
        setDetailLoading(false);
      });
  }, [selectedUserId]);

  const totalPages = Math.ceil(total / limit) || 1;

  const handlePrevPage = () => {
    if (page > 1) setPage(page - 1);
  };

  const handleNextPage = () => {
    if (page < totalPages) setPage(page + 1);
  };

  const getRiskBadgeClass = (level?: string) => {
    switch (level) {
      case "Critical":
        return "bg-danger/10 text-danger border-danger/25";
      case "High":
        return "bg-warning/10 text-warning border-warning/25";
      case "Medium":
        return "bg-amber-500/10 text-amber-400 border-amber-500/25";
      default:
        return "bg-safe/10 text-safe border-safe/25";
    }
  };

  const getStatusBadgeClass = (status?: string) => {
    if (status?.includes("Threat")) {
      return "bg-danger/20 text-red-300 border-danger/30 font-semibold";
    }
    return "bg-gray-800 text-gray-400 border-gray-700";
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">User Explorer</h1>
          <p className="text-gray-400 text-sm">Audit, search, and inspect individual access logs and security scores.</p>
        </div>
        <div className="text-sm text-gray-500 bg-gray-900 border border-gray-800 px-3 py-1.5 rounded-lg">
          Showing <span className="text-white font-medium">{users.length}</span> of{" "}
          <span className="text-white font-medium">{total.toLocaleString()}</span> users
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="bg-gray-900 border border-gray-800 p-4 rounded-xl flex flex-col md:flex-row gap-4 items-center">
        {/* Search */}
        <div className="relative w-full md:w-80">
          <Search className="absolute left-3 top-2.5 text-gray-500" size={17} />
          <input
            type="text"
            placeholder="Search by ID, name, or role..."
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
          {/* Risk Level */}
          <select
            value={riskLevel}
            onChange={(e) => setRiskLevel(e.target.value)}
            className="bg-gray-950 border border-gray-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-brand-500"
          >
            <option value="">All Risk Levels</option>
            <option value="Low">Low Risk</option>
            <option value="Medium">Medium Risk</option>
            <option value="High">High Risk</option>
            <option value="Critical">Critical Risk</option>
          </select>

          {/* Anomaly status */}
          <select
            value={anomalyLabel}
            onChange={(e) => setAnomalyLabel(e.target.value)}
            className="bg-gray-950 border border-gray-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-brand-500"
          >
            <option value="">All Statuses</option>
            <option value="Normal">Normal</option>
            <option value="Suspicious">Suspicious</option>
          </select>

          {/* Department */}
          <select
            value={department}
            onChange={(e) => setDepartment(e.target.value)}
            className="bg-gray-950 border border-gray-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-brand-500 col-span-2 md:col-span-1"
          >
            <option value="">All Departments</option>
            <option value="1 - Executive">1 - Executive</option>
            <option value="2 - Engineering">2 - Engineering</option>
            <option value="3 - Assembly">3 - Assembly</option>
            <option value="4 - Quality Assurance">4 - Quality Assurance</option>
            <option value="5 - Security">5 - Security</option>
          </select>
        </div>
      </div>

      {/* Main Content Area */}
      {error ? (
        <div className="bg-gray-900 border border-danger/20 p-6 rounded-xl text-center max-w-md mx-auto">
          <AlertTriangle className="text-danger mx-auto mb-3" size={36} />
          <h3 className="text-white font-medium mb-1">Failed to load profiles</h3>
          <p className="text-gray-400 text-xs">{error}</p>
        </div>
      ) : loading ? (
        <div className="bg-gray-900 border border-gray-800 rounded-xl min-h-[300px] flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-500"></div>
        </div>
      ) : users.length === 0 ? (
        <div className="bg-gray-900 border border-gray-800 rounded-xl min-h-[300px] flex flex-col items-center justify-center text-center p-6">
          <ShieldAlert className="text-gray-600 mb-3" size={36} />
          <h3 className="text-white font-medium mb-1">No matching users found</h3>
          <p className="text-gray-500 text-xs">Try adjusting your filters or refining your search parameters.</p>
        </div>
      ) : (
        <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
          {/* Table Container */}
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-gray-800 bg-gray-950 text-gray-400 text-xs uppercase tracking-wider">
                  <th className="py-3 px-4 font-semibold">User ID</th>
                  <th className="py-3 px-4 font-semibold">Name</th>
                  <th className="py-3 px-4 font-semibold">Department</th>
                  <th className="py-3 px-4 font-semibold">Role</th>
                  <th className="py-3 px-4 font-semibold text-center">Risk Score</th>
                  <th className="py-3 px-4 font-semibold text-center">Anomaly Label</th>
                  <th className="py-3 px-4 font-semibold text-center">Security Status</th>
                  <th className="py-3 px-4 font-semibold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800 text-sm text-gray-300">
                {users.map((u) => (
                  <tr key={u.user_id} className="hover:bg-gray-800/40 transition-colors">
                    <td className="py-3 px-4 font-mono text-brand-400 font-semibold">{u.user_id}</td>
                    <td className="py-3 px-4 text-white font-medium">{u.name || "N/A"}</td>
                    <td className="py-3 px-4 text-gray-400">{u.department || "N/A"}</td>
                    <td className="py-3 px-4 text-gray-400">{u.role || "N/A"}</td>
                    <td className="py-3 px-4 text-center">
                      <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border ${getRiskBadgeClass(u.risk_level)}`}>
                        {u.risk_score?.toFixed(1) || "0.0"} ({u.risk_level})
                      </span>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span
                        className={`px-2 py-0.5 rounded-md text-xs font-semibold ${
                          u.anomaly_label === "Suspicious"
                            ? "bg-danger/10 text-danger border border-danger/25"
                            : "bg-gray-800 text-gray-500 border border-gray-700"
                        }`}
                      >
                        {u.anomaly_label}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span className={`px-2 py-0.5 rounded text-xs border ${getStatusBadgeClass(u.security_status)}`}>
                        {u.security_status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => setSelectedUserId(u.user_id)}
                        className="p-1 text-gray-400 hover:text-white transition-colors"
                        title="View Profile Details"
                      >
                        <Eye size={17} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination Controls */}
          <div className="flex items-center justify-between px-6 py-4 border-t border-gray-800 bg-gray-950">
            <span className="text-xs text-gray-500">
              Page <span className="text-white font-medium">{page}</span> of{" "}
              <span className="text-white font-medium">{totalPages}</span>
            </span>
            <div className="flex gap-2">
              <button
                onClick={handlePrevPage}
                disabled={page === 1}
                className="p-2 border border-gray-800 rounded-lg text-gray-400 hover:text-white disabled:opacity-50 disabled:hover:text-gray-400 transition-colors"
              >
                <ChevronLeft size={16} />
              </button>
              <button
                onClick={handleNextPage}
                disabled={page === totalPages}
                className="p-2 border border-gray-800 rounded-lg text-gray-400 hover:text-white disabled:opacity-50 disabled:hover:text-gray-400 transition-colors"
              >
                <ChevronRight size={16} />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* User Details Slide-over Panel (Modal) */}
      {selectedUserId && (
        <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-sm">
          {/* Overlay click to close */}
          <div className="flex-1" onClick={() => setSelectedUserId(null)}></div>
          
          {/* Drawer Content */}
          <div className="w-full max-w-lg bg-gray-900 border-l border-gray-800 h-full p-6 flex flex-col overflow-y-auto space-y-6">
            <div className="flex items-center justify-between border-b border-gray-800 pb-4">
              <div className="space-y-1">
                <p className="text-xs text-brand-500 font-bold font-mono uppercase">Profile Inspector</p>
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                  {selectedUserId}
                  {selectedUser?.anomaly_label === "Suspicious" && (
                    <span className="text-xs bg-danger/10 text-danger border border-danger/25 px-1.5 py-0.5 rounded font-normal">
                      Suspicious Anomaly
                    </span>
                  )}
                </h2>
              </div>
              <button
                onClick={() => setSelectedUserId(null)}
                className="p-2 hover:bg-gray-800 rounded-full text-gray-400 hover:text-white transition-colors"
              >
                <X size={20} />
              </button>
            </div>

            {detailLoading ? (
              <div className="flex-1 flex flex-col items-center justify-center gap-3">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-500"></div>
                <p className="text-gray-400 text-xs">Querying security records...</p>
              </div>
            ) : detailError || !selectedUser ? (
              <div className="flex-1 flex flex-col items-center justify-center text-center p-6">
                <AlertTriangle className="text-danger mb-3" size={32} />
                <p className="text-gray-400 text-sm">{detailError || "No data loaded."}</p>
              </div>
            ) : (
              <div className="space-y-6 flex-1 text-sm text-gray-300">
                {/* General Info */}
                <div className="bg-gray-950 border border-gray-850 p-4 rounded-xl space-y-3">
                  <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Demographics</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs text-gray-500">Full Name</p>
                      <p className="font-semibold text-white">{selectedUser.name || "N/A"}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Email Address</p>
                      <p className="text-xs font-mono text-gray-300 break-all">{selectedUser.email || "N/A"}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Role / Designation</p>
                      <p className="text-white">{selectedUser.role || "N/A"}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Department</p>
                      <p className="text-white">{selectedUser.department || "N/A"}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Assigned Team</p>
                      <p className="text-white">{selectedUser.team || "N/A"}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Reporting Manager</p>
                      <p className="text-white">{selectedUser.manager || "N/A"}</p>
                    </div>
                  </div>
                </div>

                {/* Threat Telemetry */}
                <div className="bg-gray-950 border border-gray-850 p-4 rounded-xl space-y-3">
                  <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Risk Evaluation</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs text-gray-500">Risk Assessment Score</p>
                      <p className={`text-xl font-bold mt-1 ${
                        selectedUser.risk_level === "Critical" || selectedUser.risk_level === "High"
                          ? "text-danger"
                          : selectedUser.risk_level === "Medium"
                          ? "text-warning"
                          : "text-safe"
                      }`}>
                        {selectedUser.risk_score?.toFixed(1) || "0.0"}{" "}
                        <span className="text-xs font-normal text-gray-400">({selectedUser.risk_level})</span>
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Anomaly Index Score</p>
                      <p className={`text-xl font-bold mt-1 ${selectedUser.anomaly_label === "Suspicious" ? "text-danger" : "text-gray-400"}`}>
                        {selectedUser.anomaly_score?.toFixed(4) || "0.0000"}{" "}
                        <span className="text-xs font-normal text-gray-400">({selectedUser.anomaly_label})</span>
                      </p>
                    </div>
                    <div className="col-span-2">
                      <p className="text-xs text-gray-500">Security Clearance Status</p>
                      <p className={`inline-block border px-3 py-1 rounded-lg text-sm mt-1.5 ${getStatusBadgeClass(selectedUser.security_status)}`}>
                        {selectedUser.security_status}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Explanation Context */}
                {selectedUser.anomaly_label === "Suspicious" && (
                  <div className="p-4 bg-danger/10 border border-danger/25 rounded-xl flex items-start gap-3">
                    <ShieldAlert className="text-danger flex-shrink-0 mt-0.5" size={20} />
                    <div className="space-y-1">
                      <p className="font-semibold text-danger text-xs uppercase tracking-wider">Flagged Threats Alert</p>
                      <p className="text-gray-400 text-xs leading-relaxed">
                        This user profile represents high behavioral deviations compared to counterparts. Common indicators include elevated off-hours logon schedules, suspicious USB connection ratios, or usage of rare/unauthorized computer endpoints.
                      </p>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
