import { NavLink, useNavigate } from "react-router-dom";
import { Home, Users, ScanLine, Activity, User } from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { to: "/", label: "Home", icon: Home, exact: true },
  { to: "/groups", label: "Groups", icon: Users, exact: false },
  { to: "/scan", label: "Scan", icon: ScanLine, exact: false, isPrimary: true },
  { to: "/activity", label: "Activity", icon: Activity, exact: false },
  { to: "/profile", label: "Profile", icon: User, exact: false },
];

export function BottomNav() {
  const navigate = useNavigate();

  return (
    <nav
      aria-label="Main navigation"
      className="fixed bottom-0 left-0 right-0 z-50 bg-surface-card border-t border-border/60 flex items-end justify-around px-2"
      style={{ paddingBottom: "env(safe-area-inset-bottom)" }}
    >
      {navItems.map(({ to, label, icon: Icon, exact, isPrimary }) => {
        if (isPrimary) {
          return (
            <button
              key={to}
              onClick={() => navigate(to)}
              aria-label="Scan bill"
              className="flex flex-col items-center -mt-5 mb-1"
            >
              {/* Floating action button for Scan */}
              <span className="flex h-14 w-14 items-center justify-center rounded-full bg-brand-600 text-white shadow-lg shadow-brand-600/30 active:scale-95 transition-transform">
                <Icon className="h-6 w-6" aria-hidden />
              </span>
              <span className="text-[10px] font-medium text-brand-600 mt-1">
                {label}
              </span>
            </button>
          );
        }

        return (
          <NavLink
            key={to}
            to={to}
            end={exact}
            className={({ isActive }) =>
              cn(
                "flex flex-col items-center justify-center gap-0.5 py-3 px-3 min-w-[56px] transition-colors",
                isActive ? "text-brand-600" : "text-ink-subtle"
              )
            }
          >
            {({ isActive }) => (
              <>
                <Icon
                  className={cn(
                    "h-5 w-5 transition-transform",
                    isActive && "scale-110"
                  )}
                  aria-hidden
                />
                <span className="text-[10px] font-medium">{label}</span>
              </>
            )}
          </NavLink>
        );
      })}
    </nav>
  );
}
