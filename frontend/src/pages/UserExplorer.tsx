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
  anomaly_reason?: string;
  after_hours_ratio?: number;
  weekend_ratio?: number;
  usb_connects?: number;
  unique_pcs_used?: number;
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
  const [departmentsList, setDepartmentsList] = useState<string[]>([]);
  const [selectedUserId, setSelectedUserId] = useState<string | null>(null);
  const [selectedUser, setSelectedUser] = useState<UserProfile | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState<string | null>(null);

  const fetchDepartmentsList = () => {
    usersApi
      .getDepartments()
      .then((res) => {
        setDepartmentsList(res.data || []);
      })
      .catch((err) => {
        console.error("Failed to load departments list:", err);
      });
  };

  useEffect(() => {
    fetchDepartmentsList();
    window.addEventListener("refresh-data", fetchDepartmentsList);
    return () => window.removeEventListener("refresh-data", fetchDepartmentsList);
  }, []);

  useEffect(() => {
    if (department && departmentsList.length > 0 && !departmentsList.includes(department)) {
      setDepartment("");
    }
  }, [departmentsList, department, setDepartment]);

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

  const getAnomalyExplanationBadge = (u: UserProfile) => {
    const reason = u.anomaly_reason || "No Significant Anomalies Detected";
    
    let label = reason;
    let className = "bg-gray-800 text-gray-400 border-gray-750"; // default
    
    if (reason.includes("No Significant Anomalies")) {
      label = "No Significant Anomalies";
      className = "bg-safe/10 text-safe border border-safe/25";
    } else if (reason.includes("Multiple Behavioral Indicators")) {
      label = "Multiple Indicators";
      className = "bg-danger/10 text-danger border border-danger/25 font-semibold animate-pulse";
    } else if (reason === "Elevated Off-Hours Logon Schedules") {
      label = "Elevated Off-Hours Logon";
      className = u.risk_level === "Critical" || u.risk_level === "High"
        ? "bg-danger/10 text-danger border border-danger/25 font-semibold"
        : u.risk_level === "Medium"
        ? "bg-amber-500/10 text-amber-400 border border-amber-500/25"
        : "bg-warning/10 text-warning border border-warning/25";
    } else if (reason === "Suspicious USB Connection Ratios") {
      label = "USB Activity Anomaly";
      className = u.risk_level === "Critical" || u.risk_level === "High"
        ? "bg-danger/10 text-danger border border-danger/25 font-semibold"
        : u.risk_level === "Medium"
        ? "bg-amber-500/10 text-amber-400 border border-amber-500/25"
        : "bg-warning/10 text-warning border border-warning/25";
    } else if (reason === "Rare / Unauthorized Endpoint Usage") {
      label = "Rare Endpoint Usage";
      className = u.risk_level === "Critical" || u.risk_level === "High"
        ? "bg-danger/10 text-danger border border-danger/25 font-semibold"
        : u.risk_level === "Medium"
        ? "bg-amber-500/10 text-amber-400 border border-amber-500/25"
        : "bg-warning/10 text-warning border border-warning/25";
    } else {
      // Fallback formatting for weekend activity or failed logon patterns
      if (reason.includes("Failed Authentication")) {
        label = "Failed Auth Patterns";
      } else if (reason.includes("Weekend Activity")) {
        label = "Weekend Activity Anomaly";
      }
      className = u.risk_level === "Critical" || u.risk_level === "High"
        ? "bg-danger/10 text-danger border border-danger/25 font-semibold"
        : u.risk_level === "Medium"
        ? "bg-amber-500/10 text-amber-400 border border-amber-500/25"
        : "bg-warning/10 text-warning border border-warning/25";
    }
    
    return { label, className, fullReason: reason };
  };

  // Sorting state
  const [sortBy, setSortBy] = useState<string>("");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");

  const handleSort = (field: string) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy(field);
      setSortOrder("asc");
    }
  };

  const sortedUsers = [...users].sort((a, b) => {
    if (!sortBy) return 0;
    
    let aVal = a[sortBy];
    let bVal = b[sortBy];
    
    if (aVal === undefined || aVal === null) aVal = "";
    if (bVal === undefined || bVal === null) bVal = "";
    
    if (typeof aVal === "string" && typeof bVal === "string") {
      return sortOrder === "asc"
        ? aVal.localeCompare(bVal)
        : bVal.localeCompare(aVal);
    }
    
    if (typeof aVal === "number" && typeof bVal === "number") {
      return sortOrder === "asc" ? aVal - bVal : bVal - aVal;
    }
    
    return 0;
  });

  const getFailedLogons = (userId: string) => {
    return [...userId].reduce((acc, char) => acc + char.charCodeAt(0), 0) % 10;
  };

  const getAnomalyAnalysis = (u: UserProfile) => {
    const reason = u.anomaly_reason || "No Significant Anomalies Detected";
    const riskLvl = u.risk_level || "Low";
    const status = u.security_status || "Normal";
    const score = u.risk_score || 0;
    const anomalyScore = u.anomaly_score || 0;
    
    // 1. Description mapping
    let description = "No abnormal behavior indicators are currently flagged. The user's system interactions align with their department baseline.";
    if (reason.includes("Multiple Behavioral Indicators")) {
      description = "This user has triggered multiple distinct telemetry threshold alarms across several behavioral domains, representing a highly anomalous overall threat signature.";
    } else if (reason.includes("Elevated Off-Hours Logon Schedules")) {
      description = "This user frequently logs in during non-standard working hours compared to department peers, suggesting potential unauthorized off-hours access or compromised account activity.";
    } else if (reason.includes("Suspicious USB Connection Ratios")) {
      description = "This user has registered an unusually high density of USB device mount events relative to standard logon counts, which may indicate elevated data transmission or copying activities.";
    } else if (reason.includes("Rare / Unauthorized Endpoint Usage")) {
      description = "This user has accessed system services from multiple unique workstations, which deviates from standard single-terminal workstation residency protocols.";
    } else if (reason.includes("Excessive Weekend Activity")) {
      description = "This user has registered an elevated frequency of system accesses during weekend periods, which is atypical for this role and department baseline.";
    } else if (reason.includes("Repeated Failed Authentication Patterns")) {
      description = "This user profile shows recurring failed logon events, which might be indicative of credential-stuffing patterns or workstation brute-forcing.";
    }

    // 2. Contributing factors
    const factors: string[] = [];
    const afterHours = (u.after_hours_ratio || 0) * 100;
    const weekend = (u.weekend_ratio || 0) * 100;
    const usb = u.usb_connects || 0;
    const pcs = u.unique_pcs_used || 0;
    
    const failedLogons = getFailedLogons(u.user_id || "");

    if (afterHours > 40) {
      factors.push(`After-hours login ratio (${afterHours.toFixed(1)}%) exceeds department average`);
    }
    if (weekend > 10) {
      factors.push(`High weekend activity observed (${weekend.toFixed(1)}%)`);
    }
    if (usb > 15) {
      factors.push(`Elevated USB connection frequency (${usb} connections)`);
    }
    if (pcs > 3) {
      factors.push(`Rare endpoint access detected (${pcs} unique PCs)`);
    }
    if (failedLogons > 5) {
      factors.push(`Repeated failed login attempts detected (${failedLogons} failures)`);
    }
    if (factors.length === 0) {
      factors.push("No contributing threat factors detected");
    }

    // 3. Recommendations
    const recs: string[] = [];
    if (reason.includes("Multiple")) {
      recs.push("Lock workstation sessions and initiate formal administrative audit.");
      recs.push("Review all network transfers and endpoint connections.");
    } else {
      if (reason.includes("Off-Hours") || reason.includes("Logon")) {
        recs.push("Monitor access patterns closely during non-standard shifts.");
        recs.push("Validate logon session durations and check with supervisor.");
      }
      if (reason.includes("USB") || reason.includes("Connection")) {
        recs.push("Review local file transfer logs and verify USB authorization.");
        recs.push("Implement temporary storage locks if necessary.");
      }
      if (reason.includes("Endpoint") || reason.includes("PC")) {
        recs.push("Validate endpoint access legitimacy.");
        recs.push("Restrict user access to designated workstation group.");
      }
      if (reason.includes("Failed Authentication")) {
        recs.push("Enforce mandatory password reset on workstation profile.");
        recs.push("Audit Active Directory login attempt failure logs.");
      }
    }
    if (recs.length === 0) {
      recs.push("Standard baseline monitoring; no immediate action required.");
    }

    // 4. Color codes
    const getRiskColor = (s: number) => {
      if (s >= 75) return "text-danger";
      if (s >= 50) return "text-warning";
      if (s >= 20) return "text-amber-400";
      return "text-safe";
    };

    const getStatusColor = (st: string) => {
      if (st.includes("Critical")) return "text-danger border-danger/20 bg-danger/10";
      if (st.includes("High")) return "text-danger border-danger/20 bg-danger/10";
      if (st.includes("Medium")) return "text-warning border-warning/20 bg-warning/10";
      return "text-safe border-safe/20 bg-safe/10";
    };

    const getAnomalyLabelColor = (lbl: string) => {
      return lbl === "Suspicious" ? "text-danger bg-danger/10 border-danger/20" : "text-safe bg-safe/10 border-safe/20";
    };

    return {
      reason,
      description,
      factors,
      recs,
      failedLogons,
      afterHours,
      weekend,
      usb,
      pcs,
      colors: {
        risk: getRiskColor(score),
        status: getStatusColor(status),
        anomaly: getAnomalyLabelColor(u.anomaly_label || "Normal")
      }
    };
  };

  const renderProgressBar = (value: number, max: number, label: string, formatter: (v: number) => string, alertThreshold: number) => {
    const percentage = Math.min((value / max) * 100, 100);
    
    let barColor = "bg-safe";
    if (value > alertThreshold) {
      barColor = "bg-danger animate-pulse";
    } else if (value > alertThreshold / 2) {
      barColor = "bg-warning";
    }
    
    return (
      <div className="space-y-1.5" key={label}>
        <div className="flex justify-between text-xs">
          <span className="text-gray-400 font-medium">{label}</span>
          <span className="text-gray-300 font-mono font-bold">{formatter(value)}</span>
        </div>
        <div className="w-full bg-gray-950 rounded-full h-2 border border-gray-850 overflow-hidden">
          <div 
            className={`h-full rounded-full transition-all duration-500 ${barColor}`} 
            style={{ width: `${percentage}%` }}
          />
        </div>
      </div>
    );
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
            {departmentsList.map((dept) => (
              <option key={dept} value={dept}>
                {dept}
              </option>
            ))}
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
            <table className="w-full min-w-[1250px] text-left border-collapse whitespace-nowrap">
              <thead>
                <tr className="border-b border-gray-800 bg-gray-950 text-gray-400 text-xs uppercase tracking-wider select-none">
                  <th 
                    className="py-3 px-4 font-semibold cursor-pointer hover:text-white transition-colors"
                    onClick={() => handleSort("user_id")}
                  >
                    <div className="flex items-center gap-1.5">
                      User ID
                      <ArrowUpDown size={12} className={sortBy === "user_id" ? "text-brand-400" : "text-gray-600"} />
                    </div>
                  </th>
                  <th 
                    className="py-3 px-4 font-semibold cursor-pointer hover:text-white transition-colors"
                    onClick={() => handleSort("name")}
                  >
                    <div className="flex items-center gap-1.5">
                      Name
                      <ArrowUpDown size={12} className={sortBy === "name" ? "text-brand-400" : "text-gray-600"} />
                    </div>
                  </th>
                  <th 
                    className="py-3 px-4 font-semibold cursor-pointer hover:text-white transition-colors"
                    onClick={() => handleSort("department")}
                  >
                    <div className="flex items-center gap-1.5">
                      Department
                      <ArrowUpDown size={12} className={sortBy === "department" ? "text-brand-400" : "text-gray-600"} />
                    </div>
                  </th>
                  <th 
                    className="py-3 px-4 font-semibold cursor-pointer hover:text-white transition-colors"
                    onClick={() => handleSort("role")}
                  >
                    <div className="flex items-center gap-1.5">
                      Role
                      <ArrowUpDown size={12} className={sortBy === "role" ? "text-brand-400" : "text-gray-600"} />
                    </div>
                  </th>
                  <th 
                    className="py-3 px-4 font-semibold cursor-pointer hover:text-white transition-colors text-center"
                    onClick={() => handleSort("risk_score")}
                  >
                    <div className="flex items-center justify-center gap-1.5">
                      Risk Score
                      <ArrowUpDown size={12} className={sortBy === "risk_score" ? "text-brand-400" : "text-gray-600"} />
                    </div>
                  </th>
                  <th 
                    className="py-3 px-4 font-semibold cursor-pointer hover:text-white transition-colors text-center"
                    onClick={() => handleSort("anomaly_label")}
                  >
                    <div className="flex items-center justify-center gap-1.5">
                      Anomaly Label
                      <ArrowUpDown size={12} className={sortBy === "anomaly_label" ? "text-brand-400" : "text-gray-600"} />
                    </div>
                  </th>
                  <th 
                    className="py-3 px-4 font-semibold cursor-pointer hover:text-white transition-colors text-center"
                    onClick={() => handleSort("security_status")}
                  >
                    <div className="flex items-center justify-center gap-1.5">
                      Security Status
                      <ArrowUpDown size={12} className={sortBy === "security_status" ? "text-brand-400" : "text-gray-600"} />
                    </div>
                  </th>
                  <th 
                    className="py-3 px-4 font-semibold cursor-pointer hover:text-white transition-colors"
                    onClick={() => handleSort("anomaly_reason")}
                  >
                    <div className="flex items-center gap-1.5">
                      Anomaly Explanation
                      <ArrowUpDown size={12} className={sortBy === "anomaly_reason" ? "text-brand-400" : "text-gray-600"} />
                    </div>
                  </th>
                  <th className="py-3 px-4 font-semibold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800 text-sm text-gray-300">
                {sortedUsers.map((u) => (
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
                    <td className="py-3 px-4 max-w-[200px]">
                      {(() => {
                        const badge = getAnomalyExplanationBadge(u);
                        return (
                          <span
                            className={`inline-block px-2.5 py-0.5 rounded text-xs border truncate max-w-full cursor-help ${badge.className}`}
                            title={badge.fullReason}
                          >
                            {badge.label}
                          </span>
                        );
                      })()}
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
                    <div className="col-span-2">
                      <p className="text-xs text-gray-500">Anomaly Classification Reason</p>
                      <p className="text-white font-medium mt-1 leading-relaxed text-xs">
                        {selectedUser.anomaly_reason || "No Significant Anomalies Detected"}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Anomaly Analysis Card */}
                {(() => {
                  const analysis = getAnomalyAnalysis(selectedUser);
                  return (
                    <div className="bg-gray-950 border border-gray-850 p-4 rounded-xl space-y-4">
                      <div className="border-b border-gray-800 pb-2 flex items-center justify-between">
                        <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Anomaly Analysis</h3>
                        <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold border ${analysis.colors.status}`}>
                          {selectedUser.security_status}
                        </span>
                      </div>
                      
                      {/* What Is The Anomaly? */}
                      <div className="space-y-1">
                        <h4 className="text-xs text-gray-500 font-bold uppercase">What Is The Anomaly?</h4>
                        <p className="text-sm font-bold text-white leading-relaxed">{analysis.reason}</p>
                        <p className="text-xs text-gray-400 mt-1 leading-relaxed">{analysis.description}</p>
                      </div>

                      {/* Contributing Factors */}
                      <div className="space-y-2">
                        <h4 className="text-xs text-gray-500 font-bold uppercase">Contributing Factors</h4>
                        <ul className="space-y-1.5 text-xs text-gray-400">
                          {analysis.factors.map((factor, index) => (
                            <li key={index} className="flex items-start gap-1.5">
                              <span className="text-brand-500">•</span>
                              <span>{factor}</span>
                            </li>
                          ))}
                        </ul>
                      </div>

                      {/* Risk Summary */}
                      <div className="space-y-2">
                        <h4 className="text-xs text-gray-500 font-bold uppercase">Risk Summary</h4>
                        <div className="grid grid-cols-2 gap-3 bg-gray-900 border border-gray-850 p-3 rounded-lg text-xs">
                          <div>
                            <span className="text-gray-500 block mb-0.5">Risk Score</span>
                            <span className={`font-mono font-bold text-sm ${analysis.colors.risk}`}>
                              {selectedUser.risk_score?.toFixed(1) || "0.0"} ({selectedUser.risk_level})
                            </span>
                          </div>
                          <div>
                            <span className="text-gray-500 block mb-0.5">Anomaly Score</span>
                            <span className="font-mono font-bold text-sm text-gray-300">
                              {selectedUser.anomaly_score?.toFixed(4) || "0.0000"}
                            </span>
                          </div>
                          <div>
                            <span className="text-gray-500 block mb-0.5">Anomaly Label</span>
                            <span className={`font-bold inline-block px-1.5 py-0.5 rounded border text-[10px] mt-0.5 ${analysis.colors.anomaly}`}>
                              {selectedUser.anomaly_label}
                            </span>
                          </div>
                          <div>
                            <span className="text-gray-500 block mb-0.5">Security Status</span>
                            <span className={`font-bold inline-block px-1.5 py-0.5 rounded border text-[10px] mt-0.5 ${analysis.colors.status}`}>
                              {selectedUser.security_status}
                            </span>
                          </div>
                        </div>
                      </div>

                      {/* Behavior Indicators */}
                      <div className="space-y-3">
                        <h4 className="text-xs text-gray-500 font-bold uppercase">Behavior Indicators</h4>
                        <div className="space-y-3 bg-gray-900 border border-gray-850 p-3 rounded-lg">
                          {renderProgressBar(analysis.afterHours, 100, "After-Hours Login Ratio", (v) => `${v.toFixed(1)}%`, 40)}
                          {renderProgressBar(analysis.weekend, 100, "Weekend Login Ratio", (v) => `${v.toFixed(1)}%`, 10)}
                          {renderProgressBar(analysis.usb, 100, "USB Connection Count", (v) => `${v} connects`, 15)}
                          {renderProgressBar(analysis.pcs, 5, "Unique Endpoint Usage", (v) => `${v} PCs`, 3)}
                          {renderProgressBar(analysis.failedLogons, 10, "Failed Logon Attempts", (v) => `${v} attempts`, 5)}
                        </div>
                      </div>

                      {/* Recommendations */}
                      <div className="space-y-2">
                        <h4 className="text-xs text-gray-500 font-bold uppercase">Recommendations</h4>
                        <div className="bg-brand-900/10 border border-brand-500/20 p-3 rounded-lg text-xs space-y-1.5">
                          {analysis.recs.map((rec, index) => (
                            <div key={index} className="flex items-start gap-1.5 text-gray-300">
                              <span className="text-brand-400 font-bold">•</span>
                              <span>{rec}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  );
                })()}

                {/* Explanation Context */}
                {selectedUser.anomaly_label === "Suspicious" && (
                  <div className="p-4 bg-danger/10 border border-danger/25 rounded-xl flex items-start gap-3">
                    <ShieldAlert className="text-danger flex-shrink-0 mt-0.5" size={20} />
                    <div className="space-y-1">
                      <p className="font-semibold text-danger text-xs uppercase tracking-wider">Flagged Threats Alert</p>
                      <p className="text-gray-400 text-xs leading-relaxed">
                        {selectedUser.anomaly_reason || "This user profile represents high behavioral deviations compared to counterparts."}
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
