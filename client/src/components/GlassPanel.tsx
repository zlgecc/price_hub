import type { ReactNode } from "react";

interface Props {
  children: ReactNode;
  className?: string;
  padding?: "none" | "sm" | "md" | "lg";
}

const paddingMap = {
  none: "",
  sm: "p-4",
  md: "p-6",
  lg: "p-8",
};

export function GlassPanel({ children, className = "", padding = "md" }: Props) {
  return (
    <section
      className={`rounded-2xl border border-white/70 bg-white/60 shadow-[0_8px_32px_rgba(15,23,42,0.06)] backdrop-blur-2xl ${paddingMap[padding]} ${className}`}
    >
      {children}
    </section>
  );
}
