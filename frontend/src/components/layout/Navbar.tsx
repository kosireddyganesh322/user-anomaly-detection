import { useState, useEffect } from "react";
import { Bell, RefreshCw, Database } from "lucide-react";
import { alertsApi, datasetsApi } from "../../services/api";
import { useNavigate } from "react-router-dom";

export default function Navbar() {
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const [activeDataset, setActiveDataset] = useState<string>("CERT");
  const navigate = useNavigate();

  const fetchUnreadCount = () => {
    alertsApi
      .getAll({ acknowledged: false })
      .then((res) => {
        setUnreadCount(res.data?.length || 0);
      })
      .catch((err) => {
        console.error("Failed to fetch unread alerts count:", err);
      });
  };

  const fetchActiveDataset = () => {
    datasetsApi
      .getActive()
      .then((res) => {
        setActiveDataset(res.data?.name || "CERT");
      })
      .catch((err) => {
        console.error("Failed to fetch active dataset name:", err);
      });
  };

  useEffect(() => {
    fetchUnreadCount();
    fetchActiveDataset();
    // Poll every 30 seconds to update alerts count dynamically
    const interval = setInterval(fetchUnreadCount, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const handleRefresh = () => {
      fetchUnreadCount();
      fetchActiveDataset();
    };
    window.addEventListener("refresh-data", handleRefresh);
    return () => window.removeEventListener("refresh-data", handleRefresh);
  }, []);

  const handleRefresh = () => {
    fetchUnreadCount();
    fetchActiveDataset();
    // Emit a custom global event to notify other pages (e.g. Alerts page or Dashboard) to refresh
    window.dispatchEvent(new Event("refresh-data"));
  };

  return (
    <header className="h-14 bg-gray-900 border-b border-gray-800 flex items-center justify-between px-6">
      <div className="flex items-center gap-3">
        <span className="text-sm text-gray-400">Nuclear Fuel Complex — Insider Threat Detection System</span>
        <span className="flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-extrabold bg-brand-500/10 text-brand-400 border border-brand-500/25 uppercase tracking-wider">
          <Database size={10} />
          Active: {activeDataset === "CERT" ? "CERT Dataset" : activeDataset}
        </span>
      </div>
      <div className="flex items-center gap-4">
        <button 
          onClick={handleRefresh}
          className="text-gray-400 hover:text-white transition-colors" 
          title="Refresh Data"
        >
          <RefreshCw size={17} />
        </button>
        <button 
          onClick={() => navigate("/alerts")}
          className="relative text-gray-400 hover:text-white transition-colors" 
          title="Alerts"
        >
          <Bell size={17} />
          {unreadCount > 0 && (
            <span className="absolute -top-1.5 -right-1.5 bg-danger text-white text-[9px] font-extrabold w-4 h-4 rounded-full flex items-center justify-center border border-gray-900 animate-pulse">
              {unreadCount > 99 ? "99+" : unreadCount}
            </span>
          )}
        </button>
        <div className="w-8 h-8 rounded-full bg-brand-500 flex items-center justify-center text-xs font-bold text-white">
          A
        </div>
      </div>
    </header>
  );
}

