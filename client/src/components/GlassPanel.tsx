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
      className={`rounded-2xl border border-white/10 bg-white/5 shadow-[0_8px_32px_rgba(0,0,0,0.4)] backdrop-blur-2xl ${paddingMap[padding]} ${className}`}
    >
      {children}
    </section>
  );
}
