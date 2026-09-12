import { useState } from "react";
import { LogOut, CreditCard, User, Check, Pencil } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuthStore } from "@/store/authStore";
import { authApi } from "@/api/auth";
import { usersApi } from "@/api/users";
import { ApiRequestError } from "@/api/client";
import type { UpdateUPIResponse } from "@/types/api";

export function ProfilePage() {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();

  const [editingUPI, setEditingUPI] = useState(false);
  const [upiInput, setUpiInput] = useState("");
  const [upiState, setUpiState] = useState<UpdateUPIResponse | null>(null);
  const [upiLoading, setUpiLoading] = useState(false);
  const [upiError, setUpiError] = useState<string | null>(null);

  const handleLogout = async () => {
    await authApi.logout().catch(() => {});
    logout();
    navigate("/login", { replace: true });
  };

  const handleSaveUPI = async () => {
    if (upiInput.trim().length < 5) {
      setUpiError("Enter a valid UPI ID (e.g. name@upi).");
      return;
    }
    setUpiError(null);
    setUpiLoading(true);
    try {
      const res = await usersApi.updateUpi({ upi_id: upiInput.trim() });
      setUpiState(res);
      setEditingUPI(false);
    } catch (err) {
      setUpiError(err instanceof ApiRequestError ? err.detail : "Failed to save UPI ID.");
    } finally {
      setUpiLoading(false);
    }
  };

  const displayUpi = upiState?.upi_id ?? null;

  return (
    <div>
      <PageHeader title="Profile" />
      <div className="px-5 pt-5 flex flex-col gap-4 pb-safe">

        {/* Avatar + name */}
        <div className="flex flex-col items-center gap-3 py-4">
          <div className="h-16 w-16 rounded-full bg-brand-100 flex items-center justify-center text-brand-700 font-bold text-2xl">
            {user?.name?.charAt(0)?.toUpperCase() ?? <User className="h-6 w-6" />}
          </div>
          <div className="text-center">
            <p className="font-semibold text-ink">{user?.name}</p>
            <p className="text-sm text-ink-muted">{user?.email}</p>
          </div>
        </div>

        {/* UPI section */}
        <Card>
          <CardContent className="pt-5 pb-5">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-brand-50">
                  <CreditCard className="h-4 w-4 text-brand-600" aria-hidden />
                </span>
                <div>
                  <p className="text-sm font-medium text-ink">UPI ID</p>
                  {displayUpi ? (
                    <div className="flex items-center gap-1">
                      <p className="text-xs font-mono text-ink-muted">{displayUpi}</p>
                      {upiState?.upi_verified ? (
                        <Check className="h-3 w-3 text-brand-600" aria-label="Verified" />
                      ) : (
                        <span className="text-xs text-amber-600">(unverified)</span>
                      )}
                    </div>
                  ) : (
                    <p className="text-xs text-ink-muted">Not set — required for UPI payments</p>
                  )}
                </div>
              </div>
              <button
                onClick={() => { setEditingUPI(!editingUPI); setUpiInput(displayUpi ?? ""); setUpiError(null); }}
                className="text-xs text-brand-600 font-medium flex items-center gap-1"
              >
                <Pencil className="h-3 w-3" aria-hidden />
                {displayUpi ? "Edit" : "Add"}
              </button>
            </div>

            {editingUPI && (
              <div className="flex flex-col gap-2 mt-2">
                <Label htmlFor="upi-id">Your UPI ID</Label>
                <Input
                  id="upi-id"
                  value={upiInput}
                  onChange={(e) => setUpiInput(e.target.value)}
                  placeholder="yourname@upi"
                  minLength={5}
                  maxLength={100}
                />
                {upiError && <p className="text-xs text-red-600">{upiError}</p>}
                <div className="flex gap-2 mt-1">
                  <Button size="sm" onClick={handleSaveUPI} disabled={upiLoading} className="flex-1">
                    {upiLoading ? "Saving…" : "Save"}
                  </Button>
                  <Button size="sm" variant="outline" onClick={() => setEditingUPI(false)} className="flex-1">
                    Cancel
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Logout */}
        <Button variant="outline" className="w-full" onClick={handleLogout}>
          <LogOut className="h-4 w-4" aria-hidden />
          Log out
        </Button>
      </div>
    </div>
  );
}
