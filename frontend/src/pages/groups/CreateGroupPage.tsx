import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { groupsApi } from "@/api/groups";
import { ApiRequestError } from "@/api/client";

export function CreateGroupPage() {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) { setError("Group name is required."); return; }
    setLoading(true);
    setError(null);
    try {
      const group = await groupsApi.createGroup({
        name: name.trim(),
        description: description.trim() || null,
      });
      navigate(`/groups/${group.id}`, { replace: true });
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.detail : "Failed to create group.");
      setLoading(false);
    }
  };

  return (
    <div>
      <PageHeader title="New Group" showBack />
      <form onSubmit={handleSubmit} className="px-5 pt-6 flex flex-col gap-5">
        {error && (
          <div className="rounded-xl bg-red-50 border border-red-100 p-4 text-sm text-red-700">
            {error}
          </div>
        )}

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="name">Group name *</Label>
          <Input
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Goa Trip, Flat 4B, Movie Night…"
            maxLength={100}
            required
          />
        </div>

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="desc">Description (optional)</Label>
          <Input
            id="desc"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Short description"
            maxLength={500}
          />
        </div>

        <Button type="submit" size="lg" className="w-full" disabled={loading}>
          {loading ? "Creating…" : "Create Group"}
        </Button>
      </form>
    </div>
  );
}
