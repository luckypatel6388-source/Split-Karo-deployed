import { ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { cn } from "@/lib/utils";

interface PageHeaderProps {
  title: string;
  showBack?: boolean;
  onBack?: () => void;
  right?: React.ReactNode;
  className?: string;
}

export function PageHeader({
  title,
  showBack = false,
  onBack,
  right,
  className,
}: PageHeaderProps) {
  const navigate = useNavigate();

  const handleBack = onBack ?? (() => navigate(-1));

  return (
    <header
      className={cn(
        "sticky top-0 z-40 flex items-center gap-3 px-4 py-4 bg-surface/80 backdrop-blur-md border-b border-border/40",
        className
      )}
    >
      {showBack && (
        <button
          onClick={handleBack}
          aria-label="Go back"
          className="flex h-9 w-9 items-center justify-center rounded-xl hover:bg-surface-muted transition-colors"
        >
          <ArrowLeft className="h-5 w-5 text-ink" aria-hidden />
        </button>
      )}
      <h1 className="flex-1 text-lg font-semibold text-ink truncate">{title}</h1>
      {right && <div className="shrink-0">{right}</div>}
    </header>
  );
}
