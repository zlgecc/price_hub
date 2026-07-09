import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getItemHistory } from "../api/client";
import { SubscribeButton } from "../components/SubscribeButton";
import { TrendChart } from "../components/TrendChart";
import type { ItemDetail } from "../types";
import { changeColor, formatChange, formatPrice } from "../utils/format";

export function DetailPage() {
  const { code } = useParams<{ code: string }>();
  const [detail, setDetail] = useState<ItemDetail | null>(null);
  const [days, setDays] = useState(30);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!code) return;
    setLoading(true);
    getItemHistory(code, days)
      .then(setDetail)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [code, days]);

  if (loading) return <p className="text-slate-500">加载中...</p>;
  if (error) return <p className="text-red-600">{error}</p>;
  if (!detail) return <p className="text-slate-500">未找到该品种</p>;

  return (
    <div className="space-y-6">
      <Link to="/catalog" className="text-sm text-blue-600 hover:underline">
        ← 返回目录
      </Link>

      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">{detail.name}</h1>
          <p className="mt-1 text-slate-500">
            {detail.category_name} · {detail.region} · {detail.source}
          </p>
        </div>
        <SubscribeButton code={detail.code} />
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-6">
        <div className="flex items-end gap-4">
          <p className="text-4xl font-bold">{formatPrice(detail.latest_price)}</p>
          <p className="text-sm text-slate-400">{detail.unit}</p>
          <p className={`text-lg font-medium ${changeColor(detail.change_pct)}`}>
            {formatChange(detail.change_pct)}
          </p>
        </div>
        {detail.record_date && (
          <p className="mt-2 text-sm text-slate-400">更新于 {detail.record_date}</p>
        )}
      </div>

      <div>
        <div className="mb-3 flex items-center gap-2">
          <span className="text-sm text-slate-500">趋势周期：</span>
          {[30, 90, 180].map((d) => (
            <button
              key={d}
              type="button"
              onClick={() => setDays(d)}
              className={`rounded-lg px-3 py-1 text-sm ${
                days === d
                  ? "bg-blue-600 text-white"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              {d} 天
            </button>
          ))}
        </div>
        <TrendChart history={detail.history} unit={detail.unit} />
      </div>
    </div>
  );
}
