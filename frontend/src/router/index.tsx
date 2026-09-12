import { Routes, Route, Navigate } from "react-router-dom";
import { AppShell } from "@/components/layout/AppShell";
import { AuthGuard, GuestGuard } from "./AuthGuard";

// Auth
import { LoginPage } from "@/pages/auth/LoginPage";
import { RegisterPage } from "@/pages/auth/RegisterPage";

// App pages
import { HomePage } from "@/pages/home/HomePage";
import { GroupsPage } from "@/pages/groups/GroupsPage";
import { CreateGroupPage } from "@/pages/groups/CreateGroupPage";
import { GroupDetailPage } from "@/pages/groups/GroupDetailPage";
import { CreateExpensePage } from "@/pages/expenses/CreateExpensePage";
import { ScanPage } from "@/pages/scan/ScanPage";
import { BillReviewPage } from "@/pages/scan/BillReviewPage";
import { SettlementsPage } from "@/pages/settlements/SettlementsPage";
import { PaymentPage } from "@/pages/payments/PaymentPage";
import { ActivityPage } from "@/pages/activity/ActivityPage";
import { ProfilePage } from "@/pages/profile/ProfilePage";
import { JoinGroupPage } from "@/pages/invite/JoinGroupPage";
import { ExpenseDetailPage } from "@/pages/expenses/ExpenseDetailPage";

export function AppRouter() {
  return (
    <Routes>
      {/* Guest-only */}
      <Route element={<GuestGuard />}>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
      </Route>
      <Route path="/join/:token" element={<JoinGroupPage />} />

      {/* Authenticated */}
      <Route element={<AuthGuard />}>
        <Route element={<AppShell />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/groups" element={<GroupsPage />} />
          <Route path="/groups/new" element={<CreateGroupPage />} />
          <Route path="/groups/:groupId" element={<GroupDetailPage />} />
          <Route path="/groups/:groupId/expense" element={<CreateExpensePage />} />
          <Route path="/expenses/:expenseId" element={<ExpenseDetailPage />} />
          <Route path="/groups/:groupId/scan" element={<ScanPage />} />
          <Route path="/groups/:groupId/scan/review" element={<BillReviewPage />} />
          <Route path="/groups/:groupId/settlements" element={<SettlementsPage />} />
          <Route path="/groups/:groupId/payment/:settlementId" element={<PaymentPage />} />
          {/* Top-level scan (no group context yet) */}
          <Route path="/scan" element={<ScanPage />} />
          <Route path="/scan/review" element={<BillReviewPage />} />
          <Route path="/activity" element={<ActivityPage />} />
          <Route path="/profile" element={<ProfilePage />} />
        </Route>
      </Route>

      {/* Catch-all */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
