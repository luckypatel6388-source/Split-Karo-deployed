import { AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";

interface ErrorMessageProps {
  message: string;
  className?: string;
}

export function ErrorMessage({ message, className }: ErrorMessageProps) {
  return (
    <div
      role="alert"
      className={cn(
        "flex items-start gap-2 rounded-xl bg-red-50 border border-red-100 p-4 text-sm text-red-700",
        className
      )}
    >
      <AlertCircle className="h-4 w-4 mt-0.5 shrink-0" aria-hidden />
      <span>{message}</span>
    </div>
  );
}
