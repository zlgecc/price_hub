import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { PriceRecord } from "../types";

interface Props {
  history: PriceRecord[];
  unit?: string;
}

export function TrendChart({ history, unit }: Props) {
  if (!history.length) {
    return (
      <div className="flex h-64 items-center justify-center rounded-xl border border-dashed border-slate-200/80 bg-white/30 text-sm text-slate-400">
        暂无历史数据
      </div>
    );
  }

  const data = history.map((r) => ({
    date: r.record_date.slice(5),
    price: Number(r.price),
  }));

  return (
    <div className="h-72 w-full rounded-xl border border-slate-200/60 bg-white/40 p-4">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.25)" vertical={false} />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 12, fill: "#64748b" }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 12, fill: "#64748b" }}
            axisLine={false}
            tickLine={false}
            domain={["auto", "auto"]}
          />
          <Tooltip
            contentStyle={{
              borderRadius: "12px",
              border: "1px solid rgba(226, 232, 240, 0.8)",
              background: "rgba(255, 255, 255, 0.9)",
              backdropFilter: "blur(12px)",
              boxShadow: "0 8px 24px rgba(15, 23, 42, 0.08)",
            }}
            formatter={(value) => {
              const num = Number(value);
              return [`${Number.isFinite(num) ? num : value} ${unit ?? ""}`, "价格"];
            }}
            labelFormatter={(label) => `日期: ${label}`}
          />
          <Line
            type="monotone"
            dataKey="price"
            stroke="#4f46e5"
            strokeWidth={2.5}
            dot={false}
            activeDot={{ r: 4, fill: "#4f46e5", strokeWidth: 0 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
