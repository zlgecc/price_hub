type NumericInput = number | string | null | undefined;

function toNumber(value: NumericInput): number | null {
  if (value == null || value === "") return null;
  const num = typeof value === "number" ? value : Number(value);
  return Number.isFinite(num) ? num : null;
}

export function formatPrice(price: NumericInput, unit?: string): string {
  const num = toNumber(price);
  if (num == null) return "—";
  const formatted = num.toLocaleString("zh-CN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 4,
  });
  return unit ? `${formatted} ${unit}` : formatted;
}

export function formatChange(pct: NumericInput): string {
  const num = toNumber(pct);
  if (num == null) return "—";
  const sign = num > 0 ? "+" : "";
  return `${sign}${num.toFixed(2)}%`;
}

export function changeColor(pct: NumericInput): string {
  const num = toNumber(pct);
  if (num == null) return "text-slate-500";
  if (num > 0) return "text-red-400";
  if (num < 0) return "text-emerald-400";
  return "text-slate-500";
}
