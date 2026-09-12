import { Outlet } from "react-router-dom";
import { BottomNav } from "./BottomNav";

/**
 * AppShell wraps authenticated pages.
 * Renders the page content via <Outlet> and the persistent BottomNav.
 */
export function AppShell() {
  return (
    <div className="flex flex-col min-h-dvh bg-surface">
      {/* Page content — padded above bottom nav */}
      <main className="flex-1 pb-safe">
        <Outlet />
      </main>
      <BottomNav />
    </div>
  );
}
