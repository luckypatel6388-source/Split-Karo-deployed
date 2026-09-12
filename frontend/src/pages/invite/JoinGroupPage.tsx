import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { Check, Users } from "lucide-react";
import { groupsApi } from "@/api/groups";
import { ApiRequestError } from "@/api/client";
import { useAuthStore } from "@/store/authStore";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { FullPageSpinner } from "@/components/shared/LoadingSpinner";
import type { InvitePreviewResponse } from "@/types/api";

export function JoinGroupPage() {
  const { token } = useParams<{ token: string }>();
  const navigate = useNavigate();
  const { isAuthenticated, isLoading: authLoading } = useAuthStore();
  const [invite, setInvite] = useState<InvitePreviewResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [joining, setJoining] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    groupsApi.getInvitePreview(token)
      .then(setInvite)
      .catch((err) => setError(err instanceof ApiRequestError ? err.detail : "This invite is unavailable."))
      .finally(() => setLoading(false));
  }, [token]);

  if (loading || authLoading) return <FullPageSpinner />;

  const join = async () => {
    if (!token) return;
    if (!isAuthenticated) {
      navigate(`/login?next=${encodeURIComponent(`/join/${token}`)}`);
      return;
    }
    setJoining(true);
    setError(null);
    try {
      const result = await groupsApi.joinGroup(token);
      navigate(`/groups/${result.group_id}`, { replace: true });
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.detail : "Could not join this group.");
      setJoining(false);
    }
  };

  return (
    <div className="min-h-dvh bg-surface flex items-center justify-center px-5 py-10">
      <Card className="w-full max-w-sm">
        <CardContent className="pt-7 pb-7 text-center">
          <span className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-50 text-brand-600">
            <Users className="h-7 w-7" aria-hidden />
          </span>
          {error && !invite ? (
            <>
              <h1 className="mt-5 text-xl font-bold text-ink">Invite unavailable</h1>
              <p className="mt-2 text-sm text-red-600">{error}</p>
              <Link to="/" className="mt-6 inline-block text-sm font-medium text-brand-600">Go to SplitKaro</Link>
            </>
          ) : invite ? (
            <>
              <h1 className="mt-5 text-xl font-bold text-ink">Join {invite.group_name}</h1>
              <p className="mt-2 text-sm text-ink-muted">{invite.group_description ?? "You have been invited to split expenses with this group."}</p>
              {invite.expires_at && <p className="mt-3 text-xs text-ink-subtle">Invite expires {new Date(invite.expires_at).toLocaleDateString()}</p>}
              {error && <p className="mt-4 text-sm text-red-600">{error}</p>}
              <Button className="mt-6 w-full" onClick={join} disabled={joining}>
                <Check className="h-4 w-4" aria-hidden />
                {joining ? "Joining…" : isAuthenticated ? "Join group" : "Log in to join"}
              </Button>
              {!isAuthenticated && (
                <p className="mt-4 text-xs text-ink-muted">
                  New to SplitKaro?{" "}
                  <Link className="font-medium text-brand-600" to={`/register?next=${encodeURIComponent(`/join/${token}`)}`}>
                    Create an account
                  </Link>
                </p>
              )}
            </>
          ) : null}
        </CardContent>
      </Card>
    </div>
  );
}