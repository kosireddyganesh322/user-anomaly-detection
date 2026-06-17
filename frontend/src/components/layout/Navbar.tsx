import { Bell, RefreshCw } from "lucide-react";

export default function Navbar() {
  return (
    <header className="h-14 bg-gray-900 border-b border-gray-800 flex items-center justify-between px-6">
      <span className="text-sm text-gray-400">Nuclear Fuel Complex — Insider Threat Detection System</span>
      <div className="flex items-center gap-4">
        <button className="text-gray-400 hover:text-white transition-colors" title="Refresh">
          <RefreshCw size={17} />
        </button>
        <button className="relative text-gray-400 hover:text-white transition-colors" title="Alerts">
          <Bell size={17} />
          {/* TODO: badge count */}
        </button>
        <div className="w-8 h-8 rounded-full bg-brand-500 flex items-center justify-center text-xs font-bold">
          A
        </div>
      </div>
    </header>
  );
}
