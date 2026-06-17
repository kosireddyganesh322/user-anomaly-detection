import { NavLink } from "react-router-dom";
import { LayoutDashboard, Users, BellRing, BarChart3, ShieldAlert } from "lucide-react";
import clsx from "clsx";

const nav = [
  { to: "/",          label: "Dashboard",     icon: LayoutDashboard },
  { to: "/users",     label: "User Explorer", icon: Users           },
  { to: "/alerts",    label: "Alerts",        icon: BellRing        },
  { to: "/analytics", label: "Analytics",     icon: BarChart3       },
];

export default function Sidebar() {
  return (
    <aside className="w-60 bg-gray-900 border-r border-gray-800 flex flex-col">
      {/* Logo */}
      <div className="flex items-center gap-2 px-5 py-5 border-b border-gray-800">
        <ShieldAlert className="text-brand-500" size={22} />
        <span className="font-semibold text-sm tracking-wide">NFC · Anomaly Detect</span>
      </div>

      {/* Nav links */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {nav.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              clsx(
                "flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors",
                isActive
                  ? "bg-brand-500/20 text-brand-400 font-medium"
                  : "text-gray-400 hover:bg-gray-800 hover:text-gray-100"
              )
            }
          >
            <Icon size={17} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="px-5 py-4 text-xs text-gray-600 border-t border-gray-800">
        NFC / DAE — Internal Use Only
      </div>
    </aside>
  );
}
