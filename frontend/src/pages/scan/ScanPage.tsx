import { useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Camera, Upload, ScanLine, AlertCircle } from "lucide-react";
import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/button";
import { billScanApi } from "@/api/billScan";
import { ApiRequestError } from "@/api/client";

export function ScanPage() {
  const { groupId } = useParams<{ groupId?: string }>();
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Reset input so same file can be re-selected
    e.target.value = "";

    if (file.size > 10 * 1024 * 1024) {
      setError("Image is too large. Maximum size is 10 MB.");
      return;
    }

    setError(null);
    setScanning(true);
    try {
      const result = await billScanApi.scanBill(file);
      // Navigate to review page, passing result and groupId via state
      const reviewPath = groupId
        ? `/groups/${groupId}/scan/review`
        : `/scan/review`;
      navigate(reviewPath, { state: { scanResult: result, groupId: groupId ?? null } });
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.detail : "Scan failed. Please try again.");
      setScanning(false);
    }
  };

  return (
    <div>
      <PageHeader title="Scan Bill" showBack />

      <div className="px-5 pt-8 flex flex-col items-center gap-6">
        <div className="flex flex-col items-center gap-3 text-center">
          <span className="flex h-20 w-20 items-center justify-center rounded-3xl bg-brand-50">
            <ScanLine className="h-10 w-10 text-brand-600" aria-hidden />
          </span>
          <div>
            <h2 className="text-xl font-bold text-ink">Scan your bill</h2>
            <p className="text-sm text-ink-muted mt-1 max-w-xs">
              Take a photo or upload an image. AI will extract the items — you review everything before anything is saved.
            </p>
          </div>
        </div>

        {error && (
          <div className="w-full max-w-xs rounded-xl bg-red-50 border border-red-100 p-4 flex items-start gap-2 text-sm text-red-700">
            <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" aria-hidden />
            <span>{error}</span>
          </div>
        )}

        {scanning ? (
          <div className="flex flex-col items-center gap-3">
            <div className="h-10 w-10 rounded-full border-2 border-brand-200 border-t-brand-600 animate-spin" />
            <p className="text-sm text-ink-muted">AI is reading your bill…</p>
          </div>
        ) : (
          <div className="flex flex-col gap-3 w-full max-w-xs">
            <Button size="lg" className="w-full" onClick={() => cameraInputRef.current?.click()}>
              <Camera className="h-5 w-5" aria-hidden />
              Take Photo
            </Button>
            <Button variant="outline" size="lg" className="w-full" onClick={() => fileInputRef.current?.click()}>
              <Upload className="h-5 w-5" aria-hidden />
              Upload from Gallery
            </Button>
          </div>
        )}

        <p className="text-xs text-ink-subtle text-center max-w-xs">
          Accepts JPEG, PNG, WebP · Max 10 MB
        </p>

        <input ref={cameraInputRef} type="file"
          accept="image/jpeg,image/png,image/webp" capture="environment"
          className="sr-only" onChange={handleFile} aria-hidden />
        <input ref={fileInputRef} type="file"
          accept="image/jpeg,image/png,image/webp"
          className="sr-only" onChange={handleFile} aria-hidden />
      </div>
    </div>
  );
}
