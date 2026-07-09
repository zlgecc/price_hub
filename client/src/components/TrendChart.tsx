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
      <div className="flex h-64 items-center justify-center rounded-xl border border-dashed border-white/10 bg-white/3 text-sm text-slate-500">
        暂无历史数据
      </div>
    );
  }

  const data = history.map((r) => ({
    date: r.record_date.slice(5),
    price: Number(r.price),
  }));

  return (
    <div className="h-72 w-full rounded-xl border border-white/8 bg-black/20 p-4">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.06)" vertical={false} />
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
              border: "1px solid rgba(255, 255, 255, 0.1)",
              background: "rgba(15, 15, 20, 0.92)",
              backdropFilter: "blur(12px)",
              boxShadow: "0 8px 24px rgba(0, 0, 0, 0.5)",
              color: "#e2e8f0",
            }}
            itemStyle={{ color: "#a5b4fc" }}
            labelStyle={{ color: "#94a3b8" }}
            formatter={(value) => {
              const num = Number(value);
              return [`${Number.isFinite(num) ? num : value} ${unit ?? ""}`, "价格"];
            }}
            labelFormatter={(label) => `日期: ${label}`}
          />
          <Line
            type="monotone"
            dataKey="price"
            stroke="#818cf8"
            strokeWidth={2.5}
            dot={false}
            activeDot={{ r: 4, fill: "#818cf8", strokeWidth: 0 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
