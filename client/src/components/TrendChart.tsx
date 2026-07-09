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
      <div className="flex h-64 items-center justify-center rounded-xl border border-dashed border-slate-200 text-slate-400">
        暂无历史数据
      </div>
    );
  }

  const data = history.map((r) => ({
    date: r.record_date.slice(5),
    price: Number(r.price),
  }));

  return (
    <div className="h-72 w-full rounded-xl border border-slate-200 bg-white p-4">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="date" tick={{ fontSize: 12 }} stroke="#94a3b8" />
          <YAxis tick={{ fontSize: 12 }} stroke="#94a3b8" domain={["auto", "auto"]} />
          <Tooltip
            formatter={(value) => {
              const num = Number(value);
              return [`${Number.isFinite(num) ? num : value} ${unit ?? ""}`, "价格"];
            }}
            labelFormatter={(label) => `日期: ${label}`}
          />
          <Line
            type="monotone"
            dataKey="price"
            stroke="#2563eb"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
