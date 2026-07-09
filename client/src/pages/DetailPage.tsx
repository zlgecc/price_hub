import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getItemHistory } from "../api/client";
import { GlassPanel } from "../components/GlassPanel";
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

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="loading-shimmer h-10 w-32" />
        <div className="loading-shimmer h-40" />
        <div className="loading-shimmer h-80" />
      </div>
    );
  }
  if (error) {
    return (
      <GlassPanel>
        <p className="text-sm text-red-600">{error}</p>
      </GlassPanel>
    );
  }
  if (!detail) {
    return (
      <GlassPanel>
        <p className="text-sm text-slate-500">未找到该品种</p>
      </GlassPanel>
    );
  }

  const historyRows = [...detail.history].reverse();

  return (
    <div className="space-y-6">
      <Link to="/catalog" className="glass-button inline-flex">
        ← 返回目录
      </Link>

      <GlassPanel padding="lg">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-xs font-medium uppercase tracking-wider text-indigo-500">
              {detail.category_name}
            </p>
            <h1 className="mt-2 text-3xl font-semibold tracking-tight text-slate-900">{detail.name}</h1>
            <p className="mt-2 text-sm text-slate-500">
              {detail.region} · {detail.source}
            </p>
          </div>
          <SubscribeButton code={detail.code} />
        </div>

        <div className="mt-8 grid gap-4 sm:grid-cols-3">
          <div className="rounded-xl border border-slate-200/60 bg-white/50 px-5 py-4 sm:col-span-2">
            <p className="text-xs font-medium uppercase tracking-wider text-slate-400">最新价格</p>
            <div className="mt-2 flex flex-wrap items-end gap-3">
              <p className="text-4xl font-semibold tabular-nums text-slate-900">
                {formatPrice(detail.latest_price)}
              </p>
              <p className="pb-1 text-sm text-slate-400">{detail.unit}</p>
            </div>
          </div>
          <div className="rounded-xl border border-slate-200/60 bg-white/50 px-5 py-4">
            <p className="text-xs font-medium uppercase tracking-wider text-slate-400">涨跌幅</p>
            <p className={`mt-2 text-3xl font-semibold tabular-nums ${changeColor(detail.change_pct)}`}>
              {formatChange(detail.change_pct)}
            </p>
            {detail.record_date && (
              <p className="mt-2 text-xs text-slate-400">更新于 {detail.record_date}</p>
            )}
          </div>
        </div>
      </GlassPanel>

      <GlassPanel>
        <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-lg font-semibold text-slate-900">价格趋势</h2>
          <div className="flex gap-2">
            {[30, 90, 180].map((d) => (
              <button
                key={d}
                type="button"
                onClick={() => setDays(d)}
                className={days === d ? "glass-button glass-button--active" : "glass-button"}
              >
                {d} 天
              </button>
            ))}
          </div>
        </div>
        <TrendChart history={detail.history} unit={detail.unit} />
      </GlassPanel>

      <GlassPanel>
        <h2 className="mb-5 text-lg font-semibold text-slate-900">历史数据</h2>
        <div className="overflow-hidden rounded-xl border border-slate-200/60 bg-white/40">
          <div className="max-h-96 overflow-auto">
            <table className="w-full border-collapse text-left text-sm">
              <thead className="sticky top-0 bg-slate-50/90 backdrop-blur-md">
                <tr className="border-b border-slate-200/70 text-xs font-medium uppercase tracking-wider text-slate-500">
                  <th className="px-5 py-3 font-medium">日期</th>
                  <th className="px-5 py-3 text-right font-medium">价格</th>
                  <th className="px-5 py-3 text-right font-medium">涨跌</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200/50">
                {historyRows.map((row) => (
                  <tr key={row.record_date} className="transition-colors hover:bg-white/60">
                    <td className="px-5 py-3 text-slate-600">{row.record_date}</td>
                    <td className="px-5 py-3 text-right font-medium tabular-nums text-slate-900">
                      {formatPrice(row.price)} <span className="text-xs text-slate-400">{detail.unit}</span>
                    </td>
                    <td className={`px-5 py-3 text-right font-medium tabular-nums ${changeColor(row.change_pct)}`}>
                      {formatChange(row.change_pct)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </GlassPanel>
    </div>
  );
}
